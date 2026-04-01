"""
store.py — In-Memory Data Store (v2)
Added: InternshipApplication support
DAO pattern — MySQL migration = replace method bodies only
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import threading
from models import StudentProfile, LORApplication, BonafideApplication, InternshipApplication


class DataStore:
    def __init__(self):
        self._lock        = threading.Lock()
        self._students    = {}
        self._lor         = {}
        self._bonafide    = {}
        self._internship  = {}

    # ── Student ──────────────────────────────────────────────
    def create_student(self, profile):
        with self._lock:
            if profile.registration_id in self._students:
                return False
            self._students[profile.registration_id] = profile
            return True

    def get_student(self, reg_id):
        return self._students.get(reg_id)

    def student_exists(self, reg_id):
        return reg_id in self._students

    def get_all_students(self):
        return list(self._students.values())

    # ── LOR ──────────────────────────────────────────────────
    def create_lor(self, app):
        with self._lock:
            self._lor[app.application_id] = app
        return app

    def get_lor(self, app_id):
        return self._lor.get(app_id)

    def update_lor_status(self, app_id, status, remarks=""):
        with self._lock:
            app = self._lor.get(app_id)
            if app:
                from datetime import datetime
                app.status        = status
                app.admin_remarks = remarks
                app.reviewed_on   = datetime.now().strftime("%d %b %Y, %I:%M %p")
                return True
        return False

    def get_all_lor(self):
        return list(self._lor.values())

    # ── Bonafide ─────────────────────────────────────────────
    def create_bonafide(self, app):
        with self._lock:
            self._bonafide[app.application_id] = app
        return app

    def get_bonafide(self, app_id):
        return self._bonafide.get(app_id)

    def update_bonafide_status(self, app_id, status, remarks=""):
        with self._lock:
            app = self._bonafide.get(app_id)
            if app:
                from datetime import datetime
                app.status        = status
                app.admin_remarks = remarks
                app.reviewed_on   = datetime.now().strftime("%d %b %Y, %I:%M %p")
                return True
        return False

    def get_all_bonafide(self):
        return list(self._bonafide.values())

    # ── Internship ────────────────────────────────────────────
    def create_internship(self, app):
        with self._lock:
            self._internship[app.application_id] = app
        return app

    def get_internship(self, app_id):
        return self._internship.get(app_id)

    def update_internship_status(self, app_id, status, remarks=""):
        with self._lock:
            app = self._internship.get(app_id)
            if app:
                from datetime import datetime
                app.status        = status
                app.admin_remarks = remarks
                app.reviewed_on   = datetime.now().strftime("%d %b %Y, %I:%M %p")
                return True
        return False

    def get_all_internship(self):
        return list(self._internship.values())

    # ── All Applications by Student ───────────────────────────
    def get_applications_by_student(self, reg_id):
        apps = (
            [a.to_dict() for a in self._lor.values()         if a.registration_id == reg_id] +
            [a.to_dict() for a in self._bonafide.values()    if a.registration_id == reg_id] +
            [a.to_dict() for a in self._internship.values()  if a.registration_id == reg_id]
        )
        return sorted(apps, key=lambda x: x["submitted_on"], reverse=True)

    # ── Admin: all applications ───────────────────────────────
    def get_all_applications(self):
        apps = (
            [a.to_dict() for a in self._lor.values()] +
            [a.to_dict() for a in self._bonafide.values()] +
            [a.to_dict() for a in self._internship.values()]
        )
        return sorted(apps, key=lambda x: x["submitted_on"], reverse=True)


store = DataStore()
