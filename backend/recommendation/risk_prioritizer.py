"""
Sentinel AI - High Risk Zone & Incident Prioritizer
===================================================
File: backend/recommendation/risk_prioritizer.py
Purpose: Evaluates multi-dimensional risk scores across geographical hotspots and pending
         incidents to produce priority rankings for emergency dispatch and proactive patrol.

Dependencies: pydantic, typing, loguru, backend.recommendation.scoring, backend.recommendation.utils
"""

from datetime import datetime
from typing import Any, Dict, List, Optional
from loguru import logger
from pydantic import BaseModel, Field

from backend.recommendation.scoring import ScoringEngine
from backend.recommendation.utils import haversine_distance, normalize_scores


class PrioritizedZone(BaseModel):
    """Schema for a prioritized geographic crime hotspot zone."""

    zone_id: str = Field(description="Unique zone or sector ID")
    district: str = Field(description="Police district or precinct name")
    latitude: float = Field(description="Zone center latitude")
    longitude: float = Field(description="Zone center longitude")
    risk_score: float = Field(description="Composite risk score (0.0 to 1.0)")
    priority_level: str = Field(description="CRITICAL, HIGH, MEDIUM, or LOW")
    predicted_crime_type: str = Field(default="general_crime")
    hotspot_confidence: float = Field(default=0.80)
    recommended_patrol_frequency: int = Field(default=4, description="Patrol passes per 8-hour shift")
    recommended_officer_count: int = Field(default=2)
    contributing_factors: List[str] = Field(default_factory=list)


class PrioritizedIncident(BaseModel):
    """Schema for a prioritized active crime incident requiring response."""

    incident_id: str = Field(description="Incident CAD / case number")
    crime_type: str = Field(description="Reported crime type")
    location_name: str = Field(description="Address or landmark name")
    latitude: float = Field(description="Incident latitude")
    longitude: float = Field(description="Incident longitude")
    priority_rank: int = Field(description="1-based priority rank")
    composite_priority_score: float = Field(description="Priority score (0.0 to 1.0)")
    priority_level: str = Field(description="CRITICAL, HIGH, MEDIUM, or LOW")
    crime_severity_score: float = Field(description="Calculated severity")
    weapons_involved: bool = Field(default=False)
    casualties: int = Field(default=0)
    estimated_response_urgency: str = Field(default="IMMEDIATE")
    recommended_units: List[str] = Field(default_factory=list)


class RiskPrioritizer:
    """
    Risk Prioritization Engine for Sentinel AI.

    Combines ML hotspot predictions, real-time incident queues, historical crime density,
    and temporal factors to rank zones and incidents by operational priority.
    """

    def __init__(self, scoring_engine: Optional[ScoringEngine] = None) -> None:
        """Initialize Risk Prioritizer with Scoring Engine."""
        self.scoring = scoring_engine or ScoringEngine()
        logger.info("RiskPrioritizer initialized.")

    def prioritize_zones(
        self,
        hotspot_predictions: List[Dict[str, Any]],
        analytics_crime_stats: Optional[Dict[str, Any]] = None,
        top_k: int = 10,
    ) -> List[PrioritizedZone]:
        """
        Rank geographic zones by overall risk and generate deployment recommendations.

        Args:
            hotspot_predictions: Hotspot prediction dictionaries from PredictionAgent/models.
            analytics_crime_stats: Historical crime density & analytics metrics.
            top_k: Maximum number of top high-risk zones to return.

        Returns:
            Sorted list of PrioritizedZone objects (highest risk first).
        """
        prioritized_list: List[PrioritizedZone] = []
        stats = analytics_crime_stats or {}

        for idx, hotspot in enumerate(hotspot_predictions):
            zone_id = hotspot.get("zone_id", f"ZONE-{idx+1:03d}")
            district = hotspot.get("district", hotspot.get("name", "Central District"))
            lat = float(hotspot.get("latitude", hotspot.get("lat", 0.0)))
            lon = float(hotspot.get("longitude", hotspot.get("lon", 0.0)))
            raw_prob = float(hotspot.get("probability", hotspot.get("risk_score", 0.5)))
            predicted_type = hotspot.get("predicted_crime_type", "property_crime")
            confidence = float(hotspot.get("confidence", 0.85))

            # Retrieve district density multiplier
            district_stats = stats.get("districts", {}).get(district, {})
            hist_density = float(district_stats.get("historical_density", 0.5))

            # Calculate area risk score using MCDA scoring
            area_risk = self.scoring.calculate_area_risk_score(
                historical_crime_density=hist_density,
                hotspot_probability=raw_prob,
                time_of_day_risk_multiplier=1.15 if datetime.now().hour in range(20, 4) else 1.0,
                repeat_location_flag=bool(district_stats.get("repeat_hotspot", False)),
            )

            # Determine priority level & patrol requirements
            if area_risk >= 0.80:
                level = "CRITICAL"
                freq = 8  # Passes per shift
                offs = 4
            elif area_risk >= 0.65:
                level = "HIGH"
                freq = 6
                offs = 3
            elif area_risk >= 0.45:
                level = "MEDIUM"
                freq = 4
                offs = 2
            else:
                level = "LOW"
                freq = 2
                offs = 1

            factors = [
                f"Model Hotspot Probability: {raw_prob:.2f}",
                f"District Historical Density: {hist_density:.2f}",
                f"Predicted Crime Focus: {predicted_type.replace('_', ' ').title()}",
            ]
            if district_stats.get("repeat_hotspot"):
                factors.append("Recurrent Crime Location Pattern Identified")

            zone_item = PrioritizedZone(
                zone_id=zone_id,
                district=district,
                latitude=lat,
                longitude=lon,
                risk_score=area_risk,
                priority_level=level,
                predicted_crime_type=predicted_type,
                hotspot_confidence=confidence,
                recommended_patrol_frequency=freq,
                recommended_officer_count=offs,
                contributing_factors=factors,
            )
            prioritized_list.append(zone_item)

        # Sort by risk_score descending
        prioritized_list.sort(key=lambda z: z.risk_score, reverse=True)
        return prioritized_list[:top_k]

    def prioritize_incidents(
        self,
        active_incidents: List[Dict[str, Any]],
        officer_locations: Optional[List[Dict[str, Any]]] = None,
        top_k: int = 15,
    ) -> List[PrioritizedIncident]:
        """
        Rank active incoming CAD incidents by urgency and dispatch priority.

        Args:
            active_incidents: List of raw incident payloads.
            officer_locations: List of available officer locations for proximity calculation.
            top_k: Max incidents to return.

        Returns:
            Ranked list of PrioritizedIncident objects.
        """
        evaluated: List[PrioritizedIncident] = []

        for idx, inc in enumerate(active_incidents):
            inc_id = inc.get("incident_id", f"INC-{idx+1:04d}")
            crime_type = inc.get("crime_type", "public_disturbance")
            location_name = inc.get("location_name", inc.get("address", "Unknown Location"))
            lat = float(inc.get("latitude", 0.0))
            lon = float(inc.get("longitude", 0.0))
            weapons = bool(inc.get("weapons_involved", False))
            casualties = int(inc.get("casualties", 0))

            # Compute Crime Severity Score
            sev_score = self.scoring.calculate_crime_severity_score(
                crime_type=crime_type,
                casualties=casualties,
                weapons_involved=weapons,
                property_loss_val=float(inc.get("property_loss_val", 0.0)),
            )

            # Nearest officer distance if available
            min_dist = 999.0
            if officer_locations:
                for off in officer_locations:
                    off_lat = float(off.get("latitude", 0.0))
                    off_lon = float(off.get("longitude", 0.0))
                    d = haversine_distance(off_lat, off_lon, lat, lon)
                    if d < min_dist:
                        min_dist = d
            if min_dist == 999.0:
                min_dist = 5.0  # Default 5km fallback

            res_score = self.scoring.calculate_resource_utilization_score(distance_km=min_dist)

            # Compute overall composite priority score
            priority_res = self.scoring.compute_overall_priority_score(
                area_risk_score=0.70 if weapons else 0.40,
                crime_severity_score=sev_score,
                officer_availability_score=0.80,
                resource_utilization_score=res_score,
                prediction_confidence_score=float(inc.get("confidence", 0.90)),
            )

            score = priority_res["composite_score"]
            level = priority_res["priority_level"]

            if level == "CRITICAL":
                urgency = "IMMEDIATE (0-5 min response target)"
                units = ["SWAT Unit", "2x Patrol Squads", "Paramedic Unit"] if weapons else ["2x Patrol Squads"]
            elif level == "HIGH":
                urgency = "URGENT (5-10 min response target)"
                units = ["1x Patrol Squad", "1x Traffic Control"]
            elif level == "MEDIUM":
                urgency = "STANDARD (10-20 min response target)"
                units = ["1x Patrol Unit"]
            else:
                urgency = "LOW (Routine Queue)"
                units = ["1x Community Officer"]

            evaluated.append(
                PrioritizedIncident(
                    incident_id=inc_id,
                    crime_type=crime_type,
                    location_name=location_name,
                    latitude=lat,
                    longitude=lon,
                    priority_rank=0,  # Will be assigned after sorting
                    composite_priority_score=score,
                    priority_level=level,
                    crime_severity_score=sev_score,
                    weapons_involved=weapons,
                    casualties=casualties,
                    estimated_response_urgency=urgency,
                    recommended_units=units,
                )
            )

        # Sort descending by priority score
        evaluated.sort(key=lambda x: x.composite_priority_score, reverse=True)

        # Assign 1-based ranks
        for rank_idx, item in enumerate(evaluated[:top_k], start=1):
            item.priority_rank = rank_idx

        return evaluated[:top_k]
