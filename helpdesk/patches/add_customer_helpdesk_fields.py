import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields


def execute():
    """
    Add helpdesk-related custom fields on ERPNext Customer so it can serve as
    the billable party on HD Tickets with an email domain and default SLA.
    """
    if not frappe.db.exists("DocType", "Customer"):
        return

    custom_fields = {
        "Customer": [
            {
                "fieldname": "helpdesk_section",
                "label": "Helpdesk",
                "fieldtype": "Section Break",
                "insert_after": "website",
                "collapsible": 1,
            },
            {
                "fieldname": "email_domain",
                "label": "Email Domain",
                "fieldtype": "Data",
                "insert_after": "helpdesk_section",
                "description": "Primary email domain (e.g. bmp.com). Tickets from this domain are auto-classified to this customer.",
                "unique": 1,
            },
            {
                "fieldname": "default_sla",
                "label": "Default SLA",
                "fieldtype": "Link",
                "options": "HD Service Level Agreement",
                "insert_after": "email_domain",
                "description": "If set, tickets for this customer use this SLA by default.",
            },
        ]
    }
    create_custom_fields(custom_fields, ignore_validate=True)
