"""
Sentinel AI - Hotspot Prediction Training Pipeline
====================================================
File: ml/hotspot_prediction/train.py
Purpose: Train, evaluate, and persist hotspot prediction models using
         Random Forest and Gradient Boosting ensemble classifiers.

Integration:
    - Uses ml/hotspot_prediction/preprocess.py for data preparation
    - Uses ml/hotspot_prediction/features.py for feature engineering
    - Uses ml/utils/metrics.py for evaluation metrics
    - Trained models consumed by ml/hotspot_prediction/predict.py
    - Called by prediction_agent.py for model retraining

Dependencies: pandas, numpy, scikit-learn, joblib
"""

import logging
import os
from datetime import datetime
from typing import Any, Optional

import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import GradientBoostingClassifier, RandomForestClassifier
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
)
from sklearn.model_selection import GridSearchCV, cross_val_score

from ml.hotspot_prediction.preprocess import HotspotPreprocessor

logger = logging.getLogger(__name__)


class HotspotTrainer:
    """
    Training pipeline for crime hotspot prediction models.

    Trains and evaluates Random Forest and Gradient Boosting classifiers,
    performs hyperparameter tuning, and persists the best model.

    Attributes:
        model_dir: Directory path for saving trained models
        preprocessor: HotspotPreprocessor instance
        best_model: Best performing trained model
        best_model_name: Name of the best model
        training_metrics: Dictionary of evaluation metrics
    """

    def __init__(self, model_dir: Optional[str] = None) -> None:
        """
        Initialize the hotspot training pipeline.

        Args:
            model_dir: Directory for model persistence. Defaults to ml/models/.
        """
        self.model_dir: str = model_dir or os.getenv("ML_MODEL_DIR", "ml/models")
        self.preprocessor = HotspotPreprocessor()
        self.best_model: Optional[Any] = None
        self.best_model_name: str = ""
        self.training_metrics: dict[str, Any] = {}

        os.makedirs(self.model_dir, exist_ok=True)
        logger.info("HotspotTrainer initialized, model_dir=%s", self.model_dir)

    def train(
        self,
        df: pd.DataFrame,
        tune_hyperparameters: bool = False,
    ) -> dict[str, Any]:
        """
        Execute the full training pipeline.

        Steps:
        1. Preprocess and split data
        2. Train Random Forest classifier
        3. Train Gradient Boosting classifier
        4. Evaluate both models
        5. Select best model
        6. Save best model and preprocessor

        Args:
            df: Raw crime data DataFrame.
            tune_hyperparameters: Whether to run GridSearchCV (slower but better).

        Returns:
            Dictionary with training metrics and model info.
        """
        logger.info("Starting hotspot training pipeline with %d records", len(df))
        start_time = datetime.utcnow()

        X_train, X_test, y_train, y_test = self.preprocessor.preprocess_training_data(df)

        logger.info("Training Random Forest classifier")
        rf_model, rf_metrics = self._train_random_forest(
            X_train, y_train, X_test, y_test, tune=tune_hyperparameters,
        )

        logger.info("Training Gradient Boosting classifier")
        gb_model, gb_metrics = self._train_gradient_boosting(
            X_train, y_train, X_test, y_test, tune=tune_hyperparameters,
        )

        if rf_metrics["f1_score"] >= gb_metrics["f1_score"]:
            self.best_model = rf_model
            self.best_model_name = "random_forest"
            best_metrics = rf_metrics
        else:
            self.best_model = gb_model
            self.best_model_name = "gradient_boosting"
            best_metrics = gb_metrics

        self._save_model()
        self._save_preprocessor()

        duration_s = (datetime.utcnow() - start_time).total_seconds()

        self.training_metrics = {
            "best_model": self.best_model_name,
            "best_metrics": best_metrics,
            "random_forest_metrics": rf_metrics,
            "gradient_boosting_metrics": gb_metrics,
            "training_duration_seconds": round(duration_s, 2),
            "training_samples": len(X_train),
            "test_samples": len(X_test),
            "feature_count": X_train.shape[1],
            "trained_at": datetime.utcnow().isoformat(),
        }

        logger.info(
            "Training complete: best_model=%s, f1=%.4f, accuracy=%.4f, duration=%.1fs",
            self.best_model_name,
            best_metrics["f1_score"],
            best_metrics["accuracy"],
            duration_s,
        )

        return self.training_metrics

    def _train_random_forest(
        self,
        X_train: np.ndarray,
        y_train: np.ndarray,
        X_test: np.ndarray,
        y_test: np.ndarray,
        tune: bool = False,
    ) -> tuple[RandomForestClassifier, dict[str, float]]:
        """
        Train a Random Forest classifier.

        Args:
            X_train: Training features.
            y_train: Training labels.
            X_test: Test features.
            y_test: Test labels.
            tune: Whether to perform hyperparameter tuning.

        Returns:
            Tuple of (trained model, evaluation metrics dictionary).
        """
        if tune:
            param_grid = {
                "n_estimators": [100, 200],
                "max_depth": [10, 20, None],
                "min_samples_split": [2, 5],
                "min_samples_leaf": [1, 2],
            }
            grid_search = GridSearchCV(
                RandomForestClassifier(random_state=42, n_jobs=-1),
                param_grid,
                cv=3,
                scoring="f1",
                n_jobs=-1,
            )
            grid_search.fit(X_train, y_train)
            model = grid_search.best_estimator_
            logger.info("RF best params: %s", grid_search.best_params_)
        else:
            model = RandomForestClassifier(
                n_estimators=200,
                max_depth=20,
                min_samples_split=5,
                min_samples_leaf=2,
                random_state=42,
                n_jobs=-1,
            )
            model.fit(X_train, y_train)

        metrics = self._evaluate_model(model, X_test, y_test, "RandomForest")
        return model, metrics

    def _train_gradient_boosting(
        self,
        X_train: np.ndarray,
        y_train: np.ndarray,
        X_test: np.ndarray,
        y_test: np.ndarray,
        tune: bool = False,
    ) -> tuple[GradientBoostingClassifier, dict[str, float]]:
        """
        Train a Gradient Boosting classifier.

        Args:
            X_train: Training features.
            y_train: Training labels.
            X_test: Test features.
            y_test: Test labels.
            tune: Whether to perform hyperparameter tuning.

        Returns:
            Tuple of (trained model, evaluation metrics dictionary).
        """
        if tune:
            param_grid = {
                "n_estimators": [100, 200],
                "max_depth": [3, 5, 7],
                "learning_rate": [0.05, 0.1],
                "subsample": [0.8, 1.0],
            }
            grid_search = GridSearchCV(
                GradientBoostingClassifier(random_state=42),
                param_grid,
                cv=3,
                scoring="f1",
                n_jobs=-1,
            )
            grid_search.fit(X_train, y_train)
            model = grid_search.best_estimator_
            logger.info("GB best params: %s", grid_search.best_params_)
        else:
            model = GradientBoostingClassifier(
                n_estimators=200,
                max_depth=5,
                learning_rate=0.1,
                subsample=0.8,
                random_state=42,
            )
            model.fit(X_train, y_train)

        metrics = self._evaluate_model(model, X_test, y_test, "GradientBoosting")
        return model, metrics

    def _evaluate_model(
        self,
        model: Any,
        X_test: np.ndarray,
        y_test: np.ndarray,
        model_name: str,
    ) -> dict[str, float]:
        """
        Evaluate a trained model on the test set.

        Args:
            model: Trained classifier.
            X_test: Test features.
            y_test: Test labels.
            model_name: Name for logging.

        Returns:
            Dictionary of evaluation metrics.
        """
        y_pred = model.predict(X_test)
        y_proba = model.predict_proba(X_test)[:, 1] if hasattr(model, "predict_proba") else y_pred

        metrics = {
            "accuracy": round(accuracy_score(y_test, y_pred), 4),
            "precision": round(precision_score(y_test, y_pred, zero_division=0), 4),
            "recall": round(recall_score(y_test, y_pred, zero_division=0), 4),
            "f1_score": round(f1_score(y_test, y_pred, zero_division=0), 4),
            "roc_auc": round(roc_auc_score(y_test, y_proba), 4) if len(np.unique(y_test)) > 1 else 0.0,
        }

        logger.info(
            "%s evaluation: accuracy=%.4f, f1=%.4f, roc_auc=%.4f",
            model_name, metrics["accuracy"], metrics["f1_score"], metrics["roc_auc"],
        )

        return metrics

    def _save_model(self) -> None:
        """Save the best trained model to disk using joblib."""
        if self.best_model is None:
            logger.warning("No model to save")
            return

        model_path = os.path.join(self.model_dir, f"hotspot_{self.best_model_name}_v1.joblib")
        joblib.dump(self.best_model, model_path)
        logger.info("Model saved to %s", model_path)

    def _save_preprocessor(self) -> None:
        """Save the fitted preprocessor (scaler + encoders) to disk."""
        preprocessor_path = os.path.join(self.model_dir, "hotspot_preprocessor_v1.joblib")
        joblib.dump(self.preprocessor, preprocessor_path)
        logger.info("Preprocessor saved to %s", preprocessor_path)
