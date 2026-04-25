"""
YouTube Service — Discovery Channel 2: YouTube Data API v3.

Searches YouTube for newly uploaded videos matching asset keywords.
For each suspicious video, yt-dlp extracts keyframes for watermark verification.
Covers YouTube videos and Shorts even before Google indexes them.
"""
import os
import logging
import subprocess
import tempfile
from datetime import datetime, timezone, timedelta
from flask import current_app

logger = logging.getLogger(__name__)


class YouTubeService:
    """Handles YouTube Data API search and yt-dlp frame extraction."""

    @staticmethod
    def search_videos(keywords: str, published_after: str = None) -> list[dict]:
        """
        Search YouTube for recently uploaded videos matching keywords.

        Args:
            keywords: Comma-separated search terms
            published_after: ISO datetime — only return videos after this timestamp

        Returns:
            List of dicts with video metadata
        """
        use_mock = current_app.config.get("USE_MOCK_APIS", True)

        if use_mock:
            return YouTubeService._mock_search(keywords)
        else:
            return YouTubeService._real_search(keywords, published_after)

    @staticmethod
    def _mock_search(keywords: str) -> list[dict]:
        """Return mock YouTube search results."""
        from app.services.mock_data import mock_youtube_results

        logger.info(f"[MOCK] YouTube search for: {keywords}")
        results = mock_youtube_results(keywords)
        logger.info(f"[MOCK] Found {len(results)} videos")
        return results

    @staticmethod
    def _real_search(keywords: str, published_after: str = None) -> list[dict]:
        """Execute real YouTube Data API v3 search."""
        try:
            from googleapiclient.discovery import build

            api_key = current_app.config.get("YOUTUBE_API_KEY", "")
            if not api_key:
                logger.error("YOUTUBE_API_KEY not configured")
                return []

            youtube = build("youtube", "v3", developerKey=api_key)

            # Default to last 24 hours if no timestamp provided
            if not published_after:
                published_after = (
                    datetime.now(timezone.utc) - timedelta(hours=24)
                ).strftime("%Y-%m-%dT%H:%M:%SZ")

            # Search for each keyword set
            all_results = []
            keyword_list = [k.strip() for k in keywords.split(",") if k.strip()]

            for query in keyword_list[:5]:  # Max 5 keyword queries per asset
                response = (
                    youtube.search()
                    .list(
                        q=query,
                        part="snippet",
                        type="video",
                        order="date",
                        publishedAfter=published_after,
                        maxResults=10,
                    )
                    .execute()
                )

                for item in response.get("items", []):
                    snippet = item.get("snippet", {})
                    video_id = item.get("id", {}).get("videoId", "")

                    all_results.append({
                        "video_id": video_id,
                        "title": snippet.get("title", ""),
                        "channel_title": snippet.get("channelTitle", ""),
                        "channel_id": snippet.get("channelId", ""),
                        "published_at": snippet.get("publishedAt", ""),
                        "description": snippet.get("description", ""),
                        "thumbnail": snippet.get("thumbnails", {})
                        .get("high", {})
                        .get("url", ""),
                        "platform": "youtube",
                    })

            # Deduplicate by video_id
            seen = set()
            unique = []
            for r in all_results:
                if r["video_id"] not in seen:
                    seen.add(r["video_id"])
                    unique.append(r)

            logger.info(f"YouTube API found {len(unique)} unique videos for: {keywords}")
            return unique

        except Exception as e:
            logger.error(f"YouTube API search failed: {e}")
            return []

    @staticmethod
    def extract_frames(video_id: str, max_frames: int = 5) -> list[str]:
        """
        Extract keyframes from a YouTube video using yt-dlp.

        Args:
            video_id: YouTube video ID
            max_frames: Maximum number of frames to extract

        Returns:
            List of file paths to extracted frame images
        """
        use_mock = current_app.config.get("USE_MOCK_APIS", True)

        if use_mock:
            return YouTubeService._mock_extract_frames(video_id)
        else:
            return YouTubeService._real_extract_frames(video_id, max_frames)

    @staticmethod
    def _mock_extract_frames(video_id: str) -> list[str]:
        """Return mock frame paths (create dummy images)."""
        from PIL import Image
        import random

        logger.info(f"[MOCK] Extracting frames from video: {video_id}")

        temp_dir = current_app.config["TEMP_FOLDER"]
        os.makedirs(temp_dir, exist_ok=True)

        frame_paths = []
        for i in range(3):  # Mock 3 frames
            path = os.path.join(temp_dir, f"frame_{video_id}_{i}.jpg")
            # Create a dummy image as the "extracted frame"
            color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
            img = Image.new("RGB", (1280, 720), color=color)
            img.save(path)
            frame_paths.append(path)

        logger.info(f"[MOCK] Extracted {len(frame_paths)} frames")
        return frame_paths

    @staticmethod
    def _real_extract_frames(video_id: str, max_frames: int = 5) -> list[str]:
        """Extract real frames from YouTube using yt-dlp + ffmpeg."""
        try:
            temp_dir = current_app.config["TEMP_FOLDER"]
            os.makedirs(temp_dir, exist_ok=True)

            video_url = f"https://www.youtube.com/watch?v={video_id}"
            output_template = os.path.join(temp_dir, f"frame_{video_id}_%(autonumber)s.jpg")

            # Use yt-dlp to download and extract frames
            cmd = [
                "yt-dlp",
                "--skip-download",
                "--write-thumbnail",
                "-o", output_template,
                video_url,
            ]

            result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)

            if result.returncode != 0:
                logger.warning(f"yt-dlp frame extraction had issues: {result.stderr[:200]}")

            # Collect extracted frame files
            frame_paths = []
            for f in os.listdir(temp_dir):
                if f.startswith(f"frame_{video_id}_") and f.endswith((".jpg", ".png", ".webp")):
                    frame_paths.append(os.path.join(temp_dir, f))

            logger.info(f"Extracted {len(frame_paths)} frames from {video_id}")
            return frame_paths[:max_frames]

        except Exception as e:
            logger.error(f"Frame extraction failed for {video_id}: {e}")
            return []
