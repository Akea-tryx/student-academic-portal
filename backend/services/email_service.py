"""
email_service.py — SMTP Email Notification Service
Non-blocking: sends emails in a background thread.
Credentials loaded from environment variables only.
"""
import smtplib
import threading
import logging
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from config import Config

logger = logging.getLogger(__name__)


def _build_lor_email(student_name: str, app: dict) -> str:
    return f"""
    <html>
    <body style="font-family:Arial,sans-serif;color:#333;padding:24px;max-width:600px;">
      <div style="background:#E65100;padding:16px 20px;border-radius:8px 8px 0 0;">
        <h2 style="color:#fff;margin:0;">Academic Services Portal</h2>
        <p style="color:rgba(255,255,255,0.85);margin:4px 0 0;font-size:13px;">
          Automated Notification — Letter of Recommendation
        </p>
      </div>
      <div style="border:1px solid #ddd;border-top:none;padding:24px;border-radius:0 0 8px 8px;">
        <p>Dear <strong>{student_name}</strong>,</p>
        <p>Your <strong>Letter of Recommendation</strong> application has been received.</p>
        <table style="width:100%;border-collapse:collapse;margin:16px 0;">
          <tr style="background:#FFF3E0;">
            <td style="padding:10px;border:1px solid #FFE0B2;font-weight:600;width:40%;">Application ID</td>
            <td style="padding:10px;border:1px solid #FFE0B2;font-family:monospace;">{app['application_id']}</td>
          </tr>
          <tr>
            <td style="padding:10px;border:1px solid #eee;font-weight:600;">Faculty</td>
            <td style="padding:10px;border:1px solid #eee;">{app['faculty_name']}</td>
          </tr>
          <tr style="background:#fafafa;">
            <td style="padding:10px;border:1px solid #eee;font-weight:600;">Purpose</td>
            <td style="padding:10px;border:1px solid #eee;">{app['purpose']}</td>
          </tr>
          <tr>
            <td style="padding:10px;border:1px solid #eee;font-weight:600;">Status</td>
            <td style="padding:10px;border:1px solid #eee;color:#E65100;font-weight:600;">{app['status']}</td>
          </tr>
          <tr style="background:#fafafa;">
            <td style="padding:10px;border:1px solid #eee;font-weight:600;">Submitted On</td>
            <td style="padding:10px;border:1px solid #eee;">{app['submitted_on']}</td>
          </tr>
        </table>
        <div style="background:#FFF3E0;border-left:4px solid #E65100;padding:14px 16px;border-radius:4px;margin:16px 0;">
          <strong>Action Required:</strong><br/>
          Please personally report your application progress to
          <strong>{app['faculty_name']}</strong> within <strong>3 working days</strong>.
        </div>
        <p style="font-size:12px;color:#888;">This is an automated reminder. Do not reply to this email.</p>
      </div>
    </body>
    </html>
    """


def _build_bonafide_email(student_name: str, app: dict) -> str:
    return f"""
    <html>
    <body style="font-family:Arial,sans-serif;color:#333;padding:24px;max-width:600px;">
      <div style="background:#E65100;padding:16px 20px;border-radius:8px 8px 0 0;">
        <h2 style="color:#fff;margin:0;">Academic Services Portal</h2>
        <p style="color:rgba(255,255,255,0.85);margin:4px 0 0;font-size:13px;">
          Automated Notification — Bonafide Certificate
        </p>
      </div>
      <div style="border:1px solid #ddd;border-top:none;padding:24px;border-radius:0 0 8px 8px;">
        <p>Dear <strong>{student_name}</strong>,</p>
        <p>Your <strong>Bonafide Certificate</strong> request has been recorded.</p>
        <table style="width:100%;border-collapse:collapse;margin:16px 0;">
          <tr style="background:#FFF3E0;">
            <td style="padding:10px;border:1px solid #FFE0B2;font-weight:600;width:40%;">Application ID</td>
            <td style="padding:10px;border:1px solid #FFE0B2;font-family:monospace;">{app['application_id']}</td>
          </tr>
          <tr>
            <td style="padding:10px;border:1px solid #eee;font-weight:600;">Purpose</td>
            <td style="padding:10px;border:1px solid #eee;">{app['purpose']}</td>
          </tr>
          <tr style="background:#fafafa;">
            <td style="padding:10px;border:1px solid #eee;font-weight:600;">Status</td>
            <td style="padding:10px;border:1px solid #eee;color:#E65100;font-weight:600;">{app['status']}</td>
          </tr>
          <tr>
            <td style="padding:10px;border:1px solid #eee;font-weight:600;">Submitted On</td>
            <td style="padding:10px;border:1px solid #eee;">{app['submitted_on']}</td>
          </tr>
        </table>
        <div style="background:#FFF3E0;border-left:4px solid #E65100;padding:14px 16px;border-radius:4px;margin:16px 0;">
          <strong>Next Steps:</strong><br/>
          Visit the <strong>Academic Section / Department Office</strong> within
          <strong>5 working days</strong> to collect your certificate.
        </div>
        <p style="font-size:12px;color:#888;">This is an automated reminder. Do not reply to this email.</p>
      </div>
    </body>
    </html>
    """


def send_lor_notification(student: dict, application: dict):
    _dispatch(
        to_emails=[student["college_email"], student["personal_email"]],
        subject=f"[LOR Application Received] {application['application_id']}",
        html_body=_build_lor_email(student["full_name"], application)
    )


def send_bonafide_notification(student: dict, application: dict):
    _dispatch(
        to_emails=[student["college_email"], student["personal_email"]],
        subject=f"[Bonafide Request Received] {application['application_id']}",
        html_body=_build_bonafide_email(student["full_name"], application)
    )


def _dispatch(to_emails: list, subject: str, html_body: str):
    thread = threading.Thread(
        target=_send_smtp,
        args=(to_emails, subject, html_body),
        daemon=True
    )
    thread.start()


def _send_smtp(to_emails: list, subject: str, html_body: str):
    if not Config.SMTP_ENABLED:
        logger.info(f"[EMAIL SKIPPED] SMTP disabled. Would send to: {to_emails} | Subject: {subject}")
        return

    if not Config.SMTP_USER or not Config.SMTP_PASS:
        logger.warning("[EMAIL] SMTP_USER or SMTP_PASS not configured. Email not sent.")
        return

    try:
        server = smtplib.SMTP(Config.SMTP_HOST, Config.SMTP_PORT)
        server.ehlo()
        server.starttls()
        server.login(Config.SMTP_USER, Config.SMTP_PASS)
        for email in to_emails:
            msg = MIMEMultipart("alternative")
            msg["Subject"] = subject
            msg["From"]    = Config.SMTP_USER
            msg["To"]      = email
            msg.attach(MIMEText(html_body, "html"))
            server.sendmail(Config.SMTP_USER, email, msg.as_string())
        server.quit()
        logger.info(f"[EMAIL SENT] To: {to_emails}")
    except smtplib.SMTPAuthenticationError:
        logger.error("[EMAIL] Authentication failed. Check SMTP_USER and SMTP_PASS.")
    except smtplib.SMTPException as e:
        logger.error(f"[EMAIL] SMTP error: {e}")
    except Exception as e:
        logger.error(f"[EMAIL] Unexpected error: {e}")
