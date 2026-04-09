"""
models.py - Data Models
Each dataclass maps directly to a future MySQL table.
MySQL migration: replace to_dict() + asdict() with SQLAlchemy ORM equivalents.
"""
from dataclasses import dataclass, field, asdict
from datetime import datetime
import uuid


def _now_str():
    return datetime.now().strftime("%d %b %Y, %I:%M %p")

def _uid(prefix: str) -> str:
    return f"{prefix}-{datetime.now().strftime('%Y%m%d')}-{str(uuid.uuid4())[:6].upper()}"


@dataclass
class StudentProfile:
    """MySQL table: students | PRIMARY KEY: registration_id"""
    full_name:        str
    registration_id:  str
    program_type:     str
    department:       str
    course_duration:  str
    college_email:    str
    personal_email:   str
    mobile:           str
    cgpa:             float
    profile_verified: bool = True
    created_at:       str  = field(default_factory=_now_str)

    def to_dict(self):
        return asdict(self)


@dataclass
class LORApplication:
    """MySQL table: lor_applications | FOREIGN KEY: registration_id -> students"""
    registration_id:    str
    student_name:       str
    department:         str
    faculty_id:         str
    faculty_name:       str
    purpose:            str
    additional_details: str  = ""
    status:             str  = "Pending"
    admin_remarks:      str  = ""
    reviewed_on:        str  = ""
    reminder_sent_on:   str  = ""
    application_id:     str  = field(default_factory=lambda: _uid("LOR"))
    submitted_on:       str  = field(default_factory=_now_str)
    type:               str  = "LOR"

    def to_dict(self):
        return asdict(self)


@dataclass
class BonafideApplication:
    """MySQL table: bonafide_applications | FOREIGN KEY: registration_id -> students"""
    registration_id:  str
    student_name:     str
    department:       str
    program_type:     str
    purpose:          str
    reason:           str
    status:           str  = "Pending"
    admin_remarks:    str  = ""
    reviewed_on:      str  = ""
    reminder_sent_on: str  = ""
    application_id:   str  = field(default_factory=lambda: _uid("BON"))
    submitted_on:     str  = field(default_factory=_now_str)
    type:             str  = "Bonafide"

    def to_dict(self):
        return asdict(self)


@dataclass
class InternshipApplication:
    """MySQL table: internship_applications | FOREIGN KEY: registration_id -> students"""
    registration_id:  str
    student_name:     str
    department:       str
    program_type:     str
    company_name:     str
    internship_role:  str
    internship_type:  str
    start_date:       str
    end_date:         str
    stipend:          str
    description:      str
    status:           str  = "Pending"
    admin_remarks:    str  = ""
    reviewed_on:      str  = ""
    reminder_sent_on: str  = ""
    application_id:   str  = field(default_factory=lambda: _uid("INT"))
    submitted_on:     str  = field(default_factory=_now_str)
    type:             str  = "Internship"

    def to_dict(self):
        return asdict(self)
