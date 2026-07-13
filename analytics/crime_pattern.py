"""
Sentinel AI - Crime Pattern Detection Module
==============================================
File: analytics/crime_pattern.py
Purpose: Recurring pattern detection including MO analysis, serial crime
         identification, and Neo4j-powered relationship pattern mining.

Dependencies: pandas, numpy, neo4j
"""

import logging, os
from typing import Any, Optional
import numpy as np, pandas as pd

logger = logging.getLogger(__name__)
NEO4J_URI = os.getenv("NEO4J_URI", "bolt://localhost:7687")
NEO4J_USER = os.getenv("NEO4J_USER", "neo4j")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "password")
PG_URL = os.getenv("DATABASE_URL", "postgresql://sentinel:password@localhost:5432/sentinel_db")


class CrimePatternDetector:
    """Crime pattern detection engine using relational and graph data."""

    def __init__(self) -> None:
        self.neo4j_uri = NEO4J_URI
        self.neo4j_user = NEO4J_USER
        self.neo4j_password = NEO4J_PASSWORD
        self.pg_url = PG_URL

    async def detect_patterns(self, days: int = 90) -> dict[str, Any]:
        """Detect recurring crime patterns from all data sources."""
        mo_patterns = await self._detect_mo_patterns(days)
        serial_patterns = await self._detect_serial_crimes(days)
        graph_patterns = await self._detect_graph_patterns()
        temporal_patterns = await self._detect_temporal_cooccurrence(days)

        return {
            "modus_operandi_patterns": mo_patterns,
            "serial_crime_patterns": serial_patterns,
            "graph_patterns": graph_patterns,
            "temporal_cooccurrence": temporal_patterns,
            "period_days": days,
        }

    async def _detect_mo_patterns(self, days: int) -> list[dict[str, Any]]:
        try:
            import asyncpg
            conn = await asyncpg.connect(self.pg_url)
            try:
                rows = await conn.fetch(
                    """SELECT crime_type, district, 
                              EXTRACT(HOUR FROM occurred_at)::int as hour,
                              COUNT(*) as count
                       FROM crimes WHERE occurred_at >= NOW() - $1::interval
                       GROUP BY crime_type, district, hour
                       HAVING COUNT(*) >= 3
                       ORDER BY count DESC LIMIT 20""",
                    f"{days} days",
                )
                return [{"crime_type": r["crime_type"], "district": r["district"],
                         "hour": int(r["hour"]), "frequency": int(r["count"])} for r in rows]
            finally:
                await conn.close()
        except Exception as exc:
            logger.warning("MO pattern detection failed: %s", str(exc))
            return []

    async def _detect_serial_crimes(self, days: int) -> list[dict[str, Any]]:
        try:
            import asyncpg
            conn = await asyncpg.connect(self.pg_url)
            try:
                rows = await conn.fetch(
                    """SELECT crime_type, district, COUNT(*) as count,
                              MIN(occurred_at) as first_occurrence,
                              MAX(occurred_at) as last_occurrence
                       FROM crimes WHERE occurred_at >= NOW() - $1::interval
                       GROUP BY crime_type, district
                       HAVING COUNT(*) >= 5
                       ORDER BY count DESC LIMIT 15""",
                    f"{days} days",
                )
                return [{"crime_type": r["crime_type"], "district": r["district"],
                         "total_incidents": int(r["count"]),
                         "first": str(r["first_occurrence"]), "last": str(r["last_occurrence"]),
                         "serial_likelihood": "high" if r["count"] >= 10 else "medium"} for r in rows]
            finally:
                await conn.close()
        except Exception as exc:
            logger.warning("Serial crime detection failed: %s", str(exc))
            return []

    async def _detect_graph_patterns(self) -> list[dict[str, Any]]:
        try:
            from neo4j import AsyncGraphDatabase
            driver = AsyncGraphDatabase.driver(self.neo4j_uri, auth=(self.neo4j_user, self.neo4j_password))
            try:
                async with driver.session() as session:
                    result = await session.run(
                        """MATCH (s:Suspect)-[:COMMITTED]->(c:Crime)
                           WITH s, COUNT(c) as crime_count
                           WHERE crime_count >= 2
                           RETURN s.name as suspect, crime_count
                           ORDER BY crime_count DESC LIMIT 10""",
                    )
                    return [{"suspect": r["suspect"], "crime_count": int(r["crime_count"]),
                             "pattern": "repeat_offender"} async for r in result]
            finally:
                await driver.close()
        except Exception as exc:
            logger.warning("Graph pattern detection failed: %s", str(exc))
            return []

    async def _detect_temporal_cooccurrence(self, days: int) -> list[dict[str, Any]]:
        try:
            import asyncpg
            conn = await asyncpg.connect(self.pg_url)
            try:
                rows = await conn.fetch(
                    """SELECT a.crime_type as type_a, b.crime_type as type_b,
                              COUNT(*) as cooccurrence
                       FROM crimes a JOIN crimes b ON DATE(a.occurred_at) = DATE(b.occurred_at)
                            AND a.district = b.district AND a.id < b.id
                       WHERE a.occurred_at >= NOW() - $1::interval
                       GROUP BY a.crime_type, b.crime_type
                       HAVING COUNT(*) >= 3
                       ORDER BY cooccurrence DESC LIMIT 10""",
                    f"{days} days",
                )
                return [{"type_a": r["type_a"], "type_b": r["type_b"],
                         "cooccurrence": int(r["cooccurrence"])} for r in rows]
            finally:
                await conn.close()
        except Exception as exc:
            logger.warning("Temporal co-occurrence detection failed: %s", str(exc))
            return []
