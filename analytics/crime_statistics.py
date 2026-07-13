"""
Sentinel AI - Crime Statistics Module
=======================================
File: analytics/crime_statistics.py
Purpose: Descriptive statistics engine for crime data including counts,
         rates, distributions by type/time/location, and clearance rates.

Integration:
    - Called by backend/agents/analytics_agent.py for statistical analysis
    - Called by analytics/report_generator.py for report data
    - Reads from PostgreSQL crimes table via asyncpg

Dependencies: pandas, numpy, asyncpg
"""

import logging, os
from datetime import datetime
from typing import Any, Optional
import numpy as np, pandas as pd

logger = logging.getLogger(__name__)

PG_URL = os.getenv("DATABASE_URL", "postgresql://sentinel:password@localhost:5432/sentinel_db")


class CrimeStatistics:
    """Descriptive statistics engine for crime data analysis."""

    def __init__(self, pg_url: Optional[str] = None) -> None:
        self.pg_url = pg_url or PG_URL

    async def get_summary_statistics(self, days: int = 90) -> dict[str, Any]:
        """Get comprehensive crime summary statistics for the given period."""
        df = await self._fetch_crimes(days)
        if df.empty:
            return {"total_crimes": 0, "period_days": days}
        return {
            "total_crimes": len(df),
            "period_days": days,
            "daily_average": round(len(df) / max(days, 1), 2),
            "by_type": df["crime_type"].value_counts().to_dict(),
            "by_severity": df["severity"].value_counts().to_dict() if "severity" in df.columns else {},
            "by_district": df["district"].value_counts().to_dict() if "district" in df.columns else {},
            "by_status": df["status"].value_counts().to_dict() if "status" in df.columns else {},
            "clearance_rate": self._compute_clearance_rate(df),
            "peak_hours": self._compute_peak_hours(df),
            "peak_days": self._compute_peak_days(df),
            "severity_distribution": self._severity_distribution(df),
            "generated_at": datetime.utcnow().isoformat(),
        }

    async def get_comparative_statistics(self, current_days: int = 30, previous_days: int = 30) -> dict[str, Any]:
        """Compare current period against previous period."""
        current_df = await self._fetch_crimes(current_days)
        previous_df = await self._fetch_crimes(current_days + previous_days)
        if len(previous_df) > len(current_df):
            previous_df = previous_df.iloc[len(current_df):]

        current_count = len(current_df)
        previous_count = len(previous_df)
        pct_change = ((current_count - previous_count) / max(previous_count, 1)) * 100

        return {
            "current_period": {"days": current_days, "total": current_count},
            "previous_period": {"days": previous_days, "total": previous_count},
            "change": {"absolute": current_count - previous_count, "percentage": round(pct_change, 2)},
            "trend": "increasing" if pct_change > 5 else "decreasing" if pct_change < -5 else "stable",
        }

    def _compute_clearance_rate(self, df: pd.DataFrame) -> float:
        if "status" not in df.columns:
            return 0.0
        solved = df["status"].isin(["solved", "closed", "resolved"]).sum()
        return round(solved / max(len(df), 1) * 100, 2)

    def _compute_peak_hours(self, df: pd.DataFrame) -> dict[str, int]:
        if "occurred_at" not in df.columns:
            return {}
        hours = pd.to_datetime(df["occurred_at"]).dt.hour.value_counts().head(5)
        return {str(h): int(c) for h, c in hours.items()}

    def _compute_peak_days(self, df: pd.DataFrame) -> dict[str, int]:
        if "occurred_at" not in df.columns:
            return {}
        day_names = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        days = pd.to_datetime(df["occurred_at"]).dt.dayofweek.value_counts().head(5)
        return {day_names[d]: int(c) for d, c in days.items()}

    def _severity_distribution(self, df: pd.DataFrame) -> dict[str, float]:
        if "severity" not in df.columns:
            return {}
        dist = df["severity"].value_counts(normalize=True)
        return {str(k): round(float(v) * 100, 2) for k, v in dist.items()}

    async def _fetch_crimes(self, days: int) -> pd.DataFrame:
        try:
            import asyncpg
            conn = await asyncpg.connect(self.pg_url)
            try:
                rows = await conn.fetch(
                    "SELECT * FROM crimes WHERE occurred_at >= NOW() - $1::interval ORDER BY occurred_at DESC",
                    f"{days} days",
                )
                return pd.DataFrame([dict(r) for r in rows]) if rows else pd.DataFrame()
            finally:
                await conn.close()
        except Exception as exc:
            logger.warning("Crime statistics fetch failed: %s", str(exc))
            return pd.DataFrame()
