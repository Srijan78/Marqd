"""
Scans API — Trigger and view scan history.
"""
import threading
from flask import Blueprint, jsonify
from app.models.scan_log import ScanLog
from app.models.scan_state import ScanState
from app.models.asset import Asset
from app.models import db

scans_bp = Blueprint("scans", __name__)


@scans_bp.route("/scans/trigger", methods=["POST"])
def trigger_scan_all():
    """Manually trigger a dual-channel scan for all assets in a background thread."""
    from flask import current_app
    from app.services.scanner import ScannerService

    state = ScanState.get()
    if state.is_scanning:
        return jsonify({"message": "Scan already in progress", "status": "already_running"}), 200

    # Run the scan in a background thread so the HTTP request returns immediately.
    # The frontend polls /api/scans to check is_scanning status.
    app = current_app._get_current_object()

    def run_scan():
        with app.app_context():
            ScannerService.scan_all_assets()

    thread = threading.Thread(target=run_scan, daemon=True)
    thread.start()

    return jsonify({
        "message": "Scan started in background",
        "status": "started"
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


@scans_bp.route("/scans/stop", methods=["POST"])
def stop_scan():
    """Gracefully stop an ongoing master scan."""
    state = ScanState.get()

    if not state.is_scanning:
        return jsonify({"message": "No scan is currently running", "status": "ignored"}), 200

    state.stop_requested = True
    db.session.commit()
    return jsonify({"message": "Stop signal sent. Scan will finish the current asset and halt.", "status": "stopping"})


@scans_bp.route("/scans", methods=["GET"])
def get_scan_history():
    """Get scan history with API usage breakdown and current scan status."""
    logs = ScanLog.query.order_by(ScanLog.scanned_at.desc()).limit(100).all()
    state = ScanState.get()

    # Aggregate stats
    total_serpapi_units = sum(l.api_units_used for l in logs if l.channel == "serpapi")
    total_youtube_units = sum(l.api_units_used for l in logs if l.channel == "youtube")

    return jsonify({
        "count": len(logs),
        "is_scanning": state.is_scanning,
        "scan_logs": [l.to_dict() for l in logs],
        "usage_summary": {
            "serpapi_units_used": total_serpapi_units,
            "youtube_units_used": total_youtube_units,
            "total_scans": len(logs),
        }
    })
