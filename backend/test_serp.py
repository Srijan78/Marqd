import os
import sys
import json
import serpapi

def test():
    params = {
      "engine": "google_reverse_image",
      "image_url": "https://storage.googleapis.com/marqd-assets/assets/watermarked/19205084-9a6f-45b5-a813-d7833c776810.jpg",
      "api_key": "2a16b92f682a72b3fa4f41bd0ace3ddeac9b4b58fe73382bf0dc30041f17c326"
    }

    try:
        results = serpapi.search(params)
        
        image_results = results.get("image_results", [])
        inline_images = results.get("inline_images", [])
        
        print(f"Got {len(image_results)} image_results")
        for i, res in enumerate(image_results[:3]):
            print(f"Result {i}:")
            print(f"  title: {res.get('title')}")
            print(f"  link: {res.get('link')}")
            print(f"  thumbnail: {res.get('thumbnail')}")
            print(f"  original: {res.get('original')}")
            
        print(f"\nGot {len(inline_images)} inline_images")
        for i, res in enumerate(inline_images[:3]):
            print(f"Inline {i}:")
            print(f"  link: {res.get('link')}")
            print(f"  thumbnail: {res.get('thumbnail')}")
            print(f"  original: {res.get('original')}")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test()
