"""
Sentinel AI - Orchestrator
===========================
File: backend/agents/orchestrator.py
Purpose: Master LangGraph workflow that coordinates all 7 specialist AI agents.
         Handles intent classification, dynamic agent routing, parallel execution,
         result aggregation, and final response generation.

Architecture:
    - Central LangGraph state machine with conditional routing edges
    - Intent classification using Gemini API to determine target agent(s)
    - Supports single-agent and multi-agent parallel execution
    - Result aggregation and final response generation
    - Error recovery and graceful degradation

Integration:
    - Entry point for all AI operations from FastAPI route handlers
    - Routes to: InvestigationAgent, AnalyticsAgent, PredictionAgent,
      GraphAgent, RecommendationAgent, ReportAgent, SimulationAgent
    - Manages shared AgentState across all agents
    - Called from backend/api/chat.py and other API endpoints

Dependencies:
    - langchain-google-genai
    - langgraph
    - python-dotenv
    - All specialist agent modules
"""

import logging
import os
from datetime import datetime
from typing import Any, Optional

from dotenv import load_dotenv
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.graph import END, StateGraph

from backend.agents.prompts import AgentState, OrchestratorPrompts
from backend.agents.investigation_agent import InvestigationAgent
from backend.agents.analytics_agent import AnalyticsAgent
from backend.agents.prediction_agent import PredictionAgent
from backend.agents.graph_agent import GraphAgent
from backend.agents.recommendation_agent import RecommendationAgent
from backend.agents.report_agent import ReportAgent
from backend.agents.simulation_agent import SimulationAgent

load_dotenv()

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

VALID_INTENTS = [
    "investigation",
    "analytics",
    "prediction",
    "graph_query",
    "recommendation",
    "simulation",
    "report",
    "general",
]


class Orchestrator:
    """
    Master orchestrator that coordinates all Sentinel AI specialist agents.

    The orchestrator follows a 4-step workflow:
    1. Intent Classification - Determine user intent using Gemini
    2. Agent Routing - Route to appropriate specialist agent(s)
    3. Result Aggregation - Merge outputs from specialist agents
    4. Response Generation - Generate final user-facing response

    The orchestrator supports both single-agent and multi-agent execution,
    dynamically routing based on query complexity.

    Attributes:
        llm: Gemini API client for intent classification and response generation
        investigation_agent: Specialist agent for crime investigation
        analytics_agent: Specialist agent for statistical analysis
        prediction_agent: Specialist agent for ML predictions
        graph_agent: Specialist agent for knowledge graph operations
        recommendation_agent: Specialist agent for resource allocation
        report_agent: Specialist agent for report generation
        simulation_agent: Specialist agent for crime simulation
        graph: Compiled LangGraph state machine
    """

    def __init__(self) -> None:
        """Initialize the Orchestrator with all specialist agents and LLM."""
        self.llm = ChatGoogleGenerativeAI(
            model=os.getenv("GEMINI_MODEL", "gemini-2.0-flash"),
            google_api_key=os.getenv("GOOGLE_API_KEY"),
            temperature=0.1,
            max_output_tokens=1024,
        )

        self.investigation_agent = InvestigationAgent()
        self.analytics_agent = AnalyticsAgent()
        self.prediction_agent = PredictionAgent()
        self.graph_agent = GraphAgent()
        self.recommendation_agent = RecommendationAgent()
        self.report_agent = ReportAgent()
        self.simulation_agent = SimulationAgent()

        self.graph = self._build_graph()
        logger.info("Orchestrator initialized with all 7 specialist agents")

    def _build_graph(self) -> StateGraph:
        """
        Build the master LangGraph state machine for agent orchestration.

        The graph has conditional routing from intent classification to
        specialist agents, followed by aggregation and response generation.

        Returns:
            Compiled StateGraph for the orchestration workflow.
        """
        graph = StateGraph(AgentState)

        graph.add_node("classify_intent", self._classify_intent_node)
        graph.add_node("investigation", self._investigation_node)
        graph.add_node("analytics", self._analytics_node)
        graph.add_node("prediction", self._prediction_node)
        graph.add_node("graph_query", self._graph_query_node)
        graph.add_node("recommendation", self._recommendation_node)
        graph.add_node("report", self._report_node)
        graph.add_node("simulation", self._simulation_node)
        graph.add_node("general", self._general_node)
        graph.add_node("aggregate_results", self._aggregate_results_node)
        graph.add_node("generate_response", self._generate_response_node)

        graph.set_entry_point("classify_intent")

        graph.add_conditional_edges(
            "classify_intent",
            self._route_to_agent,
            {
                "investigation": "investigation",
                "analytics": "analytics",
                "prediction": "prediction",
                "graph_query": "graph_query",
                "recommendation": "recommendation",
                "report": "report",
                "simulation": "simulation",
                "general": "general",
            },
        )

        for agent_node in [
            "investigation", "analytics", "prediction", "graph_query",
            "recommendation", "report", "simulation", "general",
        ]:
            graph.add_edge(agent_node, "aggregate_results")

        graph.add_edge("aggregate_results", "generate_response")
        graph.add_edge("generate_response", END)

        logger.debug("Orchestrator LangGraph built with conditional routing to 8 agent nodes")
        return graph.compile()

    async def process_query(self, query: str, session_id: Optional[str] = None) -> dict[str, Any]:
        """
        Process a user query through the full orchestration pipeline.

        This is the primary entry point called by FastAPI route handlers.

        Args:
            query: User's natural language query.
            session_id: Optional session identifier for conversation tracking.

        Returns:
            Dictionary containing the response, metadata, and any errors.
        """
        logger.info("Processing query: %s", query[:100])
        start_time = datetime.utcnow()

        initial_state: AgentState = {
            "messages": [],
            "query": query,
            "intent": "",
            "target_agents": [],
            "crime_data": None,
            "graph_data": None,
            "investigation_results": None,
            "analytics_results": None,
            "ml_predictions": None,
            "graph_analysis": None,
            "recommendations": None,
            "simulation_results": None,
            "report_data": None,
            "final_response": None,
            "errors": [],
            "metadata": {
                "session_id": session_id,
                "query_received_at": start_time.isoformat(),
            },
        }

        try:
            result_state = await self.graph.ainvoke(initial_state)
            duration_ms = (datetime.utcnow() - start_time).total_seconds() * 1000

            response = {
                "response": result_state.get("final_response", "No response generated."),
                "intent": result_state.get("intent", "unknown"),
                "metadata": {
                    **result_state.get("metadata", {}),
                    "total_duration_ms": duration_ms,
                    "session_id": session_id,
                },
                "errors": result_state.get("errors", []),
            }

            if result_state.get("investigation_results"):
                response["investigation_results"] = result_state["investigation_results"]
            if result_state.get("analytics_results"):
                response["analytics_results"] = result_state["analytics_results"]
            if result_state.get("ml_predictions"):
                response["predictions"] = result_state["ml_predictions"]
            if result_state.get("graph_analysis"):
                response["graph_analysis"] = result_state["graph_analysis"]
            if result_state.get("recommendations"):
                response["recommendations"] = result_state["recommendations"]
            if result_state.get("simulation_results"):
                response["simulation_results"] = result_state["simulation_results"]
            if result_state.get("report_data"):
                response["report_data"] = result_state["report_data"]

            logger.info(
                "Query processed in %.0fms, intent=%s, errors=%d",
                duration_ms,
                result_state.get("intent", "unknown"),
                len(result_state.get("errors", [])),
            )

            return response

        except Exception as exc:
            duration_ms = (datetime.utcnow() - start_time).total_seconds() * 1000
            logger.error("Orchestrator failed: %s", str(exc), exc_info=True)
            return {
                "response": f"I encountered an error processing your request. Please try again. Error: {str(exc)}",
                "intent": "error",
                "metadata": {"total_duration_ms": duration_ms, "session_id": session_id},
                "errors": [str(exc)],
            }

    async def _classify_intent_node(self, state: AgentState) -> AgentState:
        """
        Node: Classify the user's intent to determine which agent to invoke.

        Uses Gemini with a low temperature for deterministic classification
        into one of the defined intent categories.

        Args:
            state: Initial agent state with user query.

        Returns:
            Updated state with classified intent.
        """
        logger.info("Intent classification: analyzing query")

        try:
            query = state.get("query", "")

            prompt = OrchestratorPrompts.intent_classification_prompt(query=query)

            messages = [
                SystemMessage(content=OrchestratorPrompts.SYSTEM_PROMPT),
                HumanMessage(content=prompt),
            ]

            response = await self.llm.ainvoke(messages)
            raw_intent = response.content.strip().lower()

            intent = self._parse_intent(raw_intent)

            state["intent"] = intent
            state["target_agents"] = [intent]

            logger.info("Intent classified as: %s (raw: %s)", intent, raw_intent[:50])

        except Exception as exc:
            logger.error("Intent classification failed: %s", str(exc))
            state["intent"] = "general"
            state["target_agents"] = ["general"]
            state["errors"] = state.get("errors", []) + [
                f"Intent classification error: {str(exc)}"
            ]

        return state

    def _route_to_agent(self, state: AgentState) -> str:
        """
        Routing function for conditional edges in LangGraph.

        Determines which agent node to execute based on the classified intent.

        Args:
            state: Current state with intent classified.

        Returns:
            String key of the target agent node.
        """
        intent = state.get("intent", "general")
        logger.debug("Routing to agent: %s", intent)

        if intent in VALID_INTENTS:
            return intent
        return "general"

    async def _investigation_node(self, state: AgentState) -> AgentState:
        """Route to the Investigation Agent."""
        logger.info("Executing investigation agent")
        return await self.investigation_agent.investigate(state)

    async def _analytics_node(self, state: AgentState) -> AgentState:
        """Route to the Analytics Agent."""
        logger.info("Executing analytics agent")
        return await self.analytics_agent.analyze(state)

    async def _prediction_node(self, state: AgentState) -> AgentState:
        """Route to the Prediction Agent."""
        logger.info("Executing prediction agent")
        return await self.prediction_agent.predict(state)

    async def _graph_query_node(self, state: AgentState) -> AgentState:
        """Route to the Graph Agent."""
        logger.info("Executing graph agent")
        return await self.graph_agent.analyze_graph(state)

    async def _recommendation_node(self, state: AgentState) -> AgentState:
        """Route to the Recommendation Agent."""
        logger.info("Executing recommendation agent")
        return await self.recommendation_agent.recommend(state)

    async def _report_node(self, state: AgentState) -> AgentState:
        """Route to the Report Agent."""
        logger.info("Executing report agent")
        return await self.report_agent.generate_report(state)

    async def _simulation_node(self, state: AgentState) -> AgentState:
        """Route to the Simulation Agent."""
        logger.info("Executing simulation agent")
        return await self.simulation_agent.simulate(state)

    async def _general_node(self, state: AgentState) -> AgentState:
        """
        Handle general queries that don't map to a specific agent.

        Uses Gemini directly to answer general crime intelligence questions.

        Args:
            state: Current state with query.

        Returns:
            Updated state with general response.
        """
        logger.info("Handling general query")

        try:
            query = state.get("query", "")

            messages = [
                SystemMessage(content=OrchestratorPrompts.GENERAL_SYSTEM_PROMPT),
                HumanMessage(content=query),
            ]

            response = await self.llm.ainvoke(messages)
            state["final_response"] = response.content

        except Exception as exc:
            logger.error("General query handling failed: %s", str(exc))
            state["final_response"] = (
                "I'm sorry, I couldn't process your request at this time. "
                "Please try rephrasing your query."
            )
            state["errors"] = state.get("errors", []) + [
                f"General handler error: {str(exc)}"
            ]

        return state

    async def _aggregate_results_node(self, state: AgentState) -> AgentState:
        """
        Aggregate results from all executed specialist agents.

        Merges outputs, collects errors, and prepares unified data
        for response generation.

        Args:
            state: Current state with specialist agent results.

        Returns:
            Updated state with aggregated results.
        """
        logger.info("Aggregating results from specialist agents")

        completed_agents = []
        failed_agents = []

        agent_result_keys = {
            "investigation": "investigation_results",
            "analytics": "analytics_results",
            "prediction": "ml_predictions",
            "graph_query": "graph_analysis",
            "recommendation": "recommendations",
            "report": "report_data",
            "simulation": "simulation_results",
        }

        intent = state.get("intent", "general")
        if intent in agent_result_keys:
            result_key = agent_result_keys[intent]
            result = state.get(result_key)
            if result and not (isinstance(result, dict) and result.get("status") == "failed"):
                completed_agents.append(intent)
            elif result:
                failed_agents.append(intent)

        state["metadata"] = {
            **state.get("metadata", {}),
            "completed_agents": completed_agents,
            "failed_agents": failed_agents,
            "aggregation_timestamp": datetime.utcnow().isoformat(),
        }

        logger.info(
            "Aggregation complete: %d agents succeeded, %d failed",
            len(completed_agents),
            len(failed_agents),
        )

        return state

    async def _generate_response_node(self, state: AgentState) -> AgentState:
        """
        Generate the final user-facing response from aggregated agent results.

        If a final_response is already set (by general handler), use it.
        Otherwise, synthesize a response from specialist agent outputs.

        Args:
            state: Current state with aggregated results.

        Returns:
            Updated state with final_response set.
        """
        if state.get("final_response"):
            logger.info("Using pre-set final response")
            return state

        logger.info("Generating final response from agent results")

        try:
            intent = state.get("intent", "general")

            result_summaries = []

            if state.get("investigation_results"):
                inv = state["investigation_results"]
                if isinstance(inv, dict):
                    result_summaries.append(
                        f"Investigation: {inv.get('conclusion', inv.get('status', 'completed'))}"
                    )

            if state.get("analytics_results"):
                ana = state["analytics_results"]
                if isinstance(ana, dict):
                    result_summaries.append(
                        f"Analytics: {ana.get('insights', ana.get('status', 'completed'))}"
                    )

            if state.get("ml_predictions"):
                pred = state["ml_predictions"]
                if isinstance(pred, dict):
                    result_summaries.append(
                        f"Predictions: {pred.get('risk_assessment', pred.get('status', 'completed'))}"
                    )

            if state.get("graph_analysis"):
                graph = state["graph_analysis"]
                if isinstance(graph, dict):
                    result_summaries.append(
                        f"Graph Analysis: {graph.get('insights', graph.get('status', 'completed'))}"
                    )

            if state.get("recommendations"):
                recs = state["recommendations"]
                if isinstance(recs, list) and recs:
                    result_summaries.append(
                        f"Recommendations: {len(recs)} officer deployment recommendations generated"
                    )

            if state.get("simulation_results"):
                sim = state["simulation_results"]
                if isinstance(sim, dict):
                    result_summaries.append(
                        f"Simulation: {sim.get('recommendations', sim.get('status', 'completed'))}"
                    )

            if state.get("report_data"):
                rep = state["report_data"]
                if isinstance(rep, dict):
                    result_summaries.append(
                        f"Report: {rep.get('status', 'generated')}"
                    )

            if result_summaries:
                combined_results = "\n\n".join(result_summaries)

                prompt = OrchestratorPrompts.response_generation_prompt(
                    query=state.get("query", ""),
                    intent=intent,
                    results=combined_results,
                )

                messages = [
                    SystemMessage(content=OrchestratorPrompts.RESPONSE_SYSTEM_PROMPT),
                    HumanMessage(content=prompt),
                ]

                response = await self.llm.ainvoke(messages)
                state["final_response"] = response.content
            else:
                state["final_response"] = (
                    "I processed your request but couldn't generate specific results. "
                    "Please try rephrasing your query with more details."
                )

        except Exception as exc:
            logger.error("Response generation failed: %s", str(exc))
            state["final_response"] = (
                "I've completed the analysis but encountered an issue formatting the response. "
                "The detailed results are available in the response data."
            )

        return state

    def _parse_intent(self, raw_intent: str) -> str:
        """
        Parse and normalize the raw intent string from LLM output.

        Handles cases where the LLM returns extra text around the intent.

        Args:
            raw_intent: Raw LLM output for intent classification.

        Returns:
            Normalized intent string matching a valid intent category.
        """
        clean_intent = raw_intent.strip().lower().replace('"', "").replace("'", "")

        for valid_intent in VALID_INTENTS:
            if valid_intent in clean_intent:
                return valid_intent

        intent_mapping = {
            "investigate": "investigation",
            "analyze": "analytics",
            "analysis": "analytics",
            "statistics": "analytics",
            "stats": "analytics",
            "predict": "prediction",
            "forecast": "prediction",
            "hotspot": "prediction",
            "anomaly": "prediction",
            "graph": "graph_query",
            "network": "graph_query",
            "relationship": "graph_query",
            "suspect": "graph_query",
            "recommend": "recommendation",
            "deploy": "recommendation",
            "officer": "recommendation",
            "patrol": "recommendation",
            "allocate": "recommendation",
            "simulate": "simulation",
            "what if": "simulation",
            "scenario": "simulation",
            "impact": "simulation",
            "report": "report",
            "summary": "report",
            "generate report": "report",
        }

        for keyword, mapped_intent in intent_mapping.items():
            if keyword in clean_intent:
                return mapped_intent

        return "general"
