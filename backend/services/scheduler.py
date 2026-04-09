"""
scheduler.py - Scheduled Email Reminder Service

Runs a background APScheduler job that checks every REMINDER_CHECK_HOURS
for any Pending applications that have passed the REMINDER_INTERVAL_DAYS
threshold and sends a follow-up reminder email to the student.

Design principles:
  - Scheduler starts automatically when the Flask app starts
  - Only one scheduler instance runs (protected against double-start)
  - Adding a new service type requires no changes here - the REMINDER_REGISTRY
    in email_service.py handles all service-specific logic
  - All timing constants are configurable via .env
"""

import logging
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from datetime import datetime, timedelta
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger

logger = logging.getLogger(__name__)

# Single shared scheduler instance
_scheduler = BackgroundScheduler(
    job_defaults={"coalesce": True, "max_instances": 1},
    timezone="Asia/Kolkata"
)
_started = False


def start_scheduler(store, config):
    """
    Starts the background reminder scheduler.
    Called once from app.py on application startup.

    Args:
        store  : the DataStore singleton (from data/store.py)
        config : the Config class (from config.py)
    """
    global _started
    if _started:
        logger.info("[SCHEDULER] Already running. Skipping start.")
        return

    interval_days  = config.REMINDER_INTERVAL_DAYS
    check_hours    = config.REMINDER_CHECK_HOURS

    _scheduler.add_job(
        func=_run_reminder_check,
        trigger=IntervalTrigger(hours=check_hours),
        id="pending_application_reminder",
        args=[store, config],
        replace_existing=True,
    )

    _scheduler.start()
    _started = True

    logger.info(
        f"[SCHEDULER] Started. "
        f"Reminder interval: {interval_days} day(s). "
        f"Check frequency: every {check_hours} hour(s)."
    )


def stop_scheduler():
    """Gracefully shuts down the scheduler. Called on app teardown."""
    global _started
    if _started and _scheduler.running:
        _scheduler.shutdown(wait=False)
        _started = False
        logger.info("[SCHEDULER] Stopped.")


def _run_reminder_check(store, config):
    """
    Core job function. Runs on the configured interval.

    For each service type registered in email_service.REMINDER_REGISTRY:
      1. Fetches all Pending applications of that type
      2. Checks if (now - submitted_on) >= REMINDER_INTERVAL_DAYS
      3. Checks if a reminder has not already been sent for this interval
      4. Sends the reminder email and records it in reminder_sent_on

    This function is service-agnostic. New service types are handled
    automatically once registered in email_service.REMINDER_REGISTRY.
    """
    from services.email_service import REMINDER_REGISTRY, _dispatch

    interval_days = config.REMINDER_INTERVAL_DAYS
    now           = datetime.now()
    cutoff        = now - timedelta(days=interval_days)

    logger.info(
        f"[SCHEDULER] Running reminder check at {now.strftime('%d %b %Y %H:%M')}. "
        f"Checking for applications pending since before "
        f"{cutoff.strftime('%d %b %Y %H:%M')}."
    )

    total_sent = 0

    for service_type, entry in REMINDER_REGISTRY.items():
        # Fetch all applications of this type from the store
        applications = _get_pending_applications(store, service_type)

        for app in applications:
            student = store.get_student(app.registration_id)
            if not student:
                continue

            submitted_dt = _parse_submitted_on(app.submitted_on)
            if submitted_dt is None:
                continue

            # Check if application has been pending long enough
            if submitted_dt > cutoff:
                continue

            # Check if a reminder was already sent for this interval window
            # to avoid sending duplicate reminders every check cycle
            if _reminder_already_sent(app, interval_days):
                continue

            # Build and send the reminder email
            days_pending = (now - submitted_dt).days
            app_dict     = app.to_dict()
            html         = entry["reminder_builder"](student.full_name, app_dict, days_pending)
            subject      = entry["reminder_subject"](app_dict, days_pending)

            _dispatch(
                to_emails=[student.college_email, student.personal_email],
                subject=subject,
                html_body=html
            )

            # Record that reminder was sent so it is not re-sent next cycle
            app.reminder_sent_on = now.strftime("%d %b %Y, %I:%M %p")
            total_sent += 1

            logger.info(
                f"[SCHEDULER] Reminder sent for {app.application_id} "
                f"({service_type}) — pending {days_pending} day(s). "
                f"Student: {student.full_name}."
            )

    if total_sent == 0:
        logger.info("[SCHEDULER] No reminders due at this check.")
    else:
        logger.info(f"[SCHEDULER] Check complete. {total_sent} reminder(s) sent.")


def _get_pending_applications(store, service_type: str) -> list:
    """Returns all Pending applications for the given service type."""
    type_map = {
        "LOR":        store.get_all_lor,
        "Bonafide":   store.get_all_bonafide,
        "Internship": store.get_all_internship,
    }
    fetch = type_map.get(service_type)
    if not fetch:
        return []
    return [a for a in fetch() if a.status == "Pending"]


def _parse_submitted_on(submitted_on: str):
    """
    Parses the submitted_on datetime string stored in applications.
    Returns a datetime object or None if parsing fails.
    """
    formats = [
        "%d %b %Y, %I:%M %p",  # e.g. 15 Jan 2025, 10:30 AM
        "%d %b %Y, %H:%M",     # fallback
        "%Y-%m-%dT%H:%M:%S",   # ISO format fallback
    ]
    for fmt in formats:
        try:
            return datetime.strptime(submitted_on.strip(), fmt)
        except (ValueError, AttributeError):
            continue
    logger.warning(f"[SCHEDULER] Could not parse submitted_on: '{submitted_on}'")
    return None


def _reminder_already_sent(app, interval_days: int) -> bool:
    """
    Returns True if a reminder was already sent within the current
    interval window. Prevents duplicate sends on every check cycle.
    """
    reminder_sent = getattr(app, "reminder_sent_on", None)
    if not reminder_sent:
        return False
    try:
        sent_dt  = datetime.strptime(reminder_sent.strip(), "%d %b %Y, %I:%M %p")
        due_again = sent_dt + timedelta(days=interval_days)
        return datetime.now() < due_again
    except (ValueError, AttributeError):
        return False
