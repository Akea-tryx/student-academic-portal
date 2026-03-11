"""
store.py — In-Memory Data Store
Thread-safe. Designed so method signatures match a future MySQL DAO layer.
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import threading
from typing import Optional, List
from models import StudentProfile, LORApplication, BonafideApplication


class DataStore:
    def __init__(self):
        self._lock      = threading.Lock()
        self._students  = {}
        self._lor       = {}
        self._bonafide  = {}

    # ── Student ──────────────────────────────────────────
    def create_student(self, profile: StudentProfile) -> bool:
        with self._lock:
            if profile.registration_id in self._students:
                return False
            self._students[profile.registration_id] = profile
            return True

    def get_student(self, reg_id: str) -> Optional[StudentProfile]:
        return self._students.get(reg_id)

    def student_exists(self, reg_id: str) -> bool:
        return reg_id in self._students

    # ── LOR ──────────────────────────────────────────────
    def create_lor(self, app: LORApplication) -> LORApplication:
        with self._lock:
            self._lor[app.application_id] = app
        return app

    def get_lor(self, app_id: str) -> Optional[LORApplication]:
        return self._lor.get(app_id)

    # ── Bonafide ─────────────────────────────────────────
    def create_bonafide(self, app: BonafideApplication) -> BonafideApplication:
        with self._lock:
            self._bonafide[app.application_id] = app
        return app

    def get_bonafide(self, app_id: str) -> Optional[BonafideApplication]:
        return self._bonafide.get(app_id)

    # ── All Applications ─────────────────────────────────
    def get_applications_by_student(self, reg_id: str) -> List[dict]:
        lor_apps = [a.to_dict() for a in self._lor.values()      if a.registration_id == reg_id]
        bon_apps = [a.to_dict() for a in self._bonafide.values() if a.registration_id == reg_id]
        return sorted(lor_apps + bon_apps, key=lambda x: x["submitted_on"], reverse=True)


# Singleton
store = DataStore()
