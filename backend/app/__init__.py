"""
Marqd Flask Application Factory
"""
import os
from flask import Flask
from flask_cors import CORS

from config import get_config
from app.models import db
from app.api import register_blueprints


def create_app(config_override=None):
    """Create and configure the Flask application."""
    app = Flask(__name__)

    # Load config
    if config_override:
        app.config.from_object(config_override)
    else:
        app.config.from_object(get_config())

    # Ensure upload and temp directories exist
    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)
    os.makedirs(app.config["TEMP_FOLDER"], exist_ok=True)

    # 2. Configure CORS securely
    cors_origins = app.config.get("CORS_ORIGINS", "http://localhost:5173")
    CORS(app, resources={r"/api/*": {"origins": cors_origins.split(",")}}, supports_credentials=True)

    # Initialize extensions
    db.init_app(app)

    # Create database tables
    with app.app_context():
        from app.models.asset import Asset
        from app.models.violation import Violation
        from app.models.scan_log import ScanLog
        db.create_all()

    # Register API blueprints
    register_blueprints(app)

    # Health check route
    @app.route("/api/health")
    def health():
        return {"status": "healthy", "service": "marqd-backend", "version": "2.0"}

    return app
