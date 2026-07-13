import uuid
from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from backend.database.postgres import get_db
from backend.database.neo4j import neo4j_service
from backend.auth.auth_bearer import JWTBearer
from backend.auth.auth_handler import require_role
from backend.services.pipeline import sync_postgres_to_neo4j

# Create network router protected by JWTBearer
router = APIRouter(prefix="/api/network", dependencies=[Depends(JWTBearer())])

# --- HELPER ---

def parse_and_validate_uuids(comma_separated_ids: str) -> List[str]:
    """Parse comma-separated strings into a validated list of UUIDs"""
    id_list = [item.strip() for item in comma_separated_ids.split(",") if item.strip()]
    if not id_list:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="At least one criminal ID must be provided."
        )
    
    validated = []
    for cid in id_list:
        try:
            # Ensure it is a valid UUID
            val_uuid = uuid.UUID(cid)
            validated.append(str(val_uuid))
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid UUID string format: '{cid}'"
            )
    return validated

# --- ROUTES ---

@router.get("/criminal/{criminal_id}")
async def get_criminal_ego_network(
    criminal_id: uuid.UUID,
    depth: int = Query(2, ge=1, le=3)
):
    """Retrieve the ego graph network around a criminal suspect up to depth 3"""
    try:
        network = await neo4j_service.get_criminal_network(str(criminal_id), depth)
        return network
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Graph database query failed: {str(e)}"
        )

@router.get("/discover")
async def discover_hidden_network(
    criminal_ids: str = Query(..., description="Comma-separated criminal UUIDs"),
    depth: int = Query(2, ge=1, le=3)
):
    """Discover a hidden relationship network connecting multiple suspect profiles"""
    validated_ids = parse_and_validate_uuids(criminal_ids)
    try:
        network = await neo4j_service.discover_hidden_connections(validated_ids, depth)
        return network
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Network discovery query failed: {str(e)}"
        )

@router.get("/gangs")
async def get_gang_clusters():
    """Detect and return gang clusters based on network connectivity (shared indicators/knows)"""
    try:
        clusters = await neo4j_service.detect_gang_clusters()
        return clusters
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Community detection algorithm failed: {str(e)}"
        )

@router.get("/path")
async def get_shortest_connection_path(
    from_criminal_id: uuid.UUID = Query(...),
    to_criminal_id: uuid.UUID = Query(...)
):
    """Find the shortest connection path between two criminal suspects"""
    try:
        path = await neo4j_service.get_shortest_path(from_criminal_id, to_criminal_id)
        if not path.get("nodes"):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No connecting path found between these suspects."
            )
        return path
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Shortest path calculation failed: {str(e)}"
        )

@router.get("/shared-links")
async def get_shared_indicators(
    criminal_ids: str = Query(..., description="Comma-separated criminal UUIDs")
):
    """Find shared phone numbers, vehicles, and locations between suspects"""
    validated_ids = parse_and_validate_uuids(criminal_ids)
    try:
        shared = await neo4j_service.get_shared_links(validated_ids)
        return shared
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Shared link discovery failed: {str(e)}"
        )

@router.post("/sync", status_code=status.HTTP_200_OK)
async def sync_postgres_with_graph(
    db: AsyncSession = Depends(get_db),
    # Enforces admin role for this route
    _: Any = Depends(require_role("admin"))
):
    """Triggers database sync to push all Postgres entities and links to Neo4j. Protected Admin-only."""
    try:
        results = await sync_postgres_to_neo4j(db, neo4j_service)
        return {
            "status": "synchronized",
            "records_synced": results
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Sync pipeline operation failed: {str(e)}"
        )
