"""
Sentinel AI - Suspect Entity SQLAlchemy Model
=============================================
File: backend/models/suspect.py
Purpose: SQLAlchemy ORM entity representing suspects / persons of interest.
"""

from datetime import datetime
from sqlalchemy import Column, DateTime, String, Text
from backend.database.postgres import Base


class SuspectEntity(Base):
    """SQLAlchemy model for suspects table."""

    __tablename__ = "suspects"

    id = Column(String(50), primary_key=True, index=True)
    alias = Column(String(100), nullable=True)
    full_name = Column(String(150), nullable=False)
    threat_level = Column(String(50), default="MEDIUM", index=True)
    known_gang_affiliation = Column(String(100), nullable=True)
    primary_district = Column(String(100), nullable=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    notes = Column(Text, nullable=True)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "alias": self.alias,
            "full_name": self.full_name,
            "threat_level": self.threat_level,
            "known_gang_affiliation": self.known_gang_affiliation,
            "primary_district": self.primary_district,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "notes": self.notes,
        }
