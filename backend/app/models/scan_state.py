"""
ScanState Model — Persistent storage for global scanning status.

Stores scan state in the database so the "Stop Scan" button state
survives container restarts, reloads, and multi-thread environments.
"""
from datetime import datetime, timezone
from app.models import db


class ScanState(db.Model):
    __tablename__ = "scan_state"

    # Singleton row with id=1
    id = db.Column(db.Integer, primary_key=True)
    is_scanning = db.Column(db.Boolean, default=False, nullable=False)
    stop_requested = db.Column(db.Boolean, default=False, nullable=False)
    last_updated = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    @staticmethod
    def get():
        """Get or create the singleton scan state row."""
        state = ScanState.query.get(1)
        if not state:
            state = ScanState(id=1, is_scanning=False, stop_requested=False)
            db.session.add(state)
            db.session.commit()
        return state

    def to_dict(self):
        return {
            "is_scanning": self.is_scanning,
            "stop_requested": self.stop_requested,
            "last_updated": self.last_updated.isoformat() if self.last_updated else None,
        }
