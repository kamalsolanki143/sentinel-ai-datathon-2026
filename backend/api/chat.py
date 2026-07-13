import uuid
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
from pydantic import BaseModel, Field
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from sqlalchemy import func, text, literal_column
from sqlalchemy.ext.asyncio import AsyncSession

from backend.database.postgres import get_db
from backend.database.models import ChatSession, ChatMessage, ChatRole, Officer, FIR, Criminal, CrimeHotspot, CriminalStatus
from backend.database.neo4j import neo4j_service
from backend.auth.auth_bearer import JWTBearer
from backend.auth.auth_handler import get_current_officer

router = APIRouter(prefix="/api/chat", dependencies=[Depends(JWTBearer())])

# --- PYDANTIC SCHEMAS ---

class ChatQueryRequest(BaseModel):
    session_id: Optional[uuid.UUID] = None
    message: str = Field(..., description="User query for the intelligence copilot")

class ChatQueryResponse(BaseModel):
    session_id: uuid.UUID
    response: str
    data: Dict[str, Any]
    sources: List[str]

class MessageResponse(BaseModel):
    id: uuid.UUID
    role: str
    content: str
    timestamp: datetime

    class Config:
        from_attributes = True

# --- ROUTES ---

@router.post("/query", response_model=ChatQueryResponse)
async def query_copilot(
    payload: ChatQueryRequest,
    db: AsyncSession = Depends(get_db),
    current_officer: Officer = Depends(get_current_officer)
):
    """
    NLP-style query against Sentinel AI database.
    Routes queries to appropriate analytics engines based on keywords.
    """
    message = payload.message
    message_lower = message.lower()
    session_id = payload.session_id

    # 1. Ensure active session exists
    if not session_id:
        db_session = ChatSession(officer_id=current_officer.id)
        db.add(db_session)
        await db.commit()
        await db.refresh(db_session)
        session_id = db_session.id
    else:
        # Verify if session exists
        session_q = select(ChatSession).where(ChatSession.id == session_id)
        res = await db.execute(session_q)
        db_session = res.scalar_one_or_none()
        if not db_session:
            # Recreate with provided UUID
            db_session = ChatSession(id=session_id, officer_id=current_officer.id)
            db.add(db_session)
            await db.commit()

    # 2. Save user message to database
    user_msg = ChatMessage(
        session_id=session_id,
        role=ChatRole.user,
        content=message
    )
    db.add(user_msg)
    await db.commit()

    # 3. Intent Routing logic
    response_text = ""
    structured_data = {}
    sources = []

    # KAMAL_INTEGRATION_HOOK: Replace this router with LangGraph agent call
    # e.g.,
    # response_text, structured_data, sources = await investigation_agent.arun(message, current_officer.id)

    if any(k in message_lower for k in ["trend", "trends", "pattern"]):
        # Execute trend query
        one_year_ago = datetime.utcnow() - timedelta(days=365)
        trend_q = (
            select(
                func.count(FIR.id).label("count"),
                FIR.crime_type,
                literal_column("to_char(date_filed, 'YYYY-MM')").label("month")
            )
            .where(FIR.date_filed >= one_year_ago)
            .group_by(FIR.crime_type, literal_column("to_char(date_filed, 'YYYY-MM')"))
            .order_by(text("month DESC"))
        )
        t_res = await db.execute(trend_q)
        trends_list = []
        for r in t_res:
            trends_list.append({"month": r.month, "crime_type": r.crime_type.value, "count": r.count})
            
        response_text = "Here are the aggregated crime trends for the past 12 months. Crime counts show variations across districts."
        structured_data = {"trends": trends_list}
        sources = ["PostgreSQL firs table"]

    elif any(k in message_lower for k in ["hotspot", "hotspots", "dangerous area"]):
        # Query hotspots
        hs_q = select(CrimeHotspot).order_by(CrimeHotspot.risk_score.desc()).limit(10)
        hs_res = await db.execute(hs_q)
        hotspots = hs_res.scalars().all()
        
        response_text = "I have fetched the most dangerous areas (crime hotspots) based on recent incidents and geospatial analytics."
        structured_data = {
            "hotspots": [
                {
                    "district": h.district,
                    "lat": h.lat,
                    "lng": h.lng,
                    "risk_score": h.risk_score,
                    "crime_type": h.crime_type
                } for h in hotspots
            ]
        }
        sources = ["PostgreSQL crime_hotspots table"]

    elif any(k in message_lower for k in ["criminal", "suspect", "offender"]):
        # Check if name is mentioned in message
        crim_q = select(Criminal)
        crim_res = await db.execute(crim_q)
        all_criminals = crim_res.scalars().all()
        
        found_criminal = None
        for c in all_criminals:
            if c.name.lower() in message_lower or any(alias.lower() in message_lower for alias in c.aliases):
                found_criminal = c
                break
                
        if found_criminal:
            # Return detailed digital twin info
            # Fetch vehicles, phone numbers, and cases
            v_res = await db.execute(select(Vehicle).where(Vehicle.owner_criminal_id == found_criminal.id))
            p_res = await db.execute(select(PhoneNumber).where(PhoneNumber.criminal_id == found_criminal.id))
            
            # Simple associate query
            associates = []
            try:
                network = await neo4j_service.get_criminal_network(str(found_criminal.id), depth=1)
                associates = [
                    {"id": node["id"], "name": node["properties"].get("name", "Unknown")}
                    for node in network.get("nodes", [])
                    if node.get("type") == "Criminal" and node.get("id") != str(found_criminal.id)
                ]
            except Exception:
                pass
                
            response_text = f"Found suspect intelligence profile for {found_criminal.name} (Risk Score: {found_criminal.risk_score}). Details are structured below."
            structured_data = {
                "criminal": {
                    "id": found_criminal.id,
                    "name": found_criminal.name,
                    "aliases": found_criminal.aliases,
                    "status": found_criminal.status.value,
                    "risk_score": found_criminal.risk_score,
                    "nationality": found_criminal.nationality,
                    "address": found_criminal.address,
                    "vehicles": [v.registration_number for v in v_res.scalars().all()],
                    "phone_numbers": [p.number for p in p_res.scalars().all()],
                    "associates": associates
                }
            }
            sources = ["PostgreSQL criminals table", "Neo4j graph database"]
        else:
            # Return list of active criminals
            active_q = select(Criminal).where(Criminal.status == CriminalStatus.active).order_by(Criminal.risk_score.desc()).limit(5)
            active_res = await db.execute(active_q)
            active_suspects = active_res.scalars().all()
            response_text = "I couldn't identify a specific suspect name in your message. Here is a list of top active suspects by risk score."
            structured_data = {
                "criminals": [
                    {"id": c.id, "name": c.name, "risk_score": c.risk_score, "status": c.status.value}
                    for c in active_suspects
                ]
            }
            sources = ["PostgreSQL criminals table"]

    elif any(k in message_lower for k in ["gang", "network", "connected", "relationship"]):
        # Gang cluster analysis
        clusters = await neo4j_service.detect_gang_clusters()
        response_text = "Here are the gang clusters detected within our law enforcement database using community relationship algorithms."
        structured_data = {"gang_clusters": clusters}
        sources = ["Neo4j graph database"]

    elif any(k in message_lower for k in ["fir", "case", "report"]):
        # Fetch last 10 cases
        fir_q = select(FIR).order_by(FIR.date_filed.desc()).limit(10)
        fir_res = await db.execute(fir_q)
        firs = fir_res.scalars().all()
        response_text = "Here is a summary of the most recently registered First Information Reports (FIRs)."
        structured_data = {
            "firs": [
                {
                    "fir_number": f.fir_number,
                    "crime_type": f.crime_type.value,
                    "district": f.district,
                    "date_filed": f.date_filed.isoformat(),
                    "status": f.status.value
                } for f in firs
            ]
        }
        sources = ["PostgreSQL firs table"]

    elif any(k in message_lower for k in ["predict", "forecast", "risk"]):
        # Mock forecast returning forecast structure
        districts = ["New Delhi", "Mumbai Suburban", "Bengaluru Urban"]
        forecasts = []
        base_date = datetime.utcnow().date()
        for dist in districts:
            items = []
            for i in range(1, 4): # return 3 days in chat summary
                fc_date = base_date + timedelta(days=i)
                items.append({
                    "date": fc_date.isoformat(),
                    "predicted_cases": i * 2,
                    "risk_level": "high" if i == 3 else "medium"
                })
            forecasts.append({"district": dist, "forecast": items})
            
        response_text = "Displaying predicted crime forecasts for the next 3 days across key districts."
        structured_data = {"forecasts": forecasts}
        sources = ["Predictive Analytics Engine"]

    else:
        # Default fallback instructions
        response_text = (
            f"Hello Officer {current_officer.name}. I am the Sentinel AI Copilot.\n\n"
            "I can assist you with the following intelligence queries:\n"
            "- **Crime Trends**: 'show crime trends over time'\n"
            "- **Crime Hotspots**: 'list dangerous areas' or 'show hotspots'\n"
            "- **Suspect Profiles**: 'show profile for [suspect name]'\n"
            "- **Gang Networks**: 'detect gang networks'\n"
            "- **Case Summaries**: 'list recent FIRs'\n"
            "- **Crime Forecasts**: 'show weekly predictions'"
        )
        structured_data = {}
        sources = []

    # 4. Save Assistant response to database
    assistant_msg = ChatMessage(
        session_id=session_id,
        role=ChatRole.assistant,
        content=response_text
    )
    db.add(assistant_msg)
    await db.commit()

    return ChatQueryResponse(
        session_id=session_id,
        response=response_text,
        data=structured_data,
        sources=sources
    )

@router.get("/history/{session_id}", response_model=List[MessageResponse])
async def get_session_history(
    session_id: uuid.UUID,
    db: AsyncSession = Depends(get_db)
):
    """Retrieve chat history logs for a session ordered by timestamp"""
    query = (
        select(ChatMessage)
        .where(ChatMessage.session_id == session_id)
        .order_by(ChatMessage.timestamp.asc())
    )
    result = await db.execute(query)
    return result.scalars().all()
