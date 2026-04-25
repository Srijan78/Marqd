"""
ScanLog Model — Records each scan cycle's metadata and API usage.
"""
import uuid
from datetime import datetime, timezone
from app.models import db


class ScanLog(db.Model):
    __tablename__ = "scan_logs"

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    asset_id = db.Column(db.String(36), db.ForeignKey("assets.id"), nullable=False)
    channel = db.Column(db.String(20), nullable=False)       # serpapi | youtube
    results_count = db.Column(db.Integer, default=0)         # Number of URLs found
    violations_found = db.Column(db.Integer, default=0)      # Confirmed violations from this scan
    api_units_used = db.Column(db.Integer, default=0)        # API credits consumed
    scan_duration_ms = db.Column(db.Integer, nullable=True)  # How long the scan took
    status = db.Column(db.String(20), default="completed")   # running|completed|failed
    error_message = db.Column(db.Text, nullable=True)
    scanned_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    def to_dict(self):
        return {
            "id": self.id,
            "asset_id": self.asset_id,
            "channel": self.channel,
            "results_count": self.results_count,
            "violations_found": self.violations_found,
            "api_units_used": self.api_units_used,
            "scan_duration_ms": self.scan_duration_ms,
            "status": self.status,
            "error_message": self.error_message,
            "scanned_at": self.scanned_at.isoformat() if self.scanned_at else None,
        }

    def __repr__(self):
        return f"<ScanLog {self.channel} @ {self.scanned_at}>"
