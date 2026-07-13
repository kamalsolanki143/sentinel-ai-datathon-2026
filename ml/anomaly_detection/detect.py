"""
Sentinel AI - Anomaly Detection Engine
========================================
File: ml/anomaly_detection/detect.py
Purpose: Detect unusual crime patterns using Isolation Forest and
         statistical threshold methods with configurable sensitivity.

Dependencies: pandas, numpy, scikit-learn, joblib
"""

import logging, os
from typing import Any, Optional
import joblib, numpy as np, pandas as pd
from sklearn.ensemble import IsolationForest
from ml.anomaly_detection.preprocess import AnomalyPreprocessor

logger = logging.getLogger(__name__)


class AnomalyDetector:
    """Crime anomaly detection using Isolation Forest and statistical methods."""

    def __init__(self, model_dir: Optional[str] = None, contamination: float = 0.05) -> None:
        self.model_dir = model_dir or os.getenv("ML_MODEL_DIR", "ml/models")
        self.contamination = contamination
        self.preprocessor = AnomalyPreprocessor()
        self.model: Optional[IsolationForest] = None
        os.makedirs(self.model_dir, exist_ok=True)
        self._load_model()

    def _load_model(self) -> None:
        path = os.path.join(self.model_dir, "anomaly_iforest_v1.joblib")
        if os.path.exists(path):
            self.model = joblib.load(path)
            logger.info("Loaded anomaly model: %s", path)
        pp_path = os.path.join(self.model_dir, "anomaly_preprocessor_v1.joblib")
        if os.path.exists(pp_path):
            self.preprocessor = joblib.load(pp_path)

    def train(self, df: pd.DataFrame) -> dict[str, Any]:
        """Train the Isolation Forest anomaly detector."""
        logger.info("Training anomaly detector on %d records", len(df))
        X = self.preprocessor.preprocess(df, fit=True)

        self.model = IsolationForest(
            n_estimators=200, contamination=self.contamination,
            max_samples="auto", random_state=42, n_jobs=-1,
        )
        self.model.fit(X)

        scores = self.model.decision_function(X)
        predictions = self.model.predict(X)
        n_anomalies = int(np.sum(predictions == -1))

        joblib.dump(self.model, os.path.join(self.model_dir, "anomaly_iforest_v1.joblib"))
        joblib.dump(self.preprocessor, os.path.join(self.model_dir, "anomaly_preprocessor_v1.joblib"))

        logger.info("Anomaly detector trained: %d anomalies in %d records", n_anomalies, len(df))
        return {"total": len(df), "anomalies": n_anomalies, "anomaly_rate": round(n_anomalies / max(len(df), 1), 4)}

    def detect(self, crime_data: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """Detect anomalies in crime data."""
        if not crime_data:
            return []

        logger.info("Running anomaly detection on %d records", len(crime_data))
        df = pd.DataFrame(crime_data)

        if self.model is not None:
            return self._detect_with_model(df)
        return self._detect_statistical(df)

    def _detect_with_model(self, df: pd.DataFrame) -> list[dict[str, Any]]:
        X = self.preprocessor.preprocess(df, fit=False)
        predictions = self.model.predict(X)
        scores = self.model.decision_function(X)

        anomalies = []
        for idx in range(len(predictions)):
            if predictions[idx] == -1:
                anomaly = {
                    "index": idx,
                    "anomaly_score": round(float(-scores[idx]), 4),
                    "severity": "high" if scores[idx] < -0.3 else "medium",
                    "model": "isolation_forest",
                }
                if "district" in df.columns:
                    anomaly["district"] = str(df.iloc[idx].get("district", "unknown"))
                if "crime_type" in df.columns:
                    anomaly["crime_type"] = str(df.iloc[idx].get("crime_type", "unknown"))
                anomalies.append(anomaly)

        logger.info("Detected %d anomalies out of %d records", len(anomalies), len(df))
        return anomalies

    def _detect_statistical(self, df: pd.DataFrame) -> list[dict[str, Any]]:
        """Statistical fallback: flag records more than 2 std from mean in key metrics."""
        anomalies = []
        if "district" in df.columns:
            counts = df["district"].value_counts()
            mean_c, std_c = counts.mean(), counts.std()
            for district, count in counts.items():
                if std_c > 0 and abs(count - mean_c) > 2 * std_c:
                    anomalies.append({
                        "district": str(district), "crime_count": int(count),
                        "anomaly_score": round(abs(count - mean_c) / max(std_c, 1), 4),
                        "severity": "high" if count > mean_c else "medium",
                        "model": "statistical",
                    })
        return anomalies
