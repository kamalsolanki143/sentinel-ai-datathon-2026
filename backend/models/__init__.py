"""Sentinel AI - Models Package."""

from backend.models.crime import CrimeIncident
from backend.models.location import LocationSector
from backend.models.report import IntelligenceReport
from backend.models.suspect import SuspectEntity
from backend.models.vehicle import PatrolVehicle

__all__ = [
    "CrimeIncident",
    "LocationSector",
    "IntelligenceReport",
    "SuspectEntity",
    "PatrolVehicle",
]
