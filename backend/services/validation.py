"""
validation.py — Input Validation Service
College email domain enforced: @muj.manipal.edu only
Format enforced: name.registrationid@muj.manipal.edu
"""
import re
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from config import Config

# ── College email rules ───────────────────────────────────────
# Accepted format : anything@muj.manipal.edu
# Example         : antriksh.2428010079@muj.manipal.edu
# Rejected        : student@gmail.com, student@manipal.edu, etc.
COLLEGE_EMAIL_DOMAIN  = "muj.manipal.edu"
COLLEGE_EMAIL_PATTERN = re.compile(
    r"^[a-zA-Z0-9][a-zA-Z0-9._+-]*@muj\.manipal\.edu$"
)

# Personal email — any valid email except @muj.manipal.edu
PERSONAL_EMAIL_PATTERN = re.compile(
    r"^[\w.+-]+@[\w-]+\.[a-zA-Z]{2,}$"
)


def validate_college_email(email: str) -> tuple:
    """
    Validates that the college email:
    1. Ends with @muj.manipal.edu (strict domain check)
    2. Matches expected format: name.registrationid@muj.manipal.edu
    3. Is not empty
    """
    email = email.strip().lower()

    if not email:
        return False, "College email is required."

    # Strict domain check — ONLY @muj.manipal.edu accepted
    if not email.endswith(f"@{COLLEGE_EMAIL_DOMAIN}"):
        return False, (
            f"College email must end with @{COLLEGE_EMAIL_DOMAIN}. "
            f"Example: name.enrollmentid@{COLLEGE_EMAIL_DOMAIN}"
        )

    # Format check — must match full pattern
    if not COLLEGE_EMAIL_PATTERN.match(email):
        return False, (
            f"Invalid college email format. "
            f"Expected format: name.enrollmentid@{COLLEGE_EMAIL_DOMAIN}"
        )

    return True, "OK"


def validate_profile(data: dict) -> tuple:
    required = [
        "full_name", "registration_id", "program_type", "department",
        "course_duration", "college_email", "personal_email", "mobile", "cgpa"
    ]
    for f in required:
        if not str(data.get(f, "")).strip():
            return False, f"Field '{f}' is required."

    if data["program_type"] not in Config.VALID_PROGRAMS:
        return False, f"Invalid program_type. Must be one of: {Config.VALID_PROGRAMS}"

    if data["department"] not in Config.VALID_DEPARTMENTS:
        return False, f"Invalid department. Must be one of: {Config.VALID_DEPARTMENTS}"

    try:
        cgpa = float(data["cgpa"])
        if not (0.0 <= cgpa <= 10.0):
            return False, "CGPA must be between 0.0 and 10.0."
    except (ValueError, TypeError):
        return False, "CGPA must be a valid number."

    # ── College email — strict MUJ domain validation ──────────
    ok, msg = validate_college_email(data.get("college_email", ""))
    if not ok:
        return False, msg

    # ── Personal email — standard format, must NOT be MUJ ─────
    personal = data.get("personal_email", "").strip()
    if not PERSONAL_EMAIL_PATTERN.match(personal):
        return False, "Invalid personal email format."
    if personal.lower().endswith(f"@{COLLEGE_EMAIL_DOMAIN}"):
        return False, "Personal email must be different from your college email. Use Gmail, Yahoo, etc."

    if not re.fullmatch(r"\d{10}", str(data.get("mobile", "")).strip()):
        return False, "Mobile must be exactly 10 digits."

    return True, "OK"


def validate_lor(data: dict, valid_faculty_ids: list) -> tuple:
    if not str(data.get("faculty_id", "")).strip():
        return False, "Faculty selection is required."
    if data["faculty_id"] not in valid_faculty_ids:
        return False, "Invalid faculty for your department."
    if not str(data.get("purpose", "")).strip():
        return False, "Purpose is required."
    if data["purpose"] not in Config.LOR_PURPOSES:
        return False, f"Invalid purpose. Must be one of: {Config.LOR_PURPOSES}"
    return True, "OK"


def validate_bonafide(data: dict) -> tuple:
    if not str(data.get("purpose", "")).strip():
        return False, "Purpose is required."
    if data["purpose"] not in Config.BONAFIDE_PURPOSES:
        return False, f"Invalid purpose. Must be one of: {Config.BONAFIDE_PURPOSES}"
    if not str(data.get("reason", "")).strip():
        return False, "Reason is required."
    if len(data["reason"].strip()) < 10:
        return False, "Reason must be at least 10 characters."
    return True, "OK"


def validate_internship(data: dict) -> tuple:
    if not str(data.get("company_name", "")).strip():
        return False, "Company name is required."
    if not str(data.get("internship_role", "")).strip():
        return False, "Internship role is required."
    if not str(data.get("start_date", "")).strip():
        return False, "Start date is required."
    if not str(data.get("end_date", "")).strip():
        return False, "End date is required."
    if not str(data.get("internship_type", "")).strip():
        return False, "Internship type is required."
    if data.get("internship_type") not in Config.INTERNSHIP_TYPES:
        return False, f"Invalid internship type. Must be one of: {Config.INTERNSHIP_TYPES}"
    if not str(data.get("description", "")).strip():
        return False, "Description is required."
    if len(data["description"].strip()) < 20:
        return False, "Description must be at least 20 characters."
    return True, "OK"
