"""
Scanner Orchestration — Step 13.

The master service that runs the dual discovery pipeline (SerpApi + YouTube),
passes results through the Verification pipeline, classifies domains with Gemini,
and stores confirmed Violations in the database.
"""
import os
import logging
from datetime import datetime, timezone
from flask import current_app

from app.models import db
from app.models.asset import Asset
from app.models.violation import Violation
from app.models.scan_log import ScanLog
from app.models.scan_state import ScanState
from app.services.serpapi_service import SerpApiService
from app.services.youtube_service import YouTubeService
from app.services.verification import VerificationService
from app.services.gemini_service import GeminiService

logger = logging.getLogger(__name__)


class ScannerService:
    """Orchestrates the entire scanning and verification process."""

    @staticmethod
    def scan_all_assets() -> dict:
        """Run scan for all embedded assets (intended for APScheduler)."""
        state = ScanState.get()
        if state.is_scanning:
            logger.warning("Scan already in progress, ignoring duplicate request.")
            return {"scanned": 0, "details": [], "status": "already_running"}

        # Mark scan as active in DB — survives reloads and container restarts
        state.is_scanning = True
        state.stop_requested = False
        db.session.commit()

        assets = Asset.query.filter(Asset.watermark_status.in_(["embedded", "failed"])).all()
        logger.info(f"Starting master scan for {len(assets)} assets")

        results = []
        try:
            for asset in assets:
                # Re-read stop flag from DB so it works across threads and reloads
                db.session.refresh(state)
                if state.stop_requested:
                    logger.info("Stop signal detected in DB. Halting scan gracefully.")
                    break

                res = ScannerService.scan_asset(asset)
                results.append({
                    "asset_id": asset.asset_id,
                    "status": "success" if res else "failed"
                })
        finally:
            # Always clear the scanning flag when done, even if an error occurs
            state.is_scanning = False
            state.stop_requested = False
            db.session.commit()

        return {"scanned": len(results), "details": results}

    @staticmethod
    def scan_asset(asset: Asset) -> dict:
        """
        Run the dual-channel scan for a single asset.
        """
        logger.info(f"Scanning asset: {asset.asset_id}")
        start_time = datetime.now(timezone.utc)
        violations_created = 0

        try:
            # 1. Discovery Channel 1: SerpApi (Web)
            serpapi_results = []
            if asset.watermarked_url:
                serpapi_url = asset.watermarked_url
                # In local dev, use a dummy public URL if it's a local path
                if serpapi_url.startswith("/uploads/"):
                    serpapi_url = "https://example.com/dummy.jpg"

                serpapi_results = SerpApiService.reverse_image_search(asset.asset_id, serpapi_url)

                # Log SerpApi usage
                db.session.add(ScanLog(
                    asset_id=asset.id,
                    channel="serpapi",
                    results_count=len(serpapi_results),
                    api_units_used=1,  # 1 search = 1 credit
                    status="completed"
                ))

            # 2. Discovery Channel 2: YouTube API
            youtube_results = []
            if asset.keywords:
                # Find the last scan time for this asset on YouTube to avoid duplicates
                last_scan = ScanLog.query.filter_by(
                    asset_id=asset.id, channel="youtube", status="completed"
                ).order_by(ScanLog.scanned_at.desc()).first()

                if last_scan and last_scan.scanned_at:
                    # YouTube API requires RFC 3339 format (must end with 'Z')
                    dt = last_scan.scanned_at
                    if dt.tzinfo is None:
                        pub_after = dt.isoformat() + "Z"
                    else:
                        # If it has a timezone, convert to UTC and add Z
                        pub_after = dt.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
                else:
                    pub_after = None
                youtube_results = YouTubeService.search_videos(asset.keywords, pub_after)

                # Log YouTube usage (approx 100 units per search query)
                db.session.add(ScanLog(
                    asset_id=asset.id,
                    channel="youtube",
                    results_count=len(youtube_results),
                    api_units_used=100,
                    status="completed"
                ))

            db.session.commit()

            # 3. Process SerpApi Results (Verify + Classify)
            if serpapi_results:
                violations_created += ScannerService._process_web_results(asset, serpapi_results)

            # 4. Process YouTube Results (Extract + Verify)
            if youtube_results:
                violations_created += ScannerService._process_youtube_results(asset, youtube_results)

            end_time = datetime.now(timezone.utc)
            duration_ms = int((end_time - start_time).total_seconds() * 1000)

            logger.info(f"Scan complete for {asset.asset_id}. Found {violations_created} violations in {duration_ms}ms.")

            return {
                "serpapi_results": len(serpapi_results),
                "youtube_results": len(youtube_results),
                "violations_created": violations_created,
                "duration_ms": duration_ms
            }

        except Exception as e:
            logger.error(f"Scan failed for asset {asset.asset_id}: {e}")
            db.session.rollback()
            return {}

    @staticmethod
    def _process_web_results(asset: Asset, results: list[dict]) -> int:
        """Verify web results, classify domains, and create violations."""
        created = 0

        # Classify all domains in one batch via Gemini
        classified = GeminiService.classify_domains(results, asset.org_name)
        class_map = {c["url"]: c for c in classified}

        for result in results:
            url = result["url"]
            thumbnail = result.get("thumbnail")

            # Check if violation already exists
            existing = Violation.query.filter_by(asset_id=asset.id, source_url=url).first()
            if existing:
                continue

            # Step 11 implementation: Download and Verify
            candidate_urls = []
            if thumbnail:
                candidate_urls.append(thumbnail)
            if url and url not in candidate_urls:
                candidate_urls.append(url)

            local_path = None
            for candidate_url in candidate_urls:
                local_path = VerificationService.download_image(candidate_url)
                if local_path:
                    break

            if not local_path:
                logger.info(
                    f"Skipping web result; unable to download a valid image from {url}"
                )
                continue

            v_res = VerificationService.verify_content(local_path, asset.asset_id, asset.phash)

            if v_res["match"]:
                c_info = class_map.get(url, {})

                violation = Violation(
                    asset_id=asset.id,
                    source_url=url,
                    platform="web",
                    domain=result.get("domain"),
                    confidence_score=v_res["confidence"],
                    watermark_match=v_res["watermark_match"],
                    phash_distance=v_res["phash_distance"],
                    classification=c_info.get("category", "unclassified"),
                    classification_reason=c_info.get("reason"),
                    thumbnail_url=thumbnail,
                    geo_location=result.get("geo")
                )
                db.session.add(violation)
                created += 1

            # Cleanup temp file
            if os.path.exists(local_path):
                os.remove(local_path)

        if created > 0:
            db.session.commit()
        return created

    @staticmethod
    def _process_youtube_results(asset: Asset, results: list[dict]) -> int:
        """Extract frames from YouTube videos, verify, and create violations."""
        created = 0

        for result in results:
            video_id = result.get("video_id", "")
            if not YouTubeService.validate_video_id(video_id):
                logger.warning(f"Skipping YouTube result with invalid video_id: {video_id!r}")
                continue

            url = f"https://www.youtube.com/watch?v={video_id}"

            # Check if violation already exists
            existing = Violation.query.filter_by(asset_id=asset.id, video_id=video_id).first()
            if existing:
                continue

            # Step 10 & 11 implementation: Extract thumbnail frames and verify
            frame_paths = YouTubeService.extract_frames(video_id, max_frames=3)
            is_match = False
            best_confidence = 0.0
            wm_match = False
            best_phash = None

            for frame_path in frame_paths:
                v_res = VerificationService.verify_content(frame_path, asset.asset_id, asset.phash)
                if v_res["match"]:
                    is_match = True
                    wm_match = wm_match or v_res["watermark_match"]
                    best_confidence = max(best_confidence, v_res["confidence"])
                    best_phash = v_res["phash_distance"] if best_phash is None else min(best_phash, v_res["phash_distance"])

            if is_match:
                violation = Violation(
                    asset_id=asset.id,
                    source_url=url,
                    platform="youtube_shorts" if "shorts" in result.get("title", "").lower() else "youtube",
                    domain="youtube.com",
                    confidence_score=best_confidence,
                    watermark_match=wm_match,
                    phash_distance=best_phash,
                    classification="violation",  # YouTube re-uploads are generally violations
                    classification_reason=f"Unauthorized re-upload on channel: {result.get('channel_title')}",
                    thumbnail_url=result.get("thumbnail"),
                    video_id=video_id,
                    video_title=result.get("title")
                )
                db.session.add(violation)
                created += 1

            # Cleanup frames
            for frame_path in frame_paths:
                if os.path.exists(frame_path):
                    os.remove(frame_path)

        if created > 0:
            db.session.commit()
        return created
