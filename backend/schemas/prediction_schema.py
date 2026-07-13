"""
Sentinel AI - Prediction & Recommendation Schemas
===================================================
File: backend/schemas/prediction_schema.py
Purpose: Pydantic models for ML predictions, risk scoring,
         and resource recommendations.

Dependencies: pydantic
"""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class RiskScoreResponse(BaseModel):
    """Schema for an area or entity risk score."""
    entity_id: str
    entity_type: str = Field(..., description="e.g., district, address, suspect")
    composite_risk: float = Field(..., ge=0, le=1)
    risk_level: str
    factors: Dict[str, float]
    trend: str


class PredictionRequest(BaseModel):
    """Request schema for crime forecasting."""
    district: Optional[str] = None
    crime_type: Optional[str] = None
    horizon_days: int = Field(7, ge=1, le=90)
    include_factors: bool = False


class ForecastPoint(BaseModel):
    """A single point in a time-series forecast."""
    date: str
    predicted_count: float
    confidence_interval_low: float
    confidence_interval_high: float


class PredictionResponse(BaseModel):
    """Response schema for crime forecasting."""
    district: Optional[str] = None
    crime_type: Optional[str] = None
    horizon_days: int
    total_predicted: float
    daily_average: float
    trend: str
    forecast: List[ForecastPoint]
    model_used: str


class OfficerAssignment(BaseModel):
    """Schema for an officer to area recommendation."""
    officer_id: str
    officer_name: str
    district: str
    composite_score: float
    match_reason: str


class RecommendationResponse(BaseModel):
    """Response schema for resource allocation recommendations."""
    assignments: List[OfficerAssignment]
    hotspot_patrols: List[Dict[str, Any]]
    generated_at: str
