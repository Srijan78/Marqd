"""
Marqd Database Models
"""
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

from app.models.asset import Asset
from app.models.violation import Violation
from app.models.scan_log import ScanLog

__all__ = ["db", "Asset", "Violation", "ScanLog"]
