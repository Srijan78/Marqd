import os
from PIL import Image
from app import create_app
from app.services.verification import VerificationService
from app.models.asset import Asset

app = create_app()

with app.app_context():
    watermarked_path = r"d:\Project\Marqd\backend\uploads\assets\watermarked\85ed5db7-5f46-4a44-b7f0-864546187958.jpg"
    expected_id = "IOC_OLYMPI_ISTOCK-174662203_D482CB"
    asset = Asset.query.filter_by(asset_id=expected_id).first()
    
    # Simulating a LIGHT piracy (e.g. someone right-clicking and saving the image)
    # We will just re-save it with standard JPEG compression (Quality 90) without resizing
    light_stolen_path = "light_stolen_image.jpg"
    
    img = Image.open(watermarked_path)
    img.save(light_stolen_path, "JPEG", quality=90)
    
    print("--- Running Verification on LIGHTLY Modified Image ---")
    app.config["USE_MOCK_APIS"] = False
    result = VerificationService.verify_content(light_stolen_path, expected_id, asset.phash)
    
    print(f"Watermark Match: {result['watermark_match']}")
    if result['watermark_match']:
        print(f"Extracted ID string: {result['extracted_id']}")
