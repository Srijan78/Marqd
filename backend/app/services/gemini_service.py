"""
Gemini AI Service — Domain classification and DMCA report generation.

Integrates Google Gemini 3.1 Flash Lite for two non-decorative purposes:
1. Domain Classification: categorize flagged URLs as AUTHORIZED/SUSPICIOUS/VIOLATION
2. DMCA Report Generation: produce professionally worded takedown notices
"""
import logging
from datetime import datetime, timezone
from flask import current_app

logger = logging.getLogger(__name__)


class GeminiService:
    """Handles Gemini AI interactions for classification and report generation."""

    @staticmethod
    def classify_domains(urls: list[dict], org_name: str, authorized_domains: str = "") -> list[dict]:
        """
        Classify URLs as AUTHORIZED, SUSPICIOUS, or VIOLATION using Gemini.

        Args:
            urls: List of dicts with 'url' and 'domain' keys
            org_name: The rights-holding organization name
            authorized_domains: Comma-separated list of authorized partner domains

        Returns:
            List of dicts with 'url', 'domain', 'category', 'reason'
        """
        use_mock = current_app.config.get("USE_MOCK_APIS", True)

        if use_mock:
            return GeminiService._mock_classify(urls, org_name)
        else:
            return GeminiService._real_classify(urls, org_name, authorized_domains)

    @staticmethod
    def _mock_classify(urls: list[dict], org_name: str) -> list[dict]:
        """Return mock Gemini classification results."""
        from app.services.mock_data import mock_gemini_classification

        logger.info(f"[MOCK] Gemini classifying {len(urls)} domains for {org_name}")
        return mock_gemini_classification(urls, org_name)

    @staticmethod
    def _real_classify(urls: list[dict], org_name: str, authorized_domains: str) -> list[dict]:
        """Call real Gemini API for domain classification."""
        try:
            import google.generativeai as genai
            import json

            api_key = current_app.config.get("GEMINI_API_KEY", "")
            model_name = current_app.config.get("GEMINI_MODEL", "gemini-3.1-flash-lite")

            if not api_key:
                logger.error("GEMINI_API_KEY not configured")
                return [{"url": u.get("url"), "domain": u.get("domain"),
                         "category": "SUSPICIOUS", "reason": "API key not configured"}
                        for u in urls]

            genai.configure(api_key=api_key)
            model = genai.GenerativeModel(model_name)

            url_list = "\n".join([f"- {u.get('url', '')} (domain: {u.get('domain', '')})" for u in urls])

            prompt = f"""Classify each of these URLs for an official sports media asset.
Categories: AUTHORIZED | SUSPICIOUS | VIOLATION
Context: Asset belongs to {org_name}, authorized on {authorized_domains or 'no specific domains listed'}
URLs:
{url_list}

Return ONLY valid JSON array: [{{"url": "...", "domain": "...", "category": "...", "reason": "..."}}]"""

            response = model.generate_content(prompt)
            text = response.text.strip()

            # Extract JSON from response
            if "```json" in text:
                text = text.split("```json")[1].split("```")[0].strip()
            elif "```" in text:
                text = text.split("```")[1].split("```")[0].strip()

            results = json.loads(text)
            logger.info(f"Gemini classified {len(results)} domains")
            return results

        except Exception as e:
            logger.error(f"Gemini classification failed: {e}")
            return [{"url": u.get("url"), "domain": u.get("domain"),
                     "category": "SUSPICIOUS", "reason": f"Classification failed: {str(e)}"}
                    for u in urls]

    @staticmethod
    def generate_dmca_report(
        org_name: str,
        asset_id: str,
        violation_url: str,
        platform: str,
        watermark_id: str,
        detection_date: str = None,
    ) -> str:
        """
        Generate a DMCA takedown notice using Gemini.

        Args:
            org_name: Rights-holding organization
            asset_id: Original asset identifier
            violation_url: URL of the infringing content
            platform: 'web' or 'youtube'
            watermark_id: Extracted watermark ID as proof
            detection_date: When the violation was detected

        Returns:
            String containing the full DMCA notice text
        """
        if not detection_date:
            detection_date = datetime.now(timezone.utc).strftime("%Y-%m-%d")

        use_mock = current_app.config.get("USE_MOCK_APIS", True)

        if use_mock:
            return GeminiService._mock_dmca(
                org_name, asset_id, violation_url, platform, watermark_id, detection_date
            )
        else:
            return GeminiService._real_dmca(
                org_name, asset_id, violation_url, platform, watermark_id, detection_date
            )

    @staticmethod
    def _mock_dmca(org_name, asset_id, violation_url, platform, watermark_id, detection_date):
        """Return mock DMCA report."""
        from app.services.mock_data import mock_gemini_dmca_report

        logger.info(f"[MOCK] Gemini generating DMCA for {violation_url}")
        return mock_gemini_dmca_report(
            org_name, asset_id, violation_url, platform, watermark_id, detection_date
        )

    @staticmethod
    def _real_dmca(org_name, asset_id, violation_url, platform, watermark_id, detection_date):
        """Call real Gemini API for DMCA report generation."""
        try:
            import google.generativeai as genai

            api_key = current_app.config.get("GEMINI_API_KEY", "")
            model_name = current_app.config.get("GEMINI_MODEL", "gemini-3.1-flash-lite")

            if not api_key:
                logger.error("GEMINI_API_KEY not configured — falling back to mock")
                from app.services.mock_data import mock_gemini_dmca_report
                return mock_gemini_dmca_report(
                    org_name, asset_id, violation_url, platform, watermark_id, detection_date
                )

            genai.configure(api_key=api_key)
            model = genai.GenerativeModel(model_name)

            platform_context = (
                "This is for a YouTube copyright strike process."
                if platform == "youtube"
                else "This is for a web host DMCA takedown request."
            )

            prompt = f"""Generate a formal DMCA takedown notice with the following details:
- Rights Owner: {org_name}
- Original Asset ID: {asset_id}
- Infringing URL: {violation_url}
- Detection Date: {detection_date}
- Proof of Ownership: Watermark ID "{watermark_id}" extracted from infringing content
- {platform_context}
Format as a professional legal document ready to send."""

            response = model.generate_content(prompt)
            text = response.text.strip()

            logger.info(f"Gemini generated DMCA report: {len(text)} chars")
            return text

        except Exception as e:
            logger.error(f"Gemini DMCA generation failed: {e}")
            from app.services.mock_data import mock_gemini_dmca_report
            return mock_gemini_dmca_report(
                org_name, asset_id, violation_url, platform, watermark_id, detection_date
            )
