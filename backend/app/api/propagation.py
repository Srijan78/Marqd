"""
Propagation API — Asset spread visualization data.
Stub endpoints for Day 1. Full propagation intelligence in Day 2.
"""
from flask import Blueprint, jsonify
from app.models.asset import Asset
from app.models.violation import Violation

propagation_bp = Blueprint("propagation", __name__)


@propagation_bp.route("/propagation", methods=["GET"])
def get_global_propagation_data():
    """Get aggregated propagation data for the global map visualization."""
    violations = Violation.query.all()
    
    platforms = {"web": 0, "youtube": 0, "youtube_shorts": 0}
    geo_counts = {}
    
    for v in violations:
        platforms[v.platform] = platforms.get(v.platform, 0) + 1
        
        # Mock geo clusters based on domains or defaults for visualization
        geo = v.geo_location or ("US" if v.platform == "youtube" else "RU")
        geo_counts[geo] = geo_counts.get(geo, 0) + 1

    # Map country codes to rough coordinates for the map
    geo_coords = {
        "US": {"lat": 37.0902, "lng": -95.7129},
        "IN": {"lat": 20.5937, "lng": 78.9629},
        "RU": {"lat": 61.5240, "lng": 105.3188},
        "GB": {"lat": 55.3781, "lng": -3.4360},
        "BR": {"lat": -14.2350, "lng": -51.9253}
    }

    geo_clusters = []
    for country, count in geo_counts.items():
        coords = geo_coords.get(country, {"lat": 0, "lng": 0})
        geo_clusters.append({
            "country": country,
            "count": count,
            "lat": coords["lat"],
            "lng": coords["lng"]
        })

    return jsonify({
        "propagation_data": {
            "total_nodes": len(violations),
            "platform_breakdown": platforms,
            "geo_clusters": geo_clusters
        }
    })

@propagation_bp.route("/propagation/<asset_db_id>", methods=["GET"])
def get_propagation_data(asset_db_id):
    """Get propagation data for map visualization."""
    asset = Asset.query.get(asset_db_id)
    if not asset:
        return jsonify({"error": "Asset not found"}), 404

    violations = Violation.query.filter_by(asset_id=asset_db_id).all()

    # Build propagation data
    domains = {}
    platforms = {"web": 0, "youtube": 0}
    timeline = []

    for v in violations:
        # Domain breakdown
        if v.domain:
            domains[v.domain] = domains.get(v.domain, 0) + 1

        # Platform split
        platforms[v.platform] = platforms.get(v.platform, 0) + 1

        # Timeline
        timeline.append({
            "date": v.detected_at.isoformat() if v.detected_at else None,
            "platform": v.platform,
            "domain": v.domain,
            "url": v.source_url,
            "geo": v.geo_location,
        })

    # Sort timeline chronologically
    timeline.sort(key=lambda x: x["date"] or "")

    return jsonify({
        "asset_id": asset.asset_id,
        "total_violations": len(violations),
        "domain_breakdown": domains,
        "platform_breakdown": platforms,
        "timeline": timeline,
        "spread_velocity": len(violations),  # TODO: Calculate proper velocity
    })
