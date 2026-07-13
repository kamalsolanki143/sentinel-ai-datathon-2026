"""
Sentinel AI - Crime Forecasting Training Pipeline
===================================================
File: ml/crime_forecasting/train.py
Purpose: Train time-series regression models for crime count forecasting
         using lag-based features with Ridge and Gradient Boosting regressors.

Dependencies: pandas, numpy, scikit-learn, joblib
"""

import logging, os
from datetime import datetime
from typing import Any, Optional
import joblib, numpy as np, pandas as pd
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.linear_model import Ridge
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import TimeSeriesSplit
from ml.crime_forecasting.preprocess import ForecastPreprocessor

logger = logging.getLogger(__name__)


class ForecastTrainer:
    """Training pipeline for crime forecasting models."""

    def __init__(self, model_dir: Optional[str] = None) -> None:
        self.model_dir = model_dir or os.getenv("ML_MODEL_DIR", "ml/models")
        self.preprocessor = ForecastPreprocessor()
        self.best_model: Optional[Any] = None
        self.best_model_name: str = ""
        os.makedirs(self.model_dir, exist_ok=True)

    def train(self, df: pd.DataFrame) -> dict[str, Any]:
        """Execute full training pipeline."""
        logger.info("Starting forecast training with %d records", len(df))
        start = datetime.utcnow()
        ts_df = self.preprocessor.prepare_time_series(df)

        target = "crime_count"
        feature_cols = [c for c in ts_df.columns if c not in [target, "occurred_at", "district"]]
        X = ts_df[feature_cols].values
        y = ts_df[target].values

        split_idx = int(len(X) * 0.8)
        X_train, X_test = X[:split_idx], X[split_idx:]
        y_train, y_test = y[:split_idx], y[split_idx:]

        ridge = Ridge(alpha=1.0)
        ridge.fit(X_train, y_train)
        ridge_metrics = self._evaluate(ridge, X_test, y_test, "Ridge")

        gb = GradientBoostingRegressor(n_estimators=200, max_depth=5, learning_rate=0.1, random_state=42)
        gb.fit(X_train, y_train)
        gb_metrics = self._evaluate(gb, X_test, y_test, "GradientBoosting")

        if gb_metrics["mae"] <= ridge_metrics["mae"]:
            self.best_model, self.best_model_name = gb, "gradient_boosting"
            best_metrics = gb_metrics
        else:
            self.best_model, self.best_model_name = ridge, "ridge"
            best_metrics = ridge_metrics

        joblib.dump(self.best_model, os.path.join(self.model_dir, f"forecast_{self.best_model_name}_v1.joblib"))
        joblib.dump(self.preprocessor, os.path.join(self.model_dir, "forecast_preprocessor_v1.joblib"))

        duration = (datetime.utcnow() - start).total_seconds()
        logger.info("Forecast training complete: model=%s, MAE=%.4f in %.1fs", self.best_model_name, best_metrics["mae"], duration)
        return {"best_model": self.best_model_name, "metrics": best_metrics, "duration_s": round(duration, 2)}

    def _evaluate(self, model: Any, X_test: np.ndarray, y_test: np.ndarray, name: str) -> dict[str, float]:
        y_pred = model.predict(X_test)
        y_pred = np.maximum(y_pred, 0)
        metrics = {
            "mae": round(mean_absolute_error(y_test, y_pred), 4),
            "rmse": round(np.sqrt(mean_squared_error(y_test, y_pred)), 4),
            "r2": round(r2_score(y_test, y_pred), 4),
            "mape": round(np.mean(np.abs((y_test - y_pred) / np.maximum(y_test, 1))) * 100, 2),
        }
        logger.info("%s: MAE=%.4f, RMSE=%.4f, R²=%.4f, MAPE=%.2f%%", name, metrics["mae"], metrics["rmse"], metrics["r2"], metrics["mape"])
        return metrics
