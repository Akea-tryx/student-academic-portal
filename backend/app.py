"""
app.py - Flask Application Entry Point

Modules registered:
  /api/student    - profile, faculty, applications
  /api/lor        - letter of recommendation
  /api/bonafide   - bonafide certificate
  /api/internship - internship approval
  /api/admin      - admin panel

On startup:
  - Background scheduler starts automatically
  - Checks every REMINDER_CHECK_HOURS for Pending applications
  - Sends follow-up reminder emails after REMINDER_INTERVAL_DAYS
"""

import sys
import os
import logging
import atexit
sys.path.insert(0, os.path.dirname(__file__))

from flask import Flask, jsonify
from flask_cors import CORS

from config import Config
from data.store import store
from routes.student    import student_bp
from routes.lor        import lor_bp
from routes.bonafide   import bonafide_bp
from routes.internship import internship_bp
from routes.admin      import admin_bp
from services.scheduler import start_scheduler, stop_scheduler

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
logger = logging.getLogger(__name__)


def create_app() -> Flask:
    app = Flask(__name__)
    app.config.from_object(Config)
    app.secret_key = Config.SECRET_KEY

    CORS(app, resources={r"/api/*": {"origins": "*"}}, supports_credentials=True)

    # Register all service blueprints
    app.register_blueprint(student_bp)
    app.register_blueprint(lor_bp)
    app.register_blueprint(bonafide_bp)
    app.register_blueprint(internship_bp)
    app.register_blueprint(admin_bp)

    @app.route("/api/health")
    def health():
        return jsonify({
            "status":          "running",
            "service":         "Student Academic Services Portal",
            "version":         "2.0.0",
            "modules":         ["profile", "lor", "bonafide", "internship", "admin"],
            "reminder_days":   Config.REMINDER_INTERVAL_DAYS,
            "reminder_check":  f"every {Config.REMINDER_CHECK_HOURS} hour(s)",
        })

    @app.errorhandler(404)
    def not_found(e):
        return jsonify({"success": False, "message": "Endpoint not found."}), 404

    @app.errorhandler(405)
    def method_not_allowed(e):
        return jsonify({"success": False, "message": "Method not allowed."}), 405

    @app.errorhandler(500)
    def internal_error(e):
        logger.error(f"Internal server error: {e}")
        return jsonify({"success": False, "message": "Internal server error."}), 500

    # Start the background reminder scheduler
    start_scheduler(store, Config)

    # Gracefully stop scheduler when Flask shuts down
    atexit.register(stop_scheduler)

    return app


if __name__ == "__main__":
    application = create_app()
    logger.info("=" * 65)
    logger.info("  Student Academic Services Portal — v2.0.0")
    logger.info("  Running at       : http://localhost:5000")
    logger.info("  Admin Panel      : open frontend/admin.html")
    logger.info(f"  Reminder interval: every {Config.REMINDER_INTERVAL_DAYS} day(s)")
    logger.info(f"  Reminder checks  : every {Config.REMINDER_CHECK_HOURS} hour(s)")
    logger.info("=" * 65)
    application.run(debug=Config.DEBUG, host="0.0.0.0", port=5000)
