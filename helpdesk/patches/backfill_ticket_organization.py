import frappe


def execute():
    """
    Backfill `party` (ERPNext Customer) on existing HD Ticket rows.

    Resolution order per ticket:
        1. Contact.Dynamic Link -> Customer
        2. Customer.portal_users manual mapping (raised_by email)
        3. Sender email domain -> Customer.email_domain
    """
    if not frappe.db.has_column("HD Ticket", "party"):
        return
    if not frappe.db.exists("DocType", "Customer"):
        return

    _backfill_from_contact()
    _backfill_from_portal_users()
    _backfill_from_email_domain()


def _backfill_from_contact():
    frappe.db.sql(
        """
        UPDATE `tabHD Ticket` t
        INNER JOIN `tabDynamic Link` dl
            ON dl.parent = t.contact
           AND dl.parenttype = 'Contact'
           AND dl.link_doctype = 'Customer'
        SET t.party = dl.link_name
        WHERE (t.party IS NULL OR t.party = '')
          AND t.contact IS NOT NULL
        """
    )


def _backfill_from_portal_users():
    frappe.db.sql(
        """
        UPDATE `tabHD Ticket` t
        INNER JOIN `tabPortal User` pu
            ON pu.parenttype = 'Customer'
           AND pu.user = t.raised_by
        SET t.party = pu.parent
        WHERE (t.party IS NULL OR t.party = '')
        """
    )


def _backfill_from_email_domain():
    if not frappe.db.has_column("Customer", "email_domain"):
        return
    customers = frappe.get_all(
        "Customer",
        filters=[["email_domain", "is", "set"]],
        fields=["name", "email_domain"],
    )
    for c in customers:
        domain = (c.email_domain or "").lower().strip()
        if not domain:
            continue
        frappe.db.sql(
            """
            UPDATE `tabHD Ticket`
            SET party = %s
            WHERE (party IS NULL OR party = '')
              AND LOWER(SUBSTRING_INDEX(raised_by, '@', -1)) = %s
            """,
            (c.name, domain),
        )
