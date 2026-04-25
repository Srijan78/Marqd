"""
Watermark Service — Embeds and extracts invisible watermarks using blind_watermark (DWT+DCT).

This is the core of Layer 1 (Authentication). Each asset gets a unique Asset ID
embedded as an invisible watermark that survives compression, resizing, and screenshots.
"""
import os
import logging
import numpy as np
from PIL import Image

logger = logging.getLogger(__name__)


class WatermarkService:
    """Handles invisible watermark embedding and extraction."""

    # Watermark image dimensions — the watermark is encoded as a small binary image
    WM_WIDTH = 64
    WM_HEIGHT = 64

    @staticmethod
    def _text_to_bits(text: str) -> np.ndarray:
        """Convert a text string into a binary bit array for watermark embedding."""
        bits = []
        for char in text:
            char_bits = format(ord(char), '08b')
            bits.extend([int(b) for b in char_bits])
        # Pad or truncate to fit WM_WIDTH * WM_HEIGHT
        target_size = WatermarkService.WM_WIDTH * WatermarkService.WM_HEIGHT
        if len(bits) < target_size:
            bits.extend([0] * (target_size - len(bits)))
        else:
            bits = bits[:target_size]
        return np.array(bits)

    @staticmethod
    def _bits_to_text(bits: np.ndarray) -> str:
        """Convert a binary bit array back to a text string."""
        flat = bits.tolist()
        chars = []
        for i in range(0, len(flat), 8):
            byte = flat[i:i+8]
            if len(byte) < 8:
                break
            char_code = int(''.join(str(int(b)) for b in byte), 2)
            if char_code == 0:
                break
            if 32 <= char_code <= 126:  # Printable ASCII
                chars.append(chr(char_code))
        return ''.join(chars)

    @staticmethod
    def embed_watermark(input_path: str, output_path: str, asset_id: str) -> bool:
        """
        Embed an invisible watermark containing the asset_id into an image.

        Args:
            input_path: Path to the original image file
            output_path: Path where the watermarked image will be saved
            asset_id: Unique identifier to embed (e.g., 'IPL_2025_FINAL_IMG_047')

        Returns:
            True if successful, False otherwise
        """
        try:
            from blind_watermark import WaterMark

            bwm = WaterMark(password_img=1, password_wm=1)
            bwm.read_img(input_path)

            # Convert asset_id to binary watermark
            wm_bits = WatermarkService._text_to_bits(asset_id)
            bwm.read_wm(wm_bits, mode='bit')

            bwm.embed(output_path)

            logger.info(f"Watermark embedded successfully: {asset_id} -> {output_path}")
            return True

        except Exception as e:
            logger.error(f"Failed to embed watermark for {asset_id}: {e}")
            return False

    @staticmethod
    def extract_watermark(image_path: str) -> str | None:
        """
        Extract watermark from an image and return the decoded asset_id.

        Args:
            image_path: Path to the potentially watermarked image

        Returns:
            Extracted asset_id string, or None if extraction fails
        """
        try:
            from blind_watermark import WaterMark

            bwm = WaterMark(password_img=1, password_wm=1)
            wm_extract = bwm.extract(
                image_path,
                wm_shape=WatermarkService.WM_HEIGHT * WatermarkService.WM_WIDTH,
                mode='bit'
            )

            # Convert extracted bits back to text
            asset_id = WatermarkService._bits_to_text(np.array(wm_extract))

            if asset_id and len(asset_id) >= 3:  # Minimum viable asset ID
                logger.info(f"Watermark extracted successfully: {asset_id}")
                return asset_id
            else:
                logger.warning(f"Extracted watermark too short or empty: '{asset_id}'")
                return None

        except Exception as e:
            logger.error(f"Failed to extract watermark from {image_path}: {e}")
            return None

    @staticmethod
    def verify_watermark(image_path: str, expected_asset_id: str) -> dict:
        """
        Verify if an image contains the expected watermark.

        Returns:
            Dict with 'match' (bool), 'extracted_id' (str), and 'confidence' (float)
        """
        extracted_id = WatermarkService.extract_watermark(image_path)

        if extracted_id is None:
            return {"match": False, "extracted_id": None, "confidence": 0.0}

        # Calculate character-level match ratio
        match_chars = sum(1 for a, b in zip(extracted_id, expected_asset_id) if a == b)
        max_len = max(len(extracted_id), len(expected_asset_id), 1)
        confidence = match_chars / max_len

        return {
            "match": confidence > 0.7,  # 70% threshold for match
            "extracted_id": extracted_id,
            "confidence": round(confidence, 4),
        }
