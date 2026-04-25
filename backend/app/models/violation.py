"""
Violation Model — Stores confirmed unauthorized usage of registered assets.
"""
import uuid
from datetime import datetime, timezone
from app.models import db


class Violation(db.Model):
    __tablename__ = "violations"

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    asset_id = db.Column(db.String(36), db.ForeignKey("assets.id"), nullable=False)
    source_url = db.Column(db.String(1000), nullable=False)          # URL where violation was found
    platform = db.Column(db.String(50), nullable=False)              # web | youtube
    domain = db.Column(db.String(255), nullable=True)                # Extracted domain name
    confidence_score = db.Column(db.Float, default=0.0)              # 0.0 to 1.0
    watermark_match = db.Column(db.Boolean, default=False)           # Watermark verified?
    phash_distance = db.Column(db.Integer, nullable=True)            # Hamming distance from original
    classification = db.Column(db.String(20), default="unclassified")  # authorized|suspicious|violation
    classification_reason = db.Column(db.Text, nullable=True)        # Gemini's reasoning
    status = db.Column(db.String(20), default="detected")            # detected|confirmed|dmca_sent|resolved
    dmca_report_url = db.Column(db.String(500), nullable=True)       # Path to generated DMCA PDF
    thumbnail_url = db.Column(db.String(500), nullable=True)         # Screenshot/thumbnail of violation
    video_id = db.Column(db.String(50), nullable=True)               # YouTube video ID if applicable
    video_title = db.Column(db.String(500), nullable=True)           # YouTube video title
    geo_location = db.Column(db.String(100), nullable=True)          # Approximate geo (country/region)
    detected_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    def to_dict(self):
        return {
            "id": self.id,
            "asset_id": self.asset_id,
            "source_url": self.source_url,
            "platform": self.platform,
            "domain": self.domain,
            "confidence_score": self.confidence_score,
            "watermark_match": self.watermark_match,
            "phash_distance": self.phash_distance,
            "classification": self.classification,
            "classification_reason": self.classification_reason,
            "status": self.status,
            "dmca_report_url": self.dmca_report_url,
            "thumbnail_url": self.thumbnail_url,
            "video_id": self.video_id,
            "video_title": self.video_title,
            "geo_location": self.geo_location,
            "detected_at": self.detected_at.isoformat() if self.detected_at else None,
        }

    def __repr__(self):
        return f"<Violation {self.platform}:{self.source_url[:50]}>"
