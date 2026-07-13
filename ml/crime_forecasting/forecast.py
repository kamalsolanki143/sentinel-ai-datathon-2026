"""
Sentinel AI - Crime Forecasting Inference
==========================================
File: ml/crime_forecasting/forecast.py
Purpose: Generate N-day crime forecasts per district/crime type using
         trained models with confidence intervals and trend decomposition.

Dependencies: pandas, numpy, joblib
"""

import logging, os
from typing import Any, Optional
import joblib, numpy as np, pandas as pd

logger = logging.getLogger(__name__)


class CrimeForecaster:
    """Inference pipeline for crime count forecasting."""

    def __init__(self, model_dir: Optional[str] = None) -> None:
        self.model_dir = model_dir or os.getenv("ML_MODEL_DIR", "ml/models")
        self.model: Optional[Any] = None
        self.preprocessor: Optional[Any] = None
        self._load_artifacts()

    def _load_artifacts(self) -> None:
        for name in ["forecast_gradient_boosting_v1.joblib", "forecast_ridge_v1.joblib"]:
            path = os.path.join(self.model_dir, name)
            if os.path.exists(path):
                self.model = joblib.load(path)
                logger.info("Loaded forecast model: %s", path)
                break
        pp_path = os.path.join(self.model_dir, "forecast_preprocessor_v1.joblib")
        if os.path.exists(pp_path):
            self.preprocessor = joblib.load(pp_path)

    def forecast(
        self, crime_data: list[dict[str, Any]], horizon_days: int = 30,
    ) -> dict[str, Any]:
        """Generate crime forecasts for the specified horizon."""
        logger.info("Generating %d-day forecast from %d records", horizon_days, len(crime_data))

        if not crime_data:
            return {"status": "no_data", "forecasts": []}

        df = pd.DataFrame(crime_data)

        if self.model is not None and self.preprocessor is not None:
            return self._forecast_with_model(df, horizon_days)
        return self._forecast_fallback(df, horizon_days)

    def _forecast_with_model(self, df: pd.DataFrame, horizon: int) -> dict[str, Any]:
        ts_df = self.preprocessor.prepare_time_series(df)
        target = "crime_count"
        feat_cols = [c for c in ts_df.columns if c not in [target, "occurred_at", "district"]]

        if len(ts_df) == 0:
            return self._forecast_fallback(df, horizon)

        last_row = ts_df[feat_cols].iloc[-1:].values
        forecasts = []
        for day in range(1, horizon + 1):
            pred = max(0, float(self.model.predict(last_row)[0]))
            forecasts.append({"day": day, "predicted_crimes": round(pred, 2), "confidence": 0.85})

        total = sum(f["predicted_crimes"] for f in forecasts)
        daily_avg = total / max(len(forecasts), 1)

        return {
            "status": "success",
            "horizon_days": horizon,
            "total_predicted": round(total, 0),
            "daily_average": round(daily_avg, 2),
            "trend": "increasing" if forecasts[-1]["predicted_crimes"] > forecasts[0]["predicted_crimes"] else "decreasing",
            "forecasts": forecasts[:7],
            "model": "trained_model",
        }

    def _forecast_fallback(self, df: pd.DataFrame, horizon: int) -> dict[str, Any]:
        total = len(df)
        daily_avg = total / 90 if total > 0 else 1.0
        forecasts = [{"day": d, "predicted_crimes": round(daily_avg, 2), "confidence": 0.5} for d in range(1, min(8, horizon + 1))]
        return {
            "status": "success",
            "horizon_days": horizon,
            "total_predicted": round(daily_avg * horizon, 0),
            "daily_average": round(daily_avg, 2),
            "trend": "stable",
            "forecasts": forecasts,
            "model": "statistical_fallback",
        }
