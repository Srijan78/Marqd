import os
from PIL import Image
from app import create_app
from app.services.verification import VerificationService
from app.models.asset import Asset

app = create_app()

with app.app_context():
    # 1. Locate the watermarked image
    watermarked_path = r"d:\Project\Marqd\backend\uploads\assets\watermarked\85ed5db7-5f46-4a44-b7f0-864546187958.jpg"
    expected_id = "IOC_OLYMPI_ISTOCK-174662203_D482CB"
    asset = Asset.query.filter_by(asset_id=expected_id).first()
    original_phash = asset.phash
    
    stolen_path = "stolen_image.jpg"
    
    print(f"--- Simulating Piracy ---")
    img = Image.open(watermarked_path)
    # Resize to 90%
    new_size = (int(img.width * 0.9), int(img.height * 0.9))
    stolen_img = img.resize(new_size, Image.Resampling.LANCZOS)
    # Save with JPEG compression quality 50
    stolen_img.save(stolen_path, "JPEG", quality=50)
    
    # 2. Feed the stolen image into our Verification Engine (including pHash fallback)
    print(f"\n--- Running Verification Engine ---")
    app.config["USE_MOCK_APIS"] = False
    
    result = VerificationService.verify_content(stolen_path, expected_id, original_phash)
    
    print("\nRESULTS:")
    print(f"Watermark Match: {result['watermark_match']}")
    print(f"Extracted ID string: {result['extracted_id']}")
    print(f"pHash Distance: {result['phash_distance']} (out of 64 bits)")
    print(f"Overall Confidence Score: {result['confidence']:.2f}")
    
    if result['match']:
        print("\nSUCCESS: The verification engine caught the stolen image via pHash fallback!")
    else:
        print("\nFAILED: Both watermark and pHash were destroyed.")
