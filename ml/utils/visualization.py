"""
Sentinel AI - ML Visualization Utilities
==========================================
File: ml/utils/visualization.py
Purpose: Plot generators for feature importance, confusion matrix,
         time-series forecasts, ROC curves, and crime heatmaps.

Dependencies: matplotlib, numpy, pandas
"""

import logging, os
from typing import Any, Optional
import numpy as np, pandas as pd

logger = logging.getLogger(__name__)

try:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    HAS_MATPLOTLIB = True
except ImportError:
    HAS_MATPLOTLIB = False
    logger.warning("matplotlib not available, visualization functions will return None")


def plot_feature_importance(
    feature_names: list[str], importances: np.ndarray,
    title: str = "Feature Importance", output_path: Optional[str] = None, top_k: int = 15,
) -> Optional[str]:
    """Plot top-K feature importance as horizontal bar chart."""
    if not HAS_MATPLOTLIB:
        return None
    idx = np.argsort(importances)[-top_k:]
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.barh([feature_names[i] for i in idx], importances[idx], color="#4F46E5")
    ax.set_title(title, fontsize=14, fontweight="bold")
    ax.set_xlabel("Importance")
    path = output_path or "ml/outputs/feature_importance.png"
    os.makedirs(os.path.dirname(path), exist_ok=True)
    fig.savefig(path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    logger.info("Feature importance plot saved to %s", path)
    return path


def plot_confusion_matrix(
    cm: np.ndarray, labels: list[str] | None = None,
    title: str = "Confusion Matrix", output_path: Optional[str] = None,
) -> Optional[str]:
    """Plot confusion matrix as heatmap."""
    if not HAS_MATPLOTLIB:
        return None
    labels = labels or ["Negative", "Positive"]
    fig, ax = plt.subplots(figsize=(6, 5))
    im = ax.imshow(cm, interpolation="nearest", cmap="Blues")
    ax.set_title(title, fontsize=14, fontweight="bold")
    ax.set_xticks(range(len(labels)))
    ax.set_yticks(range(len(labels)))
    ax.set_xticklabels(labels)
    ax.set_yticklabels(labels)
    ax.set_ylabel("Actual")
    ax.set_xlabel("Predicted")
    for i in range(len(labels)):
        for j in range(len(labels)):
            ax.text(j, i, str(cm[i, j]), ha="center", va="center", fontsize=14)
    fig.colorbar(im, ax=ax)
    path = output_path or "ml/outputs/confusion_matrix.png"
    os.makedirs(os.path.dirname(path), exist_ok=True)
    fig.savefig(path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    logger.info("Confusion matrix saved to %s", path)
    return path


def plot_forecast(
    actual: np.ndarray, predicted: np.ndarray,
    title: str = "Crime Forecast", output_path: Optional[str] = None,
) -> Optional[str]:
    """Plot actual vs predicted time-series."""
    if not HAS_MATPLOTLIB:
        return None
    fig, ax = plt.subplots(figsize=(12, 5))
    ax.plot(actual, label="Actual", color="#1E40AF", linewidth=2)
    ax.plot(predicted, label="Predicted", color="#DC2626", linewidth=2, linestyle="--")
    ax.set_title(title, fontsize=14, fontweight="bold")
    ax.set_xlabel("Time")
    ax.set_ylabel("Crime Count")
    ax.legend()
    ax.grid(alpha=0.3)
    path = output_path or "ml/outputs/forecast.png"
    os.makedirs(os.path.dirname(path), exist_ok=True)
    fig.savefig(path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    logger.info("Forecast plot saved to %s", path)
    return path


def plot_roc_curve(
    fpr: np.ndarray, tpr: np.ndarray, auc_score: float,
    title: str = "ROC Curve", output_path: Optional[str] = None,
) -> Optional[str]:
    """Plot ROC curve with AUC score."""
    if not HAS_MATPLOTLIB:
        return None
    fig, ax = plt.subplots(figsize=(7, 6))
    ax.plot(fpr, tpr, color="#4F46E5", linewidth=2, label=f"AUC = {auc_score:.4f}")
    ax.plot([0, 1], [0, 1], color="gray", linestyle="--", linewidth=1)
    ax.set_title(title, fontsize=14, fontweight="bold")
    ax.set_xlabel("False Positive Rate")
    ax.set_ylabel("True Positive Rate")
    ax.legend(loc="lower right")
    ax.grid(alpha=0.3)
    path = output_path or "ml/outputs/roc_curve.png"
    os.makedirs(os.path.dirname(path), exist_ok=True)
    fig.savefig(path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    logger.info("ROC curve saved to %s", path)
    return path
