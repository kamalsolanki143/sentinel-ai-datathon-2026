"""
Sentinel AI - Graph Agent
=========================
File: backend/agents/graph_agent.py
Purpose: LangGraph-powered AI agent for Neo4j knowledge graph operations,
         criminal network analysis, entity resolution, and relationship
         pattern discovery.

Architecture:
    - LangGraph state machine with 5 nodes: query_parsing → graph_traversal
      → relationship_analysis → pattern_matching → insight_extraction
    - Direct Neo4j integration for Cypher query execution
    - Uses Gemini API for natural language query-to-Cypher translation
      and insight generation from graph patterns

Integration:
    - Called by orchestrator.py via LangGraph state routing
    - Directly queries Neo4j knowledge graph
    - Outputs graph_analysis into shared AgentState
    - Results consumed by investigation_agent.py and report_agent.py
    - Provides criminal network data to recommendation_agent.py

Dependencies:
    - langchain-google-genai
    - langgraph
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

from backend.agents.prompts import AgentState, GraphPrompts

load_dotenv()

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class GraphAgent:
    """
    AI-powered graph agent for Neo4j knowledge graph operations.

    Workflow:
    1. Query Parsing - Translate natural language to graph query intent
    2. Graph Traversal - Execute Cypher queries on Neo4j
    3. Relationship Analysis - Analyze entity relationships and networks
    4. Pattern Matching - Identify recurring graph patterns
    5. Insight Extraction - Generate AI-enriched insights from graph data

    Attributes:
        llm: Gemini API client via LangChain
        neo4j_uri: Neo4j connection URI
        neo4j_user: Neo4j authentication user
        neo4j_password: Neo4j authentication password
        graph: Compiled LangGraph state machine
    """

    def __init__(self) -> None:
        """Initialize the Graph Agent with LLM and Neo4j configurations."""
        self.llm = ChatGoogleGenerativeAI(
            model=os.getenv("GEMINI_MODEL", "gemini-2.0-flash"),
            google_api_key=os.getenv("GOOGLE_API_KEY"),
            temperature=0.2,
            max_output_tokens=2048,
        )
        self.neo4j_uri: str = os.getenv("NEO4J_URI", "bolt://localhost:7687")
        self.neo4j_user: str = os.getenv("NEO4J_USER", "neo4j")
        self.neo4j_password: str = os.getenv("NEO4J_PASSWORD", "password")
        self.graph = self._build_graph()
        logger.info("GraphAgent initialized successfully")

    def _build_graph(self) -> StateGraph:
        """
        Build the LangGraph state machine for graph analysis workflow.

        Returns:
            Compiled StateGraph with graph analysis pipeline nodes and edges.
        """
        graph = StateGraph(AgentState)

        graph.add_node("query_parsing", self._query_parsing_node)
        graph.add_node("graph_traversal", self._graph_traversal_node)
        graph.add_node("relationship_analysis", self._relationship_analysis_node)
        graph.add_node("pattern_matching", self._pattern_matching_node)
        graph.add_node("insight_extraction", self._insight_extraction_node)

        graph.set_entry_point("query_parsing")
        graph.add_edge("query_parsing", "graph_traversal")
        graph.add_edge("graph_traversal", "relationship_analysis")
        graph.add_edge("relationship_analysis", "pattern_matching")
        graph.add_edge("pattern_matching", "insight_extraction")
        graph.add_edge("insight_extraction", END)

        logger.debug("Graph LangGraph built with 5 nodes")
        return graph.compile()

    async def analyze_graph(self, state: AgentState) -> AgentState:
        """
        Execute the full graph analysis workflow.

        Args:
            state: Current agent state containing query and context.

        Returns:
            Updated AgentState with graph_analysis populated.
        """
        logger.info("Starting graph analysis workflow for query: %s", state.get("query", "")[:100])
        start_time = datetime.utcnow()

        try:
            result_state = await self.graph.ainvoke(state)
            duration_ms = (datetime.utcnow() - start_time).total_seconds() * 1000
            logger.info("Graph analysis workflow completed in %.0fms", duration_ms)
            result_state["metadata"] = {
                **result_state.get("metadata", {}),
                "graph_analysis_duration_ms": duration_ms,
                "graph_analysis_status": "completed",
            }
            return result_state

        except Exception as exc:
            logger.error("Graph analysis workflow failed: %s", str(exc), exc_info=True)
            state["errors"] = state.get("errors", []) + [
                f"Graph agent error: {str(exc)}"
            ]
            state["graph_analysis"] = {"status": "failed", "error": str(exc)}
            return state

    async def _query_parsing_node(self, state: AgentState) -> AgentState:
        """
        Node 1: Parse the natural language query to determine graph operations.

        Uses Gemini to understand the user's intent and determine which
        graph queries and traversals are needed.

        Args:
            state: Current agent state with query context.

        Returns:
            Updated state with parsed query intent for graph operations.
        """
        logger.info("Query parsing: interpreting graph query intent")

        try:
            query = state.get("query", "")

            prompt = GraphPrompts.query_parsing_prompt(query=query)

            messages = [
                SystemMessage(content=GraphPrompts.SYSTEM_PROMPT),
                HumanMessage(content=prompt),
            ]

            response = await self.llm.ainvoke(messages)
            parsed_intent = response.content

            current_analysis = state.get("graph_analysis") or {}
            current_analysis["parsed_intent"] = parsed_intent
            current_analysis["original_query"] = query
            state["graph_analysis"] = current_analysis

            logger.info("Query parsing completed: intent extracted")

        except Exception as exc:
            logger.error("Query parsing failed: %s", str(exc))
            current_analysis = state.get("graph_analysis") or {}
            current_analysis["parsed_intent"] = state.get("query", "")
            state["graph_analysis"] = current_analysis
            state["errors"] = state.get("errors", []) + [
                f"Query parsing error: {str(exc)}"
            ]

        return state

    async def _graph_traversal_node(self, state: AgentState) -> AgentState:
        """
        Node 2: Execute Cypher queries on Neo4j knowledge graph.

        Runs a suite of graph queries including entity lookups, relationship
        traversals, and network exploration.

        Args:
            state: Current state with parsed query intent.

        Returns:
            Updated state with raw graph data from Neo4j.
        """
        logger.info("Graph traversal: executing Neo4j queries")

        try:
            query = state.get("query", "")
            graph_results = await self._execute_graph_queries(query)

            current_analysis = state.get("graph_analysis") or {}
            current_analysis["raw_graph_data"] = graph_results
            state["graph_data"] = graph_results
            state["graph_analysis"] = current_analysis

            logger.info(
                "Graph traversal complete: %d nodes, %d relationships found",
                graph_results.get("total_nodes", 0),
                graph_results.get("total_relationships", 0),
            )

        except Exception as exc:
            logger.error("Graph traversal failed: %s", str(exc))
            current_analysis = state.get("graph_analysis") or {}
            current_analysis["raw_graph_data"] = {"nodes": [], "relationships": []}
            state["graph_analysis"] = current_analysis
            state["errors"] = state.get("errors", []) + [
                f"Graph traversal error: {str(exc)}"
            ]

        return state

    async def _relationship_analysis_node(self, state: AgentState) -> AgentState:
        """
        Node 3: Analyze entity relationships and criminal networks.

        Uses Gemini to interpret graph relationships and identify key
        connections, central figures, and network structures.

        Args:
            state: Current state with raw graph data.

        Returns:
            Updated state with relationship analysis in graph_analysis.
        """
        logger.info("Relationship analysis: analyzing criminal networks")

        try:
            current_analysis = state.get("graph_analysis") or {}
            graph_data = current_analysis.get("raw_graph_data", {})

            prompt = GraphPrompts.relationship_analysis_prompt(graph_data=graph_data)

            messages = [
                SystemMessage(content=GraphPrompts.SYSTEM_PROMPT),
                HumanMessage(content=prompt),
            ]

            response = await self.llm.ainvoke(messages)
            relationship_analysis = response.content

            current_analysis["relationship_analysis"] = relationship_analysis
            state["graph_analysis"] = current_analysis

            logger.info("Relationship analysis completed successfully")

        except Exception as exc:
            logger.error("Relationship analysis failed: %s", str(exc))
            current_analysis = state.get("graph_analysis") or {}
            current_analysis["relationship_analysis"] = (
                f"Relationship analysis unavailable: {str(exc)}"
            )
            state["graph_analysis"] = current_analysis

        return state

    async def _pattern_matching_node(self, state: AgentState) -> AgentState:
        """
        Node 4: Identify recurring patterns in the knowledge graph.

        Detects patterns such as crime clusters by location, repeat offender
        networks, common modus operandi chains, and temporal co-occurrences.

        Args:
            state: Current state with relationship analysis.

        Returns:
            Updated state with matched patterns in graph_analysis.
        """
        logger.info("Pattern matching: identifying graph patterns")

        try:
            current_analysis = state.get("graph_analysis") or {}

            prompt = GraphPrompts.pattern_matching_prompt(
                graph_data=current_analysis.get("raw_graph_data", {}),
                relationship_analysis=current_analysis.get("relationship_analysis", ""),
            )

            messages = [
                SystemMessage(content=GraphPrompts.SYSTEM_PROMPT),
                HumanMessage(content=prompt),
            ]

            response = await self.llm.ainvoke(messages)
            patterns = response.content

            current_analysis["patterns"] = patterns
            state["graph_analysis"] = current_analysis

            logger.info("Pattern matching completed successfully")

        except Exception as exc:
            logger.error("Pattern matching failed: %s", str(exc))
            current_analysis = state.get("graph_analysis") or {}
            current_analysis["patterns"] = f"Pattern matching unavailable: {str(exc)}"
            state["graph_analysis"] = current_analysis

        return state

    async def _insight_extraction_node(self, state: AgentState) -> AgentState:
        """
        Node 5: Generate comprehensive insights from graph analysis.

        Synthesizes all graph analysis results into actionable intelligence
        with recommendations for investigation or deployment.

        Args:
            state: Current state with all graph analysis data.

        Returns:
            Updated state with final insights in graph_analysis.
        """
        logger.info("Insight extraction: generating graph intelligence")

        try:
            current_analysis = state.get("graph_analysis") or {}
            query = state.get("query", "")

            prompt = GraphPrompts.insight_extraction_prompt(
                query=query,
                relationship_analysis=current_analysis.get("relationship_analysis", ""),
                patterns=current_analysis.get("patterns", ""),
            )

            messages = [
                SystemMessage(content=GraphPrompts.SYSTEM_PROMPT),
                HumanMessage(content=prompt),
            ]

            response = await self.llm.ainvoke(messages)
            insights = response.content

            current_analysis["insights"] = insights
            current_analysis["status"] = "completed"
            current_analysis["completed_at"] = datetime.utcnow().isoformat()
            state["graph_analysis"] = current_analysis

            logger.info("Insight extraction completed successfully")

        except Exception as exc:
            logger.error("Insight extraction failed: %s", str(exc))
            current_analysis = state.get("graph_analysis") or {}
            current_analysis["insights"] = f"Insights unavailable: {str(exc)}"
            current_analysis["status"] = "partial"
            state["graph_analysis"] = current_analysis

        return state

    async def _execute_graph_queries(self, query: str) -> dict[str, Any]:
        """
        Execute a suite of Neo4j Cypher queries for graph analysis.

        Args:
            query: User query for graph context.

        Returns:
            Dictionary containing nodes, relationships, and network statistics.
        """
        logger.debug("Executing Neo4j graph queries")

        try:
            from neo4j import AsyncGraphDatabase

            driver = AsyncGraphDatabase.driver(
                self.neo4j_uri,
                auth=(self.neo4j_user, self.neo4j_password),
            )
            try:
                async with driver.session() as session:
                    nodes = []
                    relationships = []

                    entity_result = await session.run(
                        """
                        MATCH (n)
                        WHERE ANY(prop IN keys(n) WHERE toString(n[prop]) CONTAINS $query)
                        RETURN n, labels(n) as labels
                        LIMIT 50
                        """,
                        query=query,
                    )
                    async for record in entity_result:
                        node_data = dict(record["n"])
                        node_data["_labels"] = record["labels"]
                        nodes.append(node_data)

                    if nodes:
                        network_result = await session.run(
                            """
                            MATCH (n)-[r]-(m)
                            WHERE ANY(prop IN keys(n) WHERE toString(n[prop]) CONTAINS $query)
                            RETURN n, type(r) as rel_type, properties(r) as rel_props, m,
                                   labels(n) as n_labels, labels(m) as m_labels
                            LIMIT 200
                            """,
                            query=query,
                        )
                        async for record in network_result:
                            relationships.append({
                                "source": dict(record["n"]),
                                "target": dict(record["m"]),
                                "type": record["rel_type"],
                                "properties": dict(record["rel_props"]) if record["rel_props"] else {},
                            })

                    unique_node_ids = set()
                    unique_nodes = []
                    for node in nodes:
                        node_id = str(node.get("id", id(node)))
                        if node_id not in unique_node_ids:
                            unique_node_ids.add(node_id)
                            unique_nodes.append(node)

                    return {
                        "nodes": unique_nodes,
                        "relationships": relationships,
                        "total_nodes": len(unique_nodes),
                        "total_relationships": len(relationships),
                    }
            finally:
                await driver.close()

        except Exception as exc:
            logger.warning("Neo4j graph query failed: %s", str(exc))
            return {
                "nodes": [],
                "relationships": [],
                "total_nodes": 0,
                "total_relationships": 0,
            }
