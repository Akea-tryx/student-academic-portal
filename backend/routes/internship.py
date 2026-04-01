"""
routes/internship.py — Internship Approval API Routes
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from flask import Blueprint, request, jsonify
from data.store import store
from models import InternshipApplication
from services.validation import validate_internship
from services.email_service import send_internship_notification

internship_bp = Blueprint("internship", __name__, url_prefix="/api/internship")


@internship_bp.route("/apply", methods=["POST"])
def apply_internship():
    data = request.get_json(silent=True)
    if not data:
        return jsonify({"success": False, "message": "Request body must be valid JSON."}), 400

    for key in data:
        if isinstance(data[key], str):
            data[key] = data[key].strip()

    reg_id  = data.get("registration_id", "")
    student = store.get_student(reg_id)
    if not student:
        return jsonify({"success": False, "message": "Student profile not found. Complete your profile first."}), 403

    valid, msg = validate_internship(data)
    if not valid:
        return jsonify({"success": False, "message": msg}), 422

    application = InternshipApplication(
        registration_id = reg_id,
        student_name    = student.full_name,
        department      = student.department,
        program_type    = student.program_type,
        company_name    = data["company_name"],
        internship_role = data["internship_role"],
        internship_type = data["internship_type"],
        start_date      = data["start_date"],
        end_date        = data["end_date"],
        stipend         = data.get("stipend", "Unpaid"),
        description     = data["description"],
    )
    store.create_internship(application)
    send_internship_notification(student.to_dict(), application.to_dict())

    return jsonify({
        "success":     True,
        "message":     "Internship application submitted. Reminder emails dispatched.",
        "application": application.to_dict()
    }), 201


@internship_bp.route("/<application_id>", methods=["GET"])
def get_internship(application_id):
    app = store.get_internship(application_id)
    if not app:
        return jsonify({"success": False, "message": "Application not found."}), 404
    return jsonify({"success": True, "application": app.to_dict()})
