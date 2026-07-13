"""
Sentinel AI - Investigation Agent
=================================
File: backend/agents/investigation_agent.py
Purpose: LangGraph-powered AI agent for automated crime investigation,
         evidence analysis, suspect profiling, and case reconstruction.

Architecture:
    - LangGraph state machine with 5 nodes: case_intake → evidence_analysis
      → suspect_profiling → timeline_reconstruction → conclusion
    - Integrates with PostgreSQL (case data) and Neo4j (knowledge graph)
    - Uses Gemini API via LangChain for reasoning and analysis

Integration:
    - Called by orchestrator.py via LangGraph state routing
    - Reads from PostgreSQL (crimes, evidence, suspects tables)
    - Reads from Neo4j (suspect networks, crime relationships)
    - Outputs investigation results into shared AgentState
    - Results consumed by report_agent.py for report generation

Dependencies:
    - langchain-google-genai
    - langgraph
    - asyncpg
    - neo4j
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

from backend.agents.prompts import AgentState, InvestigationPrompts

load_dotenv()

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class InvestigationAgent:
    """
    AI-powered investigation agent that automates crime case analysis.

    This agent follows a structured investigation workflow:
    1. Case Intake - Load and validate case data from databases
    2. Evidence Analysis - Analyze evidence patterns using Gemini AI
    3. Suspect Profiling - Build suspect profiles using Neo4j graph
    4. Timeline Reconstruction - Build chronological event timeline
    5. Conclusion - Synthesize findings into investigation summary

    Attributes:
        llm: Gemini API client via LangChain
        pg_connection_string: PostgreSQL connection string
        neo4j_uri: Neo4j connection URI
        neo4j_user: Neo4j authentication user
        neo4j_password: Neo4j authentication password
        graph: Compiled LangGraph state machine
    """

    def __init__(self) -> None:
        """Initialize the Investigation Agent with LLM and database configurations."""
        self.llm = ChatGoogleGenerativeAI(
            model=os.getenv("GEMINI_MODEL", "gemini-2.0-flash"),
            google_api_key=os.getenv("GOOGLE_API_KEY"),
            temperature=0.2,
            max_output_tokens=4096,
        )
        self.pg_connection_string: str = os.getenv(
            "DATABASE_URL",
            "postgresql://sentinel:password@localhost:5432/sentinel_db",
        )
        self.neo4j_uri: str = os.getenv("NEO4J_URI", "bolt://localhost:7687")
        self.neo4j_user: str = os.getenv("NEO4J_USER", "neo4j")
        self.neo4j_password: str = os.getenv("NEO4J_PASSWORD", "password")
        self.graph = self._build_graph()
        logger.info("InvestigationAgent initialized successfully")

    def _build_graph(self) -> StateGraph:
        """
        Build the LangGraph state machine for investigation workflow.

        Returns:
            Compiled StateGraph with investigation pipeline nodes and edges.
        """
        graph = StateGraph(AgentState)

        graph.add_node("case_intake", self._case_intake_node)
        graph.add_node("evidence_analysis", self._evidence_analysis_node)
        graph.add_node("suspect_profiling", self._suspect_profiling_node)
        graph.add_node("timeline_reconstruction", self._timeline_reconstruction_node)
        graph.add_node("conclusion", self._conclusion_node)

        graph.set_entry_point("case_intake")
        graph.add_edge("case_intake", "evidence_analysis")
        graph.add_edge("evidence_analysis", "suspect_profiling")
        graph.add_edge("suspect_profiling", "timeline_reconstruction")
        graph.add_edge("timeline_reconstruction", "conclusion")
        graph.add_edge("conclusion", END)

        logger.debug("Investigation LangGraph built with 5 nodes")
        return graph.compile()

    async def investigate(self, state: AgentState) -> AgentState:
        """
        Execute the full investigation workflow.

        Args:
            state: Current agent state containing query and context.

        Returns:
            Updated AgentState with investigation_results populated.
        """
        logger.info("Starting investigation workflow for query: %s", state.get("query", "")[:100])
        start_time = datetime.utcnow()

        try:
            result_state = await self.graph.ainvoke(state)
            duration_ms = (datetime.utcnow() - start_time).total_seconds() * 1000
            logger.info(
                "Investigation workflow completed in %.0fms",
                duration_ms,
            )
            result_state["metadata"] = {
                **result_state.get("metadata", {}),
                "investigation_duration_ms": duration_ms,
                "investigation_status": "completed",
            }
            return result_state

        except Exception as exc:
            logger.error("Investigation workflow failed: %s", str(exc), exc_info=True)
            state["errors"] = state.get("errors", []) + [
                f"Investigation agent error: {str(exc)}"
            ]
            state["investigation_results"] = {
                "status": "failed",
                "error": str(exc),
                "partial_results": state.get("investigation_results"),
            }
            return state

    async def _case_intake_node(self, state: AgentState) -> AgentState:
        """
        Node 1: Load case data from PostgreSQL and Neo4j.

        Fetches crime records, associated evidence, and suspect information
        from the relational database. Also queries Neo4j for existing
        relationships and network data.

        Args:
            state: Current agent state with query context.

        Returns:
            Updated state with crime_data and graph_data populated.
        """
        logger.info("Case intake: loading case data from databases")

        try:
            crime_data = await self._fetch_crime_data(state.get("query", ""))
            graph_data = await self._fetch_graph_data(state.get("query", ""))

            state["crime_data"] = crime_data
            state["graph_data"] = graph_data

            logger.info(
                "Case intake complete: %d crime records, %d graph entities loaded",
                len(crime_data) if crime_data else 0,
                len(graph_data.get("nodes", [])) if graph_data else 0,
            )

        except Exception as exc:
            logger.warning("Case intake partial failure: %s", str(exc))
            state["crime_data"] = state.get("crime_data", [])
            state["graph_data"] = state.get("graph_data", {})
            state["errors"] = state.get("errors", []) + [
                f"Case intake error: {str(exc)}"
            ]

        return state

    async def _evidence_analysis_node(self, state: AgentState) -> AgentState:
        """
        Node 2: Analyze evidence patterns using Gemini AI.

        Takes the loaded crime and evidence data and uses the LLM to identify
        patterns, connections, and significance of each piece of evidence.

        Args:
            state: Current state with crime_data loaded.

        Returns:
            Updated state with evidence analysis in investigation_results.
        """
        logger.info("Evidence analysis: analyzing patterns with Gemini")

        try:
            crime_data = state.get("crime_data", [])
            query = state.get("query", "")

            prompt = InvestigationPrompts.evidence_analysis_prompt(
                query=query,
                crime_data=crime_data,
            )

            messages = [
                SystemMessage(content=InvestigationPrompts.SYSTEM_PROMPT),
                HumanMessage(content=prompt),
            ]

            response = await self.llm.ainvoke(messages)
            evidence_analysis = response.content

            current_results = state.get("investigation_results") or {}
            current_results["evidence_analysis"] = evidence_analysis
            state["investigation_results"] = current_results

            logger.info("Evidence analysis completed successfully")

        except Exception as exc:
            logger.error("Evidence analysis failed: %s", str(exc))
            current_results = state.get("investigation_results") or {}
            current_results["evidence_analysis"] = f"Analysis unavailable: {str(exc)}"
            state["investigation_results"] = current_results
            state["errors"] = state.get("errors", []) + [
                f"Evidence analysis error: {str(exc)}"
            ]

        return state

    async def _suspect_profiling_node(self, state: AgentState) -> AgentState:
        """
        Node 3: Build suspect profiles using Neo4j graph and Gemini AI.

        Leverages the knowledge graph to identify suspect relationships,
        known associates, criminal history, and behavioral patterns.

        Args:
            state: Current state with crime_data and graph_data.

        Returns:
            Updated state with suspect profiles in investigation_results.
        """
        logger.info("Suspect profiling: building profiles from graph data")

        try:
            graph_data = state.get("graph_data", {})
            crime_data = state.get("crime_data", [])

            prompt = InvestigationPrompts.suspect_profiling_prompt(
                crime_data=crime_data,
                graph_data=graph_data,
            )

            messages = [
                SystemMessage(content=InvestigationPrompts.SYSTEM_PROMPT),
                HumanMessage(content=prompt),
            ]

            response = await self.llm.ainvoke(messages)
            suspect_profiles = response.content

            current_results = state.get("investigation_results") or {}
            current_results["suspect_profiles"] = suspect_profiles
            state["investigation_results"] = current_results

            logger.info("Suspect profiling completed successfully")

        except Exception as exc:
            logger.error("Suspect profiling failed: %s", str(exc))
            current_results = state.get("investigation_results") or {}
            current_results["suspect_profiles"] = f"Profiling unavailable: {str(exc)}"
            state["investigation_results"] = current_results
            state["errors"] = state.get("errors", []) + [
                f"Suspect profiling error: {str(exc)}"
            ]

        return state

    async def _timeline_reconstruction_node(self, state: AgentState) -> AgentState:
        """
        Node 4: Reconstruct the chronological timeline of events.

        Uses all available data (crime records, evidence, suspect movements)
        to build a comprehensive timeline of the criminal activity.

        Args:
            state: Current state with all investigation data.

        Returns:
            Updated state with timeline in investigation_results.
        """
        logger.info("Timeline reconstruction: building chronological timeline")

        try:
            crime_data = state.get("crime_data", [])
            investigation_results = state.get("investigation_results") or {}

            prompt = InvestigationPrompts.timeline_reconstruction_prompt(
                crime_data=crime_data,
                evidence_analysis=investigation_results.get("evidence_analysis", ""),
                suspect_profiles=investigation_results.get("suspect_profiles", ""),
            )

            messages = [
                SystemMessage(content=InvestigationPrompts.SYSTEM_PROMPT),
                HumanMessage(content=prompt),
            ]

            response = await self.llm.ainvoke(messages)
            timeline = response.content

            investigation_results["timeline"] = timeline
            state["investigation_results"] = investigation_results

            logger.info("Timeline reconstruction completed successfully")

        except Exception as exc:
            logger.error("Timeline reconstruction failed: %s", str(exc))
            investigation_results = state.get("investigation_results") or {}
            investigation_results["timeline"] = f"Timeline unavailable: {str(exc)}"
            state["investigation_results"] = investigation_results
            state["errors"] = state.get("errors", []) + [
                f"Timeline reconstruction error: {str(exc)}"
            ]

        return state

    async def _conclusion_node(self, state: AgentState) -> AgentState:
        """
        Node 5: Synthesize all findings into a comprehensive conclusion.

        Combines evidence analysis, suspect profiles, and timeline into
        a cohesive investigation summary with actionable recommendations.

        Args:
            state: Current state with all investigation data.

        Returns:
            Updated state with final investigation conclusion.
        """
        logger.info("Conclusion: synthesizing investigation findings")

        try:
            investigation_results = state.get("investigation_results") or {}
            query = state.get("query", "")

            prompt = InvestigationPrompts.conclusion_prompt(
                query=query,
                evidence_analysis=investigation_results.get("evidence_analysis", ""),
                suspect_profiles=investigation_results.get("suspect_profiles", ""),
                timeline=investigation_results.get("timeline", ""),
            )

            messages = [
                SystemMessage(content=InvestigationPrompts.SYSTEM_PROMPT),
                HumanMessage(content=prompt),
            ]

            response = await self.llm.ainvoke(messages)
            conclusion = response.content

            investigation_results["conclusion"] = conclusion
            investigation_results["status"] = "completed"
            investigation_results["completed_at"] = datetime.utcnow().isoformat()
            state["investigation_results"] = investigation_results

            logger.info("Investigation conclusion generated successfully")

        except Exception as exc:
            logger.error("Conclusion generation failed: %s", str(exc))
            investigation_results = state.get("investigation_results") or {}
            investigation_results["conclusion"] = f"Conclusion unavailable: {str(exc)}"
            investigation_results["status"] = "partial"
            state["investigation_results"] = investigation_results
            state["errors"] = state.get("errors", []) + [
                f"Conclusion error: {str(exc)}"
            ]

        return state

    async def _fetch_crime_data(self, query: str) -> list[dict[str, Any]]:
        """
        Fetch crime records from PostgreSQL based on the investigation query.

        Args:
            query: Investigation query string for filtering relevant records.

        Returns:
            List of crime record dictionaries with associated evidence and suspects.
        """
        logger.debug("Fetching crime data from PostgreSQL")

        try:
            import asyncpg

            conn = await asyncpg.connect(self.pg_connection_string)
            try:
                rows = await conn.fetch(
                    """
                    SELECT c.id, c.crime_type, c.description, c.occurred_at,
                           c.status, c.latitude, c.longitude, c.district,
                           c.severity, c.fir_number, c.modus_operandi,
                           c.station
                    FROM crimes c
                    WHERE c.description ILIKE $1
                       OR c.crime_type ILIKE $1
                       OR c.district ILIKE $1
                    ORDER BY c.occurred_at DESC
                    LIMIT 50
                    """,
                    f"%{query}%",
                )
                crime_data = [dict(row) for row in rows]
                logger.info("Fetched %d crime records from PostgreSQL", len(crime_data))
                return crime_data
            finally:
                await conn.close()

        except Exception as exc:
            logger.warning("PostgreSQL fetch failed, using empty dataset: %s", str(exc))
            return []

    async def _fetch_graph_data(self, query: str) -> dict[str, Any]:
        """
        Fetch relationship data from Neo4j knowledge graph.

        Args:
            query: Investigation query for graph traversal context.

        Returns:
            Dictionary containing nodes and relationships from the graph.
        """
        logger.debug("Fetching graph data from Neo4j")

        try:
            from neo4j import AsyncGraphDatabase

            driver = AsyncGraphDatabase.driver(
                self.neo4j_uri,
                auth=(self.neo4j_user, self.neo4j_password),
            )
            try:
                async with driver.session() as session:
                    result = await session.run(
                        """
                        MATCH (s:Suspect)-[r]-(connected)
                        WHERE s.name CONTAINS $query
                           OR s.aliases CONTAINS $query
                        RETURN s, r, connected
                        LIMIT 100
                        """,
                        query=query,
                    )
                    records = [record.data() async for record in result]

                    nodes = []
                    relationships = []
                    for record in records:
                        if "s" in record:
                            nodes.append(record["s"])
                        if "connected" in record:
                            nodes.append(record["connected"])
                        if "r" in record:
                            relationships.append(record["r"])

                    graph_data = {
                        "nodes": nodes,
                        "relationships": relationships,
                        "total_nodes": len(nodes),
                        "total_relationships": len(relationships),
                    }
                    logger.info(
                        "Fetched %d nodes, %d relationships from Neo4j",
                        len(nodes),
                        len(relationships),
                    )
                    return graph_data
            finally:
                await driver.close()

        except Exception as exc:
            logger.warning("Neo4j fetch failed, using empty graph: %s", str(exc))
            return {"nodes": [], "relationships": [], "total_nodes": 0, "total_relationships": 0}
