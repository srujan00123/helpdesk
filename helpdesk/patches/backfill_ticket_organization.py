import frappe


def execute():
    """
    Backfill `organization` on existing HD Ticket rows.

    Resolution order per ticket:
        1. HD Customer.organization (if ticket.customer is set)
        2. Sender email domain -> HD Organization.email_domain
    """
    if not frappe.db.has_column("HD Ticket", "organization"):
        return

    _backfill_from_customer()
    _backfill_from_email_domain()


def _backfill_from_customer():
    frappe.db.sql(
        """
        UPDATE `tabHD Ticket` t
        INNER JOIN `tabHD Customer` c ON t.customer = c.name
        SET t.organization = c.organization
        WHERE (t.organization IS NULL OR t.organization = '')
          AND c.organization IS NOT NULL
          AND c.organization != ''
        """
    )


def _backfill_from_email_domain():
    orgs = frappe.get_all(
        "HD Organization",
        filters=[["email_domain", "is", "set"]],
        fields=["name", "email_domain"],
    )
    for org in orgs:
        domain = (org.email_domain or "").lower().strip()
        if not domain:
            continue
        frappe.db.sql(
            """
            UPDATE `tabHD Ticket`
            SET organization = %s
            WHERE (organization IS NULL OR organization = '')
              AND LOWER(SUBSTRING_INDEX(raised_by, '@', -1)) = %s
            """,
            (org.name, domain),
        )
