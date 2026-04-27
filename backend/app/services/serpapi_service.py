"""
SerpApi Service — Discovery Channel 1: Google Reverse Image Search.

Queries SerpApi's Google Reverse Image Search endpoint with the watermarked asset's
Cloud Storage URL. Returns every URL where that image or visually similar content
appears across the entire indexed web.
"""
import logging
from flask import current_app

logger = logging.getLogger(__name__)


class SerpApiService:
    """Handles SerpApi reverse image search for web-based content discovery."""

    @staticmethod
    def reverse_image_search(asset_id: str, image_url: str) -> list[dict]:
        """
        Search for an image across the web using Google Reverse Image Search via SerpApi.

        Args:
            asset_id: The asset's unique identifier
            image_url: Public URL of the watermarked image (GCS or local)

        Returns:
            List of dicts with keys: url, domain, title, thumbnail, source, geo, found_at
        """
        use_mock = current_app.config.get("USE_MOCK_APIS", False)

        if use_mock:
            return SerpApiService._mock_search(asset_id, image_url)
        else:
            return SerpApiService._real_search(asset_id, image_url)

    @staticmethod
    def _mock_search(asset_id: str, image_url: str) -> list[dict]:
        """Return mock SerpApi results for development."""
        from app.services.mock_data import mock_serpapi_results

        logger.info(f"[MOCK] SerpApi reverse image search for {asset_id}")
        results = mock_serpapi_results(asset_id, image_url)
        logger.info(f"[MOCK] Found {len(results)} results")
        return results

    @staticmethod
    def _real_search(asset_id: str, image_url: str) -> list[dict]:
        """Execute real SerpApi reverse image search."""
        try:
            import serpapi
            from urllib.parse import urlparse

            api_key = current_app.config.get("SERPAPI_KEY", "")
            if not api_key:
                logger.error("SERPAPI_KEY not configured")
                return []

            # SerpApi Google Reverse Image Search
            params = {
                "engine": "google_reverse_image",
                "image_url": image_url,
                "api_key": api_key,
            }

            search = serpapi.search(params)
            raw_results = search.get("image_results", [])

            # Normalize results
            results = []
            for item in raw_results:
                link = item.get("link", "")
                parsed = urlparse(link)
                results.append({
                    "url": link,
                    "domain": parsed.netloc,
                    "title": item.get("title", ""),
                    "thumbnail": item.get("thumbnail", None),
                    "source": item.get("source", ""),
                    "geo": None,  # SerpApi doesn't provide geo directly
                    "asset_id": asset_id,
                    "search_url": image_url,
                })

            logger.info(f"SerpApi found {len(results)} results for {asset_id}")
            return results

        except Exception as e:
            logger.error(f"SerpApi search failed for {asset_id}: {e}")
            return []
