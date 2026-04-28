"""
Assets API — Upload, register, list, and manage protected media assets.

This is the primary entry point for Layer 1 (Authentication).
POST /api/assets triggers the full pipeline: save → pHash → watermark → upload → store.
"""
import os
import uuid
import logging
from datetime import datetime, timezone
from flask import Blueprint, request, jsonify, current_app, send_from_directory
from werkzeug.utils import secure_filename

from app.models import db
from app.models.asset import Asset
from app.services.watermark import WatermarkService
from app.services.hashing import HashingService
from app.services.storage import StorageService

logger = logging.getLogger(__name__)
assets_bp = Blueprint("assets", __name__)


def _allowed_file(filename: str) -> tuple[bool, str]:
    """Check if file extension is allowed. Returns (allowed, file_type)."""
    ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
    if ext in current_app.config.get("ALLOWED_IMAGE_EXTENSIONS", set()):
        return True, "image"
    if ext in current_app.config.get("ALLOWED_VIDEO_EXTENSIONS", set()):
        return True, "video"
    return False, ""


def _generate_asset_id(org_name: str, filename: str) -> str:
    """Generate a unique asset ID like IPL_2025_FINAL_IMG_047."""
    short_id = uuid.uuid4().hex[:6].upper()
    name_part = os.path.splitext(filename)[0][:20].upper().replace(" ", "_")
    org_part = org_name[:10].upper().replace(" ", "_")
    return f"{org_part}_{name_part}_{short_id}"


@assets_bp.route("/assets", methods=["POST"])
def register_asset():
    """
    Upload and register a new asset.
    Triggers: save temp → generate pHash → embed watermark → upload to storage → save DB.

    Form fields:
        - file: The media file (required)
        - keywords: Comma-separated search keywords (required)
        - org_name: Organization name (optional, defaults to 'Marqd Org')
        - asset_id: Custom asset ID (optional, auto-generated if not provided)
    """
    # Validate file
    if "file" not in request.files:
        return jsonify({"error": "No file provided"}), 400

    file = request.files["file"]
    if file.filename == "":
        return jsonify({"error": "No file selected"}), 400

    allowed, file_type = _allowed_file(file.filename)
    if not allowed:
        return jsonify({"error": f"File type not allowed. Supported: images (jpg, png, webp), videos (mp4, mov)"}), 400

    # Extract form data
    keywords = request.form.get("keywords", "")
    org_name = request.form.get("org_name", "Marqd Org")
    custom_asset_id = request.form.get("asset_id", "")

    if not keywords.strip():
        return jsonify({"error": "Keywords are required for YouTube monitoring"}), 400

    try:
        # 1. Save to temp
        filename = secure_filename(file.filename)
        unique_id = str(uuid.uuid4())
        ext = filename.rsplit(".", 1)[-1].lower()
        temp_original = os.path.join(current_app.config["TEMP_FOLDER"], f"{unique_id}_original.{ext}")
        temp_watermarked = os.path.join(current_app.config["TEMP_FOLDER"], f"{unique_id}_watermarked.{ext}")

        file.save(temp_original)
        file_size = os.path.getsize(temp_original)

        # 2. Generate asset ID
        asset_id = custom_asset_id if custom_asset_id else _generate_asset_id(org_name, filename)

        # 3. Generate pHash (images only for now)
        phash = None
        if file_type == "image":
            phash = HashingService.generate_phash(temp_original)

        # 4. Embed watermark
        watermark_status = "pending"
        import shutil
        if file_type == "image":
            success = WatermarkService.embed_watermark(temp_original, temp_watermarked, asset_id)
            watermark_status = "embedded" if success else "failed"
            if not success:
                shutil.copy2(temp_original, temp_watermarked)
        else:
            # Video watermarking — copy original as placeholder for now
            shutil.copy2(temp_original, temp_watermarked)
            watermark_status = "pending_video"

        # 5. Upload to storage
        original_url = StorageService.upload_file(
            temp_original,
            f"assets/original/{unique_id}.{ext}",
            content_type=f"{'image' if file_type == 'image' else 'video'}/{ext}"
        )
        watermarked_url = StorageService.upload_file(
            temp_watermarked,
            f"assets/watermarked/{unique_id}.{ext}",
            content_type=f"{'image' if file_type == 'image' else 'video'}/{ext}"
        )

        # 6. Save to database
        asset = Asset(
            id=unique_id,
            asset_id=asset_id,
            org_name=org_name,
            original_url=original_url,
            watermarked_url=watermarked_url,
            phash=phash,
            keywords=keywords.strip(),
            file_type=file_type,
            file_name=filename,
            file_size=file_size,
            watermark_status=watermark_status,
        )
        db.session.add(asset)
        db.session.commit()

        # 7. Cleanup temp files
        for temp_file in [temp_original, temp_watermarked]:
            if os.path.exists(temp_file):
                os.remove(temp_file)

        logger.info(f"Asset registered: {asset_id}")
        return jsonify({
            "message": "Asset registered successfully",
            "asset": asset.to_dict()
        }), 201

    except Exception as e:
        db.session.rollback()
        logger.error(f"Asset registration failed: {e}")
        return jsonify({"error": "Registration failed. Please try again."}), 500


@assets_bp.route("/assets", methods=["GET"])
def list_assets():
    """List all registered assets."""
    assets = Asset.query.order_by(Asset.created_at.desc()).all()
    return jsonify({
        "count": len(assets),
        "assets": [a.to_dict() for a in assets]
    })


@assets_bp.route("/assets/<asset_db_id>", methods=["GET"])
def get_asset(asset_db_id):
    """Get a single asset with its scan history and violations."""
    asset = Asset.query.get(asset_db_id)
    if not asset:
        return jsonify({"error": "Asset not found"}), 404

    data = asset.to_dict()
    data["violations"] = [v.to_dict() for v in asset.violations]
    data["scan_logs"] = [s.to_dict() for s in asset.scan_logs]
    return jsonify(data)


@assets_bp.route("/assets/<asset_db_id>", methods=["DELETE"])
def delete_asset(asset_db_id):
    """Delete an asset and its associated data."""
    asset = Asset.query.get(asset_db_id)
    if not asset:
        return jsonify({"error": "Asset not found"}), 404

    try:
        # Delete from storage
        def extract_path(url):
            if not url:
                return ""
            if url.startswith("https://storage.googleapis.com/"):
                parts = url.split("/")
                return "/".join(parts[4:])
            return url.replace("/uploads/", "")

        if asset.original_url:
            StorageService.delete_file(extract_path(asset.original_url))
        if asset.watermarked_url:
            StorageService.delete_file(extract_path(asset.watermarked_url))

        db.session.delete(asset)
        db.session.commit()

        return jsonify({"message": f"Asset {asset.asset_id} deleted successfully"})

    except Exception as e:
        db.session.rollback()
        logger.error(f"Asset deletion failed: {e}")
        return jsonify({"error": "Deletion failed. Please try again."}), 500


@assets_bp.route("/assets/<asset_id>/download", methods=["GET"])
def download_asset(asset_id):
    """Proxy download to bypass GCS CORS and trigger Save As."""
    asset = Asset.query.filter_by(asset_id=asset_id).first()
    if not asset:
        return jsonify({"error": "Asset not found"}), 404

    url = asset.watermarked_url
    if not url:
        return jsonify({"error": "No file available"}), 404

    try:
        if url.startswith("http"):
            # It's an external URL (like GCS)
            import requests
            from flask import Response
            req = requests.get(url, stream=True)
            return Response(
                req.iter_content(chunk_size=8192),
                content_type=req.headers['content-type'],
                headers={
                    "Content-Disposition": f"attachment; filename=marqd_{asset.file_name}"
                }
            )
        else:
            # It's a local file
            from flask import send_from_directory, current_app
            import os
            
            # url is like /uploads/assets/watermarked/xyz.jpg
            # Remove the /uploads/ prefix to get the relative path
            rel_path = url.replace("/uploads/", "", 1)
            upload_dir = current_app.config["UPLOAD_FOLDER"]
            directory = os.path.dirname(os.path.join(upload_dir, rel_path))
            filename = os.path.basename(rel_path)
            
            return send_from_directory(
                directory, 
                filename, 
                as_attachment=True, 
                download_name=f"marqd_{asset.file_name}"
            )
    except Exception as e:
        logger.error(f"Failed to proxy download for {asset_id}: {e}")
        return jsonify({"error": "Download failed"}), 500


@assets_bp.route("/uploads/<path:filename>", methods=["GET"])
def serve_upload(filename):
    """Serve uploaded files in development mode."""
    # Security: Prevent path traversal attacks
    if ".." in filename or filename.startswith("/"):
        return jsonify({"error": "Invalid filename"}), 400
    upload_dir = current_app.config["UPLOAD_FOLDER"]
    return send_from_directory(upload_dir, filename)
