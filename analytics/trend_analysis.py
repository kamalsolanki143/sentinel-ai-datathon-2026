"""
Sentinel AI - Trend Analysis Module
=====================================
File: analytics/trend_analysis.py
Purpose: Temporal trend detection including moving averages, seasonal
         decomposition, and change-point detection for crime data.

Dependencies: pandas, numpy, asyncpg
"""

import logging, os
from typing import Any, Optional
import numpy as np, pandas as pd

logger = logging.getLogger(__name__)
PG_URL = os.getenv("DATABASE_URL", "postgresql://sentinel:password@localhost:5432/sentinel_db")


class TrendAnalyzer:
    """Temporal crime trend analysis engine."""

    def __init__(self, pg_url: Optional[str] = None) -> None:
        self.pg_url = pg_url or PG_URL

    async def analyze_trends(self, days: int = 180, freq: str = "W") -> dict[str, Any]:
        """Perform comprehensive trend analysis."""
        df = await self._fetch_time_series(days)
        if df.empty:
            return {"status": "no_data"}

        ts = df.set_index("date")["count"].resample(freq).sum().fillna(0)
        return {
            "overall_trend": self._detect_trend_direction(ts),
            "moving_averages": self._compute_moving_averages(ts),
            "change_points": self._detect_change_points(ts),
            "seasonal_pattern": self._detect_seasonality(ts),
            "by_crime_type": await self._trends_by_type(days, freq),
            "period_days": days,
            "frequency": freq,
        }

    def _detect_trend_direction(self, ts: pd.Series) -> dict[str, Any]:
        if len(ts) < 2:
            return {"direction": "insufficient_data", "slope": 0.0}
        x = np.arange(len(ts))
        slope, intercept = np.polyfit(x, ts.values, 1)
        direction = "increasing" if slope > 0.5 else "decreasing" if slope < -0.5 else "stable"
        return {"direction": direction, "slope": round(float(slope), 4), "intercept": round(float(intercept), 4)}

    def _compute_moving_averages(self, ts: pd.Series) -> dict[str, list[float]]:
        result = {}
        for window in [7, 14, 30]:
            if len(ts) >= window:
                ma = ts.rolling(window=min(window, len(ts))).mean().dropna()
                result[f"ma_{window}"] = [round(float(v), 2) for v in ma.tail(10).values]
        return result

    def _detect_change_points(self, ts: pd.Series) -> list[dict[str, Any]]:
        if len(ts) < 4:
            return []
        changes = []
        values = ts.values
        mean_val = np.mean(values)
        std_val = np.std(values)
        if std_val == 0:
            return []
        for i in range(1, len(values)):
            diff = abs(values[i] - values[i - 1])
            if diff > 2 * std_val:
                changes.append({
                    "index": i, "date": str(ts.index[i].date()),
                    "change": round(float(diff), 2),
                    "direction": "spike" if values[i] > values[i - 1] else "drop",
                })
        return changes[:10]

    def _detect_seasonality(self, ts: pd.Series) -> dict[str, Any]:
        if len(ts) < 4:
            return {"detected": False}
        if hasattr(ts.index, 'month'):
            monthly = ts.groupby(ts.index.month).mean()
            peak_month = int(monthly.idxmax())
            low_month = int(monthly.idxmin())
            return {"detected": True, "peak_month": peak_month, "low_month": low_month,
                    "monthly_avg": {int(k): round(float(v), 2) for k, v in monthly.items()}}
        return {"detected": False}

    async def _trends_by_type(self, days: int, freq: str) -> dict[str, str]:
        df = await self._fetch_time_series(days)
        if df.empty or "crime_type" not in df.columns:
            return {}
        result = {}
        for ctype in df["crime_type"].unique()[:10]:
            subset = df[df["crime_type"] == ctype]
            if len(subset) < 2:
                result[str(ctype)] = "insufficient_data"
                continue
            ts = subset.set_index("date")["count"].resample(freq).sum().fillna(0)
            trend = self._detect_trend_direction(ts)
            result[str(ctype)] = trend["direction"]
        return result

    async def _fetch_time_series(self, days: int) -> pd.DataFrame:
        try:
            import asyncpg
            conn = await asyncpg.connect(self.pg_url)
            try:
                rows = await conn.fetch(
                    """SELECT DATE(occurred_at) as date, crime_type, COUNT(*) as count
                       FROM crimes WHERE occurred_at >= NOW() - $1::interval
                       GROUP BY DATE(occurred_at), crime_type ORDER BY date""",
                    f"{days} days",
                )
                return pd.DataFrame([dict(r) for r in rows]) if rows else pd.DataFrame()
            finally:
                await conn.close()
        except Exception as exc:
            logger.warning("Trend data fetch failed: %s", str(exc))
            return pd.DataFrame()
