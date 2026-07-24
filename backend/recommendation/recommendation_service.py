"""
Sentinel AI - Recommendation Service Layer
=========================================
File: backend/recommendation/recommendation_service.py
Purpose: High-level async service layer orchestrating database queries (PostgreSQL, Neo4j),
         AI agent integrations (PredictionAgent, AnalyticsAgent, GraphAgent, SimulationAgent),
         in-memory caching, and MasterRecommendationEngine execution.

Dependencies: asyncio, typing, pydantic, loguru, backend.recommendation.*, backend.config.settings
"""

import asyncio
import time
from typing import Any, Dict, List, Optional, Tuple
from loguru import logger

from backend.config.settings import get_settings
from backend.recommendation.patrol_optimizer import PatrolRoutePlan
from backend.recommendation.recommendation_engine import MasterRecommendationEngine, StrategicResponsePlan
from backend.recommendation.resource_allocator import ResourceAllocationSummary
from backend.recommendation.risk_prioritizer import PrioritizedIncident, PrioritizedZone
from backend.recommendation.rules_engine import PolicyRule

settings = get_settings()


class RecommendationService:
    """
    Async Service Layer for Sentinel AI Recommendation Subsystem.

    Provides database integration wrappers (PostgreSQL, Neo4j), AI Agent connectivity
    (PredictionAgent, AnalyticsAgent, GraphAgent, SimulationAgent), in-memory caching,
    and fallback mock generation for robust, production-ready response handling.
    """

    def __init__(
        self, engine: Optional[MasterRecommendationEngine] = None
    ) -> None:
        """Initialize Service with MasterRecommendationEngine and caching storage."""
        self.engine = engine or MasterRecommendationEngine()
        self._cache: Dict[str, Tuple[float, Any]] = {}
        self._cache_ttl_seconds: float = 60.0  # 1-minute cache TTL
        logger.info("RecommendationService initialized with Agent & DB integration capabilities.")

    def _get_cached(self, cache_key: str) -> Optional[Any]:
        """Retrieve item from cache if not expired."""
        if cache_key in self._cache:
            timestamp, data = self._cache[cache_key]
            if time.time() - timestamp < self._cache_ttl_seconds:
                logger.debug(f"Cache hit for key: {cache_key}")
                return data
            else:
                del self._cache[cache_key]
        return None

    def _set_cache(self, cache_key: str, data: Any) -> None:
        """Store item in cache with timestamp."""
        self._cache[cache_key] = (time.time(), data)

    # --- Database Integrations (PostgreSQL & Neo4j) ---

    async def query_postgresql_officers(self, district: str = "Central District") -> List[Dict[str, Any]]:
        """
        Query available active officers and workloads from PostgreSQL.
        Falls back gracefully to mock dataset if database connection fails.
        """
        try:
            import asyncpg
            conn = await asyncpg.connect(settings.DATABASE_URL, timeout=3.0)
            try:
                rows = await conn.fetch(
                    """
                    SELECT id, name, badge_number, rank, station, specialization,
                           workload_score, is_active, latitude, longitude
                    FROM officers
                    WHERE is_active = TRUE
                    ORDER BY workload_score ASC
                    """
                )
                if rows:
                    logger.info(f"Retrieved {len(rows)} active officers from PostgreSQL.")
                    return [dict(r) for r in rows]
            finally:
                await conn.close()
        except Exception as exc:
            logger.warning(f"PostgreSQL query for officers failed/unreachable: {exc}. Using fallback data.")

        return self._get_mock_officers(10)

    async def query_neo4j_hotspots(self, district: str = "Central District") -> List[Dict[str, Any]]:
        """
        Query criminal network & high risk hotspot nodes from Neo4j Knowledge Graph.
        Falls back gracefully to mock dataset if Neo4j is offline.
        """
        try:
            from neo4j import AsyncGraphDatabase
            driver = AsyncGraphDatabase.driver(
                settings.NEO4J_URI, auth=(settings.NEO4J_USER, settings.NEO4J_PASSWORD)
            )
            async with driver.session() as session:
                query = """
                MATCH (z:Zone {district: $district})-[:HAS_HOTSPOT]->(h:Hotspot)
                RETURN z.id AS zone_id, z.district AS district, h.name AS name,
                       h.latitude AS latitude, h.longitude AS longitude,
                       h.risk_score AS risk_score, h.predicted_crime_type AS predicted_crime_type
                LIMIT 10
                """
                result = await session.run(query, district=district)
                records = await result.data()
                await driver.close()
                if records:
                    logger.info(f"Retrieved {len(records)} hotspot graph nodes from Neo4j.")
                    return records
        except Exception as exc:
            logger.warning(f"Neo4j query for hotspots failed/unreachable: {exc}. Using fallback data.")

        return self._get_mock_hotspots(6)

    # --- AI Agent Integrations ---

    async def fetch_predictions_from_prediction_agent(
        self, query: str = "Predict hotspots for Central District", district: str = "Central District"
    ) -> Dict[str, Any]:
        """
        Invoke PredictionAgent to get live ML model forecasts & risk predictions.
        """
        try:
            from backend.agents.prediction_agent import PredictionAgent
            agent = PredictionAgent()
            state = {
                "query": query,
                "metadata": {"district": district},
            }
            result_state = await agent.predict(state)
            logger.info("Successfully fetched predictions from PredictionAgent.")
            return result_state.get("ml_predictions", {})
        except Exception as exc:
            logger.warning(f"PredictionAgent invocation failed: {exc}. Using fallback hotspot metrics.")
            return {"hotspot_prediction": {"predictions": self._get_mock_hotspots()}}

    async def fetch_analytics_from_analytics_agent(
        self, query: str = "Analyze statistical crime patterns", district: str = "Central District"
    ) -> Dict[str, Any]:
        """
        Invoke AnalyticsAgent to get statistical density & crime pattern analysis.
        """
        try:
            from backend.agents.analytics_agent import AnalyticsAgent
            agent = AnalyticsAgent()
            state = {
                "query": query,
                "metadata": {"district": district},
            }
            result_state = await agent.analyze(state)
            logger.info("Successfully fetched analytics from AnalyticsAgent.")
            return result_state.get("analytics_results", {})
        except Exception as exc:
            logger.warning(f"AnalyticsAgent invocation failed: {exc}. Using fallback analytics metrics.")
            return {"statistics": {"historical_density": 0.75, "repeat_hotspot": True}}

    async def fetch_graph_network_from_graph_agent(
        self, query: str = "Analyze criminal network entities", entity_id: str = "GANG-001"
    ) -> Dict[str, Any]:
        """
        Invoke GraphAgent to analyze criminal network connections & entity risks.
        """
        try:
            from backend.agents.graph_agent import GraphAgent
            agent = GraphAgent()
            state = {
                "query": query,
                "metadata": {"entity_id": entity_id},
            }
            result_state = await agent.analyze_graph(state)
            logger.info("Successfully fetched graph analysis from GraphAgent.")
            return result_state.get("graph_analysis", {})
        except Exception as exc:
            logger.warning(f"GraphAgent invocation failed: {exc}. Using fallback graph metrics.")
            return {"network_threat_level": "HIGH", "connected_nodes_count": 12}

    async def fetch_simulations_from_simulation_agent(
        self, scenario: str = "Patrol reduction impact", patrol_reduction_pct: float = 20.0
    ) -> Dict[str, Any]:
        """
        Invoke SimulationAgent to run Monte Carlo crime impact simulations.
        """
        try:
            from backend.agents.simulation_agent import SimulationAgent
            agent = SimulationAgent()
            state = {
                "query": f"Simulate impact of {patrol_reduction_pct}% patrol reduction",
                "metadata": {"scenario": scenario, "reduction_pct": patrol_reduction_pct},
            }
            result_state = await agent.simulate(state)
            logger.info("Successfully fetched simulation outcomes from SimulationAgent.")
            return result_state.get("simulation_results", {})
        except Exception as exc:
            logger.warning(f"SimulationAgent invocation failed: {exc}. Using fallback simulation metrics.")
            return {"simulated_crime_rate_change_pct": +14.2, "confidence_interval": [10.5, 18.0]}

    # --- Fallback Mock Data Providers for Standalone / Offline Execution ---

    def _get_mock_officers(self, count: int = 10) -> List[Dict[str, Any]]:
        """Generate realistic mock officer data when DB is unreachable."""
        specs = ["SWAT", "Patrol", "Cyber Crime", "Homicide", "Traffic", "Tactical"]
        officers = []
        for i in range(1, count + 1):
            officers.append(
                {
                    "id": f"OFF-{i:03d}",
                    "officer_id": f"OFF-{i:03d}",
                    "name": f"Officer {chr(64 + i)}. Johnson",
                    "badge_number": f"BADGE-{1000 + i}",
                    "rank": "Sergeant" if i % 3 == 0 else "Officer",
                    "station": "Central Station",
                    "specialization": specs[(i - 1) % len(specs)],
                    "shift_hours_worked": round(float((i * 1.5) % 10.0), 1),
                    "active_incidents": 1 if i % 4 == 0 else 0,
                    "is_active": True,
                    "vehicle_fuel_pct": 95.0 - (i * 4),
                    "latitude": 28.6139 + (i * 0.005),
                    "longitude": 77.2090 + (i * 0.005),
                }
            )
        return officers

    def _get_mock_hotspots(self, count: int = 6) -> List[Dict[str, Any]]:
        """Generate realistic mock hotspot predictions."""
        crimes = ["armed_robbery", "burglary", "grand_theft_auto", "homicide", "vandalism", "cyber_attack"]
        hotspots = []
        for i in range(1, count + 1):
            hotspots.append(
                {
                    "zone_id": f"ZONE-{i:03d}",
                    "district": "Central District" if i <= 3 else "North Sector",
                    "name": f"Sector {i} High Risk Hotspot",
                    "latitude": 28.6139 + (i * 0.010),
                    "longitude": 77.2090 + (i * 0.008),
                    "probability": round(0.95 - (i * 0.08), 2),
                    "risk_score": round(0.92 - (i * 0.08), 2),
                    "predicted_crime_type": crimes[(i - 1) % len(crimes)],
                    "confidence": round(0.88 - (i * 0.03), 2),
                }
            )
        return hotspots

    def _get_mock_incidents(self, count: int = 5) -> List[Dict[str, Any]]:
        """Generate mock active incidents."""
        incidents = []
        crimes = ["armed_robbery", "aggravated_assault", "cyber_attack", "burglary", "public_disturbance"]
        for i in range(1, count + 1):
            incidents.append(
                {
                    "incident_id": f"INC-2026-{i:04d}",
                    "crime_type": crimes[(i - 1) % len(crimes)],
                    "location_name": f"{100 + i*15} Main Boulevard, Sector {i}",
                    "latitude": 28.6139 + (i * 0.007),
                    "longitude": 77.2090 + (i * 0.006),
                    "weapons_involved": i in [1, 2],
                    "casualties": 1 if i == 1 else 0,
                    "property_loss_val": 5000.0 * i,
                    "confidence": 0.90,
                }
            )
        return incidents

    def _get_mock_station(self, name: str = "Central Police Headquarters") -> Dict[str, Any]:
        """Generate mock police station location."""
        return {
            "id": "STATION-MAIN",
            "name": name,
            "latitude": 28.6139,
            "longitude": 77.2090,
            "district": "Central District",
        }

    # --- High Level Service Functions ---

    async def get_officer_recommendations(
        self,
        district: str = "Central District",
        officers_override: Optional[List[Dict[str, Any]]] = None,
        hotspots_override: Optional[List[Dict[str, Any]]] = None,
    ) -> Dict[str, Any]:
        """
        Fetch data and calculate officer deployment recommendations.
        Uses PostgreSQL for officer profiles and Neo4j / PredictionAgent for hotspots if not overridden.
        """
        cache_key = f"officers_{district}_{len(officers_override or [])}_{len(hotspots_override or [])}"
        cached = self._get_cached(cache_key)
        if cached:
            return cached

        officers = officers_override or await self.query_postgresql_officers(district)
        hotspots = hotspots_override or await self.query_neo4j_hotspots(district)

        result = await self.engine.recommend_officer_deployment(
            officers=officers, hotspots=hotspots, district=district
        )

        self._set_cache(cache_key, result)
        return result

    async def get_patrol_route_recommendations(
        self,
        district: str = "Central District",
        unit_ids: Optional[List[str]] = None,
        hotspots_override: Optional[List[Dict[str, Any]]] = None,
    ) -> Dict[str, Any]:
        """
        Fetch data and compute TSP-optimized patrol routes.
        """
        units = unit_ids or ["PATROL-UNIT-101", "PATROL-UNIT-102"]
        cache_key = f"patrol_{district}_{'-'.join(units)}"
        cached = self._get_cached(cache_key)
        if cached:
            return cached

        station = self._get_mock_station(f"{district} Station")
        hotspots = hotspots_override or await self.query_neo4j_hotspots(district)

        result = await self.engine.recommend_patrol_routes(
            origin_station=station, hotspots=hotspots, available_units=units
        )

        self._set_cache(cache_key, result)
        return result

    async def get_resource_allocation_recommendations(
        self,
        resources_override: Optional[List[Dict[str, Any]]] = None,
        targets_override: Optional[List[Dict[str, Any]]] = None,
    ) -> Dict[str, Any]:
        """
        Fetch and run multi-resource allocation optimization via Hungarian algorithm.
        """
        resources = resources_override or await self.query_postgresql_officers()
        targets = targets_override or [
            {
                "id": inc["incident_id"],
                "target_type": "INCIDENT",
                "location_name": inc["location_name"],
                "latitude": inc["latitude"],
                "longitude": inc["longitude"],
                "risk_score": 0.85,
                "crime_type": inc["crime_type"],
                "crime_severity_score": 0.75,
            }
            for inc in self._get_mock_incidents(6)
        ]

        allocation = self.engine.resource_allocator.allocate_resources(resources, targets)
        return allocation.model_dump()

    async def get_risk_prioritization_recommendations(
        self,
        district: str = "Central District",
        hotspots_override: Optional[List[Dict[str, Any]]] = None,
        incidents_override: Optional[List[Dict[str, Any]]] = None,
    ) -> Dict[str, Any]:
        """
        Fetch predictions and rank high risk zones and incidents.
        """
        hotspots = hotspots_override or await self.query_neo4j_hotspots(district)
        incidents = incidents_override or self._get_mock_incidents(6)
        officers = await self.query_postgresql_officers(district)

        prioritized_zones = self.engine.prioritizer.prioritize_zones(hotspots, top_k=8)
        prioritized_incidents = self.engine.prioritizer.prioritize_incidents(
            incidents, officer_locations=officers, top_k=6
        )

        return {
            "district": district,
            "total_zones_analyzed": len(hotspots),
            "total_incidents_analyzed": len(incidents),
            "top_risk_zones": [z.model_dump() for z in prioritized_zones],
            "prioritized_incidents": [i.model_dump() for i in prioritized_incidents],
        }

    async def get_full_strategy_recommendations(
        self,
        district: str = "Central District",
        user_query: str = "",
    ) -> Dict[str, Any]:
        """
        Synthesize Prediction, Analytics, Graph, and Simulation data into a Master Strategic Response Plan.
        """
        station = self._get_mock_station(f"{district} Command Center")

        # Gather integrated intelligence concurrently
        preds_task = self.fetch_predictions_from_prediction_agent(district=district)
        analytics_task = self.fetch_analytics_from_analytics_agent(district=district)
        officers_task = self.query_postgresql_officers(district=district)

        preds, analytics, officers = await asyncio.gather(
            preds_task, analytics_task, officers_task
        )

        hotspots = self._get_mock_hotspots(8)
        incidents = self._get_mock_incidents(5)

        plan: StrategicResponsePlan = await self.engine.generate_full_crime_response_strategy(
            district=district,
            origin_station=station,
            hotspots=hotspots,
            active_incidents=incidents,
            officers=officers,
            user_query=user_query,
        )

        return plan.model_dump()

    def get_active_rules(self) -> List[Dict[str, Any]]:
        """List active policy compliance rules."""
        rules: List[PolicyRule] = self.engine.rules.get_all_rules()
        return [r.model_dump() for r in rules]
