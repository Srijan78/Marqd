"""
Marqd API Blueprints Registration
"""


def register_blueprints(app):
    """Register all API blueprints with the Flask app."""
    from app.api.assets import assets_bp
    from app.api.scans import scans_bp
    from app.api.violations import violations_bp
    from app.api.reports import reports_bp
    from app.api.propagation import propagation_bp

    app.register_blueprint(assets_bp, url_prefix="/api")
    app.register_blueprint(scans_bp, url_prefix="/api")
    app.register_blueprint(violations_bp, url_prefix="/api")
    app.register_blueprint(reports_bp, url_prefix="/api")
    app.register_blueprint(propagation_bp, url_prefix="/api")
