"""
validation.py — Input Validation Service
"""
import re
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from config import Config


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

    email_re = re.compile(r"^[\w.+-]+@[\w-]+\.[a-zA-Z]{2,}$")
    if not email_re.match(data.get("college_email", "")):
        return False, "Invalid college_email format."
    if not email_re.match(data.get("personal_email", "")):
        return False, "Invalid personal_email format."

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
