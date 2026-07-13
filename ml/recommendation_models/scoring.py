"""
Sentinel AI - Recommendation Scoring Engine
=============================================
File: ml/recommendation_models/scoring.py
Purpose: Multi-criteria scoring engine for officer-to-area assignment
         optimization with configurable weights.

Dependencies: numpy
"""

import logging
from typing import Any
import numpy as np

logger = logging.getLogger(__name__)


class ScoringEngine:
    """Multi-criteria weighted scoring engine for resource allocation."""

    DEFAULT_WEIGHTS: dict[str, float] = {
        "risk": 0.30,
        "proximity": 0.20,
        "workload": 0.20,
        "expertise": 0.20,
        "history": 0.10,
    }

    def __init__(self, weights: dict[str, float] | None = None) -> None:
        self.weights = weights or self.DEFAULT_WEIGHTS.copy()
        total = sum(self.weights.values())
        if abs(total - 1.0) > 0.01:
            logger.warning("Weights sum to %.2f, normalizing to 1.0", total)
            self.weights = {k: v / total for k, v in self.weights.items()}

    def score(self, officer: dict[str, Any], area: dict[str, Any]) -> dict[str, Any]:
        """Compute composite score for an officer-area pair."""
        risk = self._score_risk(area)
        proximity = self._score_proximity(officer, area)
        workload = self._score_workload(officer)
        expertise = self._score_expertise(officer, area)
        history = self._score_history(officer)

        composite = (
            self.weights["risk"] * risk +
            self.weights["proximity"] * proximity +
            self.weights["workload"] * workload +
            self.weights["expertise"] * expertise +
            self.weights["history"] * history
        )

        return {
            "composite_score": round(composite, 4),
            "risk_score": round(risk, 4),
            "proximity_score": round(proximity, 4),
            "workload_score": round(workload, 4),
            "expertise_score": round(expertise, 4),
            "history_score": round(history, 4),
        }

    def batch_score(
        self, officers: list[dict[str, Any]], areas: list[dict[str, Any]],
    ) -> list[dict[str, Any]]:
        """Score all officer-area combinations and return ranked results."""
        results = []
        for officer in officers:
            for area in areas:
                scores = self.score(officer, area)
                results.append({
                    "officer_id": officer.get("id"),
                    "officer_name": officer.get("name", "Unknown"),
                    "area_id": area.get("district", "Unknown"),
                    **scores,
                })
        results.sort(key=lambda x: x["composite_score"], reverse=True)
        return results

    def _score_risk(self, area: dict[str, Any]) -> float:
        level = area.get("risk_level", "medium")
        return {"critical": 1.0, "high": 0.8, "medium": 0.5, "low": 0.2}.get(level, 0.5)

    def _score_proximity(self, officer: dict[str, Any], area: dict[str, Any]) -> float:
        return 0.9 if officer.get("station") == area.get("district") else 0.4

    def _score_workload(self, officer: dict[str, Any]) -> float:
        return max(0.0, 1.0 - officer.get("workload_score", 0.5))

    def _score_expertise(self, officer: dict[str, Any], area: dict[str, Any]) -> float:
        spec = officer.get("specialization", "")
        crime_types = area.get("primary_crime_types", [])
        if spec and any(spec.lower() in ct.lower() for ct in crime_types):
            return 1.0
        return 0.5 if spec else 0.3

    def _score_history(self, officer: dict[str, Any]) -> float:
        return min(1.0, officer.get("performance_score", 0.7))
