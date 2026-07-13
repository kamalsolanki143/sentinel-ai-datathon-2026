"""
Sentinel AI - Reporting Schemas
=================================
File: backend/schemas/report_schema.py
Purpose: Pydantic models defining the structure of various 
         system-generated reports.

Dependencies: pydantic
"""

from datetime import datetime
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field


class ReportSection(BaseModel):
    """Schema for a section within a report."""
    title: str
    content: str
    data: Optional[Dict[str, Any]] = None
    visualizations: Optional[List[Dict[str, Any]]] = None


class BaseReport(BaseModel):
    """Base schema for all generated reports."""
    report_id: str
    title: str
    report_type: str
    generated_at: datetime
    generated_by: str = "System"
    summary: str


class InvestigationReport(BaseReport):
    """Schema for an AI-generated investigation summary."""
    incident_id: str
    key_findings: List[str]
    suspect_leads: List[Dict[str, Any]]
    evidence_analysis: str
    recommended_actions: List[str]
    sections: List[ReportSection]


class AnalyticsReport(BaseReport):
    """Schema for an AI-generated analytics and statistics report."""
    period_start: str
    period_end: str
    total_crimes: int
    clearance_rate: float
    trends_identified: List[str]
    sections: List[ReportSection]


class ActionableIntelligence(BaseModel):
    """Schema for a single piece of actionable intelligence."""
    priority: str
    category: str
    description: str
    recommended_action: str


class IntelligenceBrief(BaseReport):
    """Schema for a daily or shift-based intelligence brief."""
    shift: str
    active_threats: List[str]
    actionable_intel: List[ActionableIntelligence]
    patrol_focus_areas: List[str]
