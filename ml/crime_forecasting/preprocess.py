"""
Sentinel AI - Crime Forecasting Preprocessing
===============================================
File: ml/crime_forecasting/preprocess.py
Purpose: Time-series data preparation for crime forecasting including
         resampling, lag feature creation, and stationarity handling.

Dependencies: pandas, numpy
"""

import logging
from typing import Any, Optional
import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)


class ForecastPreprocessor:
    """Preprocessor for crime forecasting time-series data."""

    def __init__(self, freq: str = "D") -> None:
        self.freq: str = freq
        self.columns_used: list[str] = []

    def prepare_time_series(
        self, df: pd.DataFrame, target_col: str = "crime_count",
        date_col: str = "occurred_at", group_col: Optional[str] = "district",
    ) -> pd.DataFrame:
        """Prepare time-series data with resampling and lag features."""
        logger.info("Preparing time-series data: %d rows", len(df))
        df = df.copy()
        df[date_col] = pd.to_datetime(df[date_col], errors="coerce")
        df = df.dropna(subset=[date_col])

        if group_col and group_col in df.columns:
            ts_df = (df.groupby([pd.Grouper(key=date_col, freq=self.freq), group_col])
                     .size().reset_index(name=target_col))
        else:
            ts_df = (df.set_index(date_col).resample(self.freq)
                     .size().reset_index(name=target_col))

        ts_df = self._add_lag_features(ts_df, target_col)
        ts_df = self._add_rolling_features(ts_df, target_col)
        ts_df = self._add_date_features(ts_df, date_col)
        ts_df = ts_df.dropna()

        logger.info("Time-series prepared: %d rows, %d features", len(ts_df), len(ts_df.columns))
        return ts_df

    def _add_lag_features(self, df: pd.DataFrame, target: str) -> pd.DataFrame:
        df = df.copy()
        for lag in [1, 3, 7, 14, 30]:
            df[f"lag_{lag}"] = df[target].shift(lag)
        return df

    def _add_rolling_features(self, df: pd.DataFrame, target: str) -> pd.DataFrame:
        df = df.copy()
        for window in [7, 14, 30]:
            df[f"rolling_mean_{window}"] = df[target].rolling(window=window).mean()
            df[f"rolling_std_{window}"] = df[target].rolling(window=window).std()
        return df

    def _add_date_features(self, df: pd.DataFrame, date_col: str) -> pd.DataFrame:
        df = df.copy()
        if date_col in df.columns:
            dt = pd.to_datetime(df[date_col])
            df["day_of_week"] = dt.dt.dayofweek
            df["month"] = dt.dt.month
            df["is_weekend"] = (dt.dt.dayofweek >= 5).astype(int)
            df["day_of_month"] = dt.dt.day
        return df
