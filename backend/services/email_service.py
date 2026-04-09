"""
email_service.py - SMTP Email Notification and Reminder Service

Responsibilities:
  1. Immediate confirmation emails on application submission (all service types)
  2. Scheduled 3-day follow-up reminder emails for all Pending applications

Design:
  - All SMTP credentials loaded exclusively from environment variables
  - Email dispatch is always non-blocking (background daemon thread)
  - Reminder logic is service-agnostic: adding a new service type requires
    only registering it in REMINDER_REGISTRY below - no other changes needed
  - HTML email templates are clean, professional, and university-appropriate
"""

import smtplib
import threading
import logging
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from config import Config

logger = logging.getLogger(__name__)


# ==============================================================
# EMAIL TEMPLATE BUILDER
# ==============================================================

def _base_template(service_name: str, notification_type: str, body_rows: list, action_text: str) -> str:
    """
    Builds a consistent HTML email for any service type.

    Args:
        service_name    : e.g. "Letter of Recommendation"
        notification_type: e.g. "Application Received" or "Follow-up Reminder"
        body_rows       : list of (label, value) tuples for the detail table
        action_text     : instruction paragraph shown below the table
    """
    rows_html = ""
    for i, (label, value) in enumerate(body_rows):
        bg = "background:#FAFAFA;" if i % 2 == 0 else ""
        rows_html += f"""
          <tr style="{bg}">
            <td style="padding:10px;border:1px solid #E0E0E0;font-weight:600;
                       width:38%;color:#555;">{label}</td>
            <td style="padding:10px;border:1px solid #E0E0E0;">{value}</td>
          </tr>"""

    return f"""<!DOCTYPE html>
<html lang="en">
<head><meta charset="UTF-8"/></head>
<body style="margin:0;padding:0;background:#F5F5F5;font-family:Arial,sans-serif;">
  <table width="100%" cellpadding="0" cellspacing="0"
         style="background:#F5F5F5;padding:30px 0;">
    <tr><td align="center">
      <table width="600" cellpadding="0" cellspacing="0"
             style="background:#FFFFFF;border-radius:6px;
                    border:1px solid #E0E0E0;overflow:hidden;">

        <!-- Header -->
        <tr>
          <td style="background:#E65100;padding:20px 28px;">
            <p style="margin:0;color:#FFFFFF;font-size:18px;font-weight:bold;">
              Manipal University Jaipur
            </p>
            <p style="margin:4px 0 0;color:rgba(255,255,255,0.85);font-size:13px;">
              Academic Services Portal — {service_name}
            </p>
          </td>
        </tr>

        <!-- Notification type banner -->
        <tr>
          <td style="background:#FFF3E0;padding:10px 28px;
                     border-bottom:1px solid #FFE0B2;">
            <p style="margin:0;font-size:12px;font-weight:600;
                      color:#E65100;text-transform:uppercase;
                      letter-spacing:0.5px;">
              {notification_type}
            </p>
          </td>
        </tr>

        <!-- Body -->
        <tr>
          <td style="padding:28px;">

            <!-- Detail table -->
            <table width="100%" cellpadding="0" cellspacing="0"
                   style="border-collapse:collapse;margin-bottom:20px;">
              {rows_html}
            </table>

            <!-- Action box -->
            <table width="100%" cellpadding="0" cellspacing="0">
              <tr>
                <td style="background:#FFF3E0;border-left:4px solid #E65100;
                           padding:14px 16px;border-radius:0 4px 4px 0;">
                  <p style="margin:0;font-size:13px;color:#333;line-height:1.6;">
                    {action_text}
                  </p>
                </td>
              </tr>
            </table>

          </td>
        </tr>

        <!-- Footer -->
        <tr>
          <td style="background:#F9F9F9;padding:14px 28px;
                     border-top:1px solid #E0E0E0;">
            <p style="margin:0;font-size:11px;color:#999;line-height:1.5;">
              This is an automated message from the Manipal University Jaipur
              Academic Services Portal. Please do not reply to this email.
              For queries, contact your department office directly.
            </p>
          </td>
        </tr>

      </table>
    </td></tr>
  </table>
</body>
</html>"""


# ==============================================================
# CONFIRMATION EMAIL BUILDERS  (called immediately on submission)
# ==============================================================

def _build_lor_confirmation(student_name: str, app: dict) -> str:
    rows = [
        ("Student Name",   student_name),
        ("Application ID", f"<span style='font-family:monospace;'>{app['application_id']}</span>"),
        ("Faculty",        app["faculty_name"]),
        ("Purpose",        app["purpose"]),
        ("Status",         f"<strong style='color:#E65100;'>{app['status']}</strong>"),
        ("Submitted On",   app["submitted_on"]),
    ]
    action = (
        f"Please report your application progress to <strong>{app['faculty_name']}</strong> "
        f"within <strong>3 working days</strong>. Carry your Application ID for reference."
    )
    return _base_template(
        "Letter of Recommendation",
        "Application Received",
        rows, action
    )


def _build_bonafide_confirmation(student_name: str, app: dict) -> str:
    rows = [
        ("Student Name",   student_name),
        ("Application ID", f"<span style='font-family:monospace;'>{app['application_id']}</span>"),
        ("Purpose",        app["purpose"]),
        ("Status",         f"<strong style='color:#E65100;'>{app['status']}</strong>"),
        ("Submitted On",   app["submitted_on"]),
    ]
    action = (
        "Please visit the <strong>Academic Section or Department Office</strong> "
        "within <strong>5 working days</strong> to collect your certificate. "
        "Quote your Application ID when enquiring."
    )
    return _base_template(
        "Bonafide Certificate",
        "Request Received",
        rows, action
    )


def _build_internship_confirmation(student_name: str, app: dict) -> str:
    rows = [
        ("Student Name",   student_name),
        ("Application ID", f"<span style='font-family:monospace;'>{app['application_id']}</span>"),
        ("Company",        app["company_name"]),
        ("Role",           app["internship_role"]),
        ("Type",           app["internship_type"]),
        ("Duration",       f"{app['start_date']} to {app['end_date']}"),
        ("Stipend",        app["stipend"]),
        ("Status",         f"<strong style='color:#E65100;'>{app['status']}</strong>"),
        ("Submitted On",   app["submitted_on"]),
    ]
    action = (
        "Please contact your <strong>Department Coordinator</strong> to follow up "
        "on your internship approval request within <strong>3 working days</strong>."
    )
    return _base_template(
        "Internship Approval",
        "Request Received",
        rows, action
    )


# ==============================================================
# REMINDER EMAIL BUILDERS  (called by scheduler after 3 days)
# ==============================================================

def _build_lor_reminder(student_name: str, app: dict, days: int) -> str:
    rows = [
        ("Student Name",   student_name),
        ("Application ID", f"<span style='font-family:monospace;'>{app['application_id']}</span>"),
        ("Faculty",        app["faculty_name"]),
        ("Purpose",        app["purpose"]),
        ("Current Status", f"<strong style='color:#E65100;'>{app['status']}</strong>"),
        ("Submitted On",   app["submitted_on"]),
        ("Reminder Day",   f"Day {days} follow-up"),
    ]
    action = (
        f"This is a follow-up reminder. Your Letter of Recommendation application "
        f"has been pending for <strong>{days} days</strong>. "
        f"Please visit <strong>{app['faculty_name']}</strong> at the earliest "
        f"to check the status of your application."
    )
    return _base_template(
        "Letter of Recommendation",
        f"Follow-up Reminder — Day {days}",
        rows, action
    )


def _build_bonafide_reminder(student_name: str, app: dict, days: int) -> str:
    rows = [
        ("Student Name",   student_name),
        ("Application ID", f"<span style='font-family:monospace;'>{app['application_id']}</span>"),
        ("Purpose",        app["purpose"]),
        ("Current Status", f"<strong style='color:#E65100;'>{app['status']}</strong>"),
        ("Submitted On",   app["submitted_on"]),
        ("Reminder Day",   f"Day {days} follow-up"),
    ]
    action = (
        f"This is a follow-up reminder. Your Bonafide Certificate request has been "
        f"pending for <strong>{days} days</strong>. "
        f"Please visit the <strong>Academic Section or Department Office</strong> "
        f"to follow up on your request."
    )
    return _base_template(
        "Bonafide Certificate",
        f"Follow-up Reminder — Day {days}",
        rows, action
    )


def _build_internship_reminder(student_name: str, app: dict, days: int) -> str:
    rows = [
        ("Student Name",   student_name),
        ("Application ID", f"<span style='font-family:monospace;'>{app['application_id']}</span>"),
        ("Company",        app["company_name"]),
        ("Role",           app["internship_role"]),
        ("Current Status", f"<strong style='color:#E65100;'>{app['status']}</strong>"),
        ("Submitted On",   app["submitted_on"]),
        ("Reminder Day",   f"Day {days} follow-up"),
    ]
    action = (
        f"This is a follow-up reminder. Your Internship Approval request has been "
        f"pending for <strong>{days} days</strong>. "
        f"Please contact your <strong>Department Coordinator</strong> "
        f"to check the status of your application."
    )
    return _base_template(
        "Internship Approval",
        f"Follow-up Reminder — Day {days}",
        rows, action
    )


# ==============================================================
# REMINDER REGISTRY
# ---------------------------------------------------------------
# To add a new service (e.g. "ExamPermit"), add one entry here.
# No other changes needed anywhere in the codebase.
#
# Each entry maps a service type string to:
#   - confirmation_builder : fn(student_name, app) -> html
#   - reminder_builder     : fn(student_name, app, days) -> html
#   - confirmation_subject : email subject for immediate notification
#   - reminder_subject     : email subject for scheduled reminders
# ==============================================================

REMINDER_REGISTRY = {
    "LOR": {
        "confirmation_builder": _build_lor_confirmation,
        "reminder_builder":     _build_lor_reminder,
        "confirmation_subject": lambda app: f"Application Received - {app['application_id']}",
        "reminder_subject":     lambda app, days: f"Follow-up Reminder (Day {days}) - {app['application_id']}",
    },
    "Bonafide": {
        "confirmation_builder": _build_bonafide_confirmation,
        "reminder_builder":     _build_bonafide_reminder,
        "confirmation_subject": lambda app: f"Request Received - {app['application_id']}",
        "reminder_subject":     lambda app, days: f"Follow-up Reminder (Day {days}) - {app['application_id']}",
    },
    "Internship": {
        "confirmation_builder": _build_internship_confirmation,
        "reminder_builder":     _build_internship_reminder,
        "confirmation_subject": lambda app: f"Internship Request Received - {app['application_id']}",
        "reminder_subject":     lambda app, days: f"Follow-up Reminder (Day {days}) - {app['application_id']}",
    },
}


# ==============================================================
# PUBLIC NOTIFICATION FUNCTIONS  (called by route handlers)
# ==============================================================

def send_confirmation(student: dict, application: dict):
    """
    Sends an immediate confirmation email for any service type.
    The correct template is resolved automatically from REMINDER_REGISTRY.
    """
    app_type = application.get("type")
    entry    = REMINDER_REGISTRY.get(app_type)
    if not entry:
        logger.warning(f"[EMAIL] No registry entry for type '{app_type}'. Skipping confirmation.")
        return

    html    = entry["confirmation_builder"](student["full_name"], application)
    subject = entry["confirmation_subject"](application)
    _dispatch(
        to_emails=[student["college_email"], student["personal_email"]],
        subject=subject,
        html_body=html
    )


# Legacy named functions kept for backward compatibility with existing routes
def send_lor_notification(student: dict, application: dict):
    send_confirmation(student, application)

def send_bonafide_notification(student: dict, application: dict):
    send_confirmation(student, application)

def send_internship_notification(student: dict, application: dict):
    send_confirmation(student, application)


# ==============================================================
# SMTP TRANSPORT
# ==============================================================

def _dispatch(to_emails: list, subject: str, html_body: str):
    """Launches a daemon thread to send email without blocking the API."""
    thread = threading.Thread(
        target=_send_smtp,
        args=(to_emails, subject, html_body),
        daemon=True
    )
    thread.start()


def _send_smtp(to_emails: list, subject: str, html_body: str):
    """Connects to SMTP server and sends HTML email to all recipients."""
    if not Config.SMTP_ENABLED:
        logger.info(
            f"[EMAIL SKIPPED] SMTP disabled. "
            f"Would send '{subject}' to: {to_emails}"
        )
        return

    if not Config.SMTP_USER or not Config.SMTP_PASS:
        logger.warning("[EMAIL] SMTP_USER or SMTP_PASS not set in .env. Email not sent.")
        return

    try:
        server = smtplib.SMTP(Config.SMTP_HOST, Config.SMTP_PORT)
        server.ehlo()
        server.starttls()
        server.login(Config.SMTP_USER, Config.SMTP_PASS)

        for recipient in to_emails:
            msg             = MIMEMultipart("alternative")
            msg["Subject"]  = subject
            msg["From"]     = f"MUJ Academic Services Portal <{Config.SMTP_USER}>"
            msg["To"]       = recipient
            msg.attach(MIMEText(html_body, "html"))
            server.sendmail(Config.SMTP_USER, recipient, msg.as_string())

        server.quit()
        logger.info(f"[EMAIL SENT] Subject: '{subject}' | To: {to_emails}")

    except smtplib.SMTPAuthenticationError:
        logger.error("[EMAIL] Authentication failed. Verify SMTP_USER and SMTP_PASS in .env.")
    except smtplib.SMTPConnectError:
        logger.error(f"[EMAIL] Could not connect to {Config.SMTP_HOST}:{Config.SMTP_PORT}.")
    except smtplib.SMTPException as e:
        logger.error(f"[EMAIL] SMTP error: {e}")
    except Exception as e:
        logger.error(f"[EMAIL] Unexpected error: {e}")
