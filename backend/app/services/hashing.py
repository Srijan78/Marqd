"""
Hashing Service — Generates perceptual hashes (pHash) for image fingerprinting.

pHash serves as a secondary verification mechanism alongside watermarks.
It's robust against resizing, minor color changes, and compression.
"""
import logging

logger = logging.getLogger(__name__)


class HashingService:
    """Handles perceptual hash generation and comparison."""

    @staticmethod
    def generate_phash(image_path: str) -> str | None:
        """
        Generate a perceptual hash (pHash) for an image.

        Args:
            image_path: Path to the image file

        Returns:
            Hex string of the pHash, or None on failure
        """
        try:
            import imagehash
            from PIL import Image

            img = Image.open(image_path)
            phash = imagehash.phash(img, hash_size=16)  # 16x16 for higher precision
            hash_str = str(phash)

            logger.info(f"pHash generated: {hash_str[:16]}... for {image_path}")
            return hash_str

        except Exception as e:
            logger.error(f"Failed to generate pHash for {image_path}: {e}")
            return None

    @staticmethod
    def compare_hashes(hash1: str, hash2: str) -> dict:
        """
        Compare two perceptual hashes and calculate similarity.

        Args:
            hash1: First pHash hex string
            hash2: Second pHash hex string

        Returns:
            Dict with 'distance' (int), 'similarity' (float 0-1), and 'is_match' (bool)
        """
        try:
            import imagehash

            h1 = imagehash.hex_to_hash(hash1)
            h2 = imagehash.hex_to_hash(hash2)

            # Hamming distance — lower = more similar
            distance = h1 - h2
            max_distance = len(h1.hash.flatten())
            similarity = 1.0 - (distance / max_distance) if max_distance > 0 else 0.0

            return {
                "distance": distance,
                "similarity": round(similarity, 4),
                "is_match": distance <= 10,  # Threshold: <=10 bits different = likely same image
            }

        except Exception as e:
            logger.error(f"Failed to compare hashes: {e}")
            return {"distance": -1, "similarity": 0.0, "is_match": False}

    @staticmethod
    def compare_image_to_hash(image_path: str, target_hash: str) -> dict:
        """
        Generate a pHash for an image and compare it to a known hash.

        Args:
            image_path: Path to the image to check
            target_hash: Known pHash to compare against

        Returns:
            Same as compare_hashes, with additional 'generated_hash' field
        """
        generated = HashingService.generate_phash(image_path)
        if generated is None:
            return {"distance": -1, "similarity": 0.0, "is_match": False, "generated_hash": None}

        result = HashingService.compare_hashes(generated, target_hash)
        result["generated_hash"] = generated
        return result
