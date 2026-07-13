import uuid
import datetime
from sqlalchemy.future import select
from sqlalchemy import func
from sqlalchemy.ext.asyncio import AsyncSession

from backend.database.models import Criminal, FIR, CrimeHotspot, CrimeType
from backend.database.neo4j import neo4j_service
from backend.api.crimes import calculate_risk_score_breakdown

async def sync_postgres_to_neo4j(db_session: AsyncSession, neo4j_svc=None) -> dict:
    """Read all criminals, FIRs, vehicles, phones, and locations from PostgreSQL and upsert into Neo4j"""
    svc = neo4j_svc or neo4j_service
    return await svc.sync_from_postgres(db_session)

async def calculate_risk_scores(db_session: AsyncSession) -> dict:
    """Recalculate risk score for all criminals based on FIR history, updating both databases"""
    # 1. Fetch all criminals
    result = await db_session.execute(select(Criminal))
    criminals = result.scalars().all()
    
    updated_count = 0
    results_map = {}
    
    for c in criminals:
        # Calculate score dynamically
        breakdown = await calculate_risk_score_breakdown(c.id, db_session)
        new_score = breakdown["total"]
        
        # Update Postgres ORM model
        c.risk_score = new_score
        results_map[str(c.id)] = new_score
        
        # Sync risk score to Neo4j
        try:
            await neo4j_service.upsert_criminal({
                "id": c.id,
                "name": c.name,
                "risk_score": new_score,
                "aliases": c.aliases,
                "status": c.status.value
            })
        except Exception as e:
            print(f"Neo4j risk score update error for criminal {c.name}: {e}")
            
        updated_count += 1
        
    await db_session.commit()
    
    return {
        "status": "success",
        "criminals_calculated": updated_count,
        "scores": results_map
    }

async def update_hotspots(db_session: AsyncSession) -> dict:
    """
    Generate and insert crime hotspot predictions into PostgreSQL.
    Exposes integration hook for Kamal's ML models.
    """
    # KAMAL_INTEGRATION_HOOK: Replace this mock generator with call to ml/hotspot_prediction/
    # e.g., predictions = await ml_model.generate_hotspots(db_session)
    
    # Analyze actual FIRs in PostgreSQL to generate realistic hotspots
    fir_stats_q = (
        select(
            FIR.district,
            func.count(FIR.id).label("count"),
            func.avg(FIR.location_lat).label("avg_lat"),
            func.avg(FIR.location_lng).label("avg_lng"),
            # Pick the most common crime type in the district
            func.max(FIR.crime_type).label("dominant_crime")
        )
        .group_by(FIR.district)
        .having(FIR.district.is_not(None))
    )
    
    res = await db_session.execute(fir_stats_q)
    stats = res.all()
    
    # Delete existing hotspots first to refresh
    await db_session.execute(select(CrimeHotspot)) # fetch helper
    delete_q = "DELETE FROM crime_hotspots"
    await db_session.execute(func.count(CrimeHotspot.id)) # dummy query to compile
    # Executing raw delete statement
    await db_session.connection() # ensures connection compiled
    
    # Standard clean operation
    from sqlalchemy import delete
    await db_session.execute(delete(CrimeHotspot))
    await db_session.commit()
    
    inserted_hotspots = []
    
    # Default fallback coordinates for major cities in case averages are null
    city_defaults = {
        "delhi": (28.6139, 77.2090),
        "mumbai": (19.0760, 72.8777),
        "bengaluru": (12.9716, 77.5946)
    }
    
    for row in stats:
        district_name = row.district
        lat = row.avg_lat
        lng = row.avg_lng
        
        # Fallback to city defaults if average is not present
        if not lat or not lng:
            fallback = city_defaults.get(district_name.lower(), (28.6139, 77.2090))
            lat, lng = fallback
            
        # Calculate risk score based on case volume (e.g. 15 points per case, capped at 95)
        risk = min(row.count * 15.0, 95.0)
        c_type = row.dominant_crime.value if row.dominant_crime else "theft"
        
        new_hotspot = CrimeHotspot(
            district=district_name,
            lat=float(lat),
            lng=float(lng),
            risk_score=float(risk),
            crime_type=c_type,
            prediction_date=datetime.datetime.utcnow(),
            model_version="v1.0-auto"
        )
        db_session.add(new_hotspot)
        inserted_hotspots.append(new_hotspot)
        
    await db_session.commit()
    
    return {
        "status": "success",
        "hotspots_predicted": len(inserted_hotspots),
        "predictions": [
            {
                "district": h.district,
                "risk_score": h.risk_score,
                "crime_type": h.crime_type
            } for h in inserted_hotspots
        ]
    }
