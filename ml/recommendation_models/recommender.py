"""
Sentinel AI - Officer Recommendation Engine
=============================================
File: ml/recommendation_models/recommender.py
Purpose: Officer-to-case assignment optimization and patrol route
         recommendation using scoring and constraint satisfaction.

Dependencies: numpy, pandas
"""

import logging
from typing import Any
import numpy as np
from ml.recommendation_models.scoring import ScoringEngine

logger = logging.getLogger(__name__)


class OfficerRecommender:
    """Officer assignment optimization engine."""

    def __init__(self, max_assignments_per_officer: int = 5) -> None:
        self.scoring_engine = ScoringEngine()
        self.max_assignments = max_assignments_per_officer

    def recommend_assignments(
        self, officers: list[dict[str, Any]], areas: list[dict[str, Any]],
        top_k: int = 20,
    ) -> list[dict[str, Any]]:
        """Generate optimal officer-to-area assignments."""
        logger.info("Generating assignments: %d officers, %d areas", len(officers), len(areas))

        all_scores = self.scoring_engine.batch_score(officers, areas)
        assignments = self._apply_constraints(all_scores)

        assignments = assignments[:top_k]
        for i, a in enumerate(assignments):
            a["rank"] = i + 1

        logger.info("Generated %d assignments", len(assignments))
        return assignments

    def recommend_patrol_routes(
        self, hotspots: list[dict[str, Any]], officer_count: int = 10,
    ) -> list[dict[str, Any]]:
        """Generate patrol route recommendations based on hotspot data."""
        logger.info("Generating patrol routes for %d hotspots", len(hotspots))

        sorted_spots = sorted(hotspots, key=lambda x: x.get("confidence", 0), reverse=True)
        routes = []

        for idx, spot in enumerate(sorted_spots[:officer_count]):
            routes.append({
                "route_id": idx + 1,
                "primary_area": spot.get("district", "Unknown"),
                "risk_level": spot.get("risk_level", "medium"),
                "priority": "high" if idx < officer_count // 3 else "medium",
                "recommended_patrol_frequency": "every_2_hours" if spot.get("risk_level") == "critical" else "every_4_hours",
                "confidence": spot.get("confidence", 0.5),
            })

        return routes

    def _apply_constraints(self, scored: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """Apply assignment constraints: max assignments per officer."""
        officer_counts: dict[str, int] = {}
        constrained = []

        for assignment in scored:
            oid = assignment.get("officer_id")
            count = officer_counts.get(oid, 0)
            if count < self.max_assignments:
                constrained.append(assignment)
                officer_counts[oid] = count + 1

        return constrained
