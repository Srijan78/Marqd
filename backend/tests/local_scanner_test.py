
import os
import sys
from dotenv import load_dotenv

# Add the parent directory to sys.path so we can import 'app'
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app
from app.models.asset import Asset
from app.services.scanner import ScannerService

def test_single_asset_scan():
    load_dotenv()
    os.environ['USE_MOCK_APIS'] = 'false'  # Force real APIs
    
    app = create_app()
    with app.app_context():
        # Get the first asset that has embedded status
        asset = Asset.query.filter_by(watermark_status='embedded').first()
        
        if not asset:
            print("No asset found with 'embedded' status. Please upload or register an asset first.")
            return

        print(f"--- Starting local scan for asset: {asset.asset_id} ---")
        print(f"URL: {asset.watermarked_url}")
        print(f"Keywords: {asset.keywords}")
        
        # Run the scan directly (not in a thread)
        result = ScannerService.scan_asset(asset)
        
        print("\n--- Scan Results ---")
        if not result:
            print("Scan returned empty result (likely failed). Check logs above.")
        else:
            print(f"SerpApi results: {result.get('serpapi_results', 0)}")
            print(f"YouTube results: {result.get('youtube_results', 0)}")
            print(f"Violations created: {result.get('violations_created', 0)}")
            print(f"Duration: {result.get('duration_ms', 0)}ms")

if __name__ == "__main__":
    test_single_asset_scan()
