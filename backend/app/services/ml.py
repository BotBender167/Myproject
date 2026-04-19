"""
Sentinel Logistics — Modern Delivery Risk Score ML Service 
------------------------------------------------------
Calculates a composite failure_risk in [0.0, 1.0] combining:
  - Weather condition        → 0.30 weight
  - Traffic density          → 0.25 weight
  - Ambient Light            → 0.15 weight
  - Historical Location Risk → 0.30 weight 
"""

import random
from datetime import datetime
from sqlmodel import Session, select
from app.models import HistoricalDelivery

# ── Static Weights ────────────────────────────────────────────────────────────

WEIGHT_WEATHER: float = 0.30
WEIGHT_TRAFFIC: float = 0.25
WEIGHT_LIGHT: float = 0.15
WEIGHT_HISTORY: float = 0.30


def _weather_risk(weather_condition: str) -> float:
    mapping = {"Storm": 1.0, "Rain": 0.6, "Clear": 0.1}
    return mapping.get(weather_condition, 0.2)

def _light_risk(ambient_light: str) -> float:
    mapping = {"Night": 0.8, "Daylight": 0.2}
    return mapping.get(ambient_light, 0.4)

def calculate_failure_risk(
    traffic_density: float,
    weather_condition: str,
    ambient_light: str,
    historical_fail_rate: float,
) -> float:
    """
    4-factor continuous risk score.
    """
    score = (
        WEIGHT_WEATHER * _weather_risk(weather_condition)
        + WEIGHT_TRAFFIC * traffic_density
        + WEIGHT_LIGHT * _light_risk(ambient_light)
        + WEIGHT_HISTORY * historical_fail_rate
    )
    return round(max(0.0, min(1.0, score)), 4)

def get_risk_label(score: float) -> str:
    """
    Thresholds:
      Low    → [0.00, 0.40)
      Medium → [0.40, 0.70)
      High   → [0.70, 1.00]
    """
    if score < 0.40:
        return "Low"
    elif score < 0.70:
        return "Medium"
    return "High"

def get_risk_reason(
    score: float,
    traffic_density: float,
    weather_condition: str,
    ambient_light: str,
    historical_fail_rate: float,
) -> str:
    """
    Identify and return the highest contributing risk factor.
    """
    factors = {
        "Severe Weather Activity": _weather_risk(weather_condition) * WEIGHT_WEATHER,
        "High Traffic Density": traffic_density * WEIGHT_TRAFFIC,
        "Poor Ambient Lighting": _light_risk(ambient_light) * WEIGHT_LIGHT,
        "Historical Location Failures": historical_fail_rate * WEIGHT_HISTORY,
    }
    
    # Sort by highest contribution
    top_factor, contribution = max(factors.items(), key=lambda x: x[1])
    
    if score < 0.40:
        return "Low Priority - Safe Conditions"
        
    return top_factor

def get_strategic_recommendation(score: float, top_reason: str) -> str:
    """
    Generate actionable directives for active deployments based strictly on ML heuristics.
    """
    if score < 0.40:
        return "Proceed standard operations."
        
    if top_reason == "Severe Weather Activity":
        return "Switch to 4-wheeler for weather protection."
    elif top_reason == "High Traffic Density":
        return "Reroute via bypass."
    elif top_reason == "Poor Ambient Lighting":
        return "Slow transit speeds. Enable high-viz tracking."
    elif top_reason == "Historical Location Failures":
        return "Contact customer prior to departure. Double-verify address."
        
    return "Heightened caution required."

def compute_historical_fail_rate(session: Session, lat: float, lng: float, radius: float = 0.05) -> float:
    """
    Calculate the baseline failure rate in roughly a 5km bounding box.
    `radius` ~0.05 degrees is approximately 5.5km loosely speaking.
    """
    # SQLite has no native robust geodata out of box inside SQLModel, so we use a bounding box
    min_lat = lat - radius
    max_lat = lat + radius
    min_lng = lng - radius
    max_lng = lng + radius
    
    statement = select(HistoricalDelivery).where(
        HistoricalDelivery.lat >= min_lat,
        HistoricalDelivery.lat <= max_lat,
        HistoricalDelivery.lng >= min_lng,
        HistoricalDelivery.lng <= max_lng,
    )
    
    local_records = session.exec(statement).all()
    
    if not local_records:
        return 0.5 # Unknown zone, median risk
        
    total = len(local_records)
    failures = sum(1 for r in local_records if not r.was_successful)
    
    return failures / total

def compute_stop_risk(
    session: Session,
    lat: float, 
    lng: float,
    traffic_density: float,
    weather_condition: str,
    ambient_light: str,
    hour_of_day: int = 12
) -> tuple[float, str, str, str, str]:
    """
    Computes everything directly utilizing the DB session + ML Registry.
    Returns: (score, label, reason, recommendation, source)
    """
    from app.services.ml_registry import predict_risk_score, is_model_ready
    
    historical_fail_rate = compute_historical_fail_rate(session, lat, lng)
    
    if is_model_ready():
        score, source = predict_risk_score(lat, lng, hour_of_day, traffic_density, weather_condition)
    else:
        score = calculate_failure_risk(
            traffic_density=traffic_density,
            weather_condition=weather_condition,
            ambient_light=ambient_light,
            historical_fail_rate=historical_fail_rate
        )
        source = "heuristic_fallback"
    
    label = get_risk_label(score)
    reason = get_risk_reason(score, traffic_density, weather_condition, ambient_light, historical_fail_rate)
    recommendation = get_strategic_recommendation(score, reason)
    
    return score, label, reason, recommendation, source
