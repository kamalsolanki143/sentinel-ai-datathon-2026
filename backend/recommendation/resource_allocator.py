"""
Sentinel AI - Multi-Resource Allocation Engine
===============================================
File: backend/recommendation/resource_allocator.py
Purpose: Bipartite matching and constrained optimization engine for assigning Officers,
         Patrol Vehicles, Investigation Units, Cyber Units, and Emergency Response Teams
         to high-risk crime zones and active CAD incidents.

Dependencies: scipy (optional), numpy, pydantic, typing, loguru, backend.recommendation.*
"""

from typing import Any, Dict, List, Optional, Tuple
import numpy as np
from loguru import logger
from pydantic import BaseModel, Field

try:
    from scipy.optimize import linear_sum_assignment
    HAS_SCIPY = True
except ImportError:
    HAS_SCIPY = False

from backend.recommendation.rules_engine import ComplianceResult, PolicyRuleEngine
from backend.recommendation.scoring import ScoringEngine
from backend.recommendation.utils import haversine_distance


class ResourceAssignmentItem(BaseModel):
    """Specific resource-to-target assignment payload."""

    assignment_id: str = Field(description="Unique assignment identifier")
    resource_type: str = Field(description="OFFICER, VEHICLE, INVESTIGATION_TEAM, CYBER_UNIT, EMERGENCY_UNIT")
    resource_id: str = Field(description="ID of assigned resource")
    resource_name: str = Field(description="Name or call-sign of resource")
    target_type: str = Field(description="INCIDENT or HOTSPOT_ZONE")
    target_id: str = Field(description="Target ID")
    target_location_name: str = Field(description="Address or sector name")
    match_score: float = Field(description="Normalized MCDA match score (0.0 to 1.0)")
    distance_km: float = Field(description="Proximity distance to target")
    estimated_arrival_minutes: float = Field(description="Estimated travel response time")
    rule_compliance_status: str = Field(default="PASSED", description="PASSED, WARNING, or VIOLATED")
    compliance_warnings: List[str] = Field(default_factory=list)


class ResourceAllocationSummary(BaseModel):
    """Aggregate summary of multi-resource optimization."""

    allocation_id: str = Field(description="Unique allocation session ID")
    total_resources_requested: int = Field(default=0)
    total_resources_assigned: int = Field(default=0)
    unassigned_resources: int = Field(default=0)
    uncovered_targets: int = Field(default=0)
    assignments: List[ResourceAssignmentItem] = Field(default_factory=list)
    average_match_score: float = Field(default=0.0)
    total_travel_distance_km: float = Field(default=0.0)
    optimization_method: str = Field(default="Hungarian Algorithm (Linear Sum Assignment)")


class ResourceAllocator:
    """
    Operations Research Resource Allocator.

    Solves global assignment problems maximizing total utility (matching score) between available
    police units/resources and high-risk incidents/zones subject to shift, vehicle, and policy rules.
    """

    def __init__(
        self,
        scoring_engine: Optional[ScoringEngine] = None,
        rules_engine: Optional[PolicyRuleEngine] = None,
    ) -> None:
        """Initialize Resource Allocator with scoring and rules engines."""
        self.scoring = scoring_engine or ScoringEngine()
        self.rules = rules_engine or PolicyRuleEngine()
        logger.info("ResourceAllocator initialized.")

    def _solve_matching(self, cost_matrix: np.ndarray) -> List[Tuple[int, int]]:
        """
        Solve linear sum assignment problem minimizing total cost (or maximizing score).

        Args:
            cost_matrix: N x M cost matrix (where cost = 1.0 - match_score).

        Returns:
            List of (row_index, col_index) matches.
        """
        if cost_matrix.size == 0:
            return []

        n_rows, n_cols = cost_matrix.shape

        if HAS_SCIPY:
            row_ind, col_ind = linear_sum_assignment(cost_matrix)
            return list(zip(row_ind, col_ind))
        else:
            # Fallback Greedy Best-First Bipartite Matching
            matches = []
            assigned_cols = set()

            # For each row, find column with min cost
            for r in range(n_rows):
                best_col = -1
                best_val = float("inf")
                for c in range(n_cols):
                    if c not in assigned_cols and cost_matrix[r, c] < best_val:
                        best_val = cost_matrix[r, c]
                        best_col = c
                if best_col != -1:
                    matches.append((r, best_col))
                    assigned_cols.add(best_col)
            return matches

    def allocate_resources(
        self,
        available_resources: List[Dict[str, Any]],
        targets: List[Dict[str, Any]],
        emergency_override: bool = False,
    ) -> ResourceAllocationSummary:
        """
        Allocate available multi-department resources to high-risk targets.

        Args:
            available_resources: List of resource dicts (officers, vehicles, specialized teams).
            targets: List of target incident/hotspot dicts.
            emergency_override: Flag to bypass soft policy warnings during crisis.

        Returns:
            ResourceAllocationSummary with optimal assignment pairings.
        """
        if not available_resources or not targets:
            return ResourceAllocationSummary(
                allocation_id=f"ALLOC-{int(np.random.randint(1000,9999))}",
                total_resources_requested=len(targets),
                total_resources_assigned=0,
                unassigned_resources=len(available_resources),
                uncovered_targets=len(targets),
                assignments=[],
            )

        n_res = len(available_resources)
        n_tgt = len(targets)

        # Build N x M Cost Matrix (Cost = 1.0 - Composite Match Score)
        cost_matrix = np.ones((n_res, n_tgt), dtype=np.float64)
        score_matrix = np.zeros((n_res, n_tgt), dtype=np.float64)
        distance_matrix = np.zeros((n_res, n_tgt), dtype=np.float64)

        for i, res in enumerate(available_resources):
            r_lat = float(res.get("latitude", res.get("lat", 0.0)))
            r_lon = float(res.get("longitude", res.get("lon", 0.0)))
            r_spec = res.get("specialization", res.get("type", "General"))
            r_shift = float(res.get("shift_hours_worked", 0.0))
            r_fuel = float(res.get("vehicle_fuel_pct", 100.0))

            for j, tgt in enumerate(targets):
                t_lat = float(tgt.get("latitude", tgt.get("lat", 0.0)))
                t_lon = float(tgt.get("longitude", tgt.get("lon", 0.0)))
                t_crime = tgt.get("crime_type", "general_patrol")
                t_sev = float(tgt.get("crime_severity_score", 0.5))

                dist_km = haversine_distance(r_lat, r_lon, t_lat, t_lon)
                distance_matrix[i, j] = dist_km

                # Calculate components
                avail_score = self.scoring.calculate_officer_availability_score(
                    shift_hours_worked=r_shift,
                    active_incidents_count=int(res.get("active_incidents", 0)),
                    specialization=r_spec,
                    required_specialization=tgt.get("required_specialization"),
                )

                util_score = self.scoring.calculate_resource_utilization_score(
                    distance_km=dist_km,
                    vehicle_fuel_pct=r_fuel,
                )

                sev_score = self.scoring.calculate_crime_severity_score(crime_type=t_crime)

                match_res = self.scoring.compute_overall_priority_score(
                    area_risk_score=float(tgt.get("risk_score", 0.5)),
                    crime_severity_score=max(sev_score, t_sev),
                    officer_availability_score=avail_score,
                    resource_utilization_score=util_score,
                    prediction_confidence_score=float(tgt.get("confidence", 0.85)),
                )

                comp_score = match_res["composite_score"]
                score_matrix[i, j] = comp_score
                cost_matrix[i, j] = 1.0 - comp_score

        # Solve matching
        matches = self._solve_matching(cost_matrix)

        assignments: List[ResourceAssignmentItem] = []
        total_dist = 0.0
        total_score = 0.0

        for r_idx, t_idx in matches:
            res = available_resources[r_idx]
            tgt = targets[t_idx]
            match_score = score_matrix[r_idx, t_idx]
            dist_km = distance_matrix[r_idx, t_idx]

            # Evaluate policy rules
            compliance: ComplianceResult = self.rules.evaluate_officer_assignment(
                officer=res,
                incident_or_zone={**tgt, "distance_km": dist_km},
                emergency_override=emergency_override,
            )

            status = "PASSED" if compliance.is_compliant else "VIOLATED"
            if compliance.is_compliant and compliance.warnings:
                status = "WARNING"

            warn_messages = [w["reason"] for w in compliance.warnings + compliance.violated_rules]

            arr_min = round((dist_km / 40.0) * 60.0, 1)

            assignments.append(
                ResourceAssignmentItem(
                    assignment_id=f"ASN-{r_idx+1:02d}-{t_idx+1:02d}",
                    resource_type=res.get("resource_type", res.get("type", "OFFICER")),
                    resource_id=res.get("id", res.get("officer_id", f"RES-{r_idx+1}")),
                    resource_name=res.get("name", f"Unit #{r_idx+1}"),
                    target_type=tgt.get("target_type", "INCIDENT"),
                    target_id=tgt.get("id", tgt.get("incident_id", f"TGT-{t_idx+1}")),
                    target_location_name=tgt.get("location_name", tgt.get("district", "Sector A")),
                    match_score=round(match_score, 4),
                    distance_km=round(dist_km, 2),
                    estimated_arrival_minutes=arr_min,
                    rule_compliance_status=status,
                    compliance_warnings=warn_messages,
                )
            )

            total_dist += dist_km
            total_score += match_score

        avg_score = round(total_score / len(assignments), 4) if assignments else 0.0

        return ResourceAllocationSummary(
            allocation_id=f"ALLOC-{int(np.random.randint(10000,99999))}",
            total_resources_requested=n_tgt,
            total_resources_assigned=len(assignments),
            unassigned_resources=max(0, n_res - len(assignments)),
            uncovered_targets=max(0, n_tgt - len(assignments)),
            assignments=assignments,
            average_match_score=avg_score,
            total_travel_distance_km=round(total_dist, 2),
            optimization_method="Hungarian Algorithm (Linear Sum Assignment)" if HAS_SCIPY else "Greedy Priority Bipartite Matching",
        )
