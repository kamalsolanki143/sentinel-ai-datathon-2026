"""
Sentinel AI - Crime Incident SQLAlchemy Model
=============================================
File: backend/models/crime.py
Purpose: SQLAlchemy ORM entity representing crime incidents in PostgreSQL.
"""

from datetime import datetime
from sqlalchemy import Boolean, Column, DateTime, Float, Integer, String, Text
from backend.database.postgres import Base


class CrimeIncident(Base):
    """SQLAlchemy model for crime_incidents table."""

    __tablename__ = "crime_incidents"

    id = Column(String(50), primary_key=True, index=True)
    crime_type = Column(String(100), nullable=False, index=True)
    district = Column(String(100), nullable=False, index=True)
    location_name = Column(String(255), nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    reported_at = Column(DateTime, default=datetime.utcnow, index=True)
    severity_score = Column(Float, default=0.5)
    weapons_involved = Column(Boolean, default=False)
    casualties = Column(Integer, default=0)
    property_loss_val = Column(Float, default=0.0)
    status = Column(String(50), default="OPEN", index=True)
    description = Column(Text, nullable=True)

    def to_dict(self) -> dict:
        """Convert ORM object to dictionary payload."""
        return {
            "id": self.id,
            "crime_type": self.crime_type,
            "district": self.district,
            "location_name": self.location_name,
            "latitude": self.latitude,
            "longitude": self.longitude,
            "reported_at": self.reported_at.isoformat() if self.reported_at else None,
            "severity_score": self.severity_score,
            "weapons_involved": self.weapons_involved,
            "casualties": self.casualties,
            "property_loss_val": self.property_loss_val,
            "status": self.status,
            "description": self.description,
        }
