"""
routes/admin.py — Admin Panel API Routes
Faculty/Admin can: view all applications, approve/reject with remarks
Simple session-based login using Flask session
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from flask import Blueprint, request, jsonify, session
from data.store import store
from config import Config

admin_bp = Blueprint("admin", __name__, url_prefix="/api/admin")


def admin_required(f):
    """Decorator — blocks access if admin not logged in."""
    from functools import wraps
    @wraps(f)
    def decorated(*args, **kwargs):
        if not session.get("admin_logged_in"):
            return jsonify({"success": False, "message": "Admin authentication required."}), 401
        return f(*args, **kwargs)
    return decorated


@admin_bp.route("/login", methods=["POST"])
def admin_login():
    data     = request.get_json(silent=True) or {}
    username = data.get("username", "").strip()
    password = data.get("password", "").strip()

    if username == Config.ADMIN_USERNAME and password == Config.ADMIN_PASSWORD:
        session["admin_logged_in"] = True
        session["admin_username"]  = username
        return jsonify({"success": True, "message": "Admin login successful."})
    return jsonify({"success": False, "message": "Invalid username or password."}), 401


@admin_bp.route("/logout", methods=["POST"])
def admin_logout():
    session.clear()
    return jsonify({"success": True, "message": "Logged out."})


@admin_bp.route("/dashboard", methods=["GET"])
@admin_required
def dashboard():
    """Returns summary stats for admin dashboard."""
    all_apps  = store.get_all_applications()
    students  = store.get_all_students()
    return jsonify({
        "success":      True,
        "total_students":    len(students),
        "total_applications": len(all_apps),
        "pending":      sum(1 for a in all_apps if a["status"] == "Pending"),
        "approved":     sum(1 for a in all_apps if a["status"] == "Approved"),
        "rejected":     sum(1 for a in all_apps if a["status"] == "Rejected"),
        "lor_count":        sum(1 for a in all_apps if a["type"] == "LOR"),
        "bonafide_count":   sum(1 for a in all_apps if a["type"] == "Bonafide"),
        "internship_count": sum(1 for a in all_apps if a["type"] == "Internship"),
    })


@admin_bp.route("/applications", methods=["GET"])
@admin_required
def get_all_applications():
    """Returns all applications across all types with optional filters."""
    app_type = request.args.get("type", "").strip()
    status   = request.args.get("status", "").strip()
    dept     = request.args.get("department", "").strip()

    apps = store.get_all_applications()

    if app_type:
        apps = [a for a in apps if a["type"].lower() == app_type.lower()]
    if status:
        apps = [a for a in apps if a["status"].lower() == status.lower()]
    if dept:
        apps = [a for a in apps if a["department"].upper() == dept.upper()]

    return jsonify({"success": True, "applications": apps, "count": len(apps)})


@admin_bp.route("/students", methods=["GET"])
@admin_required
def get_all_students():
    students = [s.to_dict() for s in store.get_all_students()]
    return jsonify({"success": True, "students": students, "count": len(students)})


@admin_bp.route("/review", methods=["POST"])
@admin_required
def review_application():
    """
    Approve or Reject any application.
    Body: { application_id, type, status, remarks }
    """
    data       = request.get_json(silent=True) or {}
    app_id     = data.get("application_id", "").strip()
    app_type   = data.get("type", "").strip()
    new_status = data.get("status", "").strip()
    remarks    = data.get("remarks", "").strip()

    if not app_id or not app_type or not new_status:
        return jsonify({"success": False, "message": "application_id, type, and status are required."}), 422

    if new_status not in ["Approved", "Rejected", "Pending"]:
        return jsonify({"success": False, "message": "Status must be Approved, Rejected, or Pending."}), 422

    updated = False
    if app_type == "LOR":
        updated = store.update_lor_status(app_id, new_status, remarks)
    elif app_type == "Bonafide":
        updated = store.update_bonafide_status(app_id, new_status, remarks)
    elif app_type == "Internship":
        updated = store.update_internship_status(app_id, new_status, remarks)
    else:
        return jsonify({"success": False, "message": "Invalid application type."}), 422

    if not updated:
        return jsonify({"success": False, "message": "Application not found."}), 404

    return jsonify({
        "success": True,
        "message": f"Application {app_id} has been {new_status}.",
        "application_id": app_id,
        "new_status": new_status,
        "remarks": remarks
    })
