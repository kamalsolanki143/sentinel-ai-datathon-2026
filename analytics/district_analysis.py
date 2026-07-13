"""
Sentinel AI - District Analysis Module
========================================
File: analytics/district_analysis.py
Purpose: Per-district performance metrics, comparative analysis,
         resource utilization, and district ranking.

Dependencies: pandas, numpy, asyncpg
"""

import logging, os
from typing import Any, Optional
import numpy as np, pandas as pd

logger = logging.getLogger(__name__)
PG_URL = os.getenv("DATABASE_URL", "postgresql://sentinel:password@localhost:5432/sentinel_db")


class DistrictAnalyzer:
    """Per-district crime performance analysis engine."""

    def __init__(self, pg_url: Optional[str] = None) -> None:
        self.pg_url = pg_url or PG_URL

    async def analyze_districts(self, days: int = 90) -> dict[str, Any]:
        """Get comprehensive district-level analysis."""
        df = await self._fetch_district_data(days)
        if df.empty:
            return {"status": "no_data"}
        return {
            "district_metrics": self._compute_district_metrics(df),
            "rankings": self._rank_districts(df),
            "comparative": self._comparative_analysis(df),
            "resource_utilization": await self._resource_utilization(),
            "period_days": days,
        }

    def _compute_district_metrics(self, df: pd.DataFrame) -> list[dict[str, Any]]:
        if "district" not in df.columns:
            return []
        metrics = []
        for district, group in df.groupby("district"):
            m = {"district": str(district), "total_crimes": len(group)}
            if "severity" in group.columns:
                m["severity_distribution"] = group["severity"].value_counts().to_dict()
            if "crime_type" in group.columns:
                m["top_crime_types"] = group["crime_type"].value_counts().head(5).to_dict()
            if "status" in group.columns:
                solved = group["status"].isin(["solved", "closed", "resolved"]).sum()
                m["clearance_rate"] = round(solved / max(len(group), 1) * 100, 2)
            metrics.append(m)
        return sorted(metrics, key=lambda x: x["total_crimes"], reverse=True)

    def _rank_districts(self, df: pd.DataFrame) -> dict[str, list[dict[str, Any]]]:
        if "district" not in df.columns:
            return {}
        counts = df["district"].value_counts()
        by_crime_count = [{"rank": i + 1, "district": str(d), "crimes": int(c)} for i, (d, c) in enumerate(counts.items())]
        return {"by_crime_volume": by_crime_count}

    def _comparative_analysis(self, df: pd.DataFrame) -> dict[str, Any]:
        if "district" not in df.columns:
            return {}
        counts = df.groupby("district").size()
        return {
            "mean_crimes": round(float(counts.mean()), 2),
            "median_crimes": round(float(counts.median()), 2),
            "std_crimes": round(float(counts.std()), 2),
            "highest": str(counts.idxmax()), "lowest": str(counts.idxmin()),
            "disparity_ratio": round(float(counts.max() / max(counts.min(), 1)), 2),
        }

    async def _resource_utilization(self) -> list[dict[str, Any]]:
        try:
            import asyncpg
            conn = await asyncpg.connect(self.pg_url)
            try:
                rows = await conn.fetch(
                    """SELECT station, COUNT(*) as officer_count, AVG(workload_score) as avg_workload
                       FROM officers WHERE is_active = TRUE GROUP BY station""",
                )
                return [{"station": r["station"], "officers": int(r["officer_count"]),
                         "avg_workload": round(float(r["avg_workload"] or 0), 2)} for r in rows]
            finally:
                await conn.close()
        except Exception as exc:
            logger.warning("Resource utilization fetch failed: %s", str(exc))
            return []

    async def _fetch_district_data(self, days: int) -> pd.DataFrame:
        try:
            import asyncpg
            conn = await asyncpg.connect(self.pg_url)
            try:
                rows = await conn.fetch(
                    """SELECT district, crime_type, severity, status, occurred_at
                       FROM crimes WHERE occurred_at >= NOW() - $1::interval""",
                    f"{days} days",
                )
                return pd.DataFrame([dict(r) for r in rows]) if rows else pd.DataFrame()
            finally:
                await conn.close()
        except Exception as exc:
            logger.warning("District data fetch failed: %s", str(exc))
            return pd.DataFrame()
