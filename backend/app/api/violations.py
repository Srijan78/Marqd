"""
Violations API — List and manage confirmed violations.
Stub endpoints for Day 1. Full implementation in Day 2.
"""
from flask import Blueprint, jsonify, request
from app.models.violation import Violation

violations_bp = Blueprint("violations", __name__)


@violations_bp.route("/violations", methods=["GET"])
def list_violations():
    """List all confirmed violations with optional filters."""
    platform = request.args.get("platform")  # web | youtube
    status = request.args.get("status")      # detected | confirmed | dmca_sent | resolved

    query = Violation.query

    if platform:
        query = query.filter(Violation.platform == platform)
    if status:
        query = query.filter(Violation.status == status)

    violations = query.order_by(Violation.detected_at.desc()).all()

    results = []
    for v in violations:
        data = v.to_dict()
        if v.asset:
            data["original_asset"] = {
                "asset_id": v.asset.asset_id,
                "original_url": v.asset.original_url,
                "watermarked_url": v.asset.watermarked_url,
                "org_name": v.asset.org_name,
            }
        results.append(data)

    return jsonify({
        "count": len(results),
        "violations": results
    })


@violations_bp.route("/violations/<violation_id>", methods=["GET"])
def get_violation(violation_id):
    """Get detailed violation info with comparison data."""
    violation = Violation.query.get(violation_id)
    if not violation:
        return jsonify({"error": "Violation not found"}), 404

    data = violation.to_dict()
    # Include the parent asset info for side-by-side comparison
    if violation.asset:
        data["original_asset"] = {
            "asset_id": violation.asset.asset_id,
            "original_url": violation.asset.original_url,
            "watermarked_url": violation.asset.watermarked_url,
            "org_name": violation.asset.org_name,
        }

    return jsonify(data)
