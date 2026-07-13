"""
Sentinel AI - ML Evaluation Metrics
=====================================
File: ml/utils/metrics.py
Purpose: Unified evaluation metrics for classification, regression,
         time-series, and anomaly detection models.

Dependencies: numpy, scikit-learn
"""

import logging
from typing import Any
import numpy as np
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score, roc_auc_score,
    confusion_matrix, classification_report,
    mean_absolute_error, mean_squared_error, r2_score,
)

logger = logging.getLogger(__name__)


def classification_metrics(y_true: np.ndarray, y_pred: np.ndarray, y_proba: np.ndarray | None = None) -> dict[str, Any]:
    """Compute comprehensive classification metrics."""
    metrics = {
        "accuracy": round(float(accuracy_score(y_true, y_pred)), 4),
        "precision": round(float(precision_score(y_true, y_pred, zero_division=0)), 4),
        "recall": round(float(recall_score(y_true, y_pred, zero_division=0)), 4),
        "f1_score": round(float(f1_score(y_true, y_pred, zero_division=0)), 4),
        "confusion_matrix": confusion_matrix(y_true, y_pred).tolist(),
        "classification_report": classification_report(y_true, y_pred, output_dict=True, zero_division=0),
    }
    if y_proba is not None and len(np.unique(y_true)) > 1:
        metrics["roc_auc"] = round(float(roc_auc_score(y_true, y_proba)), 4)
    return metrics


def regression_metrics(y_true: np.ndarray, y_pred: np.ndarray) -> dict[str, float]:
    """Compute comprehensive regression metrics."""
    return {
        "mae": round(float(mean_absolute_error(y_true, y_pred)), 4),
        "rmse": round(float(np.sqrt(mean_squared_error(y_true, y_pred))), 4),
        "mse": round(float(mean_squared_error(y_true, y_pred)), 4),
        "r2_score": round(float(r2_score(y_true, y_pred)), 4),
        "mape": round(float(np.mean(np.abs((y_true - y_pred) / np.maximum(np.abs(y_true), 1))) * 100), 2),
    }


def anomaly_metrics(y_true: np.ndarray, y_pred: np.ndarray) -> dict[str, float]:
    """Compute anomaly detection metrics (anomaly=1, normal=0)."""
    return {
        "precision": round(float(precision_score(y_true, y_pred, zero_division=0)), 4),
        "recall": round(float(recall_score(y_true, y_pred, zero_division=0)), 4),
        "f1_score": round(float(f1_score(y_true, y_pred, zero_division=0)), 4),
        "false_positive_rate": round(float(
            np.sum((y_pred == 1) & (y_true == 0)) / max(np.sum(y_true == 0), 1)
        ), 4),
        "total_anomalies_detected": int(np.sum(y_pred == 1)),
        "total_actual_anomalies": int(np.sum(y_true == 1)),
    }


def format_metrics_report(metrics: dict[str, Any], model_name: str) -> str:
    """Format metrics into a readable report string."""
    lines = [f"=== {model_name} Evaluation Report ==="]
    for key, val in metrics.items():
        if isinstance(val, (int, float)):
            lines.append(f"  {key}: {val}")
    return "\n".join(lines)
