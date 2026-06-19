import uuid
from datetime import datetime, date, timedelta
from typing import List, Optional
from pydantic import BaseModel, Field, ConfigDict
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy import func, text, literal_column
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from backend.database.postgres import get_db
from backend.database.models import (
    FIR, Criminal, CriminalFIR, Vehicle, PhoneNumber, KnownLocation, CrimeHotspot,
    CrimeType, FIRStatus, CriminalStatus
)
from backend.database.neo4j import neo4j_service
from backend.auth.auth_bearer import JWTBearer

# Create router protected by JWTBearer by default
router = APIRouter(prefix="/api/crimes", dependencies=[Depends(JWTBearer())])

# --- PYDANTIC SCHEMAS ---

class FIRCreate(BaseModel):
    fir_number: str = Field(..., description="Unique FIR code")
    date_filed: datetime = Field(..., description="Timestamp of when the FIR was filed")
    crime_type: CrimeType = Field(..., description="Type of crime committed")
    description: Optional[str] = None
    location_lat: Optional[float] = None
    location_lng: Optional[float] = None
    location_name: Optional[str] = None
    district: Optional[str] = None
    state: Optional[str] = None
    status: FIRStatus = FIRStatus.open
    officer_id: uuid.UUID

class FIRResponse(BaseModel):
    id: uuid.UUID
    fir_number: str
    date_filed: datetime
    crime_type: CrimeType
    description: Optional[str]
    location_lat: Optional[float]
    location_lng: Optional[float]
    location_name: Optional[str]
    district: Optional[str]
    state: Optional[str]
    status: FIRStatus
    officer_id: uuid.UUID
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class CriminalCreate(BaseModel):
    name: str
    aliases: List[str] = []
    dob: Optional[date] = None
    gender: Optional[str] = None
    nationality: str = "Indian"
    address: Optional[str] = None
    photo_url: Optional[str] = None
    risk_score: float = 0.0
    status: CriminalStatus = CriminalStatus.active

class CriminalUpdate(BaseModel):
    name: Optional[str] = None
    aliases: Optional[List[str]] = None
    dob: Optional[date] = None
    gender: Optional[str] = None
    nationality: Optional[str] = None
    address: Optional[str] = None
    photo_url: Optional[str] = None
    risk_score: Optional[float] = None
    status: Optional[CriminalStatus] = None

class CriminalResponse(BaseModel):
    id: uuid.UUID
    name: str
    aliases: List[str]
    dob: Optional[date]
    gender: Optional[str]
    nationality: str
    address: Optional[str]
    photo_url: Optional[str]
    risk_score: float
    status: CriminalStatus
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

class LinkCriminalFIRRequest(BaseModel):
    role_in_crime: str = Field("suspect", description="Role: accused, suspect, witness, etc.")

class AssociateInfo(BaseModel):
    id: str
    name: str
    relationship_type: str
    strength: float

class VehicleInfo(BaseModel):
    id: uuid.UUID
    registration_number: str
    make: Optional[str]
    model: Optional[str]
    color: Optional[str]
    
    model_config = ConfigDict(from_attributes=True)

class PhoneInfo(BaseModel):
    id: uuid.UUID
    number: str
    is_active: bool
    
    model_config = ConfigDict(from_attributes=True)

class LocationInfo(BaseModel):
    id: uuid.UUID
    location_name: str
    lat: float
    lng: float
    frequency_score: int
    
    model_config = ConfigDict(from_attributes=True)

class CriminalTwinResponse(BaseModel):
    basic_info: CriminalResponse
    fir_history: List[FIRResponse]
    known_associates: List[AssociateInfo]
    vehicles: List[VehicleInfo]
    phone_numbers: List[PhoneInfo]
    known_locations: List[LocationInfo]
    risk_score: float
    risk_score_breakdown: dict

class TrendResponse(BaseModel):
    month: str
    crime_type: str
    count: int

class HotspotResponse(BaseModel):
    id: uuid.UUID
    lat: float
    lng: float
    district: str
    risk_score: float
    crime_type: str

    model_config = ConfigDict(from_attributes=True)

# --- UTILITIES ---

async def calculate_risk_score_breakdown(criminal_id: uuid.UUID, db: AsyncSession) -> dict:
    """Calculate the suspect risk score dynamically based on record, recency, and network connections"""
    # 1. Fetch FIR links
    result = await db.execute(
        select(CriminalFIR)
        .options(selectinload(CriminalFIR.fir))
        .where(CriminalFIR.criminal_id == criminal_id)
    )
    links = result.scalars().all()
    
    fir_count = len(links)
    crime_types_involved = []
    
    base_score = 0.0
    recency_penalty = 0.0
    
    now = datetime.utcnow()
    thirty_days_ago = now - timedelta(days=30)
    
    severity_weights = {
        "murder": 10.0,
        "kidnapping": 9.0,
        "robbery": 8.0,
        "drug_trafficking": 7.0,
        "assault": 6.0,
        "vehicle_theft": 5.0,
        "fraud": 4.0,
        "cybercrime": 3.0,
        "theft": 2.0,
        "other": 1.0
    }
    
    for link in links:
        fir = link.fir
        c_type = fir.crime_type.value
        crime_types_involved.append(c_type)
        
        weight = severity_weights.get(c_type, 1.0)
        
        # Recency weight (last 30 days = 2x)
        if fir.date_filed >= thirty_days_ago:
            base_score += weight * 2.0
            recency_penalty += weight
        else:
            base_score += weight

    # 2. Get network centrality score from Neo4j (number of unique associates)
    network_score = 0.0
    try:
        network = await neo4j_service.get_criminal_network(str(criminal_id), depth=1)
        associates = [
            node for node in network.get("nodes", []) 
            if node.get("type") == "Criminal" and node.get("id") != str(criminal_id)
        ]
        associate_count = len(associates)
        # 2.5 points per unique associate, capped at 30 points
        network_score = min(associate_count * 2.5, 30.0)
    except Exception:
        network_score = 0.0
        
    # Combine scores and normalize to 0-100
    # Normalized base_score represents up to 70 points (e.g. capped at 7 medium cases)
    normalized_base = min(base_score * 3.5, 70.0) 
    total = round(normalized_base + network_score, 1)
    
    return {
        "fir_count": fir_count,
        "crime_types_involved": list(set(crime_types_involved)),
        "recency_penalty": float(recency_penalty),
        "network_centrality_score": float(network_score),
        "total": min(total, 100.0)
    }

# --- ROUTES ---

@router.get("/", response_model=List[FIRResponse])
async def list_firs(
    crime_type: Optional[CrimeType] = None,
    district: Optional[str] = None,
    status: Optional[FIRStatus] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db)
):
    """Retrieve list of FIRs with filters and pagination"""
    query = select(FIR)
    if crime_type:
        query = query.where(FIR.crime_type == crime_type)
    if district:
        query = query.where(FIR.district.ilike(f"%{district}%"))
    if status:
        query = query.where(FIR.status == status)
    if start_date:
        query = query.where(FIR.date_filed >= start_date)
    if end_date:
        query = query.where(FIR.date_filed <= end_date)
        
    query = query.order_by(FIR.date_filed.desc()).offset(offset).limit(limit)
    result = await db.execute(query)
    return result.scalars().all()

@router.post("/fir", response_model=FIRResponse, status_code=status.HTTP_201_CREATED)
async def create_fir(fir_in: FIRCreate, db: AsyncSession = Depends(get_db)):
    """Create a new FIR record in Postgres and sync to Neo4j"""
    db_fir = FIR(**fir_in.model_dump())
    db.add(db_fir)
    await db.commit()
    await db.refresh(db_fir)
    
    # Sync to Neo4j
    try:
        await neo4j_service.upsert_fir({
            "id": db_fir.id,
            "fir_number": db_fir.fir_number,
            "crime_type": db_fir.crime_type.value,
            "date_filed": db_fir.date_filed,
            "location_name": db_fir.location_name,
            "district": db_fir.district
        })
        if db_fir.location_name:
            import hashlib
            loc_id = str(uuid.UUID(bytes=hashlib.md5(db_fir.location_name.encode('utf-8')).digest()))
            await neo4j_service.create_relationship(
                from_id=loc_id,
                from_label="Location",
                to_id=loc_id,
                to_label="Location",
                rel_type="OCCURRED_AT" # Merges Location node properties
            )
            # Set Location details
            set_loc_query = """
            MERGE (l:Location {id: $id})
            SET l.name = $name,
                l.lat = $lat,
                l.lng = $lng,
                l.district = $district
            """
            async with neo4j_service.driver.session() as session:
                await session.run(
                    set_loc_query,
                    id=loc_id,
                    name=db_fir.location_name,
                    lat=float(db_fir.location_lat or 0.0),
                    lng=float(db_fir.location_lng or 0.0),
                    district=db_fir.district or ""
                )
            # Create link
            await neo4j_service.create_relationship(
                from_id=str(db_fir.id),
                from_label="FIR",
                to_id=loc_id,
                to_label="Location",
                rel_type="OCCURRED_AT"
            )
    except Exception as e:
        # Log Neo4j error but do not break Postgres HTTP response
        print(f"Neo4j sync error: {e}")
        
    return db_fir

@router.get("/fir/{fir_id}")
async def get_fir(fir_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    """Retrieve an FIR and its associated suspect profiles"""
    query = select(FIR).options(selectinload(FIR.officer)).where(FIR.id == fir_id)
    result = await db.execute(query)
    fir = result.scalar_one_or_none()
    if not fir:
        raise HTTPException(status_code=404, detail="FIR not found")
        
    # Fetch linked criminals
    c_query = (
        select(Criminal)
        .join(CriminalFIR)
        .where(CriminalFIR.fir_id == fir_id)
    )
    c_res = await db.execute(c_query)
    linked_criminals = c_res.scalars().all()
    
    return {
        "fir": FIRResponse.from_orm(fir),
        "criminals": [CriminalResponse.from_orm(c) for c in linked_criminals]
    }

@router.get("/criminal/{criminal_id}", response_model=CriminalTwinResponse)
async def get_criminal_digital_twin(criminal_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    """Compile the Digital Twin profile for a criminal incorporating relational details and graph links"""
    # 1. Fetch Criminal from Postgres
    query = (
        select(Criminal)
        .options(
            selectinload(Criminal.vehicles),
            selectinload(Criminal.phone_numbers),
            selectinload(Criminal.known_locations)
        )
        .where(Criminal.id == criminal_id)
    )
    result = await db.execute(query)
    criminal = result.scalar_one_or_none()
    if not criminal:
        raise HTTPException(status_code=404, detail="Suspect profile not found")

    # 2. Fetch FIR History
    fir_history_query = (
        select(FIR)
        .join(CriminalFIR)
        .where(CriminalFIR.criminal_id == criminal_id)
        .order_by(FIR.date_filed.desc())
    )
    f_res = await db.execute(fir_history_query)
    fir_history = f_res.scalars().all()

    # 3. Fetch Graph Associates from Neo4j (direct KNOWS links)
    known_associates = []
    try:
        network = await neo4j_service.get_criminal_network(str(criminal_id), depth=1)
        for node in network.get("nodes", []):
            if node.get("type") == "Criminal" and node.get("id") != str(criminal_id):
                # Find the relationship linking them
                rel_type = "KNOWS"
                strength = 1.0
                for edge in network.get("edges", []):
                    if (edge["source"] == str(criminal_id) and edge["target"] == node["id"]) or \
                       (edge["target"] == str(criminal_id) and edge["source"] == node["id"]):
                        rel_type = edge["type"]
                        weight = edge.get("properties", {}).get("strength") or edge.get("properties", {}).get("role") or 1.0
                        # Convert string roles to safe float strength if needed
                        strength = float(weight) if isinstance(weight, (int, float)) else 1.0
                
                known_associates.append(AssociateInfo(
                    id=node["id"],
                    name=node["properties"].get("name", "Unknown"),
                    relationship_type=rel_type,
                    strength=strength
                ))
    except Exception as e:
        print(f"Neo4j associate query error: {e}")

    # 4. Calculate dynamic risk score breakdown
    breakdown = await calculate_risk_score_breakdown(criminal_id, db)
    
    # Update score in database if it has drifted
    if abs(criminal.risk_score - breakdown["total"]) > 0.1:
        criminal.risk_score = breakdown["total"]
        await db.commit()

    return CriminalTwinResponse(
        basic_info=CriminalResponse.from_orm(criminal),
        fir_history=[FIRResponse.from_orm(f) for f in fir_history],
        known_associates=known_associates,
        vehicles=[VehicleInfo.from_orm(v) for v in criminal.vehicles],
        phone_numbers=[PhoneInfo.from_orm(p) for p in criminal.phone_numbers],
        known_locations=[LocationInfo.from_orm(loc) for loc in criminal.known_locations],
        risk_score=breakdown["total"],
        risk_score_breakdown=breakdown
    )

@router.get("/criminals", response_model=List[CriminalResponse])
async def list_criminals(
    name: Optional[str] = None,
    status: Optional[CriminalStatus] = None,
    min_risk_score: Optional[float] = None,
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db)
):
    """Retrieve list of criminals with search criteria and pagination"""
    query = select(Criminal)
    if name:
        query = query.where(Criminal.name.ilike(f"%{name}%"))
    if status:
        query = query.where(Criminal.status == status)
    if min_risk_score is not None:
        query = query.where(Criminal.risk_score >= min_risk_score)
        
    query = query.order_by(Criminal.risk_score.desc()).offset(offset).limit(limit)
    result = await db.execute(query)
    return result.scalars().all()

@router.post("/criminal", response_model=CriminalResponse, status_code=status.HTTP_201_CREATED)
async def create_criminal(criminal_in: CriminalCreate, db: AsyncSession = Depends(get_db)):
    """Create a new Criminal record in Postgres and sync to Neo4j"""
    db_criminal = Criminal(**criminal_in.model_dump())
    db.add(db_criminal)
    await db.commit()
    await db.refresh(db_criminal)
    
    # Sync to Neo4j
    try:
        await neo4j_service.upsert_criminal({
            "id": db_criminal.id,
            "name": db_criminal.name,
            "risk_score": db_criminal.risk_score,
            "aliases": db_criminal.aliases,
            "status": db_criminal.status.value
        })
    except Exception as e:
        print(f"Neo4j sync error: {e}")
        
    return db_criminal

@router.put("/criminal/{criminal_id}", response_model=CriminalResponse)
async def update_criminal(
    criminal_id: uuid.UUID, 
    criminal_in: CriminalUpdate, 
    db: AsyncSession = Depends(get_db)
):
    """Update details for an existing suspect profile"""
    query = select(Criminal).where(Criminal.id == criminal_id)
    result = await db.execute(query)
    db_criminal = result.scalar_one_or_none()
    if not db_criminal:
        raise HTTPException(status_code=404, detail="Suspect not found")
        
    update_data = criminal_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_criminal, field, value)
        
    await db.commit()
    await db.refresh(db_criminal)
    
    # Sync update to Neo4j
    try:
        await neo4j_service.upsert_criminal({
            "id": db_criminal.id,
            "name": db_criminal.name,
            "risk_score": db_criminal.risk_score,
            "aliases": db_criminal.aliases,
            "status": db_criminal.status.value
        })
    except Exception as e:
        print(f"Neo4j sync error: {e}")
        
    return db_criminal

@router.get("/trends", response_model=List[TrendResponse])
async def get_crime_trends(db: AsyncSession = Depends(get_db)):
    """Get aggregated crime counts by category and calendar month for the past 12 months"""
    one_year_ago = datetime.utcnow() - timedelta(days=365)
    
    # query selects: count(FIR.id) as count, FIR.crime_type, to_char(FIR.date_filed, 'YYYY-MM') as month
    query = (
        select(
            func.count(FIR.id).label("count"),
            FIR.crime_type,
            literal_column("to_char(date_filed, 'YYYY-MM')").label("month")
        )
        .where(FIR.date_filed >= one_year_ago)
        .group_by(FIR.crime_type, literal_column("to_char(date_filed, 'YYYY-MM')"))
        .order_by(text("month DESC"))
    )
    
    result = await db.execute(query)
    trends = []
    for row in result:
        trends.append(TrendResponse(
            month=row.month,
            crime_type=row.crime_type.value,
            count=row.count
        ))
    return trends

@router.get("/hotspots", response_model=List[HotspotResponse])
async def get_crime_hotspots(db: AsyncSession = Depends(get_db)):
    """Get predicted crime hotspots for GIS maps rendering"""
    result = await db.execute(select(CrimeHotspot).order_by(CrimeHotspot.risk_score.desc()))
    return result.scalars().all()

@router.post("/criminal/{criminal_id}/fir/{fir_id}", status_code=status.HTTP_200_OK)
async def link_criminal_to_fir(
    criminal_id: uuid.UUID,
    fir_id: uuid.UUID,
    link_req: LinkCriminalFIRRequest,
    db: AsyncSession = Depends(get_db)
):
    """Establish a case involvement mapping for a suspect (creates both Postgres and Neo4j relations)"""
    # Verify existence
    c_q = select(Criminal).where(Criminal.id == criminal_id)
    f_q = select(FIR).where(FIR.id == fir_id)
    
    c_res = await db.execute(c_q)
    f_res = await db.execute(f_q)
    
    if not c_res.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Criminal profile not found")
    if not f_res.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="FIR record not found")
        
    # Check if link exists
    link_q = select(CriminalFIR).where(
        CriminalFIR.criminal_id == criminal_id, 
        CriminalFIR.fir_id == fir_id
    )
    link_res = await db.execute(link_q)
    db_link = link_res.scalar_one_or_none()
    
    if db_link:
        db_link.role_in_crime = link_req.role_in_crime
    else:
        db_link = CriminalFIR(
            criminal_id=criminal_id,
            fir_id=fir_id,
            role_in_crime=link_req.role_in_crime
        )
        db.add(db_link)
        
    await db.commit()
    
    # Sync relationship to Neo4j
    try:
        await neo4j_service.create_relationship(
            from_id=str(criminal_id),
            from_label="Criminal",
            to_id=str(fir_id),
            to_label="FIR",
            rel_type="INVOLVED_IN",
            properties={"role": link_req.role_in_crime}
        )
        
        # Proactively trigger a direct KNOWS relationship recalculation for associates in this FIR
        knows_calc_q = """
        MATCH (c1:Criminal {id: $cid})-[:INVOLVED_IN]->(f:FIR {id: $fid})<-[:INVOLVED_IN]-(c2:Criminal)
        WHERE c1.id <> c2.id
        MERGE (c1)-[r:KNOWS]->(c2)
        SET r.strength = coalesce(r.strength, 0.0) + 0.9,
            r.last_seen = date(f.date_filed)
        """
        async with neo4j_service.driver.session() as session:
            await session.run(knows_calc_q, cid=str(criminal_id), fid=str(fir_id))
            
    except Exception as e:
        print(f"Neo4j sync error: {e}")
        
    # Recalculate risk score for this criminal following the new case association
    breakdown = await calculate_risk_score_breakdown(criminal_id, db)
    
    # Re-fetch and update ORM to record updated score
    c_res2 = await db.execute(select(Criminal).where(Criminal.id == criminal_id))
    db_crim = c_res2.scalar_one()
    db_crim.risk_score = breakdown["total"]
    await db.commit()
    
    return {
        "status": "linked",
        "criminal_id": criminal_id,
        "fir_id": fir_id,
        "role_in_crime": link_req.role_in_crime,
        "new_risk_score": breakdown["total"]
    }
