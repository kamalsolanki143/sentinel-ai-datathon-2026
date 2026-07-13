"""
Sentinel AI - Global Configuration Constants
==============================================
File: backend/config/config.py
Purpose: Application constants, project metadata, and static configurations.
"""

from pathlib import Path

# Project Roots
BASE_DIR = Path(__file__).resolve().parent.parent
PROJECT_ROOT = BASE_DIR.parent

# ML Model Paths
ML_MODEL_DIR = PROJECT_ROOT / "ml" / "models"
ML_OUTPUT_DIR = PROJECT_ROOT / "ml" / "outputs"

# Application Metadata
APP_METADATA = {
    "title": "Sentinel AI - Crime Intelligence & Decision OS",
    "description": "AI-powered platform for law enforcement and crime intelligence.",
    "version": "1.0.0",
    "contact": {
        "name": "Kamal Solanki",
        "email": "kamal@example.com",
    },
}

# Supported Crime Categories
SUPPORTED_CRIME_CATEGORIES = [
    "assault",
    "burglary",
    "robbery",
    "theft",
    "homicide",
    "narcotics",
    "fraud",
    "cybercrime",
    "vandalism",
    "kidnapping",
]

# AI Agent Names Registry
AGENT_REGISTRY = {
    "investigation": "InvestigationAgent",
    "analytics": "AnalyticsAgent",
    "prediction": "PredictionAgent",
    "graph": "GraphAgent",
    "recommendation": "RecommendationAgent",
    "report": "ReportAgent",
    "simulation": "SimulationAgent",
    "orchestrator": "Orchestrator",
}

# API Configuration
API_PREFIX = "/api/v1"

# Supported Languages for NLP/Responses
SUPPORTED_LANGUAGES = ["en"]
