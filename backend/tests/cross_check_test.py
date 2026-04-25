import os
from app import create_app
from app.services.verification import VerificationService
from app.models.asset import Asset

app = create_app()

with app.app_context():
    app.config["USE_MOCK_APIS"] = False
    
    print("Fetching assets from database...")
    asset_new = Asset.query.filter_by(asset_id="IOC_OLYMPI_DOWNLOAD_5DF720").first()
    asset_old = Asset.query.filter_by(asset_id="IOC_OLYMPI_ISTOCK-174662203_D482CB").first()
    
    # Using absolute paths to the uploaded watermarked files
    path_new = f"d:\\Project\\Marqd\\backend{asset_new.watermarked_url.replace('/', '\\\\')}"
    path_old = f"d:\\Project\\Marqd\\backend{asset_old.watermarked_url.replace('/', '\\\\')}"
    
    print("\n==================================================")
    print("TEST A (True Positive): Validating NEW image against NEW Asset ID")
    print("Expected result: MATCH")
    print("==================================================")
    res_A = VerificationService.verify_content(path_new, asset_new.asset_id, asset_new.phash)
    print(f"Watermark Match: {res_A['watermark_match']}")
    print(f"Extracted ID: {res_A['extracted_id']}")
    print(f"pHash Distance: {res_A['phash_distance']}")
    print(f"Overall Match Decision: {res_A['match']} (Confidence: {res_A['confidence']})")
    
    print("\n==================================================")
    print("TEST B (True Negative): Validating NEW image against OLD Asset ID/Hash")
    print("Expected result: NO MATCH")
    print("==================================================")
    res_B = VerificationService.verify_content(path_new, asset_old.asset_id, asset_old.phash)
    print(f"Watermark Match: {res_B['watermark_match']}")
    print(f"Extracted ID: {res_B['extracted_id']}")
    print(f"pHash Distance: {res_B['phash_distance']}")
    print(f"Overall Match Decision: {res_B['match']} (Confidence: {res_B['confidence']})")

    print("\n==================================================")
    print("TEST C (True Negative): Validating OLD image against NEW Asset ID/Hash")
    print("Expected result: NO MATCH")
    print("==================================================")
    res_C = VerificationService.verify_content(path_old, asset_new.asset_id, asset_new.phash)
    print(f"Watermark Match: {res_C['watermark_match']}")
    print(f"Extracted ID: {res_C['extracted_id']}")
    print(f"pHash Distance: {res_C['phash_distance']}")
    print(f"Overall Match Decision: {res_C['match']} (Confidence: {res_C['confidence']})")
