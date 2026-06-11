import uuid
import datetime
import threading
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from sqlalchemy import func
from sqlalchemy.ext.asyncio import AsyncSession

from backend.database.postgres import get_db
from backend.database.models import FIR, Criminal, CrimeHotspot, CriminalFIR, Officer
from backend.database.neo4j import neo4j_service
from backend.auth.auth_bearer import JWTBearer
from backend.auth.auth_handler import get_current_officer

router = APIRouter(prefix="/api/reports", dependencies=[Depends(JWTBearer())])

# In-memory store for recently generated reports metadata
reports_lock = threading.Lock()
recent_reports: List[Dict[str, Any]] = []

# --- PYDANTIC SCHEMAS ---

class ReportSection(BaseModel):
    heading: str
    content: str
    data: Any

class IntelligenceReportResponse(BaseModel):
    id: uuid.UUID
    title: str
    report_type: str
    generated_at: str
    generated_by: str
    sections: List[ReportSection]

class ReportListItem(BaseModel):
    id: uuid.UUID
    title: str
    report_type: str
    generated_at: str
    generated_by: str

# --- ROUTES ---

@router.get("/generate/{report_type}", response_model=IntelligenceReportResponse)
async def generate_report(
    report_type: str,
    criminal_id: Optional[uuid.UUID] = Query(None, description="Required for 'criminal_profile' and 'network_analysis'"),
    district: Optional[str] = Query(None, description="Optional filter for 'crime_summary' and 'hotspot_report'"),
    db: AsyncSession = Depends(get_db),
    current_officer: Officer = Depends(get_current_officer)
):
    """
    Generate a dynamic structured intelligence report based on real database records.
    Supports: crime_summary, criminal_profile, network_analysis, hotspot_report
    """
    report_type = report_type.lower()
    report_id = uuid.uuid4()
    generated_time = datetime.datetime.utcnow().isoformat()
    
    title = ""
    sections = []

    if report_type == "criminal_profile":
        if not criminal_id:
            raise HTTPException(status_code=400, detail="criminal_id is required for a criminal_profile report.")
            
        # Fetch Criminal and relations from Postgres
        c_q = (
            select(Criminal)
            .options(
                selectinload(Criminal.vehicles),
                selectinload(Criminal.phone_numbers),
                selectinload(Criminal.known_locations)
            )
            .where(Criminal.id == criminal_id)
        )
        res = await db.execute(c_q)
        criminal = res.scalar_one_or_none()
        if not criminal:
            raise HTTPException(status_code=404, detail="Criminal profile not found")

        # Fetch case history
        fir_q = select(FIR).join(CriminalFIR).where(CriminalFIR.criminal_id == criminal_id)
        f_res = await db.execute(fir_q)
        firs = f_res.scalars().all()

        title = f"Criminal Suspect Intelligence Dossier: {criminal.name}"
        
        # Section 1: Demographics
        sections.append(ReportSection(
            heading="Demographic Profile",
            content=f"Suspect {criminal.name} is classified as {criminal.status.value}. National status: {criminal.nationality}.",
            data={
                "name": criminal.name,
                "aliases": criminal.aliases,
                "dob": criminal.dob.isoformat() if criminal.dob else None,
                "gender": criminal.gender,
                "status": criminal.status.value,
                "risk_score": criminal.risk_score
            }
        ))
        
        # Section 2: Vehicles & Phones
        sections.append(ReportSection(
            heading="Registered Assets & Communications",
            content=f"Discovered {len(criminal.vehicles)} vehicle links and {len(criminal.phone_numbers)} associated telephone numbers.",
            data={
                "vehicles": [
                    {"reg": v.registration_number, "make": v.make, "model": v.model} for v in criminal.vehicles
                ],
                "phone_numbers": [
                    {"number": p.number, "is_active": p.is_active} for p in criminal.phone_numbers
                ]
            }
        ))

        # Section 3: FIR cases
        sections.append(ReportSection(
            heading="Case History",
            content=f"Suspect has been formally linked to {len(firs)} First Information Reports (FIRs).",
            data=[
                {"fir_number": f.fir_number, "crime_type": f.crime_type.value, "district": f.district, "date_filed": f.date_filed.isoformat()}
                for f in firs
            ]
        ))

    elif report_type == "crime_summary":
        # Aggregate stats by crime type in Postgres
        query = select(FIR.crime_type, func.count(FIR.id)).group_by(FIR.crime_type)
        if district:
            query = query.where(FIR.district.ilike(f"%{district}%"))
        res = await db.execute(query)
        breakdown = {row[0].value: row[1] for row in res}

        # Latest cases
        latest_q = select(FIR).order_by(FIR.date_filed.desc()).limit(5)
        if district:
            latest_q = latest_q.where(FIR.district.ilike(f"%{district}%"))
        latest_res = await db.execute(latest_q)
        latest_firs = latest_res.scalars().all()

        loc_label = district if district else "National Jurisdiction"
        title = f"Executive Crime Summary Report: {loc_label}"

        sections.append(ReportSection(
            heading="Crime Type Distribution",
            content="Summary of crimes registered by category.",
            data=breakdown
        ))

        sections.append(ReportSection(
            heading="Recent Incident Chronology",
            content="Recent First Information Reports filed in the local district control room.",
            data=[
                {"fir_number": f.fir_number, "crime_type": f.crime_type.value, "date_filed": f.date_filed.isoformat(), "district": f.district}
                for f in latest_firs
            ]
        ))

    elif report_type == "network_analysis":
        if not criminal_id:
            raise HTTPException(status_code=400, detail="criminal_id is required for a network_analysis report.")
            
        c_q = select(Criminal).where(Criminal.id == criminal_id)
        res = await db.execute(c_q)
        criminal = res.scalar_one_or_none()
        if not criminal:
            raise HTTPException(status_code=404, detail="Criminal profile not found")

        # Query Neo4j ego network
        nodes = []
        edges = []
        try:
            net = await neo4j_service.get_criminal_network(str(criminal_id), depth=2)
            nodes = net.get("nodes", [])
            edges = net.get("edges", [])
        except Exception:
            pass

        title = f"Network Intelligence Analysis: {criminal.name}"

        sections.append(ReportSection(
            heading="Ego Network Metrics",
            content=f"Suspect is placed in a relationship graph containing {len(nodes)} connected entities and {len(edges)} linkages.",
            data={
                "suspect_id": str(criminal_id),
                "total_linked_entities": len(nodes),
                "total_relationships": len(edges),
                "criminal_associates_count": len([n for n in nodes if n.get("type") == "Criminal"]) - 1
            }
        ))

        sections.append(ReportSection(
            heading="Relationship Details (D3 Force Compatible)",
            content="Mapped linkages between nodes (criminals, cases, devices, locations).",
            data={
                "nodes": [{"id": n["id"], "label": n["label"], "type": n["type"]} for n in nodes],
                "edges": [{"source": e["source"], "target": e["target"], "type": e["type"]} for e in edges]
            }
        ))

    elif report_type == "hotspot_report":
        # Hotspot listing
        hs_q = select(CrimeHotspot).order_by(CrimeHotspot.risk_score.desc())
        if district:
            hs_q = hs_q.where(CrimeHotspot.district.ilike(f"%{district}%"))
        hs_res = await db.execute(hs_q)
        hotspots = hs_res.scalars().all()

        loc_label = district if district else "All Jurisdictions"
        title = f"Geospatial Crime Hotspots Report: {loc_label}"

        sections.append(ReportSection(
            heading="High-Risk Hotspot Coordinates",
            content=f"Discovered {len(hotspots)} active high-risk zone forecasts.",
            data=[
                {"district": h.district, "lat": h.lat, "lng": h.lng, "risk_score": h.risk_score, "crime_type": h.crime_type}
                for h in hotspots
            ]
        ))

    else:
        raise HTTPException(
            status_code=400,
            detail=f"Report type '{report_type}' not supported. Choose from: criminal_profile, crime_summary, network_analysis, hotspot_report."
        )

    # 4. Save report metadata to thread-safe in-memory cache
    report_data = {
        "id": report_id,
        "title": title,
        "report_type": report_type,
        "generated_at": generated_time,
        "generated_by": current_officer.name,
        "sections": [s.model_dump() for s in sections]
    }
    
    report_metadata = {
        "id": report_id,
        "title": title,
        "report_type": report_type,
        "generated_at": generated_time,
        "generated_by": current_officer.name
    }

    with reports_lock:
        recent_reports.insert(0, report_metadata)
        # Keep only the last 20 reports
        if len(recent_reports) > 20:
            recent_reports.pop()

    return IntelligenceReportResponse(**report_data)

@router.get("/list", response_model=List[ReportListItem])
async def list_recent_reports():
    """Retrieve the metadata registry of recently generated reports (last 20)"""
    with reports_lock:
        # Return a copy to avoid concurrency issues during list iteration
        return list(recent_reports)
