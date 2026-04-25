"""Day 2 verification script — tests each step in sequence."""
import sys

def verify_step_8():
    """Verify SerpApi service."""
    from app import create_app
    app = create_app()
    with app.app_context():
        from app.services.serpapi_service import SerpApiService
        results = SerpApiService.reverse_image_search("TEST_001", "http://example.com/img.jpg")
        assert len(results) >= 1, f"Expected at least 1 result, got {len(results)}"
        for r in results:
            assert "url" in r and "domain" in r, f"Missing keys in result: {r.keys()}"
            print(f"  [SerpApi] {r['domain']} -> {r['url'][:70]}")
        print(f"  STEP 8 VERIFIED OK ({len(results)} results)")

def verify_step_9():
    """Verify YouTube service."""
    from app import create_app
    app = create_app()
    with app.app_context():
        from app.services.youtube_service import YouTubeService
        results = YouTubeService.search_videos("IPL 2025 Final cricket highlights")
        assert len(results) >= 1, f"Expected at least 1 result, got {len(results)}"
        for v in results:
            assert "video_id" in v and "title" in v, f"Missing keys: {v.keys()}"
            print(f"  [YouTube] {v['video_id']} -> {v['title'][:50]}")
        print(f"  STEP 9 VERIFIED OK ({len(results)} videos)")

def verify_step_12():
    """Verify Gemini AI services."""
    from app import create_app
    app = create_app()
    with app.app_context():
        from app.services.gemini_service import GeminiService

        # Test classification
        test_urls = [
            {"url": "https://imgur.com/stolen.jpg", "domain": "imgur.com"},
            {"url": "https://espncricinfo.com/gallery", "domain": "espncricinfo.com"},
        ]
        classified = GeminiService.classify_domains(test_urls, "TestOrg")
        assert len(classified) == 2, f"Expected 2 classifications, got {len(classified)}"
        for c in classified:
            print(f"  [Gemini] {c['domain']} -> {c['category']} | {c['reason'][:50]}")

        # Test DMCA generation
        dmca_text = GeminiService.generate_dmca_report(
            org_name="TestOrg",
            asset_id="TEST_ASSET_001",
            violation_url="https://piracy.cc/stolen.jpg",
            platform="web",
            watermark_id="WM_TEST_001",
        )
        assert len(dmca_text) > 100, f"DMCA report too short: {len(dmca_text)} chars"
        assert "DMCA" in dmca_text, "DMCA keyword not found in report"
        print(f"  [Gemini] DMCA report generated: {len(dmca_text)} chars")
        print(f"  STEP 12 VERIFIED OK")

def verify_step_13():
    """Verify scanner orchestration."""
    from app import create_app
    app = create_app()
    with app.app_context():
        from app.services.scanner import ScannerService
        from app.models import db
        from app.models.asset import Asset

        # Check if we have any assets to scan
        assets = Asset.query.filter(Asset.watermark_status.in_(["embedded", "failed"])).all()
        if not assets:
            print("  No assets in DB to scan. Creating a test asset...")
            asset = Asset(
                asset_id="VERIFY_SCANNER_001",
                org_name="VerifyOrg",
                keywords="test,scanner,verify",
                file_type="image",
                watermark_status="embedded",
                watermarked_url="http://example.com/test.jpg",
            )
            db.session.add(asset)
            db.session.commit()
            assets = [asset]

        # Run scan on first asset
        result = ScannerService.scan_asset(assets[0])
        assert "serpapi_results" in result, f"Missing serpapi_results: {result.keys()}"
        assert "youtube_results" in result, f"Missing youtube_results: {result.keys()}"
        assert "violations_created" in result, f"Missing violations_created: {result.keys()}"
        print(f"  [Scanner] Asset: {assets[0].asset_id}")
        print(f"  [Scanner] SerpApi hits: {result['serpapi_results']}")
        print(f"  [Scanner] YouTube hits: {result['youtube_results']}")
        print(f"  [Scanner] Violations created: {result['violations_created']}")
        print(f"  STEP 13 VERIFIED OK")


if __name__ == "__main__":
    step = sys.argv[1] if len(sys.argv) > 1 else "all"
    steps = {
        "8": verify_step_8,
        "9": verify_step_9,
        "12": verify_step_12,
        "13": verify_step_13,
    }

    if step == "all":
        for num, fn in steps.items():
            print(f"\n--- Verifying Step {num} ---")
            fn()
    elif step in steps:
        print(f"\n--- Verifying Step {step} ---")
        steps[step]()
    else:
        print(f"Unknown step: {step}. Available: {list(steps.keys())}")
