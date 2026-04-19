#!/usr/bin/env python3
"""
Sentinel Logistics — Generate 20,000 records
Master Prompt Compliance
Features: hour (0-23), weather (0:Clear, 1:Rain), traffic_density (0.0 to 1.0), historical_crash_proximity
Target: risk_score (0-100)
"""

import numpy as np
import pandas as pd
import os

SEED = 42
N_ROWS = 20_000
OUT_PATH = os.path.join(os.path.dirname(__file__), "training_data.csv")

np.random.seed(SEED)

print(f"Generating {N_ROWS:,} synthetic training samples...")

hour = np.random.randint(0, 24, N_ROWS)
weather = np.random.choice([0, 1], size=N_ROWS, p=[0.7, 0.3]) # 0:Clear, 1:Rain
traffic_density = np.random.uniform(0.0, 1.0, N_ROWS)
historical_crash_proximity = np.random.uniform(0.0, 1.0, N_ROWS)

# Calculate Risk (0-100 scale)
# Base risk 10
# Rain adds +25
# Traffic adds up to +35
# Proximity adds up to +20
# Night (hour < 6 or > 21) adds +10

is_night = ((hour < 6) | (hour > 21)).astype(int)
base_risk = 5.0
weather_risk = weather * 25.0
traffic_risk = traffic_density * 40.0
proximity_risk = historical_crash_proximity * 20.0
night_risk = is_night * 10.0

risk_score = base_risk + weather_risk + traffic_risk + proximity_risk + night_risk

# Add minor noise
noise = np.random.normal(0, 3.0, N_ROWS)
risk_score = np.clip(risk_score + noise, 0.0, 100.0).round(1)

df = pd.DataFrame({
    "hour": hour,
    "weather": weather,
    "traffic_density": traffic_density.round(3),
    "historical_crash_proximity": historical_crash_proximity.round(3),
    "risk_score": risk_score
})

print(f"Risk score    : mean={df['risk_score'].mean():.1f}  max={df['risk_score'].max():.1f}")
df.to_csv(OUT_PATH, index=False)
print(f"[OK] Saved to: {OUT_PATH}")
