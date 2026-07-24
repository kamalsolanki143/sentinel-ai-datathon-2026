"""
Sentinel AI - Recommendation Engine Subsystem
================================================
File: backend/recommendation/__init__.py
Purpose: Package initialization for Sentinel AI Decision Intelligence & Recommendation Engine.
"""

from backend.recommendation.utils import (
    haversine_distance,
    calculate_distance_matrix,
    normalize_scores,
    softmax,
    sigmoid,
)
from backend.recommendation.scoring import ScoringEngine, MultiCriteriaWeights
from backend.recommendation.rules_engine import PolicyRuleEngine, ComplianceResult
from backend.recommendation.risk_prioritizer import RiskPrioritizer
from backend.recommendation.patrol_optimizer import PatrolOptimizer
from backend.recommendation.resource_allocator import ResourceAllocator
from backend.recommendation.recommendation_engine import MasterRecommendationEngine
from backend.recommendation.recommendation_service import RecommendationService

__all__ = [
    "haversine_distance",
    "calculate_distance_matrix",
    "normalize_scores",
    "softmax",
    "sigmoid",
    "ScoringEngine",
    "MultiCriteriaWeights",
    "PolicyRuleEngine",
    "ComplianceResult",
    "RiskPrioritizer",
    "PatrolOptimizer",
    "ResourceAllocator",
    "MasterRecommendationEngine",
    "RecommendationService",
]
