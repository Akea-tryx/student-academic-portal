"""
routes/lor.py — LOR Application API Routes
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from flask import Blueprint, request, jsonify
from data.store import store
from models import LORApplication
from services.validation import validate_lor
from services.email_service import send_lor_notification
from config import Config

lor_bp = Blueprint("lor", __name__, url_prefix="/api/lor")


@lor_bp.route("/apply", methods=["POST"])
def apply_lor():
    data = request.get_json(silent=True)
    if not data:
        return jsonify({"success": False, "message": "Request body must be valid JSON."}), 400

    for key in data:
        if isinstance(data[key], str):
            data[key] = data[key].strip()

    reg_id = data.get("registration_id", "")
    student = store.get_student(reg_id)
    if not student:
        return jsonify({
            "success": False,
            "message": "Student profile not found. Please complete your profile first."
        }), 403

    dept = student.department
    faculty_ids = [f["id"] for f in Config.FACULTY.get(dept, [])]

    valid, msg = validate_lor(data, faculty_ids)
    if not valid:
        return jsonify({"success": False, "message": msg}), 422

    faculty = next(f for f in Config.FACULTY[dept] if f["id"] == data["faculty_id"])

    application = LORApplication(
        registration_id    = reg_id,
        student_name       = student.full_name,
        department         = dept,
        faculty_id         = data["faculty_id"],
        faculty_name       = faculty["name"],
        purpose            = data["purpose"],
        additional_details = data.get("additional_details", ""),
    )
    store.create_lor(application)

    send_lor_notification(student.to_dict(), application.to_dict())

    return jsonify({
        "success":     True,
        "message":     "LOR application submitted. Reminder emails have been dispatched.",
        "application": application.to_dict()
    }), 201


@lor_bp.route("/<application_id>", methods=["GET"])
def get_lor(application_id):
    app = store.get_lor(application_id)
    if not app:
        return jsonify({"success": False, "message": "Application not found."}), 404
    return jsonify({"success": True, "application": app.to_dict()})
