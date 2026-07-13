"""
Sentinel AI - Risk Scoring Module
====================================
File: analytics/risk_score.py
Purpose: Multi-factor composite risk scoring for areas, suspects,
         and temporal periods with configurable weights.

Dependencies: pandas, numpy, asyncpg
"""

import logging, os
from typing import Any, Optional
import numpy as np

logger = logging.getLogger(__name__)
PG_URL = os.getenv("DATABASE_URL", "postgresql://sentinel:password@localhost:5432/sentinel_db")


class RiskScorer:
    """Multi-factor risk scoring engine."""

    AREA_WEIGHTS: dict[str, float] = {
        "crime_volume": 0.25,
        "crime_severity": 0.25,
        "trend_direction": 0.20,
        "clearance_rate": 0.15,
        "repeat_offender_presence": 0.15,
    }

    def __init__(self, pg_url: Optional[str] = None) -> None:
        self.pg_url = pg_url or PG_URL

    async def compute_area_risk_scores(self, days: int = 90) -> list[dict[str, Any]]:
        """Compute composite risk scores for all districts."""
        district_data = await self._fetch_district_metrics(days)
        if not district_data:
            return []

        all_counts = [d["crime_count"] for d in district_data]
        max_count = max(all_counts) if all_counts else 1

        scored = []
        for district in district_data:
            volume_score = district["crime_count"] / max(max_count, 1)
            severity_score = self._compute_severity_score(district.get("severity_dist", {}))
            trend_score = {"increasing": 0.9, "stable": 0.5, "decreasing": 0.2}.get(
                district.get("trend", "stable"), 0.5)
            clearance = district.get("clearance_rate", 50) / 100
            clearance_score = 1.0 - clearance
            repeat_score = min(1.0, district.get("repeat_offenders", 0) / 10)

            composite = (
                self.AREA_WEIGHTS["crime_volume"] * volume_score +
                self.AREA_WEIGHTS["crime_severity"] * severity_score +
                self.AREA_WEIGHTS["trend_direction"] * trend_score +
                self.AREA_WEIGHTS["clearance_rate"] * clearance_score +
                self.AREA_WEIGHTS["repeat_offender_presence"] * repeat_score
            )

            risk_level = "critical" if composite >= 0.8 else "high" if composite >= 0.6 else "medium" if composite >= 0.4 else "low"

            scored.append({
                "district": district["district"],
                "composite_risk": round(composite, 4),
                "risk_level": risk_level,
                "components": {
                    "volume": round(volume_score, 3), "severity": round(severity_score, 3),
                    "trend": round(trend_score, 3), "clearance": round(clearance_score, 3),
                    "repeat": round(repeat_score, 3),
                },
                "crime_count": district["crime_count"],
            })

        return sorted(scored, key=lambda x: x["composite_risk"], reverse=True)

    def compute_temporal_risk(self, hour: int, day_of_week: int) -> dict[str, Any]:
        """Compute time-based risk level."""
        hour_risk = 0.8 if 20 <= hour or hour <= 4 else 0.5 if 12 <= hour <= 16 else 0.3
        day_risk = 0.7 if day_of_week >= 5 else 0.4
        composite = 0.6 * hour_risk + 0.4 * day_risk
        return {
            "hour": hour, "day_of_week": day_of_week,
            "temporal_risk": round(composite, 3),
            "risk_level": "high" if composite >= 0.6 else "medium" if composite >= 0.4 else "low",
        }

    def _compute_severity_score(self, severity_dist: dict[str, int]) -> float:
        weights = {"critical": 1.0, "high": 0.75, "medium": 0.5, "low": 0.25}
        total = sum(severity_dist.values()) or 1
        weighted = sum(weights.get(s, 0.5) * c for s, c in severity_dist.items())
        return min(1.0, weighted / total)

    async def _fetch_district_metrics(self, days: int) -> list[dict[str, Any]]:
        try:
            import asyncpg
            conn = await asyncpg.connect(self.pg_url)
            try:
                rows = await conn.fetch(
                    """SELECT district, COUNT(*) as crime_count,
                              COUNT(CASE WHEN status IN ('solved','closed') THEN 1 END)::float /
                              NULLIF(COUNT(*), 0) * 100 as clearance_rate
                       FROM crimes WHERE occurred_at >= NOW() - $1::interval
                       GROUP BY district ORDER BY crime_count DESC""",
                    f"{days} days",
                )
                return [{"district": r["district"], "crime_count": int(r["crime_count"]),
                         "clearance_rate": round(float(r["clearance_rate"] or 0), 2),
                         "severity_dist": {}, "trend": "stable", "repeat_offenders": 0} for r in rows]
            finally:
                await conn.close()
        except Exception as exc:
            logger.warning("District metrics fetch failed: %s", str(exc))
            return []
