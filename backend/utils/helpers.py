"""
Sentinel AI - Utility Helpers
===============================
File: backend/utils/helpers.py
Purpose: General helper functions for date manipulation, formatting,
         and file handling.

Dependencies: datetime, json, loguru
"""

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from loguru import logger


def get_current_utc_time() -> str:
    """Return the current UTC time as an ISO format string."""
    return datetime.now(timezone.utc).isoformat()


def format_currency(amount: float, currency_symbol: str = "$") -> str:
    """Format a float amount into a currency string."""
    return f"{currency_symbol}{amount:,.2f}"


def format_date_friendly(iso_string: str) -> str:
    """Format an ISO date string into a user-friendly format."""
    try:
        dt = datetime.fromisoformat(iso_string.replace('Z', '+00:00'))
        return dt.strftime("%B %d, %Y, %I:%M %p")
    except ValueError:
        return iso_string


def save_json_file(data: Any, file_path: str | Path, ensure_dir: bool = True) -> bool:
    """Save data as formatted JSON to a file."""
    path = Path(file_path)
    if ensure_dir:
        path.parent.mkdir(parents=True, exist_ok=True)
        
    try:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, default=str)
        return True
    except Exception as exc:
        logger.error(f"Failed to save JSON to {path}: {str(exc)}")
        return False


def load_json_file(file_path: str | Path) -> Any:
    """Load JSON data from a file."""
    path = Path(file_path)
    if not path.exists():
        logger.warning(f"JSON file not found: {path}")
        return None
        
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as exc:
        logger.error(f"Failed to load JSON from {path}: {str(exc)}")
        return None
