"""
Sentinel AI - Anomaly Detection Preprocessing
===============================================
File: ml/anomaly_detection/preprocess.py
Purpose: Anomaly-specific preprocessing with outlier-aware scaling and
         temporal windowing for crime anomaly detection.

Dependencies: pandas, numpy, scikit-learn
"""

import logging
from typing import Optional
import numpy as np, pandas as pd
from sklearn.preprocessing import RobustScaler, LabelEncoder

logger = logging.getLogger(__name__)


class AnomalyPreprocessor:
    """Preprocessor for anomaly detection pipeline."""

    def __init__(self) -> None:
        self.scaler = RobustScaler()
        self.label_encoders: dict[str, LabelEncoder] = {}
        self.feature_columns: list[str] = []

    def preprocess(self, df: pd.DataFrame, fit: bool = True) -> np.ndarray:
        """Preprocess crime data for anomaly detection."""
        logger.info("Preprocessing %d records for anomaly detection", len(df))
        df = df.copy()

        if "occurred_at" in df.columns:
            dt = pd.to_datetime(df["occurred_at"], errors="coerce")
            df["hour"] = dt.dt.hour
            df["dow"] = dt.dt.dayofweek
            df["month"] = dt.dt.month
            df["is_weekend"] = (dt.dt.dayofweek >= 5).astype(int)
            df = df.drop(columns=["occurred_at"], errors="ignore")

        cat_cols = ["crime_type", "district", "severity"]
        for col in cat_cols:
            if col not in df.columns:
                continue
            if fit:
                le = LabelEncoder()
                df[col] = le.fit_transform(df[col].astype(str))
                self.label_encoders[col] = le
            elif col in self.label_encoders:
                le = self.label_encoders[col]
                df[col] = df[col].astype(str).map(
                    lambda x, _le=le: _le.transform([x])[0] if x in _le.classes_ else -1
                )

        drop_cols = ["id", "description", "fir_number", "modus_operandi", "status",
                     "station", "reported_at", "created_at", "updated_at"]
        df = df.drop(columns=[c for c in drop_cols if c in df.columns], errors="ignore")

        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        self.feature_columns = numeric_cols
        df = df[numeric_cols].fillna(0)

        if fit:
            return self.scaler.fit_transform(df.values)
        return self.scaler.transform(df.values)
