"""
Sentinel AI - Application Constants
=====================================
File: backend/utils/constants.py
Purpose: Defines shared constants such as risk levels, districts,
         status codes, and standard application values.
"""

# Risk Levels
RISK_LEVEL_LOW = "low"
RISK_LEVEL_MEDIUM = "medium"
RISK_LEVEL_HIGH = "high"
RISK_LEVEL_CRITICAL = "critical"

RISK_LEVELS = [RISK_LEVEL_LOW, RISK_LEVEL_MEDIUM, RISK_LEVEL_HIGH, RISK_LEVEL_CRITICAL]

# Crime Severities
SEVERITY_MINOR = "minor"
SEVERITY_MODERATE = "moderate"
SEVERITY_MAJOR = "major"
SEVERITY_SEVERE = "severe"

SEVERITIES = [SEVERITY_MINOR, SEVERITY_MODERATE, SEVERITY_MAJOR, SEVERITY_SEVERE]

# Case Statuses
STATUS_OPEN = "open"
STATUS_IN_PROGRESS = "in_progress"
STATUS_RESOLVED = "resolved"
STATUS_CLOSED = "closed"
STATUS_COLD = "cold"

CASE_STATUSES = [STATUS_OPEN, STATUS_IN_PROGRESS, STATUS_RESOLVED, STATUS_CLOSED, STATUS_COLD]

# Dummy District List (Extend as needed)
DISTRICTS = [
    "Downtown",
    "Northside",
    "Southside",
    "Eastend",
    "Westend",
    "Midtown",
    "Suburban Area 1",
    "Suburban Area 2",
    "Industrial Park",
    "Port District"
]

# Standard API Response Messages
MSG_SUCCESS = "Operation completed successfully"
MSG_NOT_FOUND = "Requested resource not found"
MSG_ERROR = "An error occurred during operation"
MSG_UNAUTHORIZED = "Unauthorized access"

# Agent Intents
INTENT_INVESTIGATION = "investigate"
INTENT_ANALYTICS = "analyze"
INTENT_PREDICTION = "predict"
INTENT_GRAPH_QUERY = "query_graph"
INTENT_RECOMMENDATION = "recommend"
INTENT_REPORTING = "generate_report"
INTENT_SIMULATION = "simulate"
