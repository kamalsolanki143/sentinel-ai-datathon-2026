"""
Sentinel AI - ML Helper Utilities
====================================
File: ml/utils/helpers.py
Purpose: Shared utilities for model I/O, config loading, data validation,
         and logging setup across all ML modules.

Dependencies: joblib, pandas, numpy
"""

import json, logging, os
from datetime import datetime
from typing import Any, Optional
import joblib, numpy as np, pandas as pd

logger = logging.getLogger(__name__)


def setup_ml_logging(level: str = "INFO") -> None:
    """Configure logging for ML modules."""
    numeric_level = getattr(logging, level.upper(), logging.INFO)
    logging.basicConfig(
        level=numeric_level,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    logger.info("ML logging configured at %s level", level)


def save_model(model: Any, path: str, metadata: dict[str, Any] | None = None) -> str:
    """Save a model with optional metadata sidecar."""
    os.makedirs(os.path.dirname(path), exist_ok=True)
    joblib.dump(model, path)
    if metadata:
        meta_path = path.replace(".joblib", "_metadata.json")
        metadata["saved_at"] = datetime.utcnow().isoformat()
        with open(meta_path, "w", encoding="utf-8") as f:
            json.dump(metadata, f, indent=2, default=str)
        logger.info("Model metadata saved to %s", meta_path)
    logger.info("Model saved to %s", path)
    return path


def load_model(path: str) -> Any:
    """Load a model from disk."""
    if not os.path.exists(path):
        raise FileNotFoundError(f"Model file not found: {path}")
    model = joblib.load(path)
    logger.info("Model loaded from %s", path)
    return model


def validate_dataframe(
    df: pd.DataFrame, required_columns: list[str], min_rows: int = 10,
) -> tuple[bool, list[str]]:
    """Validate DataFrame has required columns and minimum rows."""
    errors = []
    missing = [c for c in required_columns if c not in df.columns]
    if missing:
        errors.append(f"Missing columns: {missing}")
    if len(df) < min_rows:
        errors.append(f"Insufficient rows: {len(df)} < {min_rows}")
    if df.empty:
        errors.append("DataFrame is empty")
    return len(errors) == 0, errors


def load_config(config_path: str) -> dict[str, Any]:
    """Load JSON configuration file."""
    if not os.path.exists(config_path):
        logger.warning("Config not found at %s, using defaults", config_path)
        return {}
    with open(config_path, "r", encoding="utf-8") as f:
        config = json.load(f)
    logger.info("Config loaded from %s", config_path)
    return config


def get_model_dir() -> str:
    """Get the ML model directory, creating it if needed."""
    model_dir = os.getenv("ML_MODEL_DIR", "ml/models")
    os.makedirs(model_dir, exist_ok=True)
    return model_dir


def generate_model_version() -> str:
    """Generate a timestamped model version string."""
    return datetime.utcnow().strftime("v%Y%m%d_%H%M%S")
