"""
Sentinel AI - Data Validation Utilities
=========================================
File: backend/utils/validators.py
Purpose: Functions for validating inputs such as crime data, locations,
         and standard requests before processing.

Dependencies: re
"""

import re
from typing import Any
from backend.utils.constants import RISK_LEVELS, DISTRICTS


def validate_crime_category(category: str, supported_categories: list[str]) -> bool:
    """Check if the provided crime category is supported."""
    return category.lower() in [c.lower() for c in supported_categories]


def validate_location(latitude: float, longitude: float) -> bool:
    """Basic validation for geographic coordinates."""
    if not isinstance(latitude, (int, float)) or not isinstance(longitude, (int, float)):
        return False
    return -90.0 <= latitude <= 90.0 and -180.0 <= longitude <= 180.0


def validate_district(district: str) -> bool:
    """Validate if the district is known."""
    # Assuming case-insensitive match for basic validation
    return district.lower() in [d.lower() for d in DISTRICTS]


def validate_risk_level(level: str) -> bool:
    """Check if the risk level is one of the standard enum values."""
    return level.lower() in RISK_LEVELS


def is_valid_uuid(val: str) -> bool:
    """Regex validation for UUID v4 format."""
    uuid_pattern = re.compile(
        r'^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$', 
        re.IGNORECASE
    )
    return bool(uuid_pattern.match(val))


def sanitize_input(text: str) -> str:
    """Basic HTML/script tag stripping to prevent rudimentary injection."""
    if not text:
        return ""
    # Strip basic HTML tags
    clean = re.sub(r'<[^>]*>', '', text)
    return clean.strip()
