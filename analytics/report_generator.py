"""
Sentinel AI - Report Generator Module
========================================
File: analytics/report_generator.py
Purpose: Automated report generation for daily, weekly, and monthly crime
         reports with template-based generation, data injection, and
         chart embedding support.

Dependencies: pandas, asyncpg
"""

import logging, os, json
from datetime import datetime
from typing import Any, Optional
import pandas as pd

from analytics.crime_statistics import CrimeStatistics
from analytics.trend_analysis import TrendAnalyzer
from analytics.hotspot_analysis import HotspotAnalyzer
from analytics.district_analysis import DistrictAnalyzer
from analytics.risk_score import RiskScorer

logger = logging.getLogger(__name__)
PG_URL = os.getenv("DATABASE_URL", "postgresql://sentinel:password@localhost:5432/sentinel_db")


class ReportGenerator:
    """Automated crime intelligence report generator."""

    REPORT_TYPES = ["daily", "weekly", "monthly", "custom"]

    def __init__(self, pg_url: Optional[str] = None) -> None:
        self.pg_url = pg_url or PG_URL
        self.stats = CrimeStatistics(self.pg_url)
        self.trends = TrendAnalyzer(self.pg_url)
        self.hotspots = HotspotAnalyzer(self.pg_url)
        self.districts = DistrictAnalyzer(self.pg_url)
        self.risk = RiskScorer(self.pg_url)

    async def generate_report(
        self, report_type: str = "weekly", days: Optional[int] = None,
    ) -> dict[str, Any]:
        """Generate a comprehensive crime report."""
        if days is None:
            days = {"daily": 1, "weekly": 7, "monthly": 30, "custom": 30}.get(report_type, 7)

        logger.info("Generating %s report for %d days", report_type, days)
        start = datetime.utcnow()

        stats = await self.stats.get_summary_statistics(days)
        comparative = await self.stats.get_comparative_statistics(days, days)
        trend_data = await self.trends.analyze_trends(days)
        hotspot_data = await self.hotspots.analyze_hotspots(days)
        district_data = await self.districts.analyze_districts(days)
        risk_data = await self.risk.compute_area_risk_scores(days)

        report = {
            "title": f"Sentinel AI {report_type.title()} Crime Intelligence Report",
            "report_type": report_type,
            "period_days": days,
            "generated_at": datetime.utcnow().isoformat(),
            "sections": {
                "executive_summary": self._build_executive_summary(stats, comparative),
                "crime_statistics": stats,
                "comparative_analysis": comparative,
                "trend_analysis": trend_data,
                "hotspot_analysis": {
                    "total_clusters": hotspot_data.get("total_clusters", 0),
                    "top_hotspots": hotspot_data.get("district_hotspots", [])[:5],
                },
                "district_analysis": district_data,
                "risk_assessment": risk_data[:10] if risk_data else [],
            },
            "visualizations": self._recommend_visualizations(report_type),
            "duration_ms": round((datetime.utcnow() - start).total_seconds() * 1000, 0),
        }

        await self._store_report(report)
        logger.info("Report generated in %.0fms", report["duration_ms"])
        return report

    def _build_executive_summary(self, stats: dict[str, Any], comparative: dict[str, Any]) -> dict[str, Any]:
        total = stats.get("total_crimes", 0)
        daily_avg = stats.get("daily_average", 0)
        change = comparative.get("change", {})
        trend = comparative.get("trend", "stable")

        return {
            "total_crimes": total,
            "daily_average": daily_avg,
            "trend": trend,
            "change_percentage": change.get("percentage", 0),
            "clearance_rate": stats.get("clearance_rate", 0),
            "key_findings": [
                f"Total crimes in period: {total}",
                f"Daily average: {daily_avg}",
                f"Trend: {trend} ({change.get('percentage', 0):+.1f}%)",
                f"Clearance rate: {stats.get('clearance_rate', 0)}%",
            ],
        }

    def _recommend_visualizations(self, report_type: str) -> list[dict[str, str]]:
        return [
            {"type": "bar_chart", "title": "Crime Distribution by Type", "section": "crime_statistics"},
            {"type": "line_chart", "title": "Crime Trend Over Time", "section": "trend_analysis"},
            {"type": "heatmap", "title": "Crime Hotspot Map", "section": "hotspot_analysis"},
            {"type": "bar_chart", "title": "District Comparison", "section": "district_analysis"},
            {"type": "gauge", "title": "Risk Score Dashboard", "section": "risk_assessment"},
        ]

    async def _store_report(self, report: dict[str, Any]) -> None:
        try:
            import asyncpg
            conn = await asyncpg.connect(self.pg_url)
            try:
                await conn.execute(
                    """INSERT INTO reports (id, report_type, title, content, generated_by, status, generated_at)
                       VALUES (gen_random_uuid(), $1, $2, $3::jsonb, 'report_generator', 'completed', NOW())""",
                    report["report_type"], report["title"], json.dumps(report, default=str),
                )
            finally:
                await conn.close()
        except Exception as exc:
            logger.warning("Report storage failed: %s", str(exc))
