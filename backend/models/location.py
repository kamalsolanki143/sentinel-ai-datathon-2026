"""
Sentinel AI - Location & Hotspot Sector SQLAlchemy Model
=========================================================
File: backend/models/location.py
Purpose: SQLAlchemy ORM entity representing police stations, precincts, and hotspot locations.
"""

from datetime import datetime
from sqlalchemy import Boolean, Column, DateTime, Float, Integer, String
from backend.database.postgres import Base


class LocationSector(Base):
    """SQLAlchemy model for location_sectors table."""

    __tablename__ = "location_sectors"

    id = Column(String(50), primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    district = Column(String(100), nullable=False, index=True)
    location_type = Column(String(50), default="HOTSPOT", index=True)  # HOTSPOT, STATION, PRECINCTURE
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    risk_score = Column(Float, default=0.5)
    historical_crime_density = Column(Float, default=0.5)
    is_active = Column(Boolean, default=True)

    def to_dict(self) -> dict:
        """Convert ORM model to dictionary."""
        return {
            "id": self.id,
            "name": self.name,
            "district": self.district,
            "location_type": self.location_type,
            "latitude": self.latitude,
            "longitude": self.longitude,
            "risk_score": self.risk_score,
            "historical_crime_density": self.historical_crime_density,
            "is_active": self.is_active,
        }
