#!/usr/bin/env python3
"""
Sentinel Logistics - Yellowbrick ML Diagnostics
Generates visual models for Rank2D, PCADecomposition, and FeatureImportances.
"""

import os
import pandas as pd
import numpy as np
import matplotlib
import matplotlib.pyplot as plt

# Use Agg backend so it doesn't open GUI windows
matplotlib.use('Agg')

from yellowbrick.features import Rank2D, PCADecomposition
from yellowbrick.model_selection import FeatureImportances
from sklearn.ensemble import RandomForestRegressor

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
DATA_PATH = os.path.join(BASE_DIR, "training_data", "training_data.csv")
FRONTEND_DIR = os.path.abspath(os.path.join(BASE_DIR, "..", "frontend", "src", "assets", "analytics"))

os.makedirs(FRONTEND_DIR, exist_ok=True)

df = pd.read_csv(DATA_PATH)
features = ["traffic_density", "weather_severity", "time_of_day", "road_condition_index", "historical_incidents"]
X = df[features]
y = df["risk_score"]

# Create a deterministic categorical array for PCA coloring (e.g. High Risk)
y_color = np.where(y > 0.7, 1, 0)

# 1. Rank2D (Covariance)
print("Plotting Rank2D (Covariance)...")
plt.figure(figsize=(8, 6))
visualizer1 = Rank2D(algorithm='pearson', features=features)
visualizer1.fit(X, y)
visualizer1.transform(X)
visualizer1.show(outpath=os.path.join(FRONTEND_DIR, "analytics_covariance.png"))
plt.clf()

# 2. PCA Decomposition
print("Plotting PCA Decomposition...")
plt.figure(figsize=(8, 6))
# scale=True is often required for PCA
visualizer2 = PCADecomposition(scale=True, color=y_color, classes=["Low/Medium Risk", "High Risk"])
visualizer2.fit_transform(X, y_color)
visualizer2.show(outpath=os.path.join(FRONTEND_DIR, "analytics_pca.png"))
plt.clf()

# 3. Feature Importances
print("Plotting Feature Importances...")
plt.figure(figsize=(8, 6))
model = RandomForestRegressor(n_estimators=50, max_depth=5, random_state=42)
visualizer3 = FeatureImportances(model, labels=features, relative=False)
visualizer3.fit(X, y)
visualizer3.show(outpath=os.path.join(FRONTEND_DIR, "analytics_importance.png"))
plt.clf()

print(f"[OK] Yellowbrick analytics successfully outputted to {FRONTEND_DIR}")
