"""
Sentinel AI - Patrol Vehicle Fleet SQLAlchemy Model
===================================================
File: backend/models/vehicle.py
Purpose: SQLAlchemy ORM entity representing patrol vehicles and fleet units.
"""

from datetime import datetime
from sqlalchemy import Boolean, Column, DateTime, Float, String
from backend.database.postgres import Base


class PatrolVehicle(Base):
    """SQLAlchemy model for patrol_vehicles table."""

    __tablename__ = "patrol_vehicles"

    id = Column(String(50), primary_key=True, index=True)
    call_sign = Column(String(50), nullable=False, unique=True, index=True)
    unit_type = Column(String(50), default="PATROL_SQUAD", index=True)
    fuel_level_pct = Column(Float, default=100.0)
    is_available = Column(Boolean, default=True)
    assigned_station = Column(String(100), default="Central Station")
    current_latitude = Column(Float, nullable=True)
    current_longitude = Column(Float, nullable=True)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "call_sign": self.call_sign,
            "unit_type": self.unit_type,
            "fuel_level_pct": self.fuel_level_pct,
            "is_available": self.is_available,
            "assigned_station": self.assigned_station,
            "current_latitude": self.current_latitude,
            "current_longitude": self.current_longitude,
        }
