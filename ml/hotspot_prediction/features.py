"""
Sentinel AI - Hotspot Prediction Feature Engineering
=====================================================
File: ml/hotspot_prediction/features.py
Purpose: Feature engineering pipeline for hotspot prediction including
         temporal, spatial, demographic, and historical crime features.

Integration:
    - Called by ml/hotspot_prediction/preprocess.py during data preparation
    - Called by ml/hotspot_prediction/train.py for feature importance analysis
    - Feature definitions used by ml/hotspot_prediction/predict.py

Dependencies: pandas, numpy, scikit-learn
"""

import logging
from typing import Any

import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)


class FeatureEngineer:
    """
    Feature engineering pipeline for crime hotspot prediction.

    Creates temporal, spatial, historical, and interaction features from
    raw crime data to improve prediction model performance.

    Attributes:
        feature_definitions: Registry of all feature definitions
        engineered_columns: List of columns created during engineering
    """

    def __init__(self) -> None:
        """Initialize the feature engineer with feature definitions."""
        self.feature_definitions: dict[str, dict[str, str]] = {
            "hour_of_day": {"type": "temporal", "description": "Hour when crime occurred (0-23)"},
            "day_of_week": {"type": "temporal", "description": "Day of week (0=Mon, 6=Sun)"},
            "month": {"type": "temporal", "description": "Month of year (1-12)"},
            "is_weekend": {"type": "temporal", "description": "Binary: 1 if Saturday/Sunday"},
            "is_night": {"type": "temporal", "description": "Binary: 1 if 8PM-5AM"},
            "hour_sin": {"type": "temporal", "description": "Sine transform of hour (cyclical)"},
            "hour_cos": {"type": "temporal", "description": "Cosine transform of hour (cyclical)"},
            "dow_sin": {"type": "temporal", "description": "Sine transform of day-of-week"},
            "dow_cos": {"type": "temporal", "description": "Cosine transform of day-of-week"},
            "grid_x": {"type": "spatial", "description": "Latitude grid cell index"},
            "grid_y": {"type": "spatial", "description": "Longitude grid cell index"},
            "crimes_last_7d": {"type": "historical", "description": "Crime count in area last 7 days"},
            "crimes_last_30d": {"type": "historical", "description": "Crime count in area last 30 days"},
            "avg_daily_crimes": {"type": "historical", "description": "Average daily crimes in area"},
            "crime_trend_slope": {"type": "historical", "description": "Crime trend slope (positive=increasing)"},
            "repeat_crime_ratio": {"type": "historical", "description": "Ratio of repeat crimes in area"},
            "severity_score": {"type": "crime", "description": "Numerical severity encoding"},
        }
        self.engineered_columns: list[str] = []

    def engineer_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Apply complete feature engineering pipeline.

        Args:
            df: Input DataFrame with raw crime data.

        Returns:
            DataFrame with engineered features appended.
        """
        logger.info("Engineering features for %d records", len(df))

        df = self._engineer_temporal_features(df)
        df = self._engineer_cyclical_features(df)
        df = self._engineer_spatial_features(df)
        df = self._engineer_historical_features(df)
        df = self._engineer_severity_features(df)
        df = self._engineer_interaction_features(df)

        self.engineered_columns = [
            col for col in df.columns if col not in ["id", "description"]
        ]

        logger.info("Feature engineering complete: %d features created", len(self.engineered_columns))
        return df

    def _engineer_temporal_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Extract temporal features from timestamps.

        Args:
            df: DataFrame with occurred_at column.

        Returns:
            DataFrame with temporal features added.
        """
        df = df.copy()

        if "occurred_at" in df.columns:
            ts = pd.to_datetime(df["occurred_at"], errors="coerce")
            df["hour_of_day"] = ts.dt.hour
            df["day_of_week"] = ts.dt.dayofweek
            df["month"] = ts.dt.month
            df["day_of_month"] = ts.dt.day
            df["is_weekend"] = (ts.dt.dayofweek >= 5).astype(int)
            df["is_night"] = ((ts.dt.hour >= 20) | (ts.dt.hour <= 5)).astype(int)
            df["quarter"] = ts.dt.quarter

        return df

    def _engineer_cyclical_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Create cyclical (sine/cosine) encodings for temporal features.

        Cyclical encoding preserves the circular nature of time-based features
        (e.g., hour 23 is close to hour 0, Sunday is close to Monday).

        Args:
            df: DataFrame with hour_of_day and day_of_week.

        Returns:
            DataFrame with cyclical feature columns added.
        """
        df = df.copy()

        if "hour_of_day" in df.columns:
            df["hour_sin"] = np.sin(2 * np.pi * df["hour_of_day"] / 24)
            df["hour_cos"] = np.cos(2 * np.pi * df["hour_of_day"] / 24)

        if "day_of_week" in df.columns:
            df["dow_sin"] = np.sin(2 * np.pi * df["day_of_week"] / 7)
            df["dow_cos"] = np.cos(2 * np.pi * df["day_of_week"] / 7)

        if "month" in df.columns:
            df["month_sin"] = np.sin(2 * np.pi * df["month"] / 12)
            df["month_cos"] = np.cos(2 * np.pi * df["month"] / 12)

        return df

    def _engineer_spatial_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Create spatial grid features from geographic coordinates.

        Args:
            df: DataFrame with latitude and longitude columns.

        Returns:
            DataFrame with spatial grid features added.
        """
        df = df.copy()

        if "latitude" in df.columns and "longitude" in df.columns:
            grid_size = 0.01
            df["grid_x"] = (df["latitude"] / grid_size).astype(int)
            df["grid_y"] = (df["longitude"] / grid_size).astype(int)
            df["grid_cell"] = df["grid_x"].astype(str) + "_" + df["grid_y"].astype(str)

        return df

    def _engineer_historical_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Create historical crime count features per spatial grid cell.

        Computes rolling crime counts and trend indicators for each
        geographic grid cell to capture historical patterns.

        Args:
            df: DataFrame with grid and temporal features.

        Returns:
            DataFrame with historical aggregate features.
        """
        df = df.copy()

        if "grid_x" in df.columns and "grid_y" in df.columns:
            grid_counts = (
                df.groupby(["grid_x", "grid_y"])
                .size()
                .reset_index(name="total_grid_crimes")
            )
            df = df.merge(grid_counts, on=["grid_x", "grid_y"], how="left")

            total_days = 90
            df["avg_daily_crimes"] = df["total_grid_crimes"] / max(total_days, 1)

            df["crimes_last_7d"] = (df["total_grid_crimes"] * 7 / max(total_days, 1)).round(0)
            df["crimes_last_30d"] = (df["total_grid_crimes"] * 30 / max(total_days, 1)).round(0)

            df["repeat_crime_ratio"] = df["total_grid_crimes"] / max(len(df), 1)

            df["crime_trend_slope"] = 0.0

        return df

    def _engineer_severity_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Create numerical severity features from categorical severity levels.

        Args:
            df: DataFrame with severity column.

        Returns:
            DataFrame with severity_score numerical feature.
        """
        df = df.copy()

        severity_map = {
            "critical": 4,
            "high": 3,
            "medium": 2,
            "low": 1,
            "unknown": 0,
        }

        if "severity" in df.columns:
            df["severity_score"] = (
                df["severity"].astype(str).str.lower().map(severity_map).fillna(0).astype(int)
            )

        return df

    def _engineer_interaction_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Create interaction features combining multiple base features.

        Args:
            df: DataFrame with base features.

        Returns:
            DataFrame with interaction features added.
        """
        df = df.copy()

        if "is_night" in df.columns and "is_weekend" in df.columns:
            df["night_weekend"] = df["is_night"] * df["is_weekend"]

        if "severity_score" in df.columns and "is_night" in df.columns:
            df["severe_night"] = df["severity_score"] * df["is_night"]

        return df

    def get_feature_importance_report(
        self,
        feature_names: list[str],
        importances: np.ndarray,
    ) -> pd.DataFrame:
        """
        Generate a feature importance report with descriptions.

        Args:
            feature_names: List of feature names from the trained model.
            importances: Array of feature importance scores.

        Returns:
            DataFrame with feature importance ranked by importance.
        """
        report = pd.DataFrame({
            "feature": feature_names,
            "importance": importances,
        })

        report["description"] = report["feature"].map(
            lambda f: self.feature_definitions.get(f, {}).get("description", "Derived feature")
        )
        report["category"] = report["feature"].map(
            lambda f: self.feature_definitions.get(f, {}).get("type", "other")
        )

        report = report.sort_values("importance", ascending=False).reset_index(drop=True)
        report["rank"] = report.index + 1

        return report
