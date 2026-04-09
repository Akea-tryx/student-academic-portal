"""
config.py - Application Configuration
All values loaded from environment variables.
Credentials are never hardcoded.
"""
import os

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass


class Config:
    # Flask
    SECRET_KEY   = os.environ.get("SECRET_KEY", "dev-secret-key-change-in-prod")
    DEBUG        = os.environ.get("DEBUG", "True") == "True"

    # SMTP - credentials must be set in .env
    SMTP_HOST    = os.environ.get("SMTP_HOST", "smtp.gmail.com")
    SMTP_PORT    = int(os.environ.get("SMTP_PORT", 587))
    SMTP_USER    = os.environ.get("SMTP_USER", "")
    SMTP_PASS    = os.environ.get("SMTP_PASS", "")
    SMTP_ENABLED = os.environ.get("SMTP_ENABLED", "False") == "True"

    # Reminder scheduler
    # REMINDER_INTERVAL_DAYS: how many days after submission before a follow-up
    # reminder is sent to the student if the application is still Pending.
    # Default is 3 days. Change in .env as needed.
    REMINDER_INTERVAL_DAYS    = int(os.environ.get("REMINDER_INTERVAL_DAYS", 3))

    # REMINDER_CHECK_HOURS: how often the scheduler checks for due reminders.
    # Default is every 6 hours so reminders are sent within a 6-hour window
    # of the 3-day mark rather than waiting a full day.
    REMINDER_CHECK_HOURS      = int(os.environ.get("REMINDER_CHECK_HOURS", 6))

    # MySQL - for future database integration
    MYSQL_HOST   = os.environ.get("MYSQL_HOST", "localhost")
    MYSQL_PORT   = int(os.environ.get("MYSQL_PORT", 3306))
    MYSQL_USER   = os.environ.get("MYSQL_USER", "root")
    MYSQL_PASS   = os.environ.get("MYSQL_PASS", "")
    MYSQL_DB     = os.environ.get("MYSQL_DB", "academic_portal")

    # College email domain - only @muj.manipal.edu accepted
    # Format: name.enrollmentid@muj.manipal.edu
    # Example: antriksh.2428010079@muj.manipal.edu
    COLLEGE_EMAIL_DOMAIN = "muj.manipal.edu"

    # Admin panel credentials - override in .env for production
    ADMIN_USERNAME = os.environ.get("ADMIN_USERNAME", "admin")
    ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "admin123")

    # Faculty registry - department filtered
    FACULTY = {
        "CSE": [
            {"id": "CSE01", "name": "Dr. Anand Krishnamurthy",  "designation": "Professor"},
            {"id": "CSE02", "name": "Dr. Priya Venkataraman",   "designation": "Associate Professor"},
            {"id": "CSE03", "name": "Prof. Ramesh Babu",        "designation": "Assistant Professor"},
        ],
        "CCE": [
            {"id": "CCE01", "name": "Dr. Meenakshi Sundaram",   "designation": "Professor"},
            {"id": "CCE02", "name": "Prof. Karthik Selvam",     "designation": "Associate Professor"},
            {"id": "CCE03", "name": "Dr. Lakshmi Narayanan",    "designation": "Assistant Professor"},
        ],
        "ECE": [
            {"id": "ECE01", "name": "Dr. Suresh Rajan",         "designation": "Professor"},
            {"id": "ECE02", "name": "Dr. Divya Chandrasekaran", "designation": "Associate Professor"},
            {"id": "ECE03", "name": "Prof. Arjun Pillai",       "designation": "Assistant Professor"},
        ],
    }

    VALID_DEPARTMENTS  = list(FACULTY.keys())
    VALID_PROGRAMS     = ["UG", "PG", "Doctorate"]
    LOR_PURPOSES       = ["Higher Studies", "Job Application", "Research Fellowship", "Scholarship"]
    BONAFIDE_PURPOSES  = [
        "Bank Account Opening", "Passport Application",
        "Visa Processing", "Educational Loan",
        "Internship Verification", "Other Official Purpose"
    ]
    INTERNSHIP_TYPES   = ["In-Person", "Remote", "Hybrid"]
    INTERNSHIP_STIPEND = ["Paid", "Unpaid"]
