"""
Sentinel AI - Centralized Prompts & Shared State
==================================================
File: backend/agents/prompts.py
Purpose: Centralized prompt templates, system prompts, and shared type
         definitions for all Sentinel AI agents. Single source of truth
         for all LLM interactions across the agent system.

Architecture:
    - AgentState TypedDict: Shared state schema for LangGraph
    - Per-agent prompt classes with static methods for each workflow node
    - System prompts defining agent personas and constraints
    - Task-specific prompt templates with dynamic context injection

Integration:
    - Imported by ALL agent modules: investigation_agent.py, analytics_agent.py,
      prediction_agent.py, graph_agent.py, recommendation_agent.py,
      report_agent.py, simulation_agent.py, orchestrator.py
    - AgentState is the core data contract for LangGraph state machines

Dependencies:
    - typing (stdlib)
"""

import json
import logging
from typing import Any, Optional, TypedDict

logger = logging.getLogger(__name__)


# =============================================================================
# SHARED AGENT STATE
# =============================================================================

class AgentState(TypedDict, total=False):
    """
    Shared state schema for all LangGraph agent workflows.

    This TypedDict flows through the LangGraph state machine, allowing
    agents to read from and write to specific fields. Each agent reads
    the fields it needs and writes its results to its designated output field.

    Fields:
        messages: Conversation history for context continuity
        query: Original user query string
        intent: Classified intent from the orchestrator
        target_agents: List of agent identifiers to invoke
        crime_data: Crime records fetched from PostgreSQL
        graph_data: Relationship data fetched from Neo4j
        investigation_results: Output from InvestigationAgent
        analytics_results: Output from AnalyticsAgent
        ml_predictions: Output from PredictionAgent
        graph_analysis: Output from GraphAgent
        recommendations: Output from RecommendationAgent
        simulation_results: Output from SimulationAgent
        report_data: Output from ReportAgent
        final_response: Final aggregated response string
        errors: List of error messages from all agents
        metadata: Processing metadata (timing, session, etc.)
    """

    messages: list
    query: str
    intent: str
    target_agents: list[str]
    crime_data: Optional[list[dict[str, Any]]]
    graph_data: Optional[dict[str, Any]]
    investigation_results: Optional[dict[str, Any]]
    analytics_results: Optional[dict[str, Any]]
    ml_predictions: Optional[dict[str, Any]]
    graph_analysis: Optional[dict[str, Any]]
    recommendations: Optional[list[dict[str, Any]]]
    simulation_results: Optional[dict[str, Any]]
    report_data: Optional[dict[str, Any]]
    final_response: Optional[str]
    errors: list[str]
    metadata: dict[str, Any]


# =============================================================================
# ORCHESTRATOR PROMPTS
# =============================================================================

class OrchestratorPrompts:
    """Prompt templates for the master orchestrator agent."""

    SYSTEM_PROMPT: str = (
        "You are the Sentinel AI Orchestrator, a master AI controller for a crime "
        "intelligence system. Your role is to classify user intents and route queries "
        "to the appropriate specialist agent. You must respond with ONLY the intent "
        "category, nothing else. Available categories: investigation, analytics, "
        "prediction, graph_query, recommendation, simulation, report, general."
    )

    GENERAL_SYSTEM_PROMPT: str = (
        "You are Sentinel AI, an advanced crime intelligence assistant. You provide "
        "expert analysis on crime data, law enforcement strategies, and public safety. "
        "Always provide actionable, data-driven insights. Be professional, precise, "
        "and helpful. If you don't have specific data, provide general expert guidance."
    )

    RESPONSE_SYSTEM_PROMPT: str = (
        "You are Sentinel AI's response synthesizer. Your job is to take the outputs "
        "from specialist AI agents and create a clear, professional, and actionable "
        "response for the user. Organize information logically, highlight key findings, "
        "and provide actionable recommendations where applicable. Use markdown formatting."
    )

    @staticmethod
    def intent_classification_prompt(query: str) -> str:
        """
        Generate the intent classification prompt.

        Args:
            query: User's natural language query.

        Returns:
            Formatted prompt string for intent classification.
        """
        return (
            f"Classify the following user query into exactly ONE category.\n\n"
            f"Categories:\n"
            f"- investigation: Queries about specific crime cases, evidence, suspects, case analysis\n"
            f"- analytics: Queries about crime statistics, trends, patterns, comparisons\n"
            f"- prediction: Queries about crime forecasts, hotspots, anomalies, risk predictions\n"
            f"- graph_query: Queries about criminal networks, relationships, entity connections\n"
            f"- recommendation: Queries about officer deployment, resource allocation, patrol routes\n"
            f"- simulation: Queries about what-if scenarios, impact analysis, strategy modeling\n"
            f"- report: Queries requesting report generation, summaries, exports\n"
            f"- general: General questions about crime, policing, or the system\n\n"
            f"User Query: {query}\n\n"
            f"Respond with ONLY the category name, nothing else."
        )

    @staticmethod
    def response_generation_prompt(query: str, intent: str, results: str) -> str:
        """
        Generate the final response synthesis prompt.

        Args:
            query: Original user query.
            intent: Classified intent.
            results: Combined results from specialist agents.

        Returns:
            Formatted prompt for response generation.
        """
        return (
            f"The user asked: \"{query}\"\n\n"
            f"Intent: {intent}\n\n"
            f"The specialist agents produced the following results:\n\n"
            f"{results}\n\n"
            f"Create a clear, well-structured response that:\n"
            f"1. Directly addresses the user's query\n"
            f"2. Presents key findings prominently\n"
            f"3. Provides actionable recommendations where relevant\n"
            f"4. Uses markdown formatting for readability\n"
            f"5. Is professional and suitable for law enforcement use"
        )


# =============================================================================
# INVESTIGATION AGENT PROMPTS
# =============================================================================

class InvestigationPrompts:
    """Prompt templates for the investigation agent."""

    SYSTEM_PROMPT: str = (
        "You are Sentinel AI's Investigation Analyst, an expert in criminal case "
        "analysis. You analyze crime evidence, build suspect profiles, reconstruct "
        "timelines, and generate investigation insights. Your analysis must be "
        "thorough, factual, and actionable. Always cite specific data points from "
        "the evidence. Structure your analysis clearly with sections and bullet points."
    )

    @staticmethod
    def evidence_analysis_prompt(query: str, crime_data: list[dict[str, Any]]) -> str:
        """Generate prompt for evidence analysis node."""
        crime_summary = json.dumps(crime_data[:10], default=str, indent=2) if crime_data else "No crime data available"
        return (
            f"Analyze the following crime evidence and data for the investigation query:\n\n"
            f"Query: {query}\n\n"
            f"Crime Data:\n{crime_summary}\n\n"
            f"Provide a detailed evidence analysis covering:\n"
            f"1. Key evidence items and their significance\n"
            f"2. Connections between evidence pieces\n"
            f"3. Evidence gaps and what additional evidence is needed\n"
            f"4. Evidentiary patterns suggesting modus operandi\n"
            f"5. Strength of evidence assessment"
        )

    @staticmethod
    def suspect_profiling_prompt(
        crime_data: list[dict[str, Any]],
        graph_data: dict[str, Any],
    ) -> str:
        """Generate prompt for suspect profiling node."""
        crime_summary = json.dumps(crime_data[:5], default=str, indent=2) if crime_data else "No crime data"
        graph_summary = json.dumps(graph_data, default=str, indent=2) if graph_data else "No graph data"
        return (
            f"Build suspect profiles based on the following crime and relationship data:\n\n"
            f"Crime Data:\n{crime_summary}\n\n"
            f"Relationship Graph Data:\n{graph_summary}\n\n"
            f"For each suspect, provide:\n"
            f"1. Known aliases and identifiers\n"
            f"2. Criminal history and patterns\n"
            f"3. Known associates and network position\n"
            f"4. Risk assessment (high/medium/low)\n"
            f"5. Recommended investigative actions"
        )

    @staticmethod
    def timeline_reconstruction_prompt(
        crime_data: list[dict[str, Any]],
        evidence_analysis: str,
        suspect_profiles: str,
    ) -> str:
        """Generate prompt for timeline reconstruction node."""
        crime_summary = json.dumps(crime_data[:10], default=str, indent=2) if crime_data else "No crime data"
        return (
            f"Reconstruct the chronological timeline of events based on:\n\n"
            f"Crime Records:\n{crime_summary}\n\n"
            f"Evidence Analysis:\n{evidence_analysis[:2000]}\n\n"
            f"Suspect Profiles:\n{suspect_profiles[:2000]}\n\n"
            f"Build a timeline that:\n"
            f"1. Lists events in chronological order\n"
            f"2. Notes time gaps and their significance\n"
            f"3. Identifies critical turning points\n"
            f"4. Maps suspect movements and activities\n"
            f"5. Highlights corroborated vs. unconfirmed events"
        )

    @staticmethod
    def conclusion_prompt(
        query: str,
        evidence_analysis: str,
        suspect_profiles: str,
        timeline: str,
    ) -> str:
        """Generate prompt for investigation conclusion node."""
        return (
            f"Synthesize the following investigation findings into a comprehensive conclusion:\n\n"
            f"Investigation Query: {query}\n\n"
            f"Evidence Analysis:\n{evidence_analysis[:2000]}\n\n"
            f"Suspect Profiles:\n{suspect_profiles[:2000]}\n\n"
            f"Timeline:\n{timeline[:2000]}\n\n"
            f"Provide:\n"
            f"1. Executive summary of findings\n"
            f"2. Primary suspect identification with confidence level\n"
            f"3. Modus operandi analysis\n"
            f"4. Recommended next steps for investigators\n"
            f"5. Case strength assessment\n"
            f"6. Risk of reoffense evaluation"
        )


# =============================================================================
# ANALYTICS AGENT PROMPTS
# =============================================================================

class AnalyticsPrompts:
    """Prompt templates for the analytics agent."""

    SYSTEM_PROMPT: str = (
        "You are Sentinel AI's Crime Analytics Expert, specializing in statistical "
        "analysis of crime data. You identify patterns, trends, and anomalies in "
        "crime statistics. Your insights must be data-driven, precise, and actionable. "
        "Use specific numbers and percentages. Compare against baselines when possible."
    )

    @staticmethod
    def pattern_detection_prompt(
        crime_data: list[dict[str, Any]],
        statistics: dict[str, Any],
    ) -> str:
        """Generate prompt for crime pattern detection."""
        stats_summary = json.dumps(statistics, default=str, indent=2)
        return (
            f"Analyze the following crime statistics to detect patterns:\n\n"
            f"Statistics:\n{stats_summary}\n\n"
            f"Total records analyzed: {len(crime_data)}\n\n"
            f"Identify:\n"
            f"1. Spatial patterns (crime clusters by location)\n"
            f"2. Temporal patterns (time-of-day, day-of-week, seasonal)\n"
            f"3. Crime type patterns (co-occurring crime types)\n"
            f"4. Severity escalation patterns\n"
            f"5. Notable outliers or anomalies"
        )

    @staticmethod
    def trend_analysis_prompt(
        crime_data: list[dict[str, Any]],
        statistics: dict[str, Any],
        patterns: str,
    ) -> str:
        """Generate prompt for trend analysis."""
        stats_summary = json.dumps(statistics, default=str, indent=2)
        return (
            f"Analyze temporal trends in the following crime data:\n\n"
            f"Statistics:\n{stats_summary}\n\n"
            f"Detected Patterns:\n{patterns[:2000]}\n\n"
            f"Provide:\n"
            f"1. Overall crime trend direction (increasing/decreasing/stable)\n"
            f"2. Crime type-specific trends\n"
            f"3. District-level trend variations\n"
            f"4. Seasonal patterns and cyclical behavior\n"
            f"5. Trend forecasting for the next 30 days"
        )

    @staticmethod
    def insight_generation_prompt(
        query: str,
        statistics: dict[str, Any],
        patterns: str,
        trends: str,
    ) -> str:
        """Generate prompt for insight generation."""
        stats_summary = json.dumps(statistics, default=str, indent=2)
        return (
            f"Generate actionable crime intelligence insights for:\n\n"
            f"Query: {query}\n\n"
            f"Statistics:\n{stats_summary}\n\n"
            f"Patterns:\n{patterns[:1500]}\n\n"
            f"Trends:\n{trends[:1500]}\n\n"
            f"Provide:\n"
            f"1. Executive summary (3-5 key findings)\n"
            f"2. Critical insights requiring immediate attention\n"
            f"3. Resource allocation recommendations\n"
            f"4. Comparative analysis (vs. previous period)\n"
            f"5. Actionable recommendations for leadership"
        )


# =============================================================================
# PREDICTION AGENT PROMPTS
# =============================================================================

class PredictionPrompts:
    """Prompt templates for the prediction agent."""

    SYSTEM_PROMPT: str = (
        "You are Sentinel AI's Predictive Intelligence Analyst. You interpret "
        "machine learning model outputs and translate them into actionable risk "
        "assessments. You contextualize predictions with domain knowledge about "
        "crime patterns and law enforcement operations. Be precise about confidence "
        "levels and always note prediction limitations."
    )

    @staticmethod
    def risk_assessment_prompt(model_results: dict[str, Any], query: str) -> str:
        """Generate prompt for risk assessment from ML results."""
        results_summary = json.dumps(model_results, default=str, indent=2)
        return (
            f"Interpret the following ML prediction results and provide a risk assessment:\n\n"
            f"User Query: {query}\n\n"
            f"Model Results:\n{results_summary}\n\n"
            f"Provide:\n"
            f"1. Overall risk level assessment (Critical/High/Medium/Low)\n"
            f"2. Risk breakdown by area/district\n"
            f"3. Time-based risk patterns\n"
            f"4. Confidence assessment for each prediction\n"
            f"5. Recommended preventive actions\n"
            f"6. Limitations and caveats of the predictions"
        )

    @staticmethod
    def alert_generation_prompt(model_results: dict[str, Any], risk_assessment: str) -> str:
        """Generate prompt for priority alert generation."""
        results_summary = json.dumps(model_results, default=str, indent=2)
        return (
            f"Generate priority-ranked alerts based on:\n\n"
            f"Prediction Results:\n{results_summary}\n\n"
            f"Risk Assessment:\n{risk_assessment[:2000]}\n\n"
            f"For each alert, provide:\n"
            f"1. Alert severity (Critical/High/Medium/Low)\n"
            f"2. Affected area and crime type\n"
            f"3. Predicted timeframe\n"
            f"4. Recommended immediate actions\n"
            f"5. Resource requirements\n\n"
            f"Order alerts by severity (most critical first)."
        )


# =============================================================================
# GRAPH AGENT PROMPTS
# =============================================================================

class GraphPrompts:
    """Prompt templates for the graph (Neo4j) agent."""

    SYSTEM_PROMPT: str = (
        "You are Sentinel AI's Criminal Network Analyst, specializing in graph-based "
        "intelligence analysis. You analyze criminal networks, entity relationships, "
        "and organizational structures in knowledge graphs. You identify key players, "
        "communication patterns, and vulnerability points in criminal organizations."
    )

    @staticmethod
    def query_parsing_prompt(query: str) -> str:
        """Generate prompt for parsing graph query intent."""
        return (
            f"Parse the following query to determine what graph analysis is needed:\n\n"
            f"Query: {query}\n\n"
            f"Determine:\n"
            f"1. Target entity type (suspect, crime, location, vehicle, gang)\n"
            f"2. Relationship types of interest\n"
            f"3. Traversal depth needed (1-hop, 2-hop, full network)\n"
            f"4. Analysis type (network mapping, central figure identification, "
            f"pattern detection, community detection)\n"
            f"5. Key search terms or identifiers"
        )

    @staticmethod
    def relationship_analysis_prompt(graph_data: dict[str, Any]) -> str:
        """Generate prompt for analyzing graph relationships."""
        graph_summary = json.dumps(graph_data, default=str, indent=2)[:3000]
        return (
            f"Analyze the following criminal network graph data:\n\n"
            f"Graph Data:\n{graph_summary}\n\n"
            f"Analyze:\n"
            f"1. Network structure and topology\n"
            f"2. Central figures (highest connectivity)\n"
            f"3. Relationship strength and types\n"
            f"4. Sub-communities or clusters\n"
            f"5. Vulnerability points (removing which node disrupts the network most)"
        )

    @staticmethod
    def pattern_matching_prompt(graph_data: dict[str, Any], relationship_analysis: str) -> str:
        """Generate prompt for graph pattern matching."""
        graph_summary = json.dumps(graph_data, default=str, indent=2)[:2000]
        return (
            f"Identify recurring patterns in the criminal network:\n\n"
            f"Graph Data:\n{graph_summary}\n\n"
            f"Relationship Analysis:\n{relationship_analysis[:2000]}\n\n"
            f"Look for:\n"
            f"1. Repeat offense patterns (same suspects, same locations)\n"
            f"2. Crime chain patterns (linked crimes over time)\n"
            f"3. Modus operandi similarities across cases\n"
            f"4. Geographic clustering of connected suspects\n"
            f"5. Temporal co-occurrence of related crimes"
        )

    @staticmethod
    def insight_extraction_prompt(query: str, relationship_analysis: str, patterns: str) -> str:
        """Generate prompt for extracting graph insights."""
        return (
            f"Generate actionable intelligence from the graph analysis:\n\n"
            f"Original Query: {query}\n\n"
            f"Relationship Analysis:\n{relationship_analysis[:2000]}\n\n"
            f"Patterns Found:\n{patterns[:2000]}\n\n"
            f"Provide:\n"
            f"1. Key intelligence findings\n"
            f"2. High-priority targets for investigation\n"
            f"3. Network disruption strategies\n"
            f"4. Predicted future connections or activities\n"
            f"5. Recommended surveillance or investigation actions"
        )


# =============================================================================
# RECOMMENDATION AGENT PROMPTS
# =============================================================================

class RecommendationPrompts:
    """Prompt templates for the recommendation agent."""

    SYSTEM_PROMPT: str = (
        "You are Sentinel AI's Resource Optimization Strategist. You develop "
        "officer deployment plans, patrol strategies, and resource allocation "
        "recommendations. Your recommendations must be operationally feasible, "
        "data-driven, and optimized for maximum crime prevention impact. Always "
        "consider officer safety, workload balance, and response time."
    )

    @staticmethod
    def strategy_formulation_prompt(
        context: dict[str, Any],
        scored_assignments: list[dict[str, Any]],
        query: str,
    ) -> str:
        """Generate prompt for deployment strategy formulation."""
        context_summary = json.dumps(context, default=str, indent=2)[:2000]
        assignments_summary = json.dumps(scored_assignments[:10], default=str, indent=2)
        return (
            f"Develop a deployment strategy based on:\n\n"
            f"Request: {query}\n\n"
            f"Operational Context:\n{context_summary}\n\n"
            f"Top Scored Assignments:\n{assignments_summary}\n\n"
            f"Formulate:\n"
            f"1. Primary deployment strategy\n"
            f"2. Shift-based scheduling recommendations\n"
            f"3. Patrol route prioritization\n"
            f"4. Backup and support positioning\n"
            f"5. Risk mitigation measures for officers"
        )

    @staticmethod
    def action_planning_prompt(
        recommendations: list[dict[str, Any]],
        strategies: str,
        query: str,
    ) -> str:
        """Generate prompt for action plan generation."""
        recs_summary = json.dumps(recommendations[:10], default=str, indent=2)
        return (
            f"Create an actionable deployment plan:\n\n"
            f"Request: {query}\n\n"
            f"Recommendations:\n{recs_summary}\n\n"
            f"Strategy:\n{strategies[:2000]}\n\n"
            f"Generate:\n"
            f"1. Step-by-step deployment instructions\n"
            f"2. Timeline and milestones\n"
            f"3. Resource requirements\n"
            f"4. Success metrics and KPIs\n"
            f"5. Contingency plans"
        )


# =============================================================================
# REPORT AGENT PROMPTS
# =============================================================================

class ReportPrompts:
    """Prompt templates for the report generation agent."""

    SYSTEM_PROMPT: str = (
        "You are Sentinel AI's Report Writer, producing professional crime intelligence "
        "reports. Your reports are used by police commanders and government officials. "
        "Write in a formal, authoritative tone. Include specific data points, statistics, "
        "and actionable recommendations. Structure reports with clear sections, "
        "executive summaries, and conclusion sections."
    )

    @staticmethod
    def narrative_generation_prompt(
        report_structure: dict[str, Any],
        aggregated_data: dict[str, Any],
        query: str,
    ) -> str:
        """Generate prompt for report narrative writing."""
        structure_summary = json.dumps(report_structure, default=str, indent=2)[:1500]
        data_summary = json.dumps(aggregated_data, default=str, indent=2)[:3000]
        return (
            f"Generate a comprehensive crime intelligence report:\n\n"
            f"Report Request: {query}\n\n"
            f"Report Structure:\n{structure_summary}\n\n"
            f"Available Data:\n{data_summary}\n\n"
            f"Write the full report with:\n"
            f"1. Executive Summary (key findings in 3-5 bullet points)\n"
            f"2. Detailed analysis for each section\n"
            f"3. Data-backed insights with specific numbers\n"
            f"4. Comparative analysis where possible\n"
            f"5. Actionable recommendations\n"
            f"6. Conclusions and next steps\n\n"
            f"Use markdown formatting with headers, bullets, and tables."
        )


# =============================================================================
# SIMULATION AGENT PROMPTS
# =============================================================================

class SimulationPrompts:
    """Prompt templates for the simulation agent."""

    SYSTEM_PROMPT: str = (
        "You are Sentinel AI's Crime Simulation Strategist. You interpret simulation "
        "scenarios, analyze Monte Carlo results, and provide strategic recommendations "
        "based on statistical outcomes. Be precise about probabilities, confidence "
        "intervals, and statistical significance. Always note assumptions and limitations."
    )

    @staticmethod
    def scenario_definition_prompt(query: str) -> str:
        """Generate prompt for parsing simulation scenarios."""
        return (
            f"Parse the following simulation scenario request:\n\n"
            f"Request: {query}\n\n"
            f"Extract:\n"
            f"1. Scenario type (resource reallocation, surveillance increase, "
            f"community intervention, general)\n"
            f"2. Target areas or zones\n"
            f"3. Key variables being changed (officer count, patrol frequency, etc.)\n"
            f"4. Expected magnitude of change\n"
            f"5. Time horizon for the simulation\n"
            f"6. Any specific crime types to focus on\n"
            f"7. Success criteria or objectives"
        )

    @staticmethod
    def recommendation_synthesis_prompt(
        scenario_definition: str,
        parameters: dict[str, Any],
        outcome_analysis: dict[str, Any],
        query: str,
    ) -> str:
        """Generate prompt for simulation recommendation synthesis."""
        params_summary = json.dumps(parameters, default=str, indent=2)
        outcome_summary = json.dumps(outcome_analysis, default=str, indent=2)
        return (
            f"Generate strategic recommendations from the simulation results:\n\n"
            f"Original Request: {query}\n\n"
            f"Scenario:\n{scenario_definition[:1500]}\n\n"
            f"Parameters:\n{params_summary}\n\n"
            f"Outcome Analysis:\n{outcome_summary}\n\n"
            f"Provide:\n"
            f"1. Key simulation findings (with confidence levels)\n"
            f"2. Recommendation: Should this intervention be implemented? (Yes/No/Conditional)\n"
            f"3. Expected impact with confidence intervals\n"
            f"4. Implementation timeline and phasing\n"
            f"5. Risk factors and mitigation strategies\n"
            f"6. Alternative scenarios to consider\n"
            f"7. Cost-benefit analysis summary"
        )
