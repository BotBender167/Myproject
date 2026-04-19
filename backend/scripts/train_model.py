#!/usr/bin/env python3
"""
Sentinel Logistics — Model Trainer for Master Prompt
"""

import os
import sys
import time

import numpy as np
import pandas as pd
import joblib
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score

SCRIPTS_DIR = os.path.dirname(__file__)
DATA_PATH   = os.path.join(SCRIPTS_DIR, "training_data.csv")
MODELS_DIR  = os.path.join(SCRIPTS_DIR, "..", "models")
MODEL_PATH  = os.path.join(MODELS_DIR, "sentinel_risk_v1.joblib")

FEATURE_COLS = [
    "hour",
    "weather",
    "traffic_density",
    "historical_crash_proximity",
]
TARGET_COL = "risk_score"

df = pd.read_csv(DATA_PATH)
X = df[FEATURE_COLS].values
y = df[TARGET_COL].values

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.20, random_state=42)

model = RandomForestRegressor(
    n_estimators=200,
    max_depth=12,
    min_samples_leaf=5,
    max_features="sqrt",
    random_state=42,
    n_jobs=-1,
)

model.fit(X_train, y_train)

y_pred = model.predict(X_test)
rmse = np.sqrt(mean_squared_error(y_test, y_pred))
r2   = r2_score(y_test, y_pred)
print(f"[EVAL] Test RMSE : {rmse:.4f}")
print(f"[EVAL] Test R²   : {r2:.4f}")

os.makedirs(MODELS_DIR, exist_ok=True)
joblib.dump(model, MODEL_PATH, compress=3)

print(f"[SAVE] Model saved to : {MODEL_PATH}")
