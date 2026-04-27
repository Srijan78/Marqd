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
    def _check_stop_requested() -> bool:
        """Check if a stop has been requested via the DB stop flag."""
        state = ScanState.query.first()
        if state and state.stop_requested:
            logger.info("Stop signal detected. Halting operation.")
            return True
        return False

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
        logger.info(f"========== MASTER SCAN STARTING ==========")
        logger.info(f"Total assets to scan: {len(assets)}")
        for a in assets:
            logger.info(f"  Asset: {a.asset_id} | watermark_status={a.watermark_status} | watermarked_url={a.watermarked_url[:80] if a.watermarked_url else 'NULL'} | keywords={a.keywords[:50] if a.keywords else 'NULL'}")

        # Log API key status (first 6 chars only for security)
        serpapi_key = current_app.config.get("SERPAPI_KEY", "")
        youtube_key = current_app.config.get("YOUTUBE_API_KEY", "")
        gemini_key = current_app.config.get("GEMINI_API_KEY", "")
        use_mock = current_app.config.get("USE_MOCK_APIS", False)
        logger.info(f"API Config: USE_MOCK_APIS={use_mock} | SERPAPI_KEY={'SET(' + serpapi_key[:6] + '...)' if serpapi_key else 'EMPTY'} | YOUTUBE_KEY={'SET(' + youtube_key[:6] + '...)' if youtube_key else 'EMPTY'} | GEMINI_KEY={'SET(' + gemini_key[:6] + '...)' if gemini_key else 'EMPTY'}")

        results = []
        try:
            for i, asset in enumerate(assets):
                # Re-read stop flag from DB so it works across threads and reloads
                db.session.refresh(state)
                if state.stop_requested:
                    logger.info("Stop signal detected in DB. Halting scan gracefully.")
                    break

                logger.info(f"--- Scanning asset {i+1}/{len(assets)}: {asset.asset_id} ---")
                res = ScannerService.scan_asset(asset)
                results.append({
                    "asset_id": asset.asset_id,
                    "status": "success" if res else "failed"
                })

                # Heartbeat so stale-state detection does not trip during long scans.
                state.last_updated = datetime.now(timezone.utc)
                db.session.commit()
                logger.info(f"--- Asset {asset.asset_id} scan complete: {res} ---")

                # Double-check stop flag after each asset completes
                if ScannerService._check_stop_requested():
                    logger.info("Stop signal detected after asset completion. Halting scan.")
                    break
        finally:
            # Always clear the scanning flag when done, even if an error occurs
            state.is_scanning = False
            state.stop_requested = False
            db.session.commit()
            logger.info(f"========== MASTER SCAN FINISHED: {len(results)} assets scanned ==========")

        return {"scanned": len(results), "details": results}

    @staticmethod
    def scan_asset(asset: Asset) -> dict:
        """
        Run the dual-channel scan for a single asset.
        """
        logger.info(f"[{asset.asset_id}] Starting dual-channel scan")
        start_time = datetime.now(timezone.utc)
        violations_created = 0

        try:
            # 1. Discovery Channel 1: SerpApi (Web)
            serpapi_results = []
            if asset.watermarked_url:
                serpapi_url = asset.watermarked_url

                # FIX: If the URL is still a local /uploads/ path, SerpApi cannot use it.
                # In dev we used a dummy URL; in production this means the asset was not
                # uploaded to GCS yet — skip SerpApi entirely rather than waste a credit
                # searching for example.com/dummy.jpg.
                if serpapi_url.startswith("/uploads/"):
                    is_production = current_app.config.get("FLASK_ENV", "development") == "production"
                    if is_production:
                        logger.error(
                            f"[{asset.asset_id}] SerpApi: SKIPPED — watermarked_url is a local path "
                            f"'{serpapi_url}' in production. Asset was not properly uploaded to GCS."
                        )
                        serpapi_url = None  # Skip this asset's SerpApi search
                    else:
                        public_backend_url = current_app.config.get("PUBLIC_BACKEND_URL", "")
                        if public_backend_url:
                            serpapi_url = f"{public_backend_url}/api{serpapi_url}"
                            logger.info(
                                f"[{asset.asset_id}] SerpApi: DEV mode — using tunneled upload URL: "
                                f"{serpapi_url[:120]}"
                            )
                        else:
                            # Dev fallback: use a publicly-accessible image for smoke-testing
                            logger.warning(
                                f"[{asset.asset_id}] SerpApi: DEV mode — using placeholder URL "
                                f"(set PUBLIC_BACKEND_URL to test your own local uploads with SerpApi)"
                            )
                            serpapi_url = "https://upload.wikimedia.org/wikipedia/commons/thumb/3/3f/JPEG_example_flower.jpg/800px-JPEG_example_flower.jpg"

                if serpapi_url:
                    logger.info(f"[{asset.asset_id}] SerpApi: Calling reverse_image_search with URL: {serpapi_url[:80]}")
                    serpapi_results = SerpApiService.reverse_image_search(asset.asset_id, serpapi_url)
                    logger.info(f"[{asset.asset_id}] SerpApi: Got {len(serpapi_results)} results")

                    # Log SerpApi usage
                    db.session.add(ScanLog(
                        asset_id=asset.id,
                        channel="serpapi",
                        results_count=len(serpapi_results),
                        api_units_used=1,  # 1 search = 1 credit
                        status="completed"
                    ))
            else:
                logger.warning(f"[{asset.asset_id}] SerpApi: SKIPPED (no watermarked_url)")

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

                logger.info(f"[{asset.asset_id}] YouTube: Searching with keywords='{asset.keywords[:50]}', published_after={pub_after}")
                youtube_results = YouTubeService.search_videos(asset.keywords, pub_after)
                logger.info(f"[{asset.asset_id}] YouTube: Got {len(youtube_results)} results")

                # Log YouTube usage (approx 100 units per search query)
                db.session.add(ScanLog(
                    asset_id=asset.id,
                    channel="youtube",
                    results_count=len(youtube_results),
                    api_units_used=100,
                    status="completed"
                ))
            else:
                logger.warning(f"[{asset.asset_id}] YouTube: SKIPPED (no keywords)")

            db.session.commit()

            # Check for stop signal before processing results
            if ScannerService._check_stop_requested():
                logger.info(f"[{asset.asset_id}] Stop signal detected before processing results. Skipping verification.")
                return {"serpapi_results": len(serpapi_results), "youtube_results": len(youtube_results), "violations_created": 0}

            # 3. Process SerpApi Results (Verify + Classify)
            if serpapi_results:
                logger.info(f"[{asset.asset_id}] Processing {len(serpapi_results)} SerpApi results...")
                violations_created += ScannerService._process_web_results(asset, serpapi_results)
            else:
                logger.info(f"[{asset.asset_id}] No SerpApi results to process")

            # 4. Process YouTube Results (Extract + Verify)
            if youtube_results:
                logger.info(f"[{asset.asset_id}] Processing {len(youtube_results)} YouTube results...")
                violations_created += ScannerService._process_youtube_results(asset, youtube_results)
            else:
                logger.info(f"[{asset.asset_id}] No YouTube results to process")

            end_time = datetime.now(timezone.utc)
            duration_ms = int((end_time - start_time).total_seconds() * 1000)

            logger.info(f"[{asset.asset_id}] Scan complete. {violations_created} violations found in {duration_ms}ms.")

            return {
                "serpapi_results": len(serpapi_results),
                "youtube_results": len(youtube_results),
                "violations_created": violations_created,
                "duration_ms": duration_ms
            }

        except Exception as e:
            logger.error(f"[{asset.asset_id}] Scan FAILED with exception: {e}", exc_info=True)
            db.session.rollback()
            return {}

    @staticmethod
    def _process_web_results(asset: Asset, results: list[dict]) -> int:
        """Verify web results, classify domains, and create violations."""
        created = 0

        # Classify all domains in one batch via Gemini
        logger.info(f"[{asset.asset_id}] Gemini: Classifying {len(results)} domains...")
        classified = GeminiService.classify_domains(results, asset.org_name)
        class_map = {c["url"]: c for c in classified}
        logger.info(f"[{asset.asset_id}] Gemini: Classification complete")

        for idx, result in enumerate(results):
            # Check for stop signal before processing each result
            if ScannerService._check_stop_requested():
                logger.info(f"[{asset.asset_id}] Stopping web result processing at result {idx+1}/{len(results)}")
                break

            url = result["url"]
            thumbnail = result.get("thumbnail")

            # Check if violation already exists
            existing = Violation.query.filter_by(asset_id=asset.id, source_url=url).first()
            if existing:
                logger.info(f"[{asset.asset_id}] Web result {idx+1}: SKIP (already exists) {url[:60]}")
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
                logger.info(f"[{asset.asset_id}] Web result {idx+1}: SKIP (download failed) {url[:60]}")
                continue

            v_res = VerificationService.verify_content(local_path, asset.asset_id, asset.phash)
            logger.info(f"[{asset.asset_id}] Web result {idx+1}: Verification → match={v_res['match']}, confidence={v_res['confidence']:.2f}")

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
                logger.info(f"[{asset.asset_id}] Web result {idx+1}: VIOLATION CREATED → {url[:60]}")

            # Cleanup temp file
            if os.path.exists(local_path):
                os.remove(local_path)

        if created > 0:
            db.session.commit()
        return created

    @staticmethod
    def _process_youtube_results(asset: Asset, results: list[dict]) -> int:
        """Extract frames from YouTube videos, verify with Gemini classification, and create violations."""
        created = 0

        # FIX: Run Gemini classification on ALL matching YouTube results upfront,
        # same as web results — so legitimate news channels are not blindly flagged.
        # Build url-info dicts that match the format GeminiService expects.
        all_url_infos = [
            {
                "url": f"https://www.youtube.com/watch?v={r.get('video_id', '')}",
                "domain": "youtube.com",
                "title": r.get("title", ""),
                "channel_title": r.get("channel_title", ""),
            }
            for r in results
            if YouTubeService.validate_video_id(r.get("video_id", ""))
        ]

        logger.info(f"[{asset.asset_id}] Gemini: Classifying {len(all_url_infos)} YouTube channels...")
        classified = GeminiService.classify_domains(all_url_infos, asset.org_name)
        class_map = {c["url"]: c for c in classified}
        logger.info(f"[{asset.asset_id}] Gemini: YouTube classification complete")

        for idx, result in enumerate(results):
            # Check for stop signal before processing each result
            if ScannerService._check_stop_requested():
                logger.info(f"[{asset.asset_id}] Stopping YouTube result processing at result {idx+1}/{len(results)}")
                break

            video_id = result.get("video_id", "")
            if not YouTubeService.validate_video_id(video_id):
                logger.warning(f"[{asset.asset_id}] YT result {idx+1}: SKIP (invalid video_id: {video_id!r})")
                continue

            url = f"https://www.youtube.com/watch?v={video_id}"

            # Check if violation already exists
            existing = Violation.query.filter_by(asset_id=asset.id, video_id=video_id).first()
            if existing:
                logger.info(f"[{asset.asset_id}] YT result {idx+1}: SKIP (already exists) {video_id}")
                continue

            # Step 10 & 11 implementation: Extract thumbnail frames and verify
            logger.info(f"[{asset.asset_id}] YT result {idx+1}: Extracting frames for {video_id}...")
            frame_paths = YouTubeService.extract_frames(video_id, max_frames=3)
            logger.info(f"[{asset.asset_id}] YT result {idx+1}: Got {len(frame_paths)} frames")

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

            logger.info(f"[{asset.asset_id}] YT result {idx+1}: Verification → match={is_match}, confidence={best_confidence:.2f}")

            if is_match:
                # Use Gemini classification result (AUTHORIZED / SUSPICIOUS / VIOLATION)
                c_info = class_map.get(url, {})
                classification = c_info.get("category", "violation").lower()
                classification_reason = c_info.get(
                    "reason",
                    f"Unauthorized re-upload on channel: {result.get('channel_title')}"
                )

                # Skip if Gemini says it's an authorized channel
                if classification == "authorized":
                    logger.info(
                        f"[{asset.asset_id}] YT result {idx+1}: AUTHORIZED by Gemini — skipping. "
                        f"Channel: {result.get('channel_title')} | Reason: {classification_reason}"
                    )
                    # Cleanup and continue
                    for frame_path in frame_paths:
                        if os.path.exists(frame_path):
                            os.remove(frame_path)
                    continue

                platform = "youtube_shorts" if "shorts" in result.get("title", "").lower() else "youtube"

                violation = Violation(
                    asset_id=asset.id,
                    source_url=url,
                    platform=platform,
                    domain="youtube.com",
                    confidence_score=best_confidence,
                    watermark_match=wm_match,
                    phash_distance=best_phash,
                    classification=classification,
                    classification_reason=classification_reason,
                    thumbnail_url=result.get("thumbnail"),
                    video_id=video_id,
                    video_title=result.get("title")
                )
                db.session.add(violation)
                created += 1
                logger.info(
                    f"[{asset.asset_id}] YT result {idx+1}: {classification.upper()} VIOLATION CREATED "
                    f"→ {video_id} | Channel: {result.get('channel_title')}"
                )

            # Cleanup frames
            for frame_path in frame_paths:
                if os.path.exists(frame_path):
                    os.remove(frame_path)

        if created > 0:
            db.session.commit()
        return created
