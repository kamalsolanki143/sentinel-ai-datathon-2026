"""
Sentinel AI - Simulation Agent
===============================
File: backend/agents/simulation_agent.py
Purpose: LangGraph-powered AI agent for crime simulation, what-if analysis,
         Monte Carlo modeling, and patrol impact assessment.

Architecture:
    - LangGraph state machine with 5 nodes: scenario_definition →
      parameter_configuration → simulation_execution → outcome_analysis
      → recommendation_synthesis
    - Implements Monte Carlo simulation for stochastic crime modeling
    - Uses Gemini API for scenario interpretation and strategic recommendations

Integration:
    - Called by orchestrator.py via LangGraph state routing
    - Uses ML predictions as baseline for simulations
    - Reads historical crime data from PostgreSQL
    - Outputs simulation_results into shared AgentState
    - Results consumed by recommendation_agent.py and report_agent.py

Dependencies:
    - langchain-google-genai
    - langgraph
    - asyncpg
    - numpy
    - python-dotenv
"""

import logging
import os
import random
from datetime import datetime
from typing import Any, Optional

import numpy as np
from dotenv import load_dotenv
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.graph import END, StateGraph

from backend.agents.prompts import AgentState, SimulationPrompts

load_dotenv()

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class SimulationAgent:
    """
    AI-powered simulation agent for crime scenario modeling.

    Workflow:
    1. Scenario Definition - Parse and validate scenario parameters
    2. Parameter Configuration - Configure simulation variables
    3. Simulation Execution - Run Monte Carlo simulation iterations
    4. Outcome Analysis - Analyze and aggregate simulation results
    5. Recommendation Synthesis - Generate strategic recommendations

    Attributes:
        llm: Gemini API client via LangChain
        pg_connection_string: PostgreSQL connection string
        default_iterations: Default number of Monte Carlo iterations
        graph: Compiled LangGraph state machine
    """

    def __init__(self) -> None:
        """Initialize the Simulation Agent with LLM and simulation configurations."""
        self.llm = ChatGoogleGenerativeAI(
            model=os.getenv("GEMINI_MODEL", "gemini-2.0-flash"),
            google_api_key=os.getenv("GOOGLE_API_KEY"),
            temperature=0.6,
            max_output_tokens=4096,
        )
        self.pg_connection_string: str = os.getenv(
            "DATABASE_URL",
            "postgresql://sentinel:password@localhost:5432/sentinel_db",
        )
        self.default_iterations: int = int(os.getenv("SIMULATION_ITERATIONS", "100"))
        self.graph = self._build_graph()
        logger.info("SimulationAgent initialized with %d default iterations", self.default_iterations)

    def _build_graph(self) -> StateGraph:
        """
        Build the LangGraph state machine for simulation workflow.

        Returns:
            Compiled StateGraph with simulation pipeline nodes and edges.
        """
        graph = StateGraph(AgentState)

        graph.add_node("scenario_definition", self._scenario_definition_node)
        graph.add_node("parameter_configuration", self._parameter_configuration_node)
        graph.add_node("simulation_execution", self._simulation_execution_node)
        graph.add_node("outcome_analysis", self._outcome_analysis_node)
        graph.add_node("recommendation_synthesis", self._recommendation_synthesis_node)

        graph.set_entry_point("scenario_definition")
        graph.add_edge("scenario_definition", "parameter_configuration")
        graph.add_edge("parameter_configuration", "simulation_execution")
        graph.add_edge("simulation_execution", "outcome_analysis")
        graph.add_edge("outcome_analysis", "recommendation_synthesis")
        graph.add_edge("recommendation_synthesis", END)

        logger.debug("Simulation LangGraph built with 5 nodes")
        return graph.compile()

    async def simulate(self, state: AgentState) -> AgentState:
        """
        Execute the full simulation workflow.

        Args:
            state: Current agent state containing query and context.

        Returns:
            Updated AgentState with simulation_results populated.
        """
        logger.info("Starting simulation workflow for query: %s", state.get("query", "")[:100])
        start_time = datetime.utcnow()

        try:
            result_state = await self.graph.ainvoke(state)
            duration_ms = (datetime.utcnow() - start_time).total_seconds() * 1000
            logger.info("Simulation workflow completed in %.0fms", duration_ms)
            result_state["metadata"] = {
                **result_state.get("metadata", {}),
                "simulation_duration_ms": duration_ms,
                "simulation_status": "completed",
            }
            return result_state

        except Exception as exc:
            logger.error("Simulation workflow failed: %s", str(exc), exc_info=True)
            state["errors"] = state.get("errors", []) + [
                f"Simulation agent error: {str(exc)}"
            ]
            state["simulation_results"] = {"status": "failed", "error": str(exc)}
            return state

    async def _scenario_definition_node(self, state: AgentState) -> AgentState:
        """
        Node 1: Parse and validate simulation scenario parameters.

        Uses Gemini to interpret the natural language scenario description
        and extract structured simulation parameters.

        Args:
            state: Current agent state with query describing the scenario.

        Returns:
            Updated state with parsed scenario definition.
        """
        logger.info("Scenario definition: parsing simulation parameters")

        try:
            query = state.get("query", "")

            prompt = SimulationPrompts.scenario_definition_prompt(query=query)

            messages = [
                SystemMessage(content=SimulationPrompts.SYSTEM_PROMPT),
                HumanMessage(content=prompt),
            ]

            response = await self.llm.ainvoke(messages)
            scenario_definition = response.content

            baseline_data = await self._fetch_baseline_data()

            current_results = state.get("simulation_results") or {}
            current_results["scenario_definition"] = scenario_definition
            current_results["baseline_data"] = baseline_data
            state["simulation_results"] = current_results

            logger.info("Scenario definition completed: baseline has %d records", len(baseline_data))

        except Exception as exc:
            logger.error("Scenario definition failed: %s", str(exc))
            current_results = state.get("simulation_results") or {}
            current_results["scenario_definition"] = f"Scenario parsing error: {str(exc)}"
            state["simulation_results"] = current_results
            state["errors"] = state.get("errors", []) + [
                f"Scenario definition error: {str(exc)}"
            ]

        return state

    async def _parameter_configuration_node(self, state: AgentState) -> AgentState:
        """
        Node 2: Configure simulation variables from parsed scenario.

        Sets up the mathematical parameters for the Monte Carlo simulation
        including distributions, bounds, and control variables.

        Args:
            state: Current state with scenario definition.

        Returns:
            Updated state with simulation parameters configured.
        """
        logger.info("Parameter configuration: setting simulation variables")

        try:
            query = state.get("query", "").lower()
            current_results = state.get("simulation_results") or {}
            baseline_data = current_results.get("baseline_data", [])

            total_baseline_crimes = len(baseline_data)
            daily_baseline = total_baseline_crimes / 90 if total_baseline_crimes > 0 else 5.0

            parameters = {
                "iterations": self.default_iterations,
                "baseline_daily_crimes": round(daily_baseline, 2),
                "simulation_days": 30,
                "confidence_level": 0.95,
                "random_seed": 42,
            }

            if "officer" in query or "patrol" in query:
                parameters["scenario_type"] = "resource_reallocation"
                parameters["officer_delta"] = self._extract_number(query, default=10)
                parameters["impact_factor"] = -0.05
            elif "cctv" in query or "camera" in query or "surveillance" in query:
                parameters["scenario_type"] = "surveillance_increase"
                parameters["coverage_increase"] = 0.20
                parameters["impact_factor"] = -0.08
            elif "community" in query or "awareness" in query:
                parameters["scenario_type"] = "community_intervention"
                parameters["program_coverage"] = 0.30
                parameters["impact_factor"] = -0.03
            else:
                parameters["scenario_type"] = "general_intervention"
                parameters["impact_factor"] = -0.05

            current_results["parameters"] = parameters
            state["simulation_results"] = current_results

            logger.info(
                "Parameters configured: type=%s, iterations=%d, baseline=%.1f crimes/day",
                parameters["scenario_type"],
                parameters["iterations"],
                parameters["baseline_daily_crimes"],
            )

        except Exception as exc:
            logger.error("Parameter configuration failed: %s", str(exc))
            state["errors"] = state.get("errors", []) + [
                f"Parameter configuration error: {str(exc)}"
            ]

        return state

    async def _simulation_execution_node(self, state: AgentState) -> AgentState:
        """
        Node 3: Execute Monte Carlo simulation.

        Runs N iterations of the crime simulation model with stochastic
        variation and computes outcome distributions.

        Args:
            state: Current state with parameters configured.

        Returns:
            Updated state with raw simulation iteration results.
        """
        logger.info("Simulation execution: running Monte Carlo iterations")

        try:
            current_results = state.get("simulation_results") or {}
            params = current_results.get("parameters", {})

            iterations = params.get("iterations", self.default_iterations)
            baseline = params.get("baseline_daily_crimes", 5.0)
            sim_days = params.get("simulation_days", 30)
            impact_factor = params.get("impact_factor", -0.05)
            seed = params.get("random_seed", 42)

            np.random.seed(seed)

            baseline_outcomes = []
            intervention_outcomes = []
            daily_crime_series = []

            for i in range(iterations):
                baseline_daily = np.random.poisson(lam=baseline, size=sim_days)
                baseline_total = int(np.sum(baseline_daily))
                baseline_outcomes.append(baseline_total)

                intervention_daily = np.random.poisson(
                    lam=max(0.1, baseline * (1 + impact_factor)),
                    size=sim_days,
                )
                intervention_total = int(np.sum(intervention_daily))
                intervention_outcomes.append(intervention_total)

                if i == 0:
                    daily_crime_series = {
                        "baseline": baseline_daily.tolist(),
                        "intervention": intervention_daily.tolist(),
                    }

            simulation_raw = {
                "baseline_outcomes": baseline_outcomes,
                "intervention_outcomes": intervention_outcomes,
                "daily_series_sample": daily_crime_series,
                "iterations_completed": iterations,
            }

            current_results["simulation_raw"] = simulation_raw
            state["simulation_results"] = current_results

            logger.info(
                "Simulation execution complete: %d iterations, mean baseline=%.1f, mean intervention=%.1f",
                iterations,
                np.mean(baseline_outcomes),
                np.mean(intervention_outcomes),
            )

        except Exception as exc:
            logger.error("Simulation execution failed: %s", str(exc))
            state["errors"] = state.get("errors", []) + [
                f"Simulation execution error: {str(exc)}"
            ]

        return state

    async def _outcome_analysis_node(self, state: AgentState) -> AgentState:
        """
        Node 4: Analyze simulation outcomes with statistical rigor.

        Computes summary statistics, confidence intervals, and impact
        metrics from the Monte Carlo results.

        Args:
            state: Current state with raw simulation results.

        Returns:
            Updated state with statistical analysis of outcomes.
        """
        logger.info("Outcome analysis: computing simulation statistics")

        try:
            current_results = state.get("simulation_results") or {}
            raw = current_results.get("simulation_raw", {})
            params = current_results.get("parameters", {})

            baseline_outcomes = raw.get("baseline_outcomes", [])
            intervention_outcomes = raw.get("intervention_outcomes", [])
            confidence = params.get("confidence_level", 0.95)

            if not baseline_outcomes or not intervention_outcomes:
                raise ValueError("No simulation data available for analysis")

            baseline_arr = np.array(baseline_outcomes)
            intervention_arr = np.array(intervention_outcomes)
            reduction_arr = baseline_arr - intervention_arr
            pct_reduction_arr = (reduction_arr / np.maximum(baseline_arr, 1)) * 100

            alpha = 1 - confidence
            lower_pct = (alpha / 2) * 100
            upper_pct = (1 - alpha / 2) * 100

            outcome_analysis = {
                "baseline_statistics": {
                    "mean": round(float(np.mean(baseline_arr)), 2),
                    "median": round(float(np.median(baseline_arr)), 2),
                    "std": round(float(np.std(baseline_arr)), 2),
                    "ci_lower": round(float(np.percentile(baseline_arr, lower_pct)), 2),
                    "ci_upper": round(float(np.percentile(baseline_arr, upper_pct)), 2),
                },
                "intervention_statistics": {
                    "mean": round(float(np.mean(intervention_arr)), 2),
                    "median": round(float(np.median(intervention_arr)), 2),
                    "std": round(float(np.std(intervention_arr)), 2),
                    "ci_lower": round(float(np.percentile(intervention_arr, lower_pct)), 2),
                    "ci_upper": round(float(np.percentile(intervention_arr, upper_pct)), 2),
                },
                "impact_metrics": {
                    "mean_reduction": round(float(np.mean(reduction_arr)), 2),
                    "median_reduction": round(float(np.median(reduction_arr)), 2),
                    "mean_pct_reduction": round(float(np.mean(pct_reduction_arr)), 2),
                    "probability_of_reduction": round(
                        float(np.mean(reduction_arr > 0)) * 100, 1
                    ),
                    "ci_lower_reduction": round(float(np.percentile(reduction_arr, lower_pct)), 2),
                    "ci_upper_reduction": round(float(np.percentile(reduction_arr, upper_pct)), 2),
                },
                "confidence_level": confidence,
            }

            current_results["outcome_analysis"] = outcome_analysis
            state["simulation_results"] = current_results

            logger.info(
                "Outcome analysis complete: %.1f%% mean reduction, %.1f%% probability of reduction",
                outcome_analysis["impact_metrics"]["mean_pct_reduction"],
                outcome_analysis["impact_metrics"]["probability_of_reduction"],
            )

        except Exception as exc:
            logger.error("Outcome analysis failed: %s", str(exc))
            current_results = state.get("simulation_results") or {}
            current_results["outcome_analysis"] = {"error": str(exc)}
            state["simulation_results"] = current_results
            state["errors"] = state.get("errors", []) + [
                f"Outcome analysis error: {str(exc)}"
            ]

        return state

    async def _recommendation_synthesis_node(self, state: AgentState) -> AgentState:
        """
        Node 5: Generate strategic recommendations from simulation outcomes.

        Uses Gemini to interpret simulation results and produce actionable
        strategic recommendations for decision makers.

        Args:
            state: Current state with outcome analysis.

        Returns:
            Updated state with final simulation recommendations.
        """
        logger.info("Recommendation synthesis: generating strategic advice")

        try:
            current_results = state.get("simulation_results") or {}
            outcome_analysis = current_results.get("outcome_analysis", {})
            params = current_results.get("parameters", {})

            prompt = SimulationPrompts.recommendation_synthesis_prompt(
                scenario_definition=current_results.get("scenario_definition", ""),
                parameters=params,
                outcome_analysis=outcome_analysis,
                query=state.get("query", ""),
            )

            messages = [
                SystemMessage(content=SimulationPrompts.SYSTEM_PROMPT),
                HumanMessage(content=prompt),
            ]

            response = await self.llm.ainvoke(messages)
            recommendations = response.content

            current_results["recommendations"] = recommendations
            current_results["status"] = "completed"
            current_results["completed_at"] = datetime.utcnow().isoformat()
            state["simulation_results"] = current_results

            logger.info("Recommendation synthesis completed successfully")

        except Exception as exc:
            logger.error("Recommendation synthesis failed: %s", str(exc))
            current_results = state.get("simulation_results") or {}
            current_results["recommendations"] = f"Recommendations unavailable: {str(exc)}"
            current_results["status"] = "partial"
            state["simulation_results"] = current_results

        return state

    async def _fetch_baseline_data(self) -> list[dict[str, Any]]:
        """
        Fetch baseline crime data from PostgreSQL for simulation reference.

        Returns:
            List of crime records from the last 90 days.
        """
        logger.debug("Fetching baseline data from PostgreSQL")

        try:
            import asyncpg

            conn = await asyncpg.connect(self.pg_connection_string)
            try:
                rows = await conn.fetch(
                    """
                    SELECT id, crime_type, occurred_at, district, severity
                    FROM crimes
                    WHERE occurred_at >= NOW() - INTERVAL '90 days'
                    ORDER BY occurred_at DESC
                    """,
                )
                return [dict(row) for row in rows]
            finally:
                await conn.close()

        except Exception as exc:
            logger.warning("Baseline data fetch failed: %s", str(exc))
            return []

    @staticmethod
    def _extract_number(text: str, default: int = 10) -> int:
        """
        Extract a numeric value from a text string.

        Args:
            text: Input text potentially containing a number.
            default: Default value if no number is found.

        Returns:
            Extracted integer or the default value.
        """
        import re

        numbers = re.findall(r"\d+", text)
        return int(numbers[0]) if numbers else default
