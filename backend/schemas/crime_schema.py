"""
Sentinel AI - Crime Schemas
=============================
File: backend/schemas/crime_schema.py
Purpose: Pydantic models representing crime entities, evidence,
         victims, suspects, and locations.

Dependencies: pydantic
"""

from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field


class LocationSchema(BaseModel):
    """Schema for a geographic location."""
    latitude: float = Field(..., ge=-90, le=90, description="Latitude coordinate")
    longitude: float = Field(..., ge=-180, le=180, description="Longitude coordinate")
    address: Optional[str] = Field(None, description="Street address")
    district: str = Field(..., description="City district or precinct")


class PersonSchema(BaseModel):
    """Base schema for people involved in a crime."""
    id: Optional[str] = None
    name: str
    age: Optional[int] = None
    gender: Optional[str] = None
    contact: Optional[str] = None


class VictimSchema(PersonSchema):
    """Schema for a crime victim."""
    statement_summary: Optional[str] = None
    injury_status: Optional[str] = None


class SuspectSchema(PersonSchema):
    """Schema for a crime suspect."""
    alias: Optional[str] = None
    physical_description: Optional[str] = None
    prior_records: bool = False
    gang_affiliation: Optional[str] = None


class EvidenceSchema(BaseModel):
    """Schema for crime scene evidence."""
    id: str
    type: str = Field(..., description="Type of evidence (e.g., weapon, dna, digital)")
    description: str
    collected_at: datetime
    collected_by: str


class CrimeSchema(BaseModel):
    """Comprehensive schema for a crime incident."""
    incident_id: str
    crime_type: str
    severity: str
    status: str
    occurred_at: datetime
    reported_at: datetime
    location: LocationSchema
    description: str
    victims: List[VictimSchema] = []
    suspects: List[SuspectSchema] = []
    evidence: List[EvidenceSchema] = []
    modus_operandi: Optional[str] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "incident_id": "INC-2026-001",
                "crime_type": "burglary",
                "severity": "major",
                "status": "open",
                "occurred_at": "2026-07-13T02:30:00Z",
                "reported_at": "2026-07-13T08:15:00Z",
                "location": {
                    "latitude": 34.0522,
                    "longitude": -118.2437,
                    "address": "123 Safe St",
                    "district": "Downtown"
                },
                "description": "Break-in at commercial property through rear window."
            }
        }
