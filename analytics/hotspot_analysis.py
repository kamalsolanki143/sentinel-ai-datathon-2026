"""
Sentinel AI - Hotspot Analysis Module
=======================================
File: analytics/hotspot_analysis.py
Purpose: Spatial crime concentration analysis with grid-based density
         mapping, DBSCAN clustering, and geographic hotspot identification.

Dependencies: pandas, numpy, scikit-learn, asyncpg
"""

import logging, os
from typing import Any, Optional
import numpy as np, pandas as pd
from sklearn.cluster import DBSCAN

logger = logging.getLogger(__name__)
PG_URL = os.getenv("DATABASE_URL", "postgresql://sentinel:password@localhost:5432/sentinel_db")


class HotspotAnalyzer:
    """Spatial crime hotspot analysis engine."""

    def __init__(self, pg_url: Optional[str] = None) -> None:
        self.pg_url = pg_url or PG_URL

    async def analyze_hotspots(self, days: int = 90, eps: float = 0.01, min_samples: int = 5) -> dict[str, Any]:
        """Perform spatial hotspot analysis using DBSCAN clustering."""
        df = await self._fetch_spatial_data(days)
        if df.empty:
            return {"status": "no_data", "hotspots": []}

        clusters = self._cluster_crimes(df, eps, min_samples)
        density_map = self._compute_density_grid(df)
        district_hotspots = self._district_level_hotspots(df)

        return {
            "total_crimes": len(df),
            "clusters": clusters,
            "total_clusters": len(clusters),
            "density_grid": density_map,
            "district_hotspots": district_hotspots,
            "period_days": days,
            "parameters": {"eps": eps, "min_samples": min_samples},
        }

    def _cluster_crimes(self, df: pd.DataFrame, eps: float, min_samples: int) -> list[dict[str, Any]]:
        if "latitude" not in df.columns or "longitude" not in df.columns:
            return []
        coords = df[["latitude", "longitude"]].dropna().values
        if len(coords) < min_samples:
            return []

        db = DBSCAN(eps=eps, min_samples=min_samples, metric="haversine", algorithm="ball_tree")
        labels = db.fit_predict(np.radians(coords))

        clusters = []
        for label in set(labels):
            if label == -1:
                continue
            mask = labels == label
            cluster_points = coords[mask]
            clusters.append({
                "cluster_id": int(label),
                "center_lat": round(float(np.mean(cluster_points[:, 0])), 6),
                "center_lon": round(float(np.mean(cluster_points[:, 1])), 6),
                "crime_count": int(mask.sum()),
                "radius_km": round(float(np.max(np.std(cluster_points, axis=0)) * 111), 2),
                "density": round(float(mask.sum() / max(len(coords), 1)) * 100, 2),
            })

        return sorted(clusters, key=lambda x: x["crime_count"], reverse=True)

    def _compute_density_grid(self, df: pd.DataFrame, grid_size: float = 0.01) -> list[dict[str, Any]]:
        if "latitude" not in df.columns or "longitude" not in df.columns:
            return []
        df = df.copy()
        df["gx"] = (df["latitude"] / grid_size).astype(int)
        df["gy"] = (df["longitude"] / grid_size).astype(int)
        grid = df.groupby(["gx", "gy"]).size().reset_index(name="count")
        grid = grid.sort_values("count", ascending=False).head(20)
        return [
            {"grid_x": int(r["gx"]), "grid_y": int(r["gy"]), "crime_count": int(r["count"]),
             "lat": round(float(r["gx"] * grid_size), 4), "lon": round(float(r["gy"] * grid_size), 4)}
            for _, r in grid.iterrows()
        ]

    def _district_level_hotspots(self, df: pd.DataFrame) -> list[dict[str, Any]]:
        if "district" not in df.columns:
            return []
        dist = df["district"].value_counts()
        mean_c, std_c = dist.mean(), dist.std()
        result = []
        for district, count in dist.items():
            z_score = (count - mean_c) / max(std_c, 1)
            result.append({
                "district": str(district), "crime_count": int(count),
                "z_score": round(float(z_score), 2),
                "is_hotspot": z_score > 1.0,
                "intensity": "high" if z_score > 2 else "medium" if z_score > 1 else "low",
            })
        return sorted(result, key=lambda x: x["crime_count"], reverse=True)

    async def _fetch_spatial_data(self, days: int) -> pd.DataFrame:
        try:
            import asyncpg
            conn = await asyncpg.connect(self.pg_url)
            try:
                rows = await conn.fetch(
                    """SELECT latitude, longitude, crime_type, district, severity
                       FROM crimes WHERE occurred_at >= NOW() - $1::interval
                       AND latitude IS NOT NULL AND longitude IS NOT NULL""",
                    f"{days} days",
                )
                return pd.DataFrame([dict(r) for r in rows]) if rows else pd.DataFrame()
            finally:
                await conn.close()
        except Exception as exc:
            logger.warning("Spatial data fetch failed: %s", str(exc))
            return pd.DataFrame()
