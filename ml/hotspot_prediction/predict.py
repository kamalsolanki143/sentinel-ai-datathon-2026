"""
Sentinel AI - Hotspot Prediction Inference
============================================
File: ml/hotspot_prediction/predict.py
Purpose: Load trained hotspot models and run batch/single predictions
         with confidence scores and risk level classification.

Integration:
    - Called by backend/agents/prediction_agent.py for ML predictions
    - Loads models saved by ml/hotspot_prediction/train.py
    - Uses preprocessor from ml/hotspot_prediction/preprocess.py

Dependencies: pandas, numpy, scikit-learn, joblib
"""

import logging
import os
from typing import Any, Optional

import joblib
import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)


class HotspotPredictor:
    """
    Inference pipeline for crime hotspot prediction.

    Loads trained models and preprocessors, runs predictions on new data,
    and returns structured results with confidence scores.

    Attributes:
        model_dir: Directory containing trained models
        model: Loaded trained classifier
        preprocessor: Loaded fitted preprocessor
        model_version: Version string of the loaded model
    """

    def __init__(self, model_dir: Optional[str] = None) -> None:
        """
        Initialize the hotspot predictor by loading trained artifacts.

        Args:
            model_dir: Directory containing trained models. Defaults to ml/models/.
        """
        self.model_dir: str = model_dir or os.getenv("ML_MODEL_DIR", "ml/models")
        self.model: Optional[Any] = None
        self.preprocessor: Optional[Any] = None
        self.model_version: str = "v1"

        self._load_model()
        logger.info("HotspotPredictor initialized, model_dir=%s", self.model_dir)

    def _load_model(self) -> None:
        """Load the trained model and preprocessor from disk."""
        model_candidates = [
            "hotspot_random_forest_v1.joblib",
            "hotspot_gradient_boosting_v1.joblib",
        ]

        for candidate in model_candidates:
            model_path = os.path.join(self.model_dir, candidate)
            if os.path.exists(model_path):
                self.model = joblib.load(model_path)
                self.model_version = candidate.replace(".joblib", "")
                logger.info("Loaded model: %s", model_path)
                break

        preprocessor_path = os.path.join(self.model_dir, "hotspot_preprocessor_v1.joblib")
        if os.path.exists(preprocessor_path):
            self.preprocessor = joblib.load(preprocessor_path)
            logger.info("Loaded preprocessor: %s", preprocessor_path)

    def predict(self, crime_data: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """
        Run hotspot predictions on crime data.

        Args:
            crime_data: List of crime record dictionaries.

        Returns:
            List of prediction result dictionaries with risk levels and confidence.
        """
        if not crime_data:
            logger.warning("Empty crime data provided for prediction")
            return []

        logger.info("Running hotspot prediction on %d records", len(crime_data))

        try:
            df = pd.DataFrame(crime_data)

            if self.model is not None and self.preprocessor is not None:
                return self._predict_with_model(df)
            else:
                logger.warning("Model not loaded, using statistical fallback")
                return self._predict_fallback(df)

        except Exception as exc:
            logger.error("Hotspot prediction failed: %s", str(exc))
            return self._predict_fallback(pd.DataFrame(crime_data))

    def _predict_with_model(self, df: pd.DataFrame) -> list[dict[str, Any]]:
        """
        Run predictions using the trained ML model.

        Args:
            df: DataFrame of crime records.

        Returns:
            List of prediction dictionaries with ML-based risk assessment.
        """
        X = self.preprocessor.preprocess_inference_data(df)
        predictions = self.model.predict(X)
        probabilities = (
            self.model.predict_proba(X)[:, 1]
            if hasattr(self.model, "predict_proba")
            else predictions.astype(float)
        )

        results = []
        for idx in range(len(predictions)):
            prob = float(probabilities[idx])
            risk_level = self._probability_to_risk_level(prob)

            result = {
                "index": idx,
                "is_hotspot": bool(predictions[idx]),
                "confidence": round(prob, 4),
                "risk_level": risk_level,
                "model_version": self.model_version,
            }

            if "district" in df.columns:
                result["district"] = str(df.iloc[idx].get("district", "unknown"))
            if "latitude" in df.columns and "longitude" in df.columns:
                result["latitude"] = float(df.iloc[idx].get("latitude", 0))
                result["longitude"] = float(df.iloc[idx].get("longitude", 0))

            results.append(result)

        hotspot_count = sum(1 for r in results if r["is_hotspot"])
        logger.info(
            "ML prediction complete: %d/%d flagged as hotspots",
            hotspot_count, len(results),
        )

        return results

    def _predict_fallback(self, df: pd.DataFrame) -> list[dict[str, Any]]:
        """
        Generate predictions using statistical aggregation when model is unavailable.

        Args:
            df: DataFrame of crime records.

        Returns:
            List of fallback prediction dictionaries based on crime density.
        """
        logger.info("Using statistical fallback for hotspot prediction")

        results = []

        if "district" in df.columns:
            district_counts = df["district"].value_counts().to_dict()
            total = len(df)
            threshold = total * 0.1

            districts_seen = set()
            for _, row in df.iterrows():
                district = str(row.get("district", "unknown"))
                if district in districts_seen:
                    continue
                districts_seen.add(district)

                count = district_counts.get(district, 0)
                ratio = count / max(total, 1)
                is_hotspot = count >= threshold
                confidence = min(0.95, ratio * 2)
                risk_level = self._probability_to_risk_level(confidence)

                results.append({
                    "district": district,
                    "crime_count": count,
                    "is_hotspot": is_hotspot,
                    "confidence": round(confidence, 4),
                    "risk_level": risk_level,
                    "model_version": "statistical_fallback",
                })
        else:
            results.append({
                "district": "all",
                "crime_count": len(df),
                "is_hotspot": len(df) > 50,
                "confidence": 0.5,
                "risk_level": "medium",
                "model_version": "statistical_fallback",
            })

        return results

    @staticmethod
    def _probability_to_risk_level(probability: float) -> str:
        """
        Convert prediction probability to human-readable risk level.

        Args:
            probability: Model prediction probability (0-1).

        Returns:
            Risk level string: critical, high, medium, or low.
        """
        if probability >= 0.8:
            return "critical"
        elif probability >= 0.6:
            return "high"
        elif probability >= 0.4:
            return "medium"
        else:
            return "low"
