"""
Asset Model — Stores registered media assets with watermark and hash metadata.
"""
import uuid
from datetime import datetime, timezone
from app.models import db


class Asset(db.Model):
    __tablename__ = "assets"

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    asset_id = db.Column(db.String(100), unique=True, nullable=False)  # e.g. IPL_2025_FINAL_IMG_047
    org_name = db.Column(db.String(200), nullable=False, default="Marqd Org")
    original_url = db.Column(db.String(500), nullable=True)     # GCS URL of original
    watermarked_url = db.Column(db.String(500), nullable=True)   # GCS URL of watermarked version
    phash = db.Column(db.String(64), nullable=True)              # Perceptual hash fingerprint
    keywords = db.Column(db.Text, nullable=True)                 # Comma-separated search keywords
    file_type = db.Column(db.String(10), nullable=False)         # image or video
    file_name = db.Column(db.String(255), nullable=True)
    file_size = db.Column(db.Integer, nullable=True)             # File size in bytes
    watermark_status = db.Column(db.String(20), default="pending")  # pending, embedded, failed
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc),
                           onupdate=lambda: datetime.now(timezone.utc))

    # Relationships
    violations = db.relationship("Violation", backref="asset", lazy=True, cascade="all, delete-orphan")
    scan_logs = db.relationship("ScanLog", backref="asset", lazy=True, cascade="all, delete-orphan")

    def to_dict(self):
        return {
            "id": self.id,
            "asset_id": self.asset_id,
            "org_name": self.org_name,
            "original_url": self.original_url,
            "watermarked_url": self.watermarked_url,
            "phash": self.phash,
            "keywords": self.keywords.split(",") if self.keywords else [],
            "file_type": self.file_type,
            "file_name": self.file_name,
            "file_size": self.file_size,
            "watermark_status": self.watermark_status,
            "violation_count": len(self.violations),
            "scan_count": len(self.scan_logs),
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

    def __repr__(self):
        return f"<Asset {self.asset_id}>"
