import frappe
from frappe import _
from frappe.utils import validate_email_address

from helpdesk.utils import agent_only, get_agent_name, publish_event


@frappe.whitelist()
@agent_only
def sent_invites(emails: list[str], send_welcome_mail_to_user: bool = True):
    """Send agent invitations to the given email addresses."""
    if not emails:
        frappe.throw(_("Please provide at least one email address"))

    for email in emails:
        if not validate_email_address(email, throw=False):
            frappe.throw(_("Invalid email address: {0}").format(email))

        if frappe.db.exists("HD Agent", {"user": email}):
            continue

        if frappe.db.exists("User", email):
            user = frappe.get_doc("User", email)
        else:
            first_name = email.split("@")[0] if "@" in email else email
            user = frappe.get_doc(
                {"doctype": "User", "email": email, "first_name": first_name}
            ).insert()

            if send_welcome_mail_to_user:
                user.send_welcome_mail_to_user()

        frappe.get_doc(
            {
                "doctype": "HD Agent",
                "ID": email,
                "user": user.name,
                "agent_name": user.full_name,
                "user_image": user.user_image,
            }
        ).insert()
    return


@frappe.whitelist()
@agent_only
def set_my_availability(availability: str) -> dict:
    if not frappe.db.exists("HD Agent Status", {"name": availability, "enable": 1}):
        frappe.throw(_("Invalid availability"), frappe.ValidationError)

    name = get_agent_name()
    if not name:
        frappe.throw(_("No HD Agent record for current user"), frappe.ValidationError)

    changed_on = frappe.utils.now()
    frappe.db.set_value(
        "HD Agent",
        name,
        {"availability": availability, "availability_changed_on": changed_on},
    )
    publish_event(
        "agent_availability_updated",
        data={
            "agent": name,
            "availability": availability,
            "availability_changed_on": changed_on,
        },
    )
    return {"availability": availability}
