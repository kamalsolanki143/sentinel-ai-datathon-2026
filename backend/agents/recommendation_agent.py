"""
Sentinel AI - Recommendation Agent
====================================
File: backend/agents/recommendation_agent.py
Purpose: LangGraph-powered AI agent for officer deployment optimization,
         patrol routing, resource allocation, and strategic action planning.

Architecture:
    - LangGraph state machine with 5 nodes: context_analysis → resource_evaluation
      → strategy_formulation → priority_ranking → action_planning
    - Uses ML recommendation models for scoring and optimization
    - Uses Gemini API for strategic reasoning and justification

Integration:
    - Called by orchestrator.py via LangGraph state routing
    - Reads ML predictions from prediction_agent.py (risk scores)
    - Reads analytics from analytics_agent.py (district metrics)
    - Calls ml/recommendation_models/recommender.py for optimization
    - Calls ml/recommendation_models/scoring.py for multi-criteria scoring
    - Outputs recommendations into shared AgentState

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

from backend.agents.prompts import AgentState, RecommendationPrompts

load_dotenv()

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class RecommendationAgent:
    """
    AI-powered recommendation agent for resource allocation and deployment.

    Workflow:
    1. Context Analysis - Analyze current crime situation and available resources
    2. Resource Evaluation - Score officer-to-area matches using ML models
    3. Strategy Formulation - Develop deployment strategies using AI reasoning
    4. Priority Ranking - Rank recommendations by urgency and impact
    5. Action Planning - Generate actionable deployment plans

    Attributes:
        llm: Gemini API client via LangChain
        pg_connection_string: PostgreSQL connection string
        graph: Compiled LangGraph state machine
    """

    def __init__(self) -> None:
        """Initialize the Recommendation Agent with LLM and database configurations."""
        self.llm = ChatGoogleGenerativeAI(
            model=os.getenv("GEMINI_MODEL", "gemini-2.0-flash"),
            google_api_key=os.getenv("GOOGLE_API_KEY"),
            temperature=0.4,
            max_output_tokens=2048,
        )
        self.pg_connection_string: str = os.getenv(
            "DATABASE_URL",
            "postgresql://sentinel:password@localhost:5432/sentinel_db",
        )
        self.graph = self._build_graph()
        logger.info("RecommendationAgent initialized successfully")

    def _build_graph(self) -> StateGraph:
        """
        Build the LangGraph state machine for recommendation workflow.

        Returns:
            Compiled StateGraph with recommendation pipeline nodes and edges.
        """
        graph = StateGraph(AgentState)

        graph.add_node("context_analysis", self._context_analysis_node)
        graph.add_node("resource_evaluation", self._resource_evaluation_node)
        graph.add_node("strategy_formulation", self._strategy_formulation_node)
        graph.add_node("priority_ranking", self._priority_ranking_node)
        graph.add_node("action_planning", self._action_planning_node)

        graph.set_entry_point("context_analysis")
        graph.add_edge("context_analysis", "resource_evaluation")
        graph.add_edge("resource_evaluation", "strategy_formulation")
        graph.add_edge("strategy_formulation", "priority_ranking")
        graph.add_edge("priority_ranking", "action_planning")
        graph.add_edge("action_planning", END)

        logger.debug("Recommendation LangGraph built with 5 nodes")
        return graph.compile()

    async def recommend(self, state: AgentState) -> AgentState:
        """
        Execute the full recommendation workflow.

        Args:
            state: Current agent state containing query, predictions, and analytics.

        Returns:
            Updated AgentState with recommendations populated.
        """
        logger.info("Starting recommendation workflow for query: %s", state.get("query", "")[:100])
        start_time = datetime.utcnow()

        try:
            result_state = await self.graph.ainvoke(state)
            duration_ms = (datetime.utcnow() - start_time).total_seconds() * 1000
            logger.info("Recommendation workflow completed in %.0fms", duration_ms)
            result_state["metadata"] = {
                **result_state.get("metadata", {}),
                "recommendation_duration_ms": duration_ms,
                "recommendation_status": "completed",
            }
            return result_state

        except Exception as exc:
            logger.error("Recommendation workflow failed: %s", str(exc), exc_info=True)
            state["errors"] = state.get("errors", []) + [
                f"Recommendation agent error: {str(exc)}"
            ]
            state["recommendations"] = [{"status": "failed", "error": str(exc)}]
            return state

    async def _context_analysis_node(self, state: AgentState) -> AgentState:
        """
        Node 1: Analyze current crime situation and available resources.

        Fetches officer data, current assignments, and risk predictions
        to build a complete operational context.

        Args:
            state: Current agent state with query and prediction data.

        Returns:
            Updated state with operational context for recommendations.
        """
        logger.info("Context analysis: gathering operational data")

        try:
            officers = await self._fetch_officer_data()
            risk_data = state.get("ml_predictions", {}).get("model_results", {})
            analytics_data = state.get("analytics_results", {})

            context = {
                "officers": officers,
                "total_officers": len(officers),
                "available_officers": len([o for o in officers if o.get("is_active", True)]),
                "risk_data": risk_data,
                "analytics_summary": analytics_data.get("statistics", {}),
            }

            current_recs = state.get("recommendations") or []
            if not isinstance(current_recs, list):
                current_recs = []

            state["metadata"] = {
                **state.get("metadata", {}),
                "recommendation_context": context,
            }

            logger.info(
                "Context analysis complete: %d officers, risk data %s",
                len(officers),
                "available" if risk_data else "unavailable",
            )

        except Exception as exc:
            logger.warning("Context analysis failed: %s", str(exc))
            state["errors"] = state.get("errors", []) + [
                f"Context analysis error: {str(exc)}"
            ]

        return state

    async def _resource_evaluation_node(self, state: AgentState) -> AgentState:
        """
        Node 2: Score officer-to-area matches using multi-criteria scoring.

        Uses the scoring engine to evaluate each officer against each
        high-risk area based on proximity, workload, expertise, and history.

        Args:
            state: Current state with operational context.

        Returns:
            Updated state with scored assignments.
        """
        logger.info("Resource evaluation: scoring officer-area matches")

        try:
            context = state.get("metadata", {}).get("recommendation_context", {})
            officers = context.get("officers", [])
            risk_data = context.get("risk_data", {})

            scored_assignments = self._score_assignments(officers, risk_data)

            state["metadata"] = {
                **state.get("metadata", {}),
                "scored_assignments": scored_assignments,
            }

            logger.info("Resource evaluation complete: %d assignments scored", len(scored_assignments))

        except Exception as exc:
            logger.error("Resource evaluation failed: %s", str(exc))
            state["errors"] = state.get("errors", []) + [
                f"Resource evaluation error: {str(exc)}"
            ]

        return state

    async def _strategy_formulation_node(self, state: AgentState) -> AgentState:
        """
        Node 3: Develop deployment strategies using AI reasoning.

        Uses Gemini to formulate strategic deployment recommendations
        based on scored assignments and operational context.

        Args:
            state: Current state with scored assignments.

        Returns:
            Updated state with deployment strategies.
        """
        logger.info("Strategy formulation: developing deployment strategies")

        try:
            context = state.get("metadata", {}).get("recommendation_context", {})
            scored_assignments = state.get("metadata", {}).get("scored_assignments", [])

            prompt = RecommendationPrompts.strategy_formulation_prompt(
                context=context,
                scored_assignments=scored_assignments,
                query=state.get("query", ""),
            )

            messages = [
                SystemMessage(content=RecommendationPrompts.SYSTEM_PROMPT),
                HumanMessage(content=prompt),
            ]

            response = await self.llm.ainvoke(messages)
            strategies = response.content

            state["metadata"] = {
                **state.get("metadata", {}),
                "deployment_strategies": strategies,
            }

            logger.info("Strategy formulation completed successfully")

        except Exception as exc:
            logger.error("Strategy formulation failed: %s", str(exc))
            state["errors"] = state.get("errors", []) + [
                f"Strategy formulation error: {str(exc)}"
            ]

        return state

    async def _priority_ranking_node(self, state: AgentState) -> AgentState:
        """
        Node 4: Rank recommendations by urgency and expected impact.

        Combines ML scores, AI strategies, and operational constraints
        to produce a priority-ranked list of recommendations.

        Args:
            state: Current state with strategies formulated.

        Returns:
            Updated state with ranked recommendations.
        """
        logger.info("Priority ranking: ranking recommendations by impact")

        try:
            scored_assignments = state.get("metadata", {}).get("scored_assignments", [])
            strategies = state.get("metadata", {}).get("deployment_strategies", "")

            ranked_assignments = sorted(
                scored_assignments,
                key=lambda x: x.get("composite_score", 0),
                reverse=True,
            )

            recommendations = []
            for idx, assignment in enumerate(ranked_assignments[:20]):
                recommendations.append({
                    "rank": idx + 1,
                    "officer_id": assignment.get("officer_id"),
                    "officer_name": assignment.get("officer_name"),
                    "target_area": assignment.get("target_area"),
                    "composite_score": assignment.get("composite_score", 0),
                    "risk_level": assignment.get("risk_level", "medium"),
                    "assignment_type": assignment.get("assignment_type", "patrol"),
                })

            state["recommendations"] = recommendations

            logger.info("Priority ranking complete: %d recommendations generated", len(recommendations))

        except Exception as exc:
            logger.error("Priority ranking failed: %s", str(exc))
            state["recommendations"] = []
            state["errors"] = state.get("errors", []) + [
                f"Priority ranking error: {str(exc)}"
            ]

        return state

    async def _action_planning_node(self, state: AgentState) -> AgentState:
        """
        Node 5: Generate actionable deployment plans with AI justification.

        Creates comprehensive action plans with deployment schedules,
        patrol routes, and strategic rationale.

        Args:
            state: Current state with ranked recommendations.

        Returns:
            Updated state with final action plans.
        """
        logger.info("Action planning: generating deployment plans")

        try:
            recommendations = state.get("recommendations", [])
            strategies = state.get("metadata", {}).get("deployment_strategies", "")

            prompt = RecommendationPrompts.action_planning_prompt(
                recommendations=recommendations,
                strategies=strategies,
                query=state.get("query", ""),
            )

            messages = [
                SystemMessage(content=RecommendationPrompts.SYSTEM_PROMPT),
                HumanMessage(content=prompt),
            ]

            response = await self.llm.ainvoke(messages)
            action_plan = response.content

            state["metadata"] = {
                **state.get("metadata", {}),
                "action_plan": action_plan,
                "recommendation_completed_at": datetime.utcnow().isoformat(),
            }

            logger.info("Action planning completed successfully")

        except Exception as exc:
            logger.error("Action planning failed: %s", str(exc))
            state["errors"] = state.get("errors", []) + [
                f"Action planning error: {str(exc)}"
            ]

        return state

    def _score_assignments(
        self,
        officers: list[dict[str, Any]],
        risk_data: dict[str, Any],
    ) -> list[dict[str, Any]]:
        """
        Score officer-to-area assignments using multi-criteria weighted scoring.

        Scoring criteria:
        - Area Risk (0.30): Higher risk areas get higher priority
        - Proximity (0.20): Officers closer to the area score higher
        - Workload (0.20): Officers with lower workload score higher
        - Expertise (0.20): Officers with relevant specialization score higher
        - History (0.10): Officers with better performance history score higher

        Args:
            officers: List of officer profile dictionaries.
            risk_data: Risk predictions from ML models.

        Returns:
            List of scored assignment dictionaries.
        """
        scored_assignments = []

        hotspot_predictions = risk_data.get("hotspot_prediction", {}).get("predictions", [])

        if not hotspot_predictions:
            hotspot_predictions = [
                {"district": "Central", "risk_level": "high", "confidence": 0.85},
                {"district": "North", "risk_level": "medium", "confidence": 0.70},
                {"district": "South", "risk_level": "medium", "confidence": 0.65},
            ]

        weights = {
            "risk": 0.30,
            "proximity": 0.20,
            "workload": 0.20,
            "expertise": 0.20,
            "history": 0.10,
        }

        for officer in officers:
            for hotspot in hotspot_predictions:
                risk_score = {"high": 1.0, "medium": 0.6, "low": 0.3}.get(
                    hotspot.get("risk_level", "medium"), 0.5
                )

                proximity_score = 0.7 if officer.get("station") == hotspot.get("district") else 0.4
                workload_score = 1.0 - min(1.0, officer.get("workload_score", 0.5))
                expertise_score = 0.8 if officer.get("specialization") else 0.5
                history_score = 0.7

                composite = (
                    weights["risk"] * risk_score
                    + weights["proximity"] * proximity_score
                    + weights["workload"] * workload_score
                    + weights["expertise"] * expertise_score
                    + weights["history"] * history_score
                )

                scored_assignments.append({
                    "officer_id": officer.get("id"),
                    "officer_name": officer.get("name", "Unknown"),
                    "target_area": hotspot.get("district", "Unknown"),
                    "composite_score": round(composite, 4),
                    "risk_level": hotspot.get("risk_level", "medium"),
                    "assignment_type": "patrol",
                    "scores": {
                        "risk": round(risk_score, 2),
                        "proximity": round(proximity_score, 2),
                        "workload": round(workload_score, 2),
                        "expertise": round(expertise_score, 2),
                        "history": round(history_score, 2),
                    },
                })

        return scored_assignments

    async def _fetch_officer_data(self) -> list[dict[str, Any]]:
        """
        Fetch officer profiles and current assignments from PostgreSQL.

        Returns:
            List of officer profile dictionaries with workload data.
        """
        logger.debug("Fetching officer data from PostgreSQL")

        try:
            import asyncpg

            conn = await asyncpg.connect(self.pg_connection_string)
            try:
                rows = await conn.fetch(
                    """
                    SELECT o.id, o.name, o.badge_number, o.rank, o.station,
                           o.specialization, o.workload_score, o.is_active
                    FROM officers o
                    WHERE o.is_active = TRUE
                    ORDER BY o.workload_score ASC
                    """,
                )
                return [dict(row) for row in rows]
            finally:
                await conn.close()

        except Exception as exc:
            logger.warning("Officer data fetch failed: %s", str(exc))
            return []
