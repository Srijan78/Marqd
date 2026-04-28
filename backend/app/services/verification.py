"""
Verification Pipeline — Step 11.

Downloads flagged images/frames and runs watermark extraction and pHash comparison
to confirm ownership before logging a violation.
"""
import os
import time
import logging
from flask import current_app

from app.services.watermark import WatermarkService
from app.services.hashing import HashingService

logger = logging.getLogger(__name__)


class VerificationService:
    """Handles the downloading and verification of flagged content."""

    @staticmethod
    def download_image(url: str) -> str | None:
        """Download an image from a URL to a temporary file."""
        use_mock = current_app.config.get("USE_MOCK_APIS", False)

        if use_mock:
            # Return a dummy image path
            temp_dir = current_app.config["TEMP_FOLDER"]
            os.makedirs(temp_dir, exist_ok=True)
            path = os.path.join(temp_dir, f"mock_dl_{int(time.time())}.jpg")
            from PIL import Image
            img = Image.new("RGB", (200, 200), color="grey")
            img.save(path)
            return path

        try:
            import requests
            import uuid
            from PIL import Image

            temp_dir = current_app.config["TEMP_FOLDER"]
            os.makedirs(temp_dir, exist_ok=True)
            path = os.path.join(temp_dir, f"dl_{uuid.uuid4().hex}.jpg")

            headers = {
                "User-Agent": (
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/124.0.0.0 Safari/537.36"
                ),
                "Accept": "image/avif,image/webp,image/apng,image/*,*/*;q=0.8",
            }

            response = requests.get(
                url,
                stream=True,
                timeout=15,
                headers=headers,
                allow_redirects=True,
            )
            response.raise_for_status()

            content_type = response.headers.get("Content-Type", "").split(";")[0].strip().lower()
            if not content_type.startswith("image/"):
                logger.warning(
                    f"Skipping non-image response from {url} (Content-Type: {content_type or 'unknown'})"
                )
                return None

            with open(path, "wb") as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)

            try:
                with Image.open(path) as img:
                    img.verify()
            except Exception as img_e:
                if os.path.exists(path):
                    os.remove(path)
                logger.warning(f"Downloaded content from {url} is not a valid image: {img_e}")
                return None

            return path

        except Exception as e:
            logger.warning(f"Failed to download image from {url}: {e}")
            return None

    @staticmethod
    def verify_content(image_path: str, expected_asset_id: str, original_phash: str = None) -> dict:
        """
        Run verification on a downloaded image or extracted frame.

        Args:
            image_path: Path to the local image file
            expected_asset_id: The asset ID we expect to find
            original_phash: The pHash of the original asset (optional)

        Returns:
            Dict containing match status, confidence score, etc.
        """
        use_mock = current_app.config.get("USE_MOCK_APIS", False)

        if use_mock:
            # Always return a match in mock mode for testing
            return {
                "match": True,
                "extracted_id": expected_asset_id,
                "confidence": 0.95,
                "phash_distance": 2,
                "watermark_match": True,
            }

        # STEP 1: Fast pHash gate (microseconds)
        # If we have a reference pHash and the image is clearly not a match,
        # skip the expensive watermark decode entirely.
        phash_result = {"distance": None, "similarity": 0.0, "is_match": False}
        if original_phash:
            phash_result = HashingService.compare_image_to_hash(image_path, original_phash)

            # Hard reject: Hamming distance > 15 means clearly different image
            if phash_result["distance"] is not None and phash_result["distance"] > 15:
                return {
                    "match": False,
                    "extracted_id": None,
                    "confidence": 0.0,
                    "phash_distance": phash_result["distance"],
                    "watermark_match": False,
                }

        # STEP 2: Watermark decode — only runs if pHash didn't hard-reject (seconds)
        wm_result = WatermarkService.verify_watermark(image_path, expected_asset_id)

        # STEP 3: Watermark confirmed — highest confidence
        if wm_result["match"]:
            return {
                "match": True,
                "extracted_id": wm_result["extracted_id"],
                "confidence": max(0.8, wm_result["confidence"]),
                "phash_distance": phash_result["distance"],
                "watermark_match": True,
            }

        # STEP 4: pHash fallback — watermark failed but image looks similar
        if original_phash and phash_result["is_match"]:
            return {
                "match": True,
                "extracted_id": wm_result["extracted_id"],
                "confidence": max(0.5, phash_result["similarity"] * 0.8),
                "phash_distance": phash_result["distance"],
                "watermark_match": False,
            }

        return {
            "match": False,
            "extracted_id": wm_result["extracted_id"],
            "confidence": 0.0,
            "phash_distance": phash_result["distance"],
            "watermark_match": False,
        }

