"""
config.py — Application Configuration
Reads from environment variables. Never hardcodes credentials.
"""
import os

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # dotenv optional; values fall back to os.environ or defaults


class Config:
    # Flask
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-key-change-in-prod")
    DEBUG = os.environ.get("DEBUG", "True") == "True"

    # SMTP Email Configuration (set in .env)
    SMTP_HOST = os.environ.get("SMTP_HOST", "smtp.gmail.com")
    SMTP_PORT = int(os.environ.get("SMTP_PORT", 587))
    SMTP_USER = os.environ.get("SMTP_USER", "")
    SMTP_PASS = os.environ.get("SMTP_PASS", "")
    SMTP_ENABLED = os.environ.get("SMTP_ENABLED", "False") == "True"

    # Future: MySQL Config
    MYSQL_HOST = os.environ.get("MYSQL_HOST", "localhost")
    MYSQL_PORT = int(os.environ.get("MYSQL_PORT", 3306))
    MYSQL_USER = os.environ.get("MYSQL_USER", "root")
    MYSQL_PASS = os.environ.get("MYSQL_PASS", "")
    MYSQL_DB   = os.environ.get("MYSQL_DB", "academic_portal")

    # Faculty Registry (Department-filtered)
    FACULTY = {
        "CSE": [
            {"id": "CSE01", "name": "Dr. Anand Krishnamurthy",  "designation": "Professor"},
            {"id": "CSE02", "name": "Dr. Priya Venkataraman",   "designation": "Associate Professor"},
            {"id": "CSE03", "name": "Prof. Ramesh Babu",         "designation": "Assistant Professor"},
        ],
        "CCE": [
            {"id": "CCE01", "name": "Dr. Meenakshi Sundaram",   "designation": "Professor"},
            {"id": "CCE02", "name": "Prof. Karthik Selvam",      "designation": "Associate Professor"},
            {"id": "CCE03", "name": "Dr. Lakshmi Narayanan",    "designation": "Assistant Professor"},
        ],
        "ECE": [
            {"id": "ECE01", "name": "Dr. Suresh Rajan",          "designation": "Professor"},
            {"id": "ECE02", "name": "Dr. Divya Chandrasekaran",  "designation": "Associate Professor"},
            {"id": "ECE03", "name": "Prof. Arjun Pillai",        "designation": "Assistant Professor"},
        ],
    }

    VALID_DEPARTMENTS = list(FACULTY.keys())
    VALID_PROGRAMS    = ["UG", "PG", "Doctorate"]
    LOR_PURPOSES      = ["Higher Studies", "Job Application", "Research Fellowship", "Scholarship"]
    BONAFIDE_PURPOSES = [
        "Bank Account Opening", "Passport Application",
        "Visa Processing", "Educational Loan",
        "Internship Verification", "Other Official Purpose"
    ]
