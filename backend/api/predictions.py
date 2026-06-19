import uuid
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
from pydantic import BaseModel, Field
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession


from backend.database.postgres import get_db
from backend.database.models import CrimeHotspot, FIR, CrimeType
from backend.auth.auth_bearer import JWTBearer
from backend.api.crimes import calculate_risk_score_breakdown

router = APIRouter(prefix="/api/predictions", dependencies=[Depends(JWTBearer())])

# --- PYDANTIC SCHEMAS ---

class HotspotResponse(BaseModel):
    id: uuid.UUID
    district: str
    lat: float
    lng: float
    risk_score: float
    crime_type: str
    prediction_date: datetime
    model_version: str

    class Config:
        from_attributes = True

class RiskScoreResponse(BaseModel):
    criminal_id: uuid.UUID
    risk_score: float
    breakdown: dict

class ForecastItem(BaseModel):
    date: str
    predicted_cases: int
    risk_level: str # "low", "medium", "high"
    primary_crime_type: str

class DistrictForecast(BaseModel):
    district: str
    forecast: List[ForecastItem]

class AnomalyResponse(BaseModel):
    district: str
    crime_type: str
    last_7_days_count: int
    thirty_day_weekly_average: float
    increase_percentage: float

# --- ROUTES ---

@router.get("/hotspots", response_model=List[HotspotResponse])
async def get_hotspots(
    district: Optional[str] = None,
    crime_type: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    """Retrieve predicted crime hotspots with optional district and crime type filters"""
    query = select(CrimeHotspot)
    if district:
        query = query.where(CrimeHotspot.district.ilike(f"%{district}%"))
    if crime_type:
        query = query.where(CrimeHotspot.crime_type == crime_type)
        
    query = query.order_by(CrimeHotspot.risk_score.desc())
    result = await db.execute(query)
    return result.scalars().all()

@router.get("/risk-score/{criminal_id}", response_model=RiskScoreResponse)
async def get_criminal_risk_score(
    criminal_id: uuid.UUID,
    db: AsyncSession = Depends(get_db)
):
    """Calculate and return a detailed dynamic risk score breakdown for a suspect"""
    breakdown = await calculate_risk_score_breakdown(criminal_id, db)
    return RiskScoreResponse(
        criminal_id=criminal_id,
        risk_score=breakdown["total"],
        breakdown=breakdown
    )

@router.get("/forecast", response_model=List[DistrictForecast])
async def get_weekly_forecast(
    district: Optional[str] = Query(None, description="Filter forecast by district name")
):
    """
    Get a 7-day crime risk forecast per district.
    Exposes integration hook for prediction ML agent.
    """
    # KAMAL_INTEGRATION_HOOK: Replace this mock implementation with prediction_agent call
    # e.g., predictions = await prediction_agent.predict_weekly_forecast(district)
    
    districts = [district] if district else ["New Delhi", "Mumbai Suburban", "Bengaluru Urban"]
    
    forecasts = []
    base_date = datetime.utcnow().date()
    
    for dist in districts:
        items = []
        for i in range(1, 8):
            fc_date = base_date + timedelta(days=i)
            # Cycle risk levels and counts deterministically for demonstration
            val = (i + len(dist)) % 3
            if val == 0:
                risk = "low"
                cases = i % 3 + 1
            elif val == 1:
                risk = "medium"
                cases = i % 3 + 3
            else:
                risk = "high"
                cases = i % 3 + 6
                
            items.append(ForecastItem(
                date=fc_date.isoformat(),
                predicted_cases=cases,
                risk_level=risk,
                primary_crime_type="robbery" if val == 2 else ("theft" if val == 1 else "cybercrime")
            ))
            
        forecasts.append(DistrictForecast(
            district=dist,
            forecast=items
        ))
        
    return forecasts

@router.get("/anomalies", response_model=List[AnomalyResponse])
async def get_crime_anomalies(db: AsyncSession = Depends(get_db)):
    """
    Identify districts/crime types where active cases in the last 7 days
    exceed the 30-day rolling average (weekly normalized baseline).
    """
    now = datetime.utcnow()
    thirty_days_ago = now - timedelta(days=30)
    seven_days_ago = now - timedelta(days=7)
    
    # Retrieve all FIRs filed in the past 30 days
    result = await db.execute(
        select(FIR.district, FIR.crime_type, FIR.date_filed)
        .where(FIR.date_filed >= thirty_days_ago)
    )
    rows = result.all()
    
    # Compute counts in memory
    stats = {} # Key: (district, crime_type) -> {'last_7': int, 'last_30': int}
    
    for dist, c_type, date_filed in rows:
        if not dist:
            continue
        key = (dist, c_type.value)
        if key not in stats:
            stats[key] = {"last_7": 0, "last_30": 0}
            
        stats[key]["last_30"] += 1
        if date_filed >= seven_days_ago:
            stats[key]["last_7"] += 1
            
    anomalies = []
    for (dist, c_type), counts in stats.items():
        last_7 = counts["last_7"]
        last_30 = counts["last_30"]
        
        # Calculate 30-day baseline normalized to 7 days
        # baseline = (total cases in 30 days / 30) * 7
        weekly_baseline = (last_30 / 30.0) * 7.0
        
        # An anomaly is flagged if the last 7 days exceed this baseline
        # Require last_7 > 1 to avoid alerting on single-event noise
        if last_7 > weekly_baseline and last_7 > 1:
            increase_pct = 100.0
            if weekly_baseline > 0:
                increase_pct = ((last_7 - weekly_baseline) / weekly_baseline) * 100
                
            anomalies.append(AnomalyResponse(
                district=dist,
                crime_type=c_type,
                last_7_days_count=last_7,
                thirty_day_weekly_average=round(weekly_baseline, 2),
                increase_percentage=round(increase_pct, 1)
            ))
            
    # Sort anomalies by highest increase percentage
    anomalies.sort(key=lambda x: x.increase_percentage, reverse=True)
    return anomalies
