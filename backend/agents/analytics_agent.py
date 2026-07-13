"""
Sentinel AI - Analytics Agent
=============================
File: backend/agents/analytics_agent.py
Purpose: LangGraph-powered AI agent for statistical crime analysis, pattern
         detection, trend identification, and AI-enriched insight generation.

Architecture:
    - LangGraph state machine with 5 nodes: data_collection → statistical_analysis
      → pattern_detection → trend_forecasting → insight_generation
    - Consumes output from the analytics module (crime_statistics, trend_analysis, etc.)
    - Uses Gemini API for natural language insight generation

Integration:
    - Called by orchestrator.py via LangGraph state routing
    - Reads from analytics/ module (crime_statistics.py, trend_analysis.py, etc.)
    - Reads from PostgreSQL for raw crime data
    - Outputs analytics_results into shared AgentState
    - Results consumed by report_agent.py and recommendation_agent.py

Dependencies:
    - langchain-google-genai
    - langgraph
    - asyncpg
    - python-dotenv
"""

import logging
import os
from datetime import datetime
from typing import Any, Optional

from dotenv import load_dotenv
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.graph import END, StateGraph

from backend.agents.prompts import AgentState, AnalyticsPrompts

load_dotenv()

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class AnalyticsAgent:
    """
    AI-powered analytics agent for crime data statistical analysis.

    Workflow:
    1. Data Collection - Gather crime data and existing analytics
    2. Statistical Analysis - Compute descriptive and inferential statistics
    3. Pattern Detection - Identify recurring crime patterns
    4. Trend Forecasting - Detect temporal trends and seasonal patterns
    5. Insight Generation - Generate AI-enriched natural language insights

    Attributes:
        llm: Gemini API client via LangChain
        pg_connection_string: PostgreSQL connection string
        graph: Compiled LangGraph state machine
    """

    def __init__(self) -> None:
        """Initialize the Analytics Agent with LLM and database configurations."""
        self.llm = ChatGoogleGenerativeAI(
            model=os.getenv("GEMINI_MODEL", "gemini-2.0-flash"),
            google_api_key=os.getenv("GOOGLE_API_KEY"),
            temperature=0.3,
            max_output_tokens=2048,
        )
        self.pg_connection_string: str = os.getenv(
            "DATABASE_URL",
            "postgresql://sentinel:password@localhost:5432/sentinel_db",
        )
        self.graph = self._build_graph()
        logger.info("AnalyticsAgent initialized successfully")

    def _build_graph(self) -> StateGraph:
        """
        Build the LangGraph state machine for analytics workflow.

        Returns:
            Compiled StateGraph with analytics pipeline nodes and edges.
        """
        graph = StateGraph(AgentState)

        graph.add_node("data_collection", self._data_collection_node)
        graph.add_node("statistical_analysis", self._statistical_analysis_node)
        graph.add_node("pattern_detection", self._pattern_detection_node)
        graph.add_node("trend_forecasting", self._trend_forecasting_node)
        graph.add_node("insight_generation", self._insight_generation_node)

        graph.set_entry_point("data_collection")
        graph.add_edge("data_collection", "statistical_analysis")
        graph.add_edge("statistical_analysis", "pattern_detection")
        graph.add_edge("pattern_detection", "trend_forecasting")
        graph.add_edge("trend_forecasting", "insight_generation")
        graph.add_edge("insight_generation", END)

        logger.debug("Analytics LangGraph built with 5 nodes")
        return graph.compile()

    async def analyze(self, state: AgentState) -> AgentState:
        """
        Execute the full analytics workflow.

        Args:
            state: Current agent state containing query and context.

        Returns:
            Updated AgentState with analytics_results populated.
        """
        logger.info("Starting analytics workflow for query: %s", state.get("query", "")[:100])
        start_time = datetime.utcnow()

        try:
            result_state = await self.graph.ainvoke(state)
            duration_ms = (datetime.utcnow() - start_time).total_seconds() * 1000
            logger.info("Analytics workflow completed in %.0fms", duration_ms)
            result_state["metadata"] = {
                **result_state.get("metadata", {}),
                "analytics_duration_ms": duration_ms,
                "analytics_status": "completed",
            }
            return result_state

        except Exception as exc:
            logger.error("Analytics workflow failed: %s", str(exc), exc_info=True)
            state["errors"] = state.get("errors", []) + [
                f"Analytics agent error: {str(exc)}"
            ]
            state["analytics_results"] = {
                "status": "failed",
                "error": str(exc),
            }
            return state

    async def _data_collection_node(self, state: AgentState) -> AgentState:
        """
        Node 1: Collect and prepare crime data for analysis.

        Fetches crime records from PostgreSQL with relevant filters and
        prepares structured datasets for statistical processing.

        Args:
            state: Current agent state with query context.

        Returns:
            Updated state with crime_data populated.
        """
        logger.info("Data collection: fetching crime data from PostgreSQL")

        try:
            crime_data = await self._fetch_analytics_data(state.get("query", ""))
            state["crime_data"] = crime_data
            logger.info("Data collection complete: %d records loaded", len(crime_data))

        except Exception as exc:
            logger.warning("Data collection failed: %s", str(exc))
            state["crime_data"] = state.get("crime_data", [])
            state["errors"] = state.get("errors", []) + [
                f"Data collection error: {str(exc)}"
            ]

        return state

    async def _statistical_analysis_node(self, state: AgentState) -> AgentState:
        """
        Node 2: Compute statistical metrics on collected crime data.

        Calculates descriptive statistics including crime counts by type,
        severity distributions, temporal distributions, and district-level
        aggregations.

        Args:
            state: Current state with crime_data loaded.

        Returns:
            Updated state with statistical analysis in analytics_results.
        """
        logger.info("Statistical analysis: computing crime metrics")

        try:
            crime_data = state.get("crime_data", [])

            statistics = self._compute_statistics(crime_data)

            current_results = state.get("analytics_results") or {}
            current_results["statistics"] = statistics
            state["analytics_results"] = current_results

            logger.info("Statistical analysis completed: %d metric groups computed", len(statistics))

        except Exception as exc:
            logger.error("Statistical analysis failed: %s", str(exc))
            current_results = state.get("analytics_results") or {}
            current_results["statistics"] = {"error": str(exc)}
            state["analytics_results"] = current_results

        return state

    async def _pattern_detection_node(self, state: AgentState) -> AgentState:
        """
        Node 3: Detect recurring crime patterns using AI analysis.

        Uses Gemini to identify patterns in crime data including spatial
        clustering, temporal patterns, and modus operandi similarities.

        Args:
            state: Current state with statistics computed.

        Returns:
            Updated state with detected patterns in analytics_results.
        """
        logger.info("Pattern detection: identifying crime patterns with Gemini")

        try:
            crime_data = state.get("crime_data", [])
            analytics_results = state.get("analytics_results") or {}
            statistics = analytics_results.get("statistics", {})

            prompt = AnalyticsPrompts.pattern_detection_prompt(
                crime_data=crime_data,
                statistics=statistics,
            )

            messages = [
                SystemMessage(content=AnalyticsPrompts.SYSTEM_PROMPT),
                HumanMessage(content=prompt),
            ]

            response = await self.llm.ainvoke(messages)
            patterns = response.content

            analytics_results["patterns"] = patterns
            state["analytics_results"] = analytics_results

            logger.info("Pattern detection completed successfully")

        except Exception as exc:
            logger.error("Pattern detection failed: %s", str(exc))
            analytics_results = state.get("analytics_results") or {}
            analytics_results["patterns"] = f"Pattern detection unavailable: {str(exc)}"
            state["analytics_results"] = analytics_results

        return state

    async def _trend_forecasting_node(self, state: AgentState) -> AgentState:
        """
        Node 4: Analyze temporal trends and forecast crime trajectories.

        Identifies seasonal patterns, upward/downward trends, and change
        points in crime data using the analytics engine outputs.

        Args:
            state: Current state with patterns detected.

        Returns:
            Updated state with trend analysis in analytics_results.
        """
        logger.info("Trend forecasting: analyzing temporal crime trends")

        try:
            crime_data = state.get("crime_data", [])
            analytics_results = state.get("analytics_results") or {}

            prompt = AnalyticsPrompts.trend_analysis_prompt(
                crime_data=crime_data,
                statistics=analytics_results.get("statistics", {}),
                patterns=analytics_results.get("patterns", ""),
            )

            messages = [
                SystemMessage(content=AnalyticsPrompts.SYSTEM_PROMPT),
                HumanMessage(content=prompt),
            ]

            response = await self.llm.ainvoke(messages)
            trends = response.content

            analytics_results["trends"] = trends
            state["analytics_results"] = analytics_results

            logger.info("Trend forecasting completed successfully")

        except Exception as exc:
            logger.error("Trend forecasting failed: %s", str(exc))
            analytics_results = state.get("analytics_results") or {}
            analytics_results["trends"] = f"Trend analysis unavailable: {str(exc)}"
            state["analytics_results"] = analytics_results

        return state

    async def _insight_generation_node(self, state: AgentState) -> AgentState:
        """
        Node 5: Generate comprehensive AI-enriched insights summary.

        Synthesizes all statistical analysis, pattern detection, and trend
        data into actionable natural language insights with recommendations.

        Args:
            state: Current state with all analytics data.

        Returns:
            Updated state with final insights in analytics_results.
        """
        logger.info("Insight generation: synthesizing analytics findings")

        try:
            analytics_results = state.get("analytics_results") or {}
            query = state.get("query", "")

            prompt = AnalyticsPrompts.insight_generation_prompt(
                query=query,
                statistics=analytics_results.get("statistics", {}),
                patterns=analytics_results.get("patterns", ""),
                trends=analytics_results.get("trends", ""),
            )

            messages = [
                SystemMessage(content=AnalyticsPrompts.SYSTEM_PROMPT),
                HumanMessage(content=prompt),
            ]

            response = await self.llm.ainvoke(messages)
            insights = response.content

            analytics_results["insights"] = insights
            analytics_results["status"] = "completed"
            analytics_results["completed_at"] = datetime.utcnow().isoformat()
            state["analytics_results"] = analytics_results

            logger.info("Insight generation completed successfully")

        except Exception as exc:
            logger.error("Insight generation failed: %s", str(exc))
            analytics_results = state.get("analytics_results") or {}
            analytics_results["insights"] = f"Insights unavailable: {str(exc)}"
            analytics_results["status"] = "partial"
            state["analytics_results"] = analytics_results

        return state

    def _compute_statistics(self, crime_data: list[dict[str, Any]]) -> dict[str, Any]:
        """
        Compute descriptive statistics from crime data.

        Args:
            crime_data: List of crime record dictionaries.

        Returns:
            Dictionary containing computed statistical metrics.
        """
        if not crime_data:
            return {
                "total_crimes": 0,
                "by_type": {},
                "by_severity": {},
                "by_district": {},
                "by_status": {},
            }

        type_counts: dict[str, int] = {}
        severity_counts: dict[str, int] = {}
        district_counts: dict[str, int] = {}
        status_counts: dict[str, int] = {}

        for crime in crime_data:
            crime_type = crime.get("crime_type", "unknown")
            type_counts[crime_type] = type_counts.get(crime_type, 0) + 1

            severity = crime.get("severity", "unknown")
            severity_counts[severity] = severity_counts.get(severity, 0) + 1

            district = crime.get("district", "unknown")
            district_counts[district] = district_counts.get(district, 0) + 1

            status = crime.get("status", "unknown")
            status_counts[status] = status_counts.get(status, 0) + 1

        return {
            "total_crimes": len(crime_data),
            "by_type": dict(sorted(type_counts.items(), key=lambda x: x[1], reverse=True)),
            "by_severity": dict(sorted(severity_counts.items(), key=lambda x: x[1], reverse=True)),
            "by_district": dict(sorted(district_counts.items(), key=lambda x: x[1], reverse=True)),
            "by_status": dict(sorted(status_counts.items(), key=lambda x: x[1], reverse=True)),
        }

    async def _fetch_analytics_data(self, query: str) -> list[dict[str, Any]]:
        """
        Fetch crime records from PostgreSQL for analytics processing.

        Args:
            query: Analytics query string for data filtering.

        Returns:
            List of crime record dictionaries.
        """
        logger.debug("Fetching analytics data from PostgreSQL")

        try:
            import asyncpg

            conn = await asyncpg.connect(self.pg_connection_string)
            try:
                rows = await conn.fetch(
                    """
                    SELECT c.id, c.crime_type, c.description, c.occurred_at,
                           c.status, c.latitude, c.longitude, c.district,
                           c.severity, c.station
                    FROM crimes c
                    WHERE c.occurred_at >= NOW() - INTERVAL '90 days'
                    ORDER BY c.occurred_at DESC
                    LIMIT 1000
                    """,
                )
                crime_data = [dict(row) for row in rows]
                logger.info("Fetched %d records for analytics", len(crime_data))
                return crime_data
            finally:
                await conn.close()

        except Exception as exc:
            logger.warning("PostgreSQL analytics fetch failed: %s", str(exc))
            return []
