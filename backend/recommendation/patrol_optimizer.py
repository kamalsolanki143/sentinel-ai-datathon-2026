"""
Sentinel AI - Patrol Route & Shift Optimization Engine
======================================================
File: backend/recommendation/patrol_optimizer.py
Purpose: Optimizes police patrol routes, shift schedules, hotspot coverage, and vehicle travel paths
         using Traveling Salesperson Problem (TSP) 2-Opt algorithms and distance minimization heuristics.

Dependencies: pydantic, typing, numpy, loguru, backend.recommendation.utils
"""

from typing import Any, Dict, List, Optional, Tuple
import numpy as np
from loguru import logger
from pydantic import BaseModel, Field

from backend.recommendation.utils import (
    calculate_distance_matrix,
    calculate_estimated_travel_time_minutes,
    haversine_distance,
)


class PatrolWaypoint(BaseModel):
    """Individual waypoint coordinate stop on an optimized patrol route."""

    stop_number: int = Field(description="Order index of stop in route sequence")
    location_id: str = Field(description="Hotspot or landmark ID")
    location_name: str = Field(description="Name or street address")
    latitude: float = Field(description="Latitude coordinate")
    longitude: float = Field(description="Longitude coordinate")
    distance_from_prev_km: float = Field(default=0.0)
    estimated_travel_time_min: float = Field(default=0.0)
    target_dwell_time_min: float = Field(default=15.0, description="Recommended patrol stop duration")
    risk_level: str = Field(default="MEDIUM")


class PatrolRoutePlan(BaseModel):
    """Complete optimized patrol route package for an officer or vehicle unit."""

    route_id: str = Field(description="Unique route plan identifier e.g. RTR-101")
    unit_id: str = Field(description="Assigned officer or vehicle unit ID")
    station_name: str = Field(description="Origin police station name")
    shift_name: str = Field(default="Day Shift (08:00 - 16:00)")
    waypoints: List[PatrolWaypoint] = Field(default_factory=list)
    total_distance_km: float = Field(description="Total round-trip travel distance in km")
    total_travel_time_min: float = Field(description="Total travel time in minutes")
    total_patrol_duration_min: float = Field(description="Total shift duration including dwell time")
    coverage_score: float = Field(description="Percentage of high-risk zone score covered (0.0 to 1.0)")
    optimized_speed_kmh: float = Field(default=40.0)


class PatrolOptimizer:
    """
    Operations Research Patrol Route & Shift Optimizer.

    Uses graph algorithms (Nearest Neighbor + 2-Opt TSP local search) to solve
    multi-waypoint route optimization, minimizing travel distance while maximizing hotspot coverage.
    """

    def __init__(self, average_speed_kmh: float = 40.0) -> None:
        """Initialize Patrol Optimizer with default travel speed in km/h."""
        self.average_speed_kmh = average_speed_kmh
        logger.info("PatrolOptimizer initialized.")

    def solve_tsp_2opt(self, distance_matrix: np.ndarray) -> List[int]:
        """
        Solve Traveling Salesperson Problem using Nearest-Neighbor initial tour + 2-Opt local search refinement.

        Args:
            distance_matrix: NxN numpy array of pairwise distances.

        Returns:
            List of node indices representing the optimized visiting order (0 is origin).
        """
        n = distance_matrix.shape[0]
        if n <= 1:
            return list(range(n))
        if n == 2:
            return [0, 1, 0]

        # Step 1: Nearest Neighbor Heuristic Construction
        unvisited = set(range(1, n))
        current = 0
        tour = [0]

        while unvisited:
            next_node = min(unvisited, key=lambda node: distance_matrix[current, node])
            tour.append(next_node)
            unvisited.remove(next_node)
            current = next_node

        tour.append(0)  # Return to origin station

        # Step 2: 2-Opt Local Search Improvement
        improved = True
        max_iterations = 50
        iteration = 0

        while improved and iteration < max_iterations:
            improved = False
            iteration += 1
            for i in range(1, n - 1):
                for j in range(i + 1, n):
                    # Check distance difference if edges (i-1, i) and (j, j+1) are swapped with (i-1, j) and (i, j+1)
                    a, b = tour[i - 1], tour[i]
                    c, d = tour[j], tour[j + 1]

                    delta = (
                        (distance_matrix[a, c] + distance_matrix[b, d])
                        - (distance_matrix[a, b] + distance_matrix[c, d])
                    )

                    if delta < -1e-5:  # Found a shorter route swap
                        tour[i : j + 1] = reversed(tour[i : j + 1])
                        improved = True

        return tour

    def optimize_patrol_route(
        self,
        origin_station: Dict[str, Any],
        hotspots: List[Dict[str, Any]],
        unit_id: str = "PATROL-UNIT-01",
        shift_duration_hours: float = 8.0,
        dwell_time_per_stop_min: float = 15.0,
    ) -> PatrolRoutePlan:
        """
        Build an optimal patrol route starting and ending at origin station, visiting key hotspots.

        Args:
            origin_station: Dict with name, latitude, longitude of starting station.
            hotspots: List of hotspot dicts with id, name, latitude, longitude, risk_level, risk_score.
            unit_id: ID of officer or patrol vehicle.
            shift_duration_hours: Maximum total shift time limit.
            dwell_time_per_stop_min: Minutes spent patrolling each stop.

        Returns:
            PatrolRoutePlan containing structured waypoints, total km, travel time, and coverage.
        """
        station_lat = float(origin_station.get("latitude", 0.0))
        station_lon = float(origin_station.get("longitude", 0.0))
        station_name = origin_station.get("name", "Central Station")

        if not hotspots:
            # Empty route fallback
            return PatrolRoutePlan(
                route_id=f"RTR-{unit_id}-001",
                unit_id=unit_id,
                station_name=station_name,
                waypoints=[],
                total_distance_km=0.0,
                total_travel_time_min=0.0,
                total_patrol_duration_min=0.0,
                coverage_score=0.0,
            )

        # Build list of all locations [Station (index 0), Hotspot 1, Hotspot 2, ...]
        all_points = [(station_lat, station_lon)] + [
            (float(h.get("latitude", 0.0)), float(h.get("longitude", 0.0))) for h in hotspots
        ]

        # Compute full distance matrix
        dist_matrix = calculate_distance_matrix(all_points, all_points)

        # Solve TSP route
        tour_indices = self.solve_tsp_2opt(dist_matrix)

        # Build waypoints list and calculate metrics
        waypoints: List[PatrolWaypoint] = []
        total_dist_km = 0.0
        total_travel_min = 0.0
        total_dwell_min = 0.0

        for stop_order, idx in enumerate(tour_indices):
            if idx == 0:
                loc_id = origin_station.get("id", "STATION-01")
                loc_name = f"{station_name} (Station Start)" if stop_order == 0 else f"{station_name} (Station Return)"
                lat, lon = station_lat, station_lon
                risk_lvl = "STATION"
                dwell = 0.0
            else:
                h_item = hotspots[idx - 1]
                loc_id = h_item.get("zone_id", h_item.get("id", f"HOTSPOT-{idx}"))
                loc_name = h_item.get("name", h_item.get("district", f"Zone Sector {idx}"))
                lat = float(h_item.get("latitude", 0.0))
                lon = float(h_item.get("longitude", 0.0))
                risk_lvl = h_item.get("risk_level", "HIGH")
                dwell = dwell_time_per_stop_min

            if stop_order > 0:
                prev_idx = tour_indices[stop_order - 1]
                leg_dist = dist_matrix[prev_idx, idx]
                leg_travel_time = calculate_estimated_travel_time_minutes(leg_dist, self.average_speed_kmh)
            else:
                leg_dist = 0.0
                leg_travel_time = 0.0

            total_dist_km += leg_dist
            total_travel_min += leg_travel_time
            total_dwell_min += dwell

            waypoints.append(
                PatrolWaypoint(
                    stop_number=stop_order + 1,
                    location_id=loc_id,
                    location_name=loc_name,
                    latitude=lat,
                    longitude=lon,
                    distance_from_prev_km=round(leg_dist, 2),
                    estimated_travel_time_min=round(leg_travel_time, 2),
                    target_dwell_time_min=dwell,
                    risk_level=risk_lvl,
                )
            )

        total_shift_min = total_travel_min + total_dwell_min

        # Calculate coverage score (ratio of visited hotspot risk scores vs total)
        visited_hotspot_indices = set(tour_indices[1:-1])
        total_possible_risk = sum([float(h.get("risk_score", 0.5)) for h in hotspots]) or 1.0
        visited_risk = sum([float(hotspots[i - 1].get("risk_score", 0.5)) for i in visited_hotspot_indices])
        coverage_score = round(min(1.0, visited_risk / total_possible_risk), 4)

        return PatrolRoutePlan(
            route_id=f"RTR-{unit_id}-{int(np.random.randint(100,999))}",
            unit_id=unit_id,
            station_name=station_name,
            waypoints=waypoints,
            total_distance_km=round(total_dist_km, 2),
            total_travel_time_min=round(total_travel_min, 2),
            total_patrol_duration_min=round(total_shift_min, 2),
            coverage_score=coverage_score,
            optimized_speed_kmh=self.average_speed_kmh,
        )
