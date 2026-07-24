"""
Sentinel AI - Recommendation Utilities
======================================
File: backend/recommendation/utils.py
Purpose: Geospatial calculations, distance matrix generation, mathematical normalization,
         temporal window parsing, and payload formatters for the Recommendation Engine.

Dependencies: math, typing, numpy, loguru
"""

import math
from datetime import datetime, time
from typing import Any, Dict, List, Optional, Tuple, Union
import numpy as np
from loguru import logger

EARTH_RADIUS_KM = 6371.0088  # Mean Earth radius in kilometers


def haversine_distance(
    lat1: float, lon1: float, lat2: float, lon2: float
) -> float:
    """
    Calculate the great circle distance between two points on the Earth in kilometers
    using the Haversine formula.

    Args:
        lat1: Latitude of point 1 in degrees.
        lon1: Longitude of point 1 in degrees.
        lat2: Latitude of point 2 in degrees.
        lon2: Longitude of point 2 in degrees.

    Returns:
        Distance in kilometers between the two coordinates.
    """
    try:
        # Convert decimal degrees to radians
        phi1, lambda1 = math.radians(lat1), math.radians(lon1)
        phi2, lambda2 = math.radians(lat2), math.radians(lon2)

        dphi = phi2 - phi1
        dlambda = lambda2 - lambda1

        a = (
            math.sin(dphi / 2.0) ** 2
            + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2.0) ** 2
        )
        c = 2.0 * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))
        distance = EARTH_RADIUS_KM * c

        return round(float(distance), 4)
    except Exception as exc:
        logger.error(f"Error computing haversine distance ({lat1},{lon1}) -> ({lat2},{lon2}): {exc}")
        return 0.0


def calculate_distance_matrix(
    origin_coords: List[Tuple[float, float]],
    destination_coords: List[Tuple[float, float]],
) -> np.ndarray:
    """
    Compute a 2D distance matrix (N x M) between N origins and M destinations in kilometers.

    Args:
        origin_coords: List of (lat, lon) tuples for origins.
        destination_coords: List of (lat, lon) tuples for destinations.

    Returns:
        2D numpy array of shape (N, M) containing pairwise distances in km.
    """
    n = len(origin_coords)
    m = len(destination_coords)

    if n == 0 or m == 0:
        return np.zeros((n, m))

    matrix = np.zeros((n, m), dtype=np.float64)

    for i in range(n):
        lat1, lon1 = origin_coords[i]
        for j in range(m):
            lat2, lon2 = destination_coords[j]
            matrix[i, j] = haversine_distance(lat1, lon1, lat2, lon2)

    return matrix


def calculate_estimated_travel_time_minutes(
    distance_km: float, average_speed_kmh: float = 40.0
) -> float:
    """
    Estimate travel time in minutes based on distance and average urban patrol vehicle speed.

    Args:
        distance_km: Travel distance in km.
        average_speed_kmh: Average travel speed in km/h (default 40 km/h for emergency response/patrol).

    Returns:
        Estimated travel time in minutes.
    """
    if average_speed_kmh <= 0:
        average_speed_kmh = 40.0
    hours = distance_km / average_speed_kmh
    minutes = hours * 60.0
    return round(float(minutes), 2)


def normalize_scores(
    scores: List[float], min_val: float = 0.0, max_val: float = 1.0
) -> List[float]:
    """
    Min-Max normalize a list of numerical scores into [min_val, max_val] range.

    Args:
        scores: Raw numerical scores.
        min_val: Target minimum boundary.
        max_val: Target maximum boundary.

    Returns:
        Normalized score list.
    """
    if not scores:
        return []

    arr = np.array(scores, dtype=np.float64)
    arr_min = np.min(arr)
    arr_max = np.max(arr)

    if math.isclose(arr_min, arr_max):
        # If all values are identical, return uniform midrange values
        mid = (min_val + max_val) / 2.0
        return [round(mid, 4)] * len(scores)

    normalized = min_val + (arr - arr_min) * (max_val - min_val) / (arr_max - arr_min)
    return [round(float(v), 4) for v in normalized]


def softmax(logits: List[float], temperature: float = 1.0) -> List[float]:
    """
    Compute softmax probabilities over input logits with optional temperature scaling.

    Args:
        logits: Input values.
        temperature: Temperature parameter (> 0). Higher values flatten the distribution.

    Returns:
        Probability distribution vector summing to 1.0.
    """
    if not logits:
        return []

    temp = max(1e-5, temperature)
    arr = np.array(logits, dtype=np.float64) / temp
    exps = np.exp(arr - np.max(arr))  # Subtract max for numerical stability
    probs = exps / np.sum(exps)

    return [round(float(p), 4) for p in probs]


def sigmoid(x: float, steepness: float = 1.0, midpoint: float = 0.0) -> float:
    """
    Compute standard or generalized logistic sigmoid function.

    Args:
        x: Input scalar.
        steepness: Growth rate / steepness of curve.
        midpoint: Sigmoidal inflection point.

    Returns:
        Scalar value between 0.0 and 1.0.
    """
    try:
        val = 1.0 / (1.0 + math.exp(-steepness * (x - midpoint)))
        return round(float(val), 4)
    except OverflowError:
        return 0.0 if (x - midpoint) < 0 else 1.0


def is_time_in_window(
    check_time: time, start_time: time, end_time: time
) -> bool:
    """
    Determine if a time falls within a given operational shift window (handles overnight wraps).

    Args:
        check_time: The time object to test.
        start_time: Shift start time.
        end_time: Shift end time.

    Returns:
        True if check_time is within shift window, False otherwise.
    """
    if start_time <= end_time:
        return start_time <= check_time <= end_time
    else:  # Overnight shift (e.g. 22:00 to 06:00)
        return check_time >= start_time or check_time <= end_time


def calculate_bounding_box(
    center_lat: float, center_lon: float, radius_km: float
) -> Dict[str, float]:
    """
    Calculate latitude and longitude bounding box for a given center point and radius.

    Args:
        center_lat: Latitude of center.
        center_lon: Longitude of center.
        radius_km: Radius in kilometers.

    Returns:
        Dictionary with min_lat, max_lat, min_lon, max_lon.
    """
    lat_delta = radius_km / 111.0  # Approx 111km per degree latitude
    lon_delta = radius_km / (111.0 * math.cos(math.radians(center_lat)))

    return {
        "min_lat": round(center_lat - lat_delta, 6),
        "max_lat": round(center_lat + lat_delta, 6),
        "min_lon": round(center_lon - abs(lon_delta), 6),
        "max_lon": round(center_lon + abs(lon_delta), 6),
    }


def format_geo_point(lat: float, lon: float) -> Dict[str, float]:
    """Format coordinate pair into standardized GeoJSON coordinate dict."""
    return {"latitude": round(lat, 6), "longitude": round(lon, 6)}
