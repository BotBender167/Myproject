#!/usr/bin/env python3
"""
Sentinel Logistics - Generate 15k analytical dataset
Features: traffic_density, weather_severity (0-1), time_of_day, road_condition_index, historical_incidents.
"""

import numpy as np
import pandas as pd
import os

SEED = 42
N_ROWS = 15_000
OUT_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "training_data")
OUT_PATH = os.path.join(OUT_DIR, "training_data.csv")

np.random.seed(SEED)

print(f"Generating {N_ROWS:,} synthetic analytical samples...")

traffic_density = np.random.uniform(0.0, 1.0, N_ROWS)
weather_severity = np.random.uniform(0.0, 1.0, N_ROWS)
time_of_day = np.random.randint(0, 24, N_ROWS)
road_condition_index = np.random.uniform(0.0, 1.0, N_ROWS)
historical_incidents = np.random.randint(0, 5, N_ROWS)

# Calculate Risk (0.0-1.0 scale)
risk_score = (
    (traffic_density * 0.3) +
    (weather_severity * 0.35) +
    ((time_of_day / 24.0) * 0.1) +
    ((1.0 - road_condition_index) * 0.15) +
    ((historical_incidents / 5.0) * 0.1)
)

# Add minor noise
noise = np.random.normal(0, 0.05, N_ROWS)
risk_score = np.clip(risk_score + noise, 0.0, 1.0).round(4)

df = pd.DataFrame({
    "traffic_density": traffic_density.round(3),
    "weather_severity": weather_severity.round(3),
    "time_of_day": time_of_day,
    "road_condition_index": road_condition_index.round(3),
    "historical_incidents": historical_incidents,
    "risk_score": risk_score
})

os.makedirs(OUT_DIR, exist_ok=True)
df.to_csv(OUT_PATH, index=False)
print(f"[OK] Saved to: {OUT_PATH}")
