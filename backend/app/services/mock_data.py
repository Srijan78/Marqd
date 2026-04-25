"""
Mock Data — Realistic mock responses for SerpApi, YouTube Data API, and Gemini.

Used during development to save API credits. Toggle via USE_MOCK_APIS=true in .env.
All mock data simulates the exact response structures of the real APIs.
"""
import random
from datetime import datetime, timezone, timedelta


def mock_serpapi_results(asset_id: str, watermarked_url: str) -> list[dict]:
    """
    Simulate SerpApi Google Reverse Image Search results.
    Returns a list of URLs where the image was "found" on the web.
    """
    mock_domains = [
        {
            "url": "https://www.imgur.com/gallery/stolen-sports-highlight-abc123",
            "domain": "imgur.com",
            "title": "Amazing IPL 2025 Final Moment",
            "thumbnail": "https://i.imgur.com/thumb_abc123.jpg",
            "source": "Imgur",
            "geo": "US",
        },
        {
            "url": "https://www.reddit.com/r/cricket/comments/xyz789/ipl_final_best_shot",
            "domain": "reddit.com",
            "title": "IPL Final - Best Shot of the Tournament",
            "thumbnail": "https://preview.redd.it/thumb_xyz789.jpg",
            "source": "Reddit",
            "geo": "US",
        },
        {
            "url": "https://sportsblog247.wordpress.com/2025/05/ipl-highlights-gallery/",
            "domain": "sportsblog247.wordpress.com",
            "title": "IPL 2025 Highlights Gallery - Unauthorized",
            "thumbnail": None,
            "source": "WordPress Blog",
            "geo": "IN",
        },
        {
            "url": "https://piracystreams.cc/sports/ipl-2025-media/",
            "domain": "piracystreams.cc",
            "title": "Free IPL 2025 Media Downloads",
            "thumbnail": None,
            "source": "Piracy Site",
            "geo": "RU",
        },
        {
            "url": "https://www.espncricinfo.com/series/ipl-2025/photos/final-gallery",
            "domain": "espncricinfo.com",
            "title": "IPL 2025 Final Photo Gallery - ESPN",
            "thumbnail": "https://img.espncricinfo.com/thumb_final.jpg",
            "source": "ESPNcricinfo",
            "geo": "US",
        },
    ]

    # Return a random subset of 2-4 results
    count = random.randint(2, min(4, len(mock_domains)))
    selected = random.sample(mock_domains, count)

    for item in selected:
        item["asset_id"] = asset_id
        item["search_url"] = watermarked_url
        item["found_at"] = datetime.now(timezone.utc).isoformat()

    return selected


def mock_youtube_results(keywords: str) -> list[dict]:
    """
    Simulate YouTube Data API v3 search results.
    Returns a list of recently uploaded videos matching the keywords.
    """
    mock_videos = [
        {
            "video_id": "dQw4w9WgXcQ",
            "title": "IPL 2025 insane moment highlights MUST WATCH",
            "channel_title": "CricketFanUploads",
            "channel_id": "UC_mock_channel_001",
            "published_at": (datetime.now(timezone.utc) - timedelta(hours=3)).isoformat(),
            "description": "Best moments from IPL 2025 final. All credits to original owners.",
            "thumbnail": "https://img.youtube.com/vi/dQw4w9WgXcQ/maxresdefault.jpg",
            "view_count": 15420,
            "platform": "youtube",
        },
        {
            "video_id": "abc123XYZ",
            "title": f"{keywords.split(',')[0].strip()} - Stolen Highlights Compilation",
            "channel_title": "SportsClipsHD",
            "channel_id": "UC_mock_channel_002",
            "published_at": (datetime.now(timezone.utc) - timedelta(hours=8)).isoformat(),
            "description": "Watch the best sports moments. Subscribe for more!",
            "thumbnail": "https://img.youtube.com/vi/abc123XYZ/maxresdefault.jpg",
            "view_count": 8930,
            "platform": "youtube",
        },
        {
            "video_id": "shorts_mock_001",
            "title": f"Wait for it... 🔥 #{keywords.split(',')[0].strip().replace(' ', '')}",
            "channel_title": "ViralSportsShorts",
            "channel_id": "UC_mock_channel_003",
            "published_at": (datetime.now(timezone.utc) - timedelta(hours=1)).isoformat(),
            "description": "",
            "thumbnail": "https://img.youtube.com/vi/shorts_mock_001/maxresdefault.jpg",
            "view_count": 125000,
            "platform": "youtube_shorts",
        },
    ]

    # Return 1-3 results
    count = random.randint(1, len(mock_videos))
    return random.sample(mock_videos, count)


def mock_gemini_classification(urls: list[dict], org_name: str) -> list[dict]:
    """
    Simulate Gemini domain classification results.
    Categories: AUTHORIZED, SUSPICIOUS, VIOLATION
    """
    classification_map = {
        "espncricinfo.com": ("AUTHORIZED", "Official sports news partner with syndication rights"),
        "reddit.com": ("SUSPICIOUS", "User-generated content platform; may be fair use or violation"),
        "imgur.com": ("VIOLATION", "Image hosting site with no syndication agreement; likely unauthorized redistribution"),
        "sportsblog247.wordpress.com": ("VIOLATION", "Unaffiliated blog redistributing content without authorization"),
        "piracystreams.cc": ("VIOLATION", "Known piracy domain distributing unauthorized sports media"),
    }

    results = []
    for url_info in urls:
        domain = url_info.get("domain", "unknown.com")
        category, reason = classification_map.get(
            domain,
            ("SUSPICIOUS", "Domain not recognized; requires manual review")
        )
        results.append({
            "url": url_info.get("url", ""),
            "domain": domain,
            "category": category,
            "reason": reason,
        })

    return results


def mock_gemini_dmca_report(
    org_name: str,
    asset_id: str,
    violation_url: str,
    platform: str,
    watermark_id: str,
    detection_date: str,
) -> str:
    """
    Simulate Gemini DMCA report generation.
    Returns a mock professionally worded DMCA takedown notice.
    """
    if platform == "youtube":
        platform_section = f"""
PLATFORM-SPECIFIC NOTICE (YouTube):
This notice is submitted under YouTube's Copyright Strike process pursuant to
17 U.S.C. § 512(c). The infringing video should be removed or access disabled
within the timeframe required by the Digital Millennium Copyright Act.

Infringing Video URL: {violation_url}
"""
    else:
        platform_section = f"""
PLATFORM-SPECIFIC NOTICE (Web Host):
This notice is directed to the hosting provider of the following URL pursuant
to 17 U.S.C. § 512(c). The infringing content should be removed or access
disabled within the timeframe required by the Digital Millennium Copyright Act.

Infringing Content URL: {violation_url}
"""

    return f"""
================================================================================
                        DMCA TAKEDOWN NOTICE
================================================================================

Date: {detection_date}
Reference: MARQD-DMCA-{asset_id}

TO WHOM IT MAY CONCERN:

I, acting on behalf of {org_name}, am the copyright owner or authorized
representative of the copyright owner of the digital media asset identified below.

ORIGINAL WORK:
  Asset ID: {asset_id}
  Rights Owner: {org_name}
  Registration Platform: Marqd Digital Asset Protection Platform

INFRINGING MATERIAL:
  URL: {violation_url}
  Detection Date: {detection_date}
  Detection Method: Automated watermark extraction and verification

PROOF OF OWNERSHIP:
  Watermark ID "{watermark_id}" was successfully extracted from the infringing
  content using blind watermark decoding (DWT+DCT frequency domain analysis).
  This watermark was embedded in the original asset at the time of registration
  and serves as cryptographic proof of ownership.
{platform_section}
DECLARATION:
I have a good faith belief that the use of the material described above is not
authorized by the copyright owner, its agent, or the law. I declare under
penalty of perjury that the information in this notification is accurate and
that I am the copyright owner or authorized to act on behalf of the owner.

Sincerely,
{org_name}
via Marqd Digital Asset Protection Platform

================================================================================
"""
