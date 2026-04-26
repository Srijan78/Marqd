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

    from flask import request, jsonify

    @app.before_request
    def require_api_key():
        # Exempt preflight requests
        if request.method == "OPTIONS":
            return
            
        # Only protect /api/ routes
        if not request.path.startswith("/api/"):
            return
            
        # Exempt health check and public media uploads path
        exempt_paths = ["/api/health", "/api/uploads/"]
        for path in exempt_paths:
            if request.path.startswith(path):
                return
                
        # Check API Key
        api_key = request.headers.get("X-API-Key")
        if not api_key or api_key != app.config.get("API_KEY"):
            return jsonify({"error": "Unauthorized. Invalid or missing X-API-Key header."}), 401
