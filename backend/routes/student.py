"""
routes/student.py — Student Profile API Routes
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from flask import Blueprint, request, jsonify
from data.store import store
from models import StudentProfile
from services.validation import validate_profile
from config import Config

student_bp = Blueprint("student", __name__, url_prefix="/api/student")


@student_bp.route("/profile", methods=["POST"])
def create_profile():
    data = request.get_json(silent=True)
    if not data:
        return jsonify({"success": False, "message": "Request body must be valid JSON."}), 400

    for key in data:
        if isinstance(data[key], str):
            data[key] = data[key].strip()

    valid, msg = validate_profile(data)
    if not valid:
        return jsonify({"success": False, "message": msg}), 422

    reg_id = data["registration_id"]
    if store.student_exists(reg_id):
        return jsonify({"success": False, "message": "A profile with this Registration ID already exists."}), 409

    profile = StudentProfile(
        full_name       = data["full_name"],
        registration_id = reg_id,
        program_type    = data["program_type"],
        department      = data["department"],
        course_duration = data["course_duration"],
        college_email   = data["college_email"],
        personal_email  = data["personal_email"],
        mobile          = data["mobile"],
        cgpa            = float(data["cgpa"]),
    )
    store.create_student(profile)

    return jsonify({
        "success": True,
        "message": "Profile created and verified. Academic services are now unlocked.",
        "student": profile.to_dict()
    }), 201


@student_bp.route("/profile/<reg_id>", methods=["GET"])
def get_profile(reg_id):
    student = store.get_student(reg_id)
    if not student:
        return jsonify({"success": False, "message": "Student not found."}), 404
    return jsonify({"success": True, "student": student.to_dict()})


@student_bp.route("/faculty/<department>", methods=["GET"])
def get_faculty(department):
    dept = department.upper()
    faculty = Config.FACULTY.get(dept)
    if not faculty:
        return jsonify({"success": False, "message": f"Invalid department: {dept}"}), 400
    return jsonify({"success": True, "department": dept, "faculty": faculty})


@student_bp.route("/applications/<reg_id>", methods=["GET"])
def get_applications(reg_id):
    if not store.student_exists(reg_id):
        return jsonify({"success": False, "message": "Student not found."}), 404
    apps = store.get_applications_by_student(reg_id)
    return jsonify({"success": True, "applications": apps, "count": len(apps)})


@student_bp.route("/reference", methods=["GET"])
def reference_data():
    return jsonify({
        "success":           True,
        "departments":       Config.VALID_DEPARTMENTS,
        "programs":          Config.VALID_PROGRAMS,
        "lor_purposes":      Config.LOR_PURPOSES,
        "bonafide_purposes": Config.BONAFIDE_PURPOSES,
        "faculty":           Config.FACULTY
    })
