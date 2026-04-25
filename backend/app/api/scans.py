"""
Scans API — Trigger and view scan history.
Stub endpoints for Day 1. Full implementation in Day 2.
"""
from flask import Blueprint, jsonify
from app.models.scan_log import ScanLog
from app.models.asset import Asset

scans_bp = Blueprint("scans", __name__)


@scans_bp.route("/scans/trigger", methods=["POST"])
def trigger_scan_all():
    """Manually trigger a dual-channel scan for all assets."""
    from app.services.scanner import ScannerService
    
    # In a real production app, this would trigger an async celery task
    # For hackathon demo purposes, we run it synchronously
    result = ScannerService.scan_all_assets()
    
    return jsonify({
        "message": f"Scan completed for {result['scanned']} assets",
        "details": result['details'],
        "status": "success"
    })


@scans_bp.route("/scans/trigger/<asset_db_id>", methods=["POST"])
def trigger_scan_single(asset_db_id):
    """Manually trigger a dual-channel scan for a single asset."""
    from app.services.scanner import ScannerService
    
    asset = Asset.query.get(asset_db_id)
    if not asset:
        return jsonify({"error": "Asset not found"}), 404

    result = ScannerService.scan_asset(asset)
    
    return jsonify({
        "message": f"Scan completed for {asset.asset_id}",
        "status": "success",
        "results": result
    })


@scans_bp.route("/scans", methods=["GET"])
def get_scan_history():
    """Get scan history with API usage breakdown."""
    logs = ScanLog.query.order_by(ScanLog.scanned_at.desc()).limit(100).all()

    # Aggregate stats
    total_serpapi_units = sum(l.api_units_used for l in logs if l.channel == "serpapi")
    total_youtube_units = sum(l.api_units_used for l in logs if l.channel == "youtube")

    return jsonify({
        "count": len(logs),
        "scan_logs": [l.to_dict() for l in logs],
        "usage_summary": {
            "serpapi_units_used": total_serpapi_units,
            "youtube_units_used": total_youtube_units,
            "total_scans": len(logs),
        }
    })
