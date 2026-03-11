"""
routes/bonafide.py — Bonafide Certificate API Routes
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from flask import Blueprint, request, jsonify
from data.store import store
from models import BonafideApplication
from services.validation import validate_bonafide
from services.email_service import send_bonafide_notification

bonafide_bp = Blueprint("bonafide", __name__, url_prefix="/api/bonafide")


@bonafide_bp.route("/apply", methods=["POST"])
def apply_bonafide():
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

    valid, msg = validate_bonafide(data)
    if not valid:
        return jsonify({"success": False, "message": msg}), 422

    application = BonafideApplication(
        registration_id = reg_id,
        student_name    = student.full_name,
        department      = student.department,
        program_type    = student.program_type,
        purpose         = data["purpose"],
        reason          = data["reason"],
    )
    store.create_bonafide(application)

    send_bonafide_notification(student.to_dict(), application.to_dict())

    return jsonify({
        "success":     True,
        "message":     "Bonafide certificate request submitted. Reminder emails dispatched.",
        "application": application.to_dict()
    }), 201


@bonafide_bp.route("/<application_id>", methods=["GET"])
def get_bonafide(application_id):
    app = store.get_bonafide(application_id)
    if not app:
        return jsonify({"success": False, "message": "Application not found."}), 404
    return jsonify({"success": True, "application": app.to_dict()})
