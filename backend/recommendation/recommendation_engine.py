"""
Sentinel AI - Master Recommendation Engine
===========================================
File: backend/recommendation/recommendation_engine.py
Purpose: Master decision intelligence orchestrator combining Scoring, Business Rules,
         Risk Prioritization, Patrol Optimization, Resource Allocation, and Gemini AI-powered
         Explainable AI output for high-level command decisions.

Dependencies: pydantic, typing, loguru, langchain_google_genai / google-genai, backend.recommendation.*
"""

import os
from datetime import datetime
from typing import Any, Dict, List, Optional
from loguru import logger
from pydantic import BaseModel, Field

from backend.config.settings import get_settings
from backend.recommendation.patrol_optimizer import PatrolOptimizer, PatrolRoutePlan
from backend.recommendation.resource_allocator import ResourceAllocationSummary, ResourceAllocator
from backend.recommendation.risk_prioritizer import PrioritizedIncident, PrioritizedZone, RiskPrioritizer
from backend.recommendation.rules_engine import PolicyRuleEngine
from backend.recommendation.scoring import MultiCriteriaWeights, ScoringEngine

settings = get_settings()


class StrategicResponsePlan(BaseModel):
    """Complete Executive Crime Response Strategy Package."""

    plan_id: str = Field(description="Unique strategy plan ID e.g. PLAN-2026-001")
    generated_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat())
    target_district: str = Field(description="Target precinct or jurisdiction sector")
    overall_threat_level: str = Field(description="CRITICAL, HIGH, MEDIUM, LOW")
    top_risk_zones: List[PrioritizedZone] = Field(default_factory=list)
    prioritized_incidents: List[PrioritizedIncident] = Field(default_factory=list)
    resource_allocations: Optional[ResourceAllocationSummary] = Field(default=None)
    patrol_routes: List[PatrolRoutePlan] = Field(default_factory=list)
    executive_ai_summary: str = Field(description="Gemini-generated explainable decision intelligence summary")
    actionable_recommendations: List[str] = Field(default_factory=list)
    policy_compliance_status: str = Field(default="COMPLIANT")


class MasterRecommendationEngine:
    """
    Master Recommendation Engine for Sentinel AI.

    Synthesizes mathematical optimization (MCDA Scoring, Hungarian Resource Allocation, TSP Patrol Routes)
    with Gemini AI generative intelligence to deliver actionable, explainable crime response recommendations.
    """

    def __init__(
        self,
        scoring_engine: Optional[ScoringEngine] = None,
        rules_engine: Optional[PolicyRuleEngine] = None,
        risk_prioritizer: Optional[RiskPrioritizer] = None,
        patrol_optimizer: Optional[PatrolOptimizer] = None,
        resource_allocator: Optional[ResourceAllocator] = None,
    ) -> None:
        """Initialize all Recommendation Engine components."""
        self.scoring = scoring_engine or ScoringEngine()
        self.rules = rules_engine or PolicyRuleEngine()
        self.prioritizer = risk_prioritizer or RiskPrioritizer(scoring_engine=self.scoring)
        self.patrol_optimizer = patrol_optimizer or PatrolOptimizer()
        self.resource_allocator = resource_allocator or ResourceAllocator(
            scoring_engine=self.scoring, rules_engine=self.rules
        )

        # Gemini LLM setup for Explainable AI
        self.api_key = settings.GEMINI_API_KEY or os.getenv("GOOGLE_API_KEY", "")
        self.model_name = settings.GEMINI_MODEL
        logger.info(f"MasterRecommendationEngine initialized with model {self.model_name}.")

    async def _generate_explainable_ai_reasoning(
        self,
        context_type: str,
        data_summary: Dict[str, Any],
        user_query: str = "",
    ) -> str:
        """
        Generate executive decision reasoning using Gemini API.

        Args:
            context_type: Type of recommendation (e.g. 'OFFICER_DEPLOYMENT', 'PATROL_ROUTE', 'CRIME_STRATEGY').
            data_summary: Structured data payload for LLM synthesis.
            user_query: Optional custom prompt query from commanding officer.

        Returns:
            Human-readable explainable rationale string.
        """
        if not self.api_key:
            logger.warning("Gemini API key not configured. Returning rule-based fallback rationale.")
            return self._build_fallback_explanation(context_type, data_summary)

        try:
            from langchain_google_genai import ChatGoogleGenerativeAI
            from langchain_core.messages import HumanMessage, SystemMessage

            llm = ChatGoogleGenerativeAI(
                model=self.model_name,
                google_api_key=self.api_key,
                temperature=settings.GEMINI_TEMPERATURE,
            )

            system_prompt = (
                "You are Sentinel AI's Chief Recommendation Officer & Decision Intelligence Specialist. "
                "Your objective is to provide police commanders with clear, concise, actionable, and explainable "
                "justifications for strategic resource deployment, risk mitigation, and patrol route decisions. "
                "Use professional military/police command language. Focus on risk scores, coverage, officer safety, and crime prevention."
            )

            user_prompt = f"""
Context: {context_type}
Command Request: {user_query or 'Generate tactical command recommendations based on operational data.'}
Data Summary:
{data_summary}

Please provide an Executive Briefing including:
1. Operational Risk Diagnosis
2. Tactical Deployment Justification
3. Expected Safety & Prevention Impact
            """

            response = await llm.ainvoke([
                SystemMessage(content=system_prompt),
                HumanMessage(content=user_prompt),
            ])

            return response.content.strip()

        except Exception as exc:
            logger.error(f"Gemini LLM invocation failed: {exc}. Using fallback explanation.")
            return self._build_fallback_explanation(context_type, data_summary)

    def _build_fallback_explanation(
        self, context_type: str, data_summary: Dict[str, Any]
    ) -> str:
        """Generate structured text explanation when LLM is unavailable."""
        return (
            f"=== Sentinel AI Decision Intelligence Briefing ({context_type}) ===\n"
            f"1. Operational Risk Diagnosis: Multi-criteria scoring identifies elevated risk factors "
            f"derived from recent crime hotspot spatial density and model confidence.\n"
            f"2. Tactical Deployment Justification: Resources have been optimally assigned using linear "
            f"sum optimization to minimize travel response time while adhering to mandatory duo dispatch and shift safety rules.\n"
            f"3. Expected Safety & Prevention Impact: Deployment maximizes high-risk coverage, ensuring "
            f"rapid emergency response capabilities across key precinct sectors."
        )

    async def recommend_officer_deployment(
        self,
        officers: List[Dict[str, Any]],
        hotspots: List[Dict[str, Any]],
        district: str = "Central District",
    ) -> Dict[str, Any]:
        """
        Generate Officer Deployment Recommendations.

        Args:
            officers: List of available officer profile dicts.
            hotspots: List of hotspot/incident target dicts.
            district: Target police district name.

        Returns:
            Dictionary with deployment assignments, risk ranking, and AI explanation.
        """
        logger.info(f"Generating officer deployment recommendations for {district}")

        # Prioritize zones
        prioritized_zones = self.prioritizer.prioritize_zones(hotspots, top_k=len(hotspots))

        # Convert zones to allocation targets
        targets = [
            {
                "id": z.zone_id,
                "target_type": "HOTSPOT_ZONE",
                "location_name": f"{z.district} ({z.predicted_crime_type})",
                "latitude": z.latitude,
                "longitude": z.longitude,
                "risk_score": z.risk_score,
                "confidence": z.hotspot_confidence,
                "crime_severity_score": 0.60 if z.priority_level == "HIGH" else 0.40,
            }
            for z in prioritized_zones
        ]

        # Solve allocation
        allocation = self.resource_allocator.allocate_resources(officers, targets)

        # AI Explainability
        explanation = await self._generate_explainable_ai_reasoning(
            context_type="OFFICER_DEPLOYMENT",
            data_summary={
                "district": district,
                "total_officers": len(officers),
                "total_zones": len(prioritized_zones),
                "assignments_made": allocation.total_resources_assigned,
                "average_match_score": allocation.average_match_score,
            },
        )

        return {
            "district": district,
            "total_available_officers": len(officers),
            "priority_zones_count": len(prioritized_zones),
            "allocation_summary": allocation.model_dump(),
            "ai_executive_summary": explanation,
        }

    async def recommend_patrol_routes(
        self,
        origin_station: Dict[str, Any],
        hotspots: List[Dict[str, Any]],
        available_units: List[str] = ["PATROL-101", "PATROL-102"],
    ) -> Dict[str, Any]:
        """
        Generate Optimized Patrol Routes for available patrol vehicle units.

        Args:
            origin_station: Dict with station coordinates and details.
            hotspots: List of high-risk patrol target dicts.
            available_units: Call-signs of patrol units.

        Returns:
            Dictionary containing optimized routes per unit and AI rationale.
        """
        logger.info(f"Generating patrol routes for {len(available_units)} units.")

        routes: List[PatrolRoutePlan] = []
        num_units = max(1, len(available_units))

        # Split hotspots among available units if multiple
        hotspot_chunks = [hotspots[i::num_units] for i in range(num_units)]

        for idx, unit_id in enumerate(available_units):
            unit_hotspots = hotspot_chunks[idx] if idx < len(hotspot_chunks) else []
            route = self.patrol_optimizer.optimize_patrol_route(
                origin_station=origin_station,
                hotspots=unit_hotspots,
                unit_id=unit_id,
            )
            routes.append(route)

        total_distance = sum(r.total_distance_km for r in routes)
        avg_coverage = (
            sum(r.coverage_score for r in routes) / len(routes) if routes else 0.0
        )

        explanation = await self._generate_explainable_ai_reasoning(
            context_type="PATROL_ROUTE_OPTIMIZATION",
            data_summary={
                "origin_station": origin_station.get("name", "Central Station"),
                "units_deployed": len(available_units),
                "total_distance_km": total_distance,
                "average_coverage_score": avg_coverage,
            },
        )

        return {
            "origin_station": origin_station.get("name", "Central Station"),
            "total_units_assigned": len(available_units),
            "total_route_distance_km": round(total_distance, 2),
            "average_hotspot_coverage_score": round(avg_coverage, 4),
            "routes": [r.model_dump() for r in routes],
            "ai_executive_summary": explanation,
        }

    async def generate_full_crime_response_strategy(
        self,
        district: str,
        origin_station: Dict[str, Any],
        hotspots: List[Dict[str, Any]],
        active_incidents: List[Dict[str, Any]],
        officers: List[Dict[str, Any]],
        user_query: str = "",
    ) -> StrategicResponsePlan:
        """
        Generate Master Comprehensive Crime Response Strategy Package.

        Args:
            district: Target precinct/district name.
            origin_station: Station details.
            hotspots: List of predicted hotspot dicts.
            active_incidents: List of active incoming incidents.
            officers: List of available officers/resources.
            user_query: Custom command directive prompt.

        Returns:
            StrategicResponsePlan object.
        """
        logger.info(f"Building Master Strategic Crime Response Plan for {district}")

        # 1. Prioritize Zones & Incidents
        top_zones = self.prioritizer.prioritize_zones(hotspots, top_k=5)
        top_incidents = self.prioritizer.prioritize_incidents(
            active_incidents, officer_locations=officers, top_k=5
        )

        # Determine Threat Level
        max_zone_risk = max([z.risk_score for z in top_zones], default=0.0)
        max_inc_score = max([i.composite_priority_score for i in top_incidents], default=0.0)
        max_threat = max(max_zone_risk, max_inc_score)

        if max_threat >= 0.80:
            threat_level = "CRITICAL"
        elif max_threat >= 0.65:
            threat_level = "HIGH"
        elif max_threat >= 0.45:
            threat_level = "MEDIUM"
        else:
            threat_level = "LOW"

        # 2. Resource Allocation
        targets = [
            {
                "id": inc.incident_id,
                "target_type": "INCIDENT",
                "location_name": inc.location_name,
                "latitude": inc.latitude,
                "longitude": inc.longitude,
                "risk_score": inc.composite_priority_score,
                "crime_severity_score": inc.crime_severity_score,
                "crime_type": inc.crime_type,
            }
            for inc in top_incidents
        ]
        alloc_summary = self.resource_allocator.allocate_resources(officers, targets)

        # 3. Patrol Route Optimization
        route_plan = self.patrol_optimizer.optimize_patrol_route(
            origin_station=origin_station,
            hotspots=[z.model_dump() for z in top_zones],
            unit_id=f"ALPHA-SQUAD-01",
        )

        # 4. Generate Explainable AI Executive Briefing
        ai_briefing = await self._generate_explainable_ai_reasoning(
            context_type="MASTER_CRIME_RESPONSE_STRATEGY",
            data_summary={
                "district": district,
                "threat_level": threat_level,
                "top_zone_risk": max_zone_risk,
                "active_incidents": len(top_incidents),
                "officers_assigned": alloc_summary.total_resources_assigned,
                "patrol_coverage": route_plan.coverage_score,
            },
            user_query=user_query,
        )

        # Actionable Bullet Points
        actions = [
            f"Deploy {alloc_summary.total_resources_assigned} officers immediately to top priority CAD incidents.",
            f"Execute Alpha Patrol Route covering {len(top_zones)} high-risk hotspot sectors in {district}.",
            f"Enforce mandatory duo dispatch protocols for CRITICAL severity incidents.",
            f"Maintain station ready-reserve status for secondary incident escalations.",
        ]

        return StrategicResponsePlan(
            plan_id=f"PLAN-{district.upper().replace(' ', '_')}-{int(datetime.utcnow().timestamp())}",
            target_district=district,
            overall_threat_level=threat_level,
            top_risk_zones=top_zones,
            prioritized_incidents=top_incidents,
            resource_allocations=alloc_summary,
            patrol_routes=[route_plan],
            executive_ai_summary=ai_briefing,
            actionable_recommendations=actions,
            policy_compliance_status="COMPLIANT",
        )
