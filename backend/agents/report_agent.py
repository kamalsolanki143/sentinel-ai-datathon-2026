"""
Sentinel AI - Report Agent
===========================
File: backend/agents/report_agent.py
Purpose: LangGraph-powered AI agent for automated report generation that
         aggregates outputs from all other agents into structured,
         narrative-rich reports.

Architecture:
    - LangGraph state machine with 5 nodes: data_aggregation →
      report_structuring → narrative_generation → visualization_selection
      → final_compilation
    - Consumes results from all other specialist agents
    - Uses Gemini API for narrative writing and report structuring

Integration:
    - Called by orchestrator.py via LangGraph state routing
    - Reads investigation_results, analytics_results, ml_predictions,
      graph_analysis, recommendations from AgentState
    - Outputs report_data into shared AgentState
    - Reports stored in PostgreSQL reports table

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

from backend.agents.prompts import AgentState, ReportPrompts

load_dotenv()

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class ReportAgent:
    """
    AI-powered report generation agent that compiles multi-agent outputs.

    Workflow:
    1. Data Aggregation - Collect results from all specialist agents
    2. Report Structuring - Organize data into logical report sections
    3. Narrative Generation - Generate AI-written narrative for each section
    4. Visualization Selection - Recommend charts and visualizations
    5. Final Compilation - Assemble the complete report

    Attributes:
        llm: Gemini API client via LangChain
        pg_connection_string: PostgreSQL connection string
        graph: Compiled LangGraph state machine
    """

    def __init__(self) -> None:
        """Initialize the Report Agent with LLM and database configurations."""
        self.llm = ChatGoogleGenerativeAI(
            model=os.getenv("GEMINI_MODEL", "gemini-2.0-flash"),
            google_api_key=os.getenv("GOOGLE_API_KEY"),
            temperature=0.5,
            max_output_tokens=8192,
        )
        self.pg_connection_string: str = os.getenv(
            "DATABASE_URL",
            "postgresql://sentinel:password@localhost:5432/sentinel_db",
        )
        self.graph = self._build_graph()
        logger.info("ReportAgent initialized successfully")

    def _build_graph(self) -> StateGraph:
        """
        Build the LangGraph state machine for report generation workflow.

        Returns:
            Compiled StateGraph with report generation pipeline.
        """
        graph = StateGraph(AgentState)

        graph.add_node("data_aggregation", self._data_aggregation_node)
        graph.add_node("report_structuring", self._report_structuring_node)
        graph.add_node("narrative_generation", self._narrative_generation_node)
        graph.add_node("visualization_selection", self._visualization_selection_node)
        graph.add_node("final_compilation", self._final_compilation_node)

        graph.set_entry_point("data_aggregation")
        graph.add_edge("data_aggregation", "report_structuring")
        graph.add_edge("report_structuring", "narrative_generation")
        graph.add_edge("narrative_generation", "visualization_selection")
        graph.add_edge("visualization_selection", "final_compilation")
        graph.add_edge("final_compilation", END)

        logger.debug("Report LangGraph built with 5 nodes")
        return graph.compile()

    async def generate_report(self, state: AgentState) -> AgentState:
        """
        Execute the full report generation workflow.

        Args:
            state: Current agent state with results from other agents.

        Returns:
            Updated AgentState with report_data populated.
        """
        logger.info("Starting report generation workflow")
        start_time = datetime.utcnow()

        try:
            result_state = await self.graph.ainvoke(state)
            duration_ms = (datetime.utcnow() - start_time).total_seconds() * 1000
            logger.info("Report generation completed in %.0fms", duration_ms)
            result_state["metadata"] = {
                **result_state.get("metadata", {}),
                "report_duration_ms": duration_ms,
                "report_status": "completed",
            }
            return result_state

        except Exception as exc:
            logger.error("Report generation failed: %s", str(exc), exc_info=True)
            state["errors"] = state.get("errors", []) + [
                f"Report agent error: {str(exc)}"
            ]
            state["report_data"] = {"status": "failed", "error": str(exc)}
            return state

    async def _data_aggregation_node(self, state: AgentState) -> AgentState:
        """
        Node 1: Aggregate data from all specialist agents.

        Collects investigation results, analytics, predictions, graph analysis,
        and recommendations into a unified data structure for report generation.

        Args:
            state: Current state with multi-agent results.

        Returns:
            Updated state with aggregated data for report.
        """
        logger.info("Data aggregation: collecting multi-agent results")

        aggregated_data = {
            "investigation": state.get("investigation_results"),
            "analytics": state.get("analytics_results"),
            "predictions": state.get("ml_predictions"),
            "graph_analysis": state.get("graph_analysis"),
            "recommendations": state.get("recommendations"),
            "simulation": state.get("simulation_results"),
            "query": state.get("query", ""),
            "aggregated_at": datetime.utcnow().isoformat(),
        }

        available_sections = [
            key for key, value in aggregated_data.items()
            if value and key not in ("query", "aggregated_at")
        ]

        report_data = state.get("report_data") or {}
        report_data["aggregated_data"] = aggregated_data
        report_data["available_sections"] = available_sections
        state["report_data"] = report_data

        logger.info(
            "Data aggregation complete: %d sections available: %s",
            len(available_sections),
            available_sections,
        )

        return state

    async def _report_structuring_node(self, state: AgentState) -> AgentState:
        """
        Node 2: Organize aggregated data into logical report structure.

        Determines report type, creates section outline, and maps data
        to report sections.

        Args:
            state: Current state with aggregated data.

        Returns:
            Updated state with report structure defined.
        """
        logger.info("Report structuring: organizing report layout")

        try:
            report_data = state.get("report_data") or {}
            available_sections = report_data.get("available_sections", [])

            report_structure = {
                "title": "Sentinel AI Crime Intelligence Report",
                "report_type": self._determine_report_type(available_sections),
                "generated_at": datetime.utcnow().isoformat(),
                "sections": [],
            }

            section_order = [
                ("executive_summary", "Executive Summary"),
                ("investigation", "Investigation Analysis"),
                ("analytics", "Crime Analytics"),
                ("predictions", "Predictive Intelligence"),
                ("graph_analysis", "Network Analysis"),
                ("recommendations", "Resource Recommendations"),
                ("simulation", "Simulation Results"),
                ("conclusion", "Conclusions & Next Steps"),
            ]

            for section_key, section_title in section_order:
                if section_key in ("executive_summary", "conclusion"):
                    report_structure["sections"].append({
                        "key": section_key,
                        "title": section_title,
                        "has_data": True,
                    })
                elif section_key in available_sections:
                    report_structure["sections"].append({
                        "key": section_key,
                        "title": section_title,
                        "has_data": True,
                    })

            report_data["structure"] = report_structure
            state["report_data"] = report_data

            logger.info(
                "Report structuring complete: %d sections planned",
                len(report_structure["sections"]),
            )

        except Exception as exc:
            logger.error("Report structuring failed: %s", str(exc))
            state["errors"] = state.get("errors", []) + [
                f"Report structuring error: {str(exc)}"
            ]

        return state

    async def _narrative_generation_node(self, state: AgentState) -> AgentState:
        """
        Node 3: Generate AI-written narrative for each report section.

        Uses Gemini to create professional, contextual narrative text
        for each section of the report.

        Args:
            state: Current state with report structure.

        Returns:
            Updated state with narrative content for each section.
        """
        logger.info("Narrative generation: writing report narratives")

        try:
            report_data = state.get("report_data") or {}
            aggregated_data = report_data.get("aggregated_data", {})
            structure = report_data.get("structure", {})

            prompt = ReportPrompts.narrative_generation_prompt(
                report_structure=structure,
                aggregated_data=aggregated_data,
                query=state.get("query", ""),
            )

            messages = [
                SystemMessage(content=ReportPrompts.SYSTEM_PROMPT),
                HumanMessage(content=prompt),
            ]

            response = await self.llm.ainvoke(messages)
            narratives = response.content

            report_data["narratives"] = narratives
            state["report_data"] = report_data

            logger.info("Narrative generation completed successfully")

        except Exception as exc:
            logger.error("Narrative generation failed: %s", str(exc))
            report_data = state.get("report_data") or {}
            report_data["narratives"] = f"Narrative generation unavailable: {str(exc)}"
            state["report_data"] = report_data

        return state

    async def _visualization_selection_node(self, state: AgentState) -> AgentState:
        """
        Node 4: Recommend appropriate visualizations for report data.

        Selects chart types, map views, and table formats that best
        represent the data in each report section.

        Args:
            state: Current state with narratives generated.

        Returns:
            Updated state with visualization recommendations.
        """
        logger.info("Visualization selection: recommending charts and maps")

        try:
            report_data = state.get("report_data") or {}
            available_sections = report_data.get("available_sections", [])

            visualizations = []

            viz_mapping = {
                "analytics": [
                    {"type": "bar_chart", "title": "Crime Distribution by Type", "data_key": "by_type"},
                    {"type": "line_chart", "title": "Crime Trend Over Time", "data_key": "trends"},
                    {"type": "pie_chart", "title": "Crime Severity Distribution", "data_key": "by_severity"},
                ],
                "predictions": [
                    {"type": "heatmap", "title": "Crime Hotspot Map", "data_key": "hotspot_prediction"},
                    {"type": "line_chart", "title": "Crime Forecast", "data_key": "crime_forecasting"},
                    {"type": "scatter_plot", "title": "Anomaly Detection Results", "data_key": "anomaly_detection"},
                ],
                "graph_analysis": [
                    {"type": "network_graph", "title": "Criminal Network Visualization", "data_key": "network"},
                    {"type": "force_directed", "title": "Entity Relationships", "data_key": "relationships"},
                ],
                "recommendations": [
                    {"type": "map_overlay", "title": "Officer Deployment Map", "data_key": "deployment"},
                    {"type": "table", "title": "Officer Assignment Matrix", "data_key": "assignments"},
                ],
            }

            for section in available_sections:
                if section in viz_mapping:
                    visualizations.extend(viz_mapping[section])

            report_data["visualizations"] = visualizations
            state["report_data"] = report_data

            logger.info(
                "Visualization selection complete: %d visualizations recommended",
                len(visualizations),
            )

        except Exception as exc:
            logger.error("Visualization selection failed: %s", str(exc))
            report_data = state.get("report_data") or {}
            report_data["visualizations"] = []
            state["report_data"] = report_data

        return state

    async def _final_compilation_node(self, state: AgentState) -> AgentState:
        """
        Node 5: Assemble the complete report and store in database.

        Compiles all sections, narratives, and visualizations into the
        final report structure and persists it.

        Args:
            state: Current state with all report components.

        Returns:
            Updated state with final compiled report.
        """
        logger.info("Final compilation: assembling complete report")

        try:
            report_data = state.get("report_data") or {}

            final_report = {
                "title": report_data.get("structure", {}).get(
                    "title", "Sentinel AI Crime Intelligence Report"
                ),
                "report_type": report_data.get("structure", {}).get("report_type", "general"),
                "generated_at": datetime.utcnow().isoformat(),
                "sections": report_data.get("structure", {}).get("sections", []),
                "narratives": report_data.get("narratives", ""),
                "visualizations": report_data.get("visualizations", []),
                "data_sources": report_data.get("available_sections", []),
                "status": "completed",
            }

            await self._store_report(final_report)

            report_data["final_report"] = final_report
            report_data["status"] = "completed"
            state["report_data"] = report_data

            logger.info("Final compilation complete: report stored successfully")

        except Exception as exc:
            logger.error("Final compilation failed: %s", str(exc))
            report_data = state.get("report_data") or {}
            report_data["status"] = "partial"
            state["report_data"] = report_data
            state["errors"] = state.get("errors", []) + [
                f"Final compilation error: {str(exc)}"
            ]

        return state

    def _determine_report_type(self, available_sections: list[str]) -> str:
        """
        Determine the report type based on available data sections.

        Args:
            available_sections: List of section keys with available data.

        Returns:
            Report type string identifier.
        """
        if "investigation" in available_sections:
            return "investigation_report"
        if "predictions" in available_sections and "analytics" in available_sections:
            return "intelligence_report"
        if "simulation" in available_sections:
            return "simulation_report"
        if "recommendations" in available_sections:
            return "deployment_report"
        if "analytics" in available_sections:
            return "analytics_report"
        return "general_report"

    async def _store_report(self, report: dict[str, Any]) -> None:
        """
        Store the generated report in PostgreSQL.

        Args:
            report: Complete report dictionary to persist.
        """
        logger.debug("Storing report in PostgreSQL")

        try:
            import asyncpg
            import json

            conn = await asyncpg.connect(self.pg_connection_string)
            try:
                await conn.execute(
                    """
                    INSERT INTO reports (id, report_type, title, content, metadata,
                                        generated_by, status, generated_at)
                    VALUES (gen_random_uuid(), $1, $2, $3::jsonb, $4::jsonb,
                            'report_agent', 'completed', NOW())
                    """,
                    report.get("report_type", "general"),
                    report.get("title", "Untitled Report"),
                    json.dumps(report),
                    json.dumps({"data_sources": report.get("data_sources", [])}),
                )
                logger.info("Report stored in PostgreSQL successfully")
            finally:
                await conn.close()

        except Exception as exc:
            logger.warning("Report storage failed (non-critical): %s", str(exc))
