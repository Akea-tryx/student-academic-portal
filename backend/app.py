"""
app.py — Flask Application Entry Point (v2)
Added: Internship Blueprint, Admin Blueprint
"""
import sys, os, logging
sys.path.insert(0, os.path.dirname(__file__))

from flask import Flask, jsonify
from flask_cors import CORS
from config import Config
from routes.student    import student_bp
from routes.lor        import lor_bp
from routes.bonafide   import bonafide_bp
from routes.internship import internship_bp
from routes.admin      import admin_bp

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
logger = logging.getLogger(__name__)


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    app.secret_key = Config.SECRET_KEY   # Required for session (admin panel)

    CORS(app, resources={r"/api/*": {"origins": "*"}}, supports_credentials=True)

    app.register_blueprint(student_bp)
    app.register_blueprint(lor_bp)
    app.register_blueprint(bonafide_bp)
    app.register_blueprint(internship_bp)
    app.register_blueprint(admin_bp)

    @app.route("/api/health")
    def health():
        return jsonify({
            "status":  "running",
            "service": "Student Academic Services Portal v2",
            "modules": ["profile", "lor", "bonafide", "internship", "admin"]
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

    return app


if __name__ == "__main__":
    application = create_app()
    logger.info("=" * 60)
    logger.info("  Student Academic Services Portal v2")
    logger.info("  Running at http://localhost:5000")
    logger.info("  Admin Panel: open admin.html in frontend/")
    logger.info("=" * 60)
    application.run(debug=Config.DEBUG, host="0.0.0.0", port=5000)
