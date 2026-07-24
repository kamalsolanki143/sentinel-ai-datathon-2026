"""
Sentinel AI - Recommendation Engine REST API Endpoints
======================================================
File: backend/api/recommendations.py
Purpose: FastAPI router delivering enterprise REST API endpoints for Officer Deployment,
         Patrol Route Optimization, Resource Allocation, Risk Prioritization, Policy Rules,
         and Master Crime Response Strategy generation.

Dependencies: fastapi, pydantic, typing, loguru, backend.recommendation.*
"""

from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from loguru import logger
from pydantic import BaseModel, Field

from backend.recommendation.recommendation_service import RecommendationService

router = APIRouter(prefix="/recommendations", tags=["Recommendations & Decision Intelligence"])

# Global Service Singleton Instance
_service_instance: Optional[RecommendationService] = None


def get_recommendation_service() -> RecommendationService:
    """Dependency injection provider for RecommendationService."""
    global _service_instance
    if _service_instance is None:
        _service_instance = RecommendationService()
    return _service_instance


# --- Pydantic Request Models ---


class OfficerDeploymentRequest(BaseModel):
    """Payload for officer deployment recommendations."""

    district: str = Field(default="Central District", description="Target precinct/district name")
    officers: Optional[List[Dict[str, Any]]] = Field(default=None, description="Optional custom officer list")
    hotspots: Optional[List[Dict[str, Any]]] = Field(default=None, description="Optional custom hotspots list")


class PatrolRouteRequest(BaseModel):
    """Payload for patrol route optimization."""

    district: str = Field(default="Central District", description="Target district name")
    unit_ids: List[str] = Field(default=["PATROL-101", "PATROL-102"], description="Call-signs of available units")
    shift_hours: float = Field(default=8.0, description="Max shift duration limit")
    hotspots: Optional[List[Dict[str, Any]]] = Field(default=None, description="Optional target hotspots")


class ResourceAllocationRequest(BaseModel):
    """Payload for multi-resource allocation optimization."""

    resources: Optional[List[Dict[str, Any]]] = Field(default=None, description="Available resources list")
    targets: Optional[List[Dict[str, Any]]] = Field(default=None, description="Target incidents/zones list")
    emergency_override: bool = Field(default=False, description="Flag to bypass soft policy warnings")


class RiskPrioritizationRequest(BaseModel):
    """Payload for risk prioritization ranking."""

    district: str = Field(default="Central District", description="Target district name")
    hotspots: Optional[List[Dict[str, Any]]] = Field(default=None, description="Hotspot predictions")
    active_incidents: Optional[List[Dict[str, Any]]] = Field(default=None, description="Active CAD incidents")


class FullStrategyRequest(BaseModel):
    """Payload for master crime response strategy generation."""

    district: str = Field(default="Central District", description="Target district name")
    user_query: str = Field(default="", description="Command directive or specific query prompt")
    hotspots: Optional[List[Dict[str, Any]]] = Field(default=None, description="Hotspots list")
    incidents: Optional[List[Dict[str, Any]]] = Field(default=None, description="Incidents list")
    officers: Optional[List[Dict[str, Any]]] = Field(default=None, description="Officers list")


# --- API Endpoint Handlers ---


@router.get("/health", summary="Recommendation Subsystem Health Check")
async def recommendation_health_check() -> Dict[str, Any]:
    """Verify that Recommendation Engine APIs and solvers are operational."""
    return {
        "subsystem": "Sentinel AI Recommendation Engine",
        "status": "healthy",
        "timestamp": status.HTTP_200_OK,
        "features_active": [
            "Officer Deployment",
            "Patrol Route Optimization (TSP 2-Opt)",
            "Multi-Resource Allocation (Hungarian Algorithm)",
            "Risk Prioritization Matrix",
            "Policy Rules Engine",
            "Gemini AI Explainable Rationale",
        ],
    }


@router.post(
    "/officer-deployment",
    summary="Recommend Officer Deployment Assignments",
    response_description="Optimized officer-to-hotspot deployment matches with AI rationale",
)
async def recommend_officer_deployment(
    payload: OfficerDeploymentRequest,
    service: RecommendationService = Depends(get_recommendation_service),
) -> Dict[str, Any]:
    """
    Generate optimal officer deployment assignments to high-risk zones using multi-criteria scoring.
    """
    try:
        result = await service.get_officer_recommendations(
            district=payload.district,
            officers_override=payload.officers,
            hotspots_override=payload.hotspots,
        )
        return result
    except Exception as exc:
        logger.error(f"Error in recommend_officer_deployment: {exc}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate officer deployment recommendations: {str(exc)}",
        )


@router.post(
    "/patrol-routes",
    summary="Generate Optimized Patrol Routes",
    response_description="TSP-optimized waypoint route plans for patrol vehicle units",
)
async def recommend_patrol_routes(
    payload: PatrolRouteRequest,
    service: RecommendationService = Depends(get_recommendation_service),
) -> Dict[str, Any]:
    """
    Compute shortest travel-distance patrol route waypoints minimizing response times while covering high-risk sectors.
    """
    try:
        result = await service.get_patrol_route_recommendations(
            district=payload.district,
            unit_ids=payload.unit_ids,
            hotspots_override=payload.hotspots,
        )
        return result
    except Exception as exc:
        logger.error(f"Error in recommend_patrol_routes: {exc}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate patrol route recommendations: {str(exc)}",
        )


@router.post(
    "/resource-allocation",
    summary="Multi-Resource Allocation Optimization",
    response_description="Constrained optimization assignment for Officers, Vehicles, and Specialized Units",
)
async def allocate_resources(
    payload: ResourceAllocationRequest,
    service: RecommendationService = Depends(get_recommendation_service),
) -> Dict[str, Any]:
    """
    Perform linear sum assignment (Hungarian algorithm) to match multi-department resources to active CAD incidents.
    """
    try:
        result = await service.get_resource_allocation_recommendations(
            resources_override=payload.resources,
            targets_override=payload.targets,
        )
        return result
    except Exception as exc:
        logger.error(f"Error in allocate_resources: {exc}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to optimize resource allocation: {str(exc)}",
        )


@router.post(
    "/risk-prioritization",
    summary="Prioritize High Risk Zones & Incidents",
    response_description="Ranked matrix of hotspot sectors and active incidents by priority score",
)
async def prioritize_risk(
    payload: RiskPrioritizationRequest,
    service: RecommendationService = Depends(get_recommendation_service),
) -> Dict[str, Any]:
    """
    Rank geographic crime hotspots and active CAD incidents by urgency, severity, and temporal risk.
    """
    try:
        result = await service.get_risk_prioritization_recommendations(
            district=payload.district,
            hotspots_override=payload.hotspots,
            incidents_override=payload.active_incidents,
        )
        return result
    except Exception as exc:
        logger.error(f"Error in prioritize_risk: {exc}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to prioritize risk zones: {str(exc)}",
        )


@router.post(
    "/full-strategy",
    summary="Master Crime Response Strategy & AI Executive Plan",
    response_description="Comprehensive crime response package with Gemini AI Explainable Briefing",
)
async def generate_full_strategy(
    payload: FullStrategyRequest,
    service: RecommendationService = Depends(get_recommendation_service),
) -> Dict[str, Any]:
    """
    Synthesize complete decision intelligence package: Risk Ranking, Resource Allocation, Patrol Routes, and Gemini AI Rationale.
    """
    try:
        result = await service.get_full_strategy_recommendations(
            district=payload.district,
            user_query=payload.user_query,
        )
        return result
    except Exception as exc:
        logger.error(f"Error in generate_full_strategy: {exc}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate master strategy plan: {str(exc)}",
        )


@router.get(
    "/rules",
    summary="Get Active Policy Rules & Compliance Thresholds",
    response_description="List of registered enterprise business and legal policy rules",
)
async def get_active_policy_rules(
    service: RecommendationService = Depends(get_recommendation_service),
) -> List[Dict[str, Any]]:
    """Retrieve active police operational rules evaluated during recommendation calculations."""
    try:
        return service.get_active_rules()
    except Exception as exc:
        logger.error(f"Error in get_active_policy_rules: {exc}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch policy rules: {str(exc)}",
        )
