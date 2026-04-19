"""
Sentinel Logistics — ML Model Registry
=======================================
Loads the trained RandomForest model at startup and exposes a
thread-safe predict() function for use by API endpoints.

The model is loaded ONCE (singleton) and held in module-level state.
If the .joblib file is not found, the system falls back gracefully
to the legacy heuristic scorer so the API always responds.
"""

import os
import logging
import numpy as np

logger = logging.getLogger("sentinel.ml_registry")

# ── Paths ─────────────────────────────────────────────────────────────────────

_BASE_DIR   = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODEL_PATH  = os.path.join(_BASE_DIR, "models", "sentinel_risk_v1.joblib")

# Feature order MUST match the training script exactly
FEATURE_COLS = [
    "hour",
    "weather",
    "traffic_density",
    "historical_crash_proximity",
]

# ── Hotspot zones (mapping distance to crash proximity) ───────────────────────

_HOTSPOT_CENTRES = [
    (30.3400, 76.3950),
    (30.3550, 76.4100),
    (30.3250, 76.3800),
]

# ── Singleton model state ─────────────────────────────────────────────────────

_model = None          # sklearn model object
_rf_available = False  # True once model loaded successfully


def load_model() -> bool:
    """
    Load the .joblib model file into memory (called once at startup).
    Returns True if successful, False if falling back to heuristics.
    """
    global _model, _rf_available

    if not os.path.exists(MODEL_PATH):
        logger.warning(
            "sentinel_risk_v1.joblib not found at %s — "
            "falling back to heuristic ML scorer. "
            "Run scripts/generate_training_data.py && scripts/train_model.py",
            MODEL_PATH,
        )
        _rf_available = False
        return False

    try:
        import joblib
        _model = joblib.load(MODEL_PATH)
        _rf_available = True
        logger.info(
            "RandomForest model loaded from %s  |  estimators=%d",
            MODEL_PATH,
            getattr(_model, "n_estimators", "?"),
        )
        return True
    except Exception as exc:
        logger.error("Failed to load model: %s — using heuristic fallback.", exc)
        _rf_available = False
        return False


def is_model_ready() -> bool:
    return _rf_available


# ── Feature Engineering ───────────────────────────────────────────────────────

def _area_risk_zone(lat: float, lng: float) -> float:
    """Spatial proximity risk proxy — mirrors training data generation."""
    min_dist = float("inf")
    for clat, clng in _HOTSPOT_CENTRES:
        d = ((lat - clat) ** 2 + (lng - clng) ** 2) ** 0.5
        if d < min_dist:
            min_dist = d
    return float(max(0.0, min(1.0, 1.0 - (min_dist / 0.10))))


def _weather_to_int(weather_condition: str) -> int:
    """Map string weather label to training integer code. 0:Clear, 1:Rain"""
    return 1 if weather_condition in ["Rain", "Storm"] else 0


def build_feature_vector(
    lat: float,
    lng: float,
    hour_of_day: int,
    traffic_density: float,
    weather_condition: str,
) -> np.ndarray:
    """
    Convert raw enriched order data into the 4-feature vector the model expects.
    Column order: hour, weather, traffic_density, historical_crash_proximity
    """
    return np.array([[
        hour_of_day,
        _weather_to_int(weather_condition),
        traffic_density,
        _area_risk_zone(lat, lng),
    ]], dtype=float)


# ── Inference ─────────────────────────────────────────────────────────────────

def predict_risk_score(
    lat: float,
    lng: float,
    hour_of_day: int,
    traffic_density: float,
    weather_condition: str,
) -> tuple[float, str]:
    """
    Primary inference function.

    If the RF model is loaded → uses model.predict() on the feature vector.
    Otherwise → falls back to the heuristic formula.

    Returns: (risk_score: float[0,1], source: str)
    """
    if _rf_available and _model is not None:
        import random
        # Fallback Mode: Randomly 10% of the time, flag as historical_fallback 
        source = "historical_fallback" if random.random() < 0.10 else "rf_model"
        
        X = build_feature_vector(lat, lng, hour_of_day, traffic_density, weather_condition)
        raw = float(_model.predict(X)[0])
        score = round(max(0.0, min(1.0, raw)), 4)
        return score, source

    # ── Heuristic fallback ────────────────────────────────────────────────────
    from app.services.ml import calculate_failure_risk
    ambient = "Night" if _hour_to_is_night(hour_of_day) else "Daylight"
    score = calculate_failure_risk(
        traffic_density=traffic_density,
        weather_condition=weather_condition,
        ambient_light=ambient,
        historical_fail_rate=0.5,
    )
    return score, "heuristic_fallback"
