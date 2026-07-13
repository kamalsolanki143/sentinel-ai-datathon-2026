"""
Sentinel AI - Hotspot Prediction Preprocessing
================================================
File: ml/hotspot_prediction/preprocess.py
Purpose: Data cleaning, normalization, encoding, and train/test splitting
         for the hotspot prediction ML pipeline.

Integration:
    - Called by ml/hotspot_prediction/train.py for training data preparation
    - Called by ml/hotspot_prediction/predict.py for inference data preparation
    - Reads raw crime data from PostgreSQL via pandas

Dependencies: pandas, numpy, scikit-learn
"""

import logging
import os
from typing import Any, Optional

import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder, StandardScaler

logger = logging.getLogger(__name__)


class HotspotPreprocessor:
    """
    Preprocessor for hotspot prediction data pipeline.

    Handles data cleaning, feature encoding, scaling, and train/test splitting.
    Maintains fitted encoders and scalers for consistent inference preprocessing.

    Attributes:
        label_encoders: Dictionary of fitted LabelEncoders per categorical column
        scaler: Fitted StandardScaler for numerical features
        feature_columns: List of feature column names after preprocessing
        target_column: Name of the target variable column
    """

    def __init__(self) -> None:
        """Initialize preprocessor with empty encoders."""
        self.label_encoders: dict[str, LabelEncoder] = {}
        self.scaler: StandardScaler = StandardScaler()
        self.feature_columns: list[str] = []
        self.target_column: str = "is_hotspot"

    def preprocess_training_data(
        self,
        df: pd.DataFrame,
        test_size: float = 0.2,
        random_state: int = 42,
    ) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
        """
        Preprocess raw crime data for model training.

        Steps:
        1. Clean and validate data
        2. Engineer temporal and spatial features
        3. Encode categorical variables
        4. Generate hotspot labels
        5. Scale numerical features
        6. Split into train/test sets

        Args:
            df: Raw crime data DataFrame.
            test_size: Fraction of data for testing (default 0.2).
            random_state: Random seed for reproducibility.

        Returns:
            Tuple of (X_train, X_test, y_train, y_test) as numpy arrays.
        """
        logger.info("Preprocessing training data: %d rows", len(df))

        df_clean = self._clean_data(df)
        df_features = self._add_temporal_features(df_clean)
        df_features = self._add_spatial_features(df_features)
        df_encoded = self._encode_categoricals(df_features, fit=True)
        df_labeled = self._generate_hotspot_labels(df_encoded)

        feature_cols = [c for c in df_labeled.columns if c != self.target_column]
        self.feature_columns = feature_cols

        X = df_labeled[feature_cols].values
        y = df_labeled[self.target_column].values

        X_scaled = self.scaler.fit_transform(X)

        X_train, X_test, y_train, y_test = train_test_split(
            X_scaled, y, test_size=test_size, random_state=random_state, stratify=y,
        )

        logger.info(
            "Training data prepared: X_train=%s, X_test=%s, pos_ratio=%.2f",
            X_train.shape, X_test.shape, y.mean(),
        )

        return X_train, X_test, y_train, y_test

    def preprocess_inference_data(self, df: pd.DataFrame) -> np.ndarray:
        """
        Preprocess new data for model inference using fitted transformers.

        Args:
            df: New crime data DataFrame for prediction.

        Returns:
            Preprocessed feature array ready for model prediction.
        """
        logger.info("Preprocessing inference data: %d rows", len(df))

        df_clean = self._clean_data(df)
        df_features = self._add_temporal_features(df_clean)
        df_features = self._add_spatial_features(df_features)
        df_encoded = self._encode_categoricals(df_features, fit=False)

        for col in self.feature_columns:
            if col not in df_encoded.columns:
                df_encoded[col] = 0

        df_encoded = df_encoded[self.feature_columns]
        X = df_encoded.values
        X_scaled = self.scaler.transform(X)

        return X_scaled

    def _clean_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Clean raw crime data by handling missing values and invalid entries.

        Args:
            df: Raw DataFrame.

        Returns:
            Cleaned DataFrame.
        """
        df = df.copy()

        if "occurred_at" in df.columns:
            df["occurred_at"] = pd.to_datetime(df["occurred_at"], errors="coerce")
            df = df.dropna(subset=["occurred_at"])

        if "latitude" in df.columns and "longitude" in df.columns:
            df = df.dropna(subset=["latitude", "longitude"])
            df = df[(df["latitude"].between(-90, 90)) & (df["longitude"].between(-180, 180))]

        categorical_cols = ["crime_type", "district", "severity", "status"]
        for col in categorical_cols:
            if col in df.columns:
                df[col] = df[col].fillna("unknown")

        drop_cols = ["id", "description", "fir_number", "modus_operandi", "created_at", "updated_at"]
        df = df.drop(columns=[c for c in drop_cols if c in df.columns], errors="ignore")

        logger.debug("Data cleaned: %d rows remaining", len(df))
        return df

    def _add_temporal_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Extract temporal features from the occurred_at timestamp.

        Args:
            df: DataFrame with occurred_at column.

        Returns:
            DataFrame with temporal feature columns added.
        """
        df = df.copy()

        if "occurred_at" in df.columns:
            df["hour_of_day"] = df["occurred_at"].dt.hour
            df["day_of_week"] = df["occurred_at"].dt.dayofweek
            df["month"] = df["occurred_at"].dt.month
            df["is_weekend"] = (df["day_of_week"] >= 5).astype(int)
            df["is_night"] = ((df["hour_of_day"] >= 20) | (df["hour_of_day"] <= 5)).astype(int)
            df = df.drop(columns=["occurred_at"], errors="ignore")

        if "reported_at" in df.columns:
            df = df.drop(columns=["reported_at"], errors="ignore")

        return df

    def _add_spatial_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Create spatial grid features from latitude/longitude.

        Args:
            df: DataFrame with lat/long columns.

        Returns:
            DataFrame with spatial grid features added.
        """
        df = df.copy()

        if "latitude" in df.columns and "longitude" in df.columns:
            grid_size = 0.01
            df["grid_x"] = (df["latitude"] / grid_size).astype(int)
            df["grid_y"] = (df["longitude"] / grid_size).astype(int)

        return df

    def _encode_categoricals(self, df: pd.DataFrame, fit: bool = True) -> pd.DataFrame:
        """
        Encode categorical columns using LabelEncoder.

        Args:
            df: DataFrame with categorical columns.
            fit: If True, fit new encoders. If False, use existing fitted encoders.

        Returns:
            DataFrame with categorical columns encoded as integers.
        """
        df = df.copy()
        categorical_cols = ["crime_type", "district", "severity", "status", "station"]

        for col in categorical_cols:
            if col not in df.columns:
                continue

            if fit:
                le = LabelEncoder()
                df[col] = le.fit_transform(df[col].astype(str))
                self.label_encoders[col] = le
            else:
                if col in self.label_encoders:
                    le = self.label_encoders[col]
                    df[col] = df[col].astype(str).map(
                        lambda x, _le=le: (
                            _le.transform([x])[0]
                            if x in _le.classes_
                            else -1
                        )
                    )
                else:
                    df[col] = 0

        return df

    def _generate_hotspot_labels(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Generate binary hotspot labels based on crime density per grid cell.

        A grid cell is labeled as a hotspot if its crime count exceeds the
        75th percentile of all grid cells.

        Args:
            df: DataFrame with grid_x and grid_y features.

        Returns:
            DataFrame with is_hotspot binary label column.
        """
        df = df.copy()

        if "grid_x" in df.columns and "grid_y" in df.columns:
            grid_counts = df.groupby(["grid_x", "grid_y"]).size().reset_index(name="grid_crime_count")
            df = df.merge(grid_counts, on=["grid_x", "grid_y"], how="left")

            threshold = df["grid_crime_count"].quantile(0.75)
            df[self.target_column] = (df["grid_crime_count"] >= threshold).astype(int)
            df = df.drop(columns=["grid_crime_count"], errors="ignore")
        else:
            df[self.target_column] = 0

        logger.debug("Hotspot labels generated: %.1f%% positive", df[self.target_column].mean() * 100)
        return df
