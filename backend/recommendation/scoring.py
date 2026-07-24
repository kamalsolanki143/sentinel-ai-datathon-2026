"""
Sentinel AI - Multi-Criteria Scoring Engine
============================================
File: backend/recommendation/scoring.py
Purpose: Multi-Criteria Decision Analysis (MCDA) engine for calculating normalized,
         weighted scores across operational dimensions (Crime Severity, Area Risk,
         Officer Availability, Resource Utilization, Prediction Confidence, Composite Priority).

Dependencies: pydantic, typing, loguru, backend.recommendation.utils
"""

from typing import Any, Dict, List, Optional
from loguru import logger
from pydantic import BaseModel, Field

from backend.recommendation.utils import haversine_distance, normalize_scores, sigmoid


class MultiCriteriaWeights(BaseModel):
    """
    Configurable weighting parameters for calculating overall composite priority scores.
    Sum of weights equals 1.0.
    """

    area_risk: float = Field(default=0.30, ge=0.0, le=1.0, description="Weight for Area Risk Score")
    crime_severity: float = Field(default=0.25, ge=0.0, le=1.0, description="Weight for Crime Severity Score")
    officer_availability: float = Field(default=0.20, ge=0.0, le=1.0, description="Weight for Officer Availability Score")
    resource_utilization: float = Field(default=0.15, ge=0.0, le=1.0, description="Weight for Resource Utilization Score")
    prediction_confidence: float = Field(default=0.10, ge=0.0, le=1.0, description="Weight for ML Model Confidence Score")

    def validate_weights(self) -> bool:
        """Verify that weights sum to approximately 1.0."""
        total = (
            self.area_risk
            + self.crime_severity
            + self.officer_availability
            + self.resource_utilization
            + self.prediction_confidence
        )
        return abs(total - 1.0) < 1e-4


# Standardized Severity Index by Crime Type
CRIME_TYPE_SEVERITY_MAP: Dict[str, float] = {
    "homicide": 1.00,
    "armed_robbery": 0.90,
    "aggravated_assault": 0.85,
    "kidnapping": 0.95,
    "sexual_assault": 0.90,
    "active_shooter": 1.00,
    "terrorism": 1.00,
    "burglary": 0.65,
    "grand_theft_auto": 0.60,
    "narcotics_trafficking": 0.70,
    "cyber_attack": 0.55,
    "financial_fraud": 0.45,
    "vandalism": 0.30,
    "public_disturbance": 0.25,
    "traffic_violation": 0.15,
    "suspicious_activity": 0.35,
}


class ScoringEngine:
    """
    Multi-Criteria Decision Analysis (MCDA) Scoring Engine for Sentinel AI.

    Computes normalized score components for officer-to-incident or officer-to-hotspot
    pairings, calculating composite priority rankings for decision support.
    """

    def __init__(self, default_weights: Optional[MultiCriteriaWeights] = None) -> None:
        """Initialize Scoring Engine with optional custom weights."""
        self.weights = default_weights or MultiCriteriaWeights()
        if not self.weights.validate_weights():
            logger.warning("Custom MCDA weights do not sum to 1.0. Re-normalizing...")
            self._renormalize_weights()

    def _renormalize_weights(self) -> None:
        """Normalize weights so their sum equals 1.0."""
        total = (
            self.weights.area_risk
            + self.weights.crime_severity
            + self.weights.officer_availability
            + self.weights.resource_utilization
            + self.weights.prediction_confidence
        )
        if total > 0:
            self.weights.area_risk /= total
            self.weights.crime_severity /= total
            self.weights.officer_availability /= total
            self.weights.resource_utilization /= total
            self.weights.prediction_confidence /= total

    def calculate_crime_severity_score(
        self,
        crime_type: str,
        casualties: int = 0,
        weapons_involved: bool = False,
        property_loss_val: float = 0.0,
    ) -> float:
        """
        Calculate Crime Severity Score (0.0 to 1.0) based on category, weapons, and harm indicators.

        Args:
            crime_type: Standardized crime category string.
            casualties: Number of injuries or casualties reported.
            weapons_involved: Flag indicating firearm/lethal weapon involvement.
            property_loss_val: Estimated financial damage value in USD/INR.

        Returns:
            Normalized severity score between 0.0 (minimal) and 1.0 (extreme emergency).
        """
        base_severity = CRIME_TYPE_SEVERITY_MAP.get(crime_type.lower().replace(" ", "_"), 0.50)

        # Multipliers / Additions for severe factors
        casualty_modifier = min(0.30, casualties * 0.10)
        weapon_modifier = 0.15 if weapons_involved else 0.0
        property_modifier = min(0.10, property_loss_val / 100000.0)

        total_score = base_severity + casualty_modifier + weapon_modifier + property_modifier
        return round(min(1.0, max(0.0, total_score)), 4)

    def calculate_area_risk_score(
        self,
        historical_crime_density: float,
        hotspot_probability: float,
        time_of_day_risk_multiplier: float = 1.0,
        repeat_location_flag: bool = False,
    ) -> float:
        """
        Calculate Area Risk Score (0.0 to 1.0) combining spatial density and ML predictions.

        Args:
            historical_crime_density: Normalized density of crimes per sq km (0.0 - 1.0).
            hotspot_probability: Model predicted probability of crime occurrence (0.0 - 1.0).
            time_of_day_risk_multiplier: Temporal risk factor (e.g. night shift multiplier 1.2).
            repeat_location_flag: True if location has recurrent incidents.

        Returns:
            Normalized area risk score.
        """
        repeat_bonus = 0.10 if repeat_location_flag else 0.0
        raw_risk = (
            (0.40 * historical_crime_density + 0.60 * hotspot_probability)
            * time_of_day_risk_multiplier
            + repeat_bonus
        )
        return round(min(1.0, max(0.0, raw_risk)), 4)

    def calculate_officer_availability_score(
        self,
        shift_hours_worked: float,
        active_incidents_count: int,
        specialization: str,
        required_specialization: Optional[str] = None,
        is_active: bool = True,
    ) -> float:
        """
        Calculate Officer Availability Score (0.0 to 1.0) balancing workload and skill match.

        Args:
            shift_hours_worked: Hours worked in current shift (0 to 12+).
            active_incidents_count: Number of currently assigned open tasks.
            specialization: Officer's specialization (e.g. SWAT, Cyber, Patrol, Homicide).
            required_specialization: Required skill for target incident.
            is_active: Officer operational status flag.

        Returns:
            Availability score (0.0 = unavailable/overloaded, 1.0 = optimal availability).
        """
        if not is_active:
            return 0.0

        # Fatigue penalty: full availability under 6 hrs, degrading up to 12 hrs
        fatigue_score = 1.0 - min(1.0, max(0.0, (shift_hours_worked - 4.0) / 8.0))

        # Workload penalty: minus 0.35 per active incident
        workload_score = max(0.0, 1.0 - (active_incidents_count * 0.35))

        # Specialization match bonus
        skill_score = 1.0
        if required_specialization and required_specialization.lower() != "general":
            if specialization.lower() == required_specialization.lower():
                skill_score = 1.0
            elif specialization.lower() in ["swat", "tactical", "emergency_response"]:
                skill_score = 0.85
            else:
                skill_score = 0.50

        combined = 0.40 * fatigue_score + 0.40 * workload_score + 0.20 * skill_score
        return round(min(1.0, max(0.0, combined)), 4)

    def calculate_resource_utilization_score(
        self,
        distance_km: float,
        vehicle_available: bool = True,
        vehicle_fuel_pct: float = 100.0,
        equipment_ready: bool = True,
    ) -> float:
        """
        Calculate Resource Utilization Score (0.0 to 1.0) assessing dispatch cost and readiness.

        Args:
            distance_km: Travel distance from officer/unit location to target zone.
            vehicle_available: Vehicle operational flag.
            vehicle_fuel_pct: Vehicle fuel/battery level (0 to 100).
            equipment_ready: Mandatory equipment readiness flag.

        Returns:
            Normalized utilization score (higher means lower travel time and higher readiness).
        """
        if not equipment_ready or not vehicle_available:
            return 0.10

        # Proximity score: Sigmoid decay over distance (half point at 10km)
        proximity_score = 1.0 - sigmoid(distance_km, steepness=0.3, midpoint=5.0)

        # Fuel level score
        fuel_score = min(1.0, max(0.0, vehicle_fuel_pct / 100.0))

        score = 0.70 * proximity_score + 0.30 * fuel_score
        return round(min(1.0, max(0.0, score)), 4)

    def calculate_prediction_confidence_score(
        self, model_confidence: float, historical_accuracy: float = 0.85
    ) -> float:
        """
        Calculate Prediction Confidence Score (0.0 to 1.0) from ML model metrics.

        Args:
            model_confidence: ML model prediction output confidence (0.0 to 1.0).
            historical_accuracy: Model validation accuracy score.

        Returns:
            Calibrated confidence score.
        """
        calibrated = 0.70 * model_confidence + 0.30 * historical_accuracy
        return round(min(1.0, max(0.0, calibrated)), 4)

    def compute_overall_priority_score(
        self,
        area_risk_score: float,
        crime_severity_score: float,
        officer_availability_score: float,
        resource_utilization_score: float,
        prediction_confidence_score: float,
        custom_weights: Optional[MultiCriteriaWeights] = None,
    ) -> Dict[str, Any]:
        """
        Compute Overall Composite Priority Score (0.0 to 1.0) using Multi-Criteria Decision Analysis.

        Formula:
            Composite = w1*AreaRisk + w2*CrimeSeverity + w3*Availability + w4*ResourceUtil + w5*Confidence

        Args:
            area_risk_score: Normalized area risk score.
            crime_severity_score: Normalized crime severity score.
            officer_availability_score: Normalized officer availability score.
            resource_utilization_score: Normalized resource utilization score.
            prediction_confidence_score: Normalized ML model confidence score.
            custom_weights: Optional overriding weights.

        Returns:
            Dictionary containing composite_score, priority_level, and breakdown of components.
        """
        w = custom_weights or self.weights

        composite = (
            w.area_risk * area_risk_score
            + w.crime_severity * crime_severity_score
            + w.officer_availability * officer_availability_score
            + w.resource_utilization * resource_utilization_score
            + w.prediction_confidence * prediction_confidence_score
        )

        composite = round(min(1.0, max(0.0, composite)), 4)

        # Classify priority level
        if composite >= 0.80:
            priority_level = "CRITICAL"
        elif composite >= 0.65:
            priority_level = "HIGH"
        elif composite >= 0.45:
            priority_level = "MEDIUM"
        else:
            priority_level = "LOW"

        return {
            "composite_score": composite,
            "priority_level": priority_level,
            "breakdown": {
                "area_risk_score": area_risk_score,
                "crime_severity_score": crime_severity_score,
                "officer_availability_score": officer_availability_score,
                "resource_utilization_score": resource_utilization_score,
                "prediction_confidence_score": prediction_confidence_score,
            },
            "weights_used": w.model_dump(),
        }
