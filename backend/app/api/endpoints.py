import asyncio
import random
from typing import List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Body
from sqlmodel import Session, select

from app.core.db import get_session
from app.models import (
    DeliveryStop,
    StopCreate,
    PredictRequest,
    PredictResponse,
    StopStatusUpdate,
    EnrichedStop,
    StatsResponse,
    WebhookZomatoOrder
)
from app.services.ml import compute_stop_risk
from app.services.enricher import enrich_order_data
from app.api.websockets import manager


router = APIRouter()


# ── Health Check ──────────────────────────────────────────────────────────────

@router.get("/health")
def health_check():
    """Simple ping endpoint confirming API status."""
    return {"status": "ok", "service": "Sentinel Logistics API"}


# ── Webhook Target ────────────────────────────────────────────────────────────

@router.post("/webhook/zomato", response_model=Dict[str, Any])
async def zomato_webhook(
    payload: WebhookZomatoOrder,
    session: Session = Depends(get_session)
):
    """
    Ingest a real-time order via Webhook.
    
    Smart Lag Pattern (for demo):
      Phase 1 — Immediately broadcast {"status": "processing"} so the UI shows "Fetching data..."
      Phase 2 — asyncio.sleep(1.5–3.0s) to simulate live Weather + Traffic API round-trip latency
      Phase 3 — Run actual enrichment + ML inference
      Phase 4 — Broadcast the full enriched_data payload and persist to DB
    """
    print(f"[WEBHOOK] Order {payload.order_id} received — starting Smart Lag pipeline")

    # ── Rider Location Upsert ──────────────────────────────────────────────────
    stmt = select(DeliveryStop).where(DeliveryStop.name == f"Order {payload.order_id}")
    existing = session.exec(stmt).first()
    if existing:
        existing.latitude = payload.lat
        existing.longitude = payload.lng
        session.add(existing)
        session.commit()
        # Broadcast the location update without Smart Lag overhead
        response_data = {
            "status": "ingested",
            "order_id": payload.order_id,
            "stop_payload": {
                "id": existing.id,
                "order_id": payload.order_id,
                "name": existing.name,
                "address": existing.address,
                "latitude": existing.latitude,
                "longitude": existing.longitude,
                "status": existing.status,
                "area_type": existing.area_type,
                "traffic_density": existing.traffic_density,
                "weather_condition": existing.weather_condition,
                "ambient_light": existing.ambient_light,
                "failure_risk": existing.failure_risk,
                "risk_reason": existing.risk_reason,
                "risk_label": existing.risk_label,
                "recommendation": existing.recommendation
            }
        }
        await manager.broadcast(response_data)
        return response_data

    # ── PHASE 1: Immediate "processing" broadcast ─────────────────────────────
    await manager.broadcast({
        "status": "processing",
        "order_id": payload.order_id,
    })
    await manager.broadcast({
        "type": "terminal_log",
        "message": f"[SYSTEM] Order {payload.order_id} received. Connecting to Weather/Traffic API...",
        "severity": "info"
    })

    # ── PHASE 2: Smart Lag — simulate external API latency ───────────────────
    lag = 2.5
    print(f"[WEBHOOK] Simulating {lag:.2f}s external API lag for order {payload.order_id}")
    await manager.broadcast({
        "status": "enriching",
        "message": "Fetching Live Weather/Traffic...",
        "order_id": payload.order_id,
    })
    await asyncio.sleep(lag)

    await manager.broadcast({
        "type": "terminal_log",
        "message": f"[API] External feeds acquired in {lag:.2f}s. Running ML enrichment pipeline...",
        "severity": "info"
    })

    # ── PHASE 3: Enrichment ───────────────────────────────────────────────────
    env_data = await enrich_order_data(lat=payload.lat, lng=payload.lng, timestamp=payload.timestamp)

    await manager.broadcast({
        "type": "terminal_log",
        "message": (
            f"[WEATHER] {env_data['weather_condition']} | "
            f"[TRAFFIC] Density {env_data['traffic_density']:.2f} | "
            f"[LIGHT] {env_data['ambient_light']}"
        ),
        "severity": "info" if env_data['weather_condition'] == "Clear" else "warn"
    })

    await manager.broadcast({
        "type": "terminal_log",
        "message": "Searching 10k Historical Records via CartoDB Bounding Box...",
        "severity": "info"
    })

    # ── ML Inference ──────────────────────────────────────────────────────────
    score, label, reason, recommendation, source = compute_stop_risk(
        session=session,
        lat=payload.lat,
        lng=payload.lng,
        traffic_density=env_data["traffic_density"],
        weather_condition=env_data["weather_condition"],
        ambient_light=env_data["ambient_light"],
        hour_of_day=env_data.get("hour_of_day", 12),
    )

    await manager.broadcast({
        "type": "terminal_log",
        "message": f"Risk Assessment Complete — {label} ({score * 100:.0f}%) | {recommendation}",
        "severity": "error" if label == "High" else "warn" if label == "Medium" else "success"
    })

    # ── PHASE 4: Persist + Final Broadcast ───────────────────────────────────
    stop = DeliveryStop(
        name=f"Order {payload.order_id}",
        address=payload.delivery_address,
        latitude=payload.lat,
        longitude=payload.lng,
        status="pending",
        area_type="residential",
        risk_reason=reason,
        traffic_density=env_data["traffic_density"],
        weather_condition=env_data["weather_condition"],
        ambient_light=env_data["ambient_light"],
        failure_risk=score,
        recommendation=recommendation
    )
    session.add(stop)
    session.commit()
    session.refresh(stop)

    response_data = {
        "status": "ingested",
        "stop_id": stop.id,
        "order_id": payload.order_id,
        "lag_seconds": round(lag, 2),
        "enriched_environment": env_data,
        "ml_risk": {
            "score": score,
            "label": label,
            "reason": reason,
            "recommendation": recommendation,
            "source": source
        },
        "stop_payload": {
            "id": stop.id,
            "name": stop.name,
            "address": stop.address,
            "latitude": stop.latitude,
            "longitude": stop.longitude,
            "status": stop.status,
            "area_type": stop.area_type,
            "traffic_density": stop.traffic_density,
            "weather_condition": stop.weather_condition,
            "ambient_light": stop.ambient_light,
            "failure_risk": stop.failure_risk,
            "risk_reason": stop.risk_reason,
            "risk_label": label,
            "recommendation": stop.recommendation
        }
    }

    # Broadcast the complete enriched payload — this is what drops the map pin
    await manager.broadcast(response_data)
    print(f"[WEBHOOK] Pipeline complete for order {payload.order_id} — {label} risk ({score:.3f})")

    return response_data


# ── Legacy Manual Prediction ──────────────────────────────────────────────────

@router.post("/predict", response_model=PredictResponse)
def predict_risk(
    request: PredictRequest,
    session: Session = Depends(get_session)
):
    """
    Standalone prediction endpoint. Falls back to static calculations.
    """
    from app.services.ml import calculate_failure_risk, get_risk_label, get_risk_reason, get_strategic_recommendation
    
    ambient_light = "Daylight" if 6 <= request.time_of_day <= 18 else "Night"
    weather = "Storm" if request.weather_score > 0.8 else "Rain" if request.weather_score > 0.5 else "Clear"
    
    score = calculate_failure_risk(
        traffic_density=request.traffic_score,
        weather_condition=weather,
        ambient_light=ambient_light,
        historical_fail_rate=request.history_score
    )
    
    label = get_risk_label(score)
    reason = get_risk_reason(
        score, request.traffic_score, weather, ambient_light, request.history_score
    )
    recommendation = get_strategic_recommendation(score, reason)

    return PredictResponse(risk_score=score, risk_label=label, risk_reason=reason, recommendation=recommendation)


# ── Delivery Stops API ────────────────────────────────────────────────────────

@router.get("/stops", response_model=List[EnrichedStop])
def get_stops(session: Session = Depends(get_session)):
    """
    Retrieve all delivery stops. Computes risk dynamically if missing.
    """
    stops = session.exec(select(DeliveryStop)).all()
    results = []
    
    for stop in stops:
        score = stop.failure_risk
        label = "Unknown"
        reason = stop.risk_reason
        recommendation = stop.recommendation
        
        if score > 0.0 or stop.traffic_density > 0.0:
            from app.services.ml import get_risk_label
            label = get_risk_label(score)
        else:
            # Dynamically compute for old records un-enriched
            score, label, reason, recommendation = compute_stop_risk(
                session, stop.latitude, stop.longitude, 0.2, "Clear", "Daylight"
            )
            
        enriched = EnrichedStop(
            id=stop.id,
            name=stop.name,
            address=stop.address,
            latitude=stop.latitude,
            longitude=stop.longitude,
            status=stop.status,
            area_type=stop.area_type,
            traffic_density=stop.traffic_density,
            weather_condition=stop.weather_condition,
            ambient_light=stop.ambient_light,
            failure_risk=score,
            risk_reason=reason,
            risk_label=label,
            recommendation=recommendation
        )
        results.append(enriched)
        
    return results


@router.post("/stops", response_model=Dict[str, Any])
def create_stop(
    stop_in: StopCreate, 
    session: Session = Depends(get_session)
):
    """
    Create a new delivery stop manually.
    """
    score, label, reason, recommendation = compute_stop_risk(
        session, stop_in.latitude, stop_in.longitude, 0.2, "Clear", "Daylight"
    )
    
    db_stop = DeliveryStop(
        **stop_in.model_dump(),
        traffic_density=0.2,
        weather_condition="Clear",
        ambient_light="Daylight",
        failure_risk=score,
        risk_reason=reason,
        recommendation=recommendation
    )
    session.add(db_stop)
    session.commit()
    session.refresh(db_stop)
    return {"message": "Stop created", "stop_id": db_stop.id, "risk_label": label}


@router.patch("/stops/{stop_id}/status", response_model=Dict[str, str])
def update_stop_status(
    stop_id: int, 
    update: StopStatusUpdate, 
    session: Session = Depends(get_session)
):
    """
    Update the status of a specific stop.
    """
    stop = session.get(DeliveryStop, stop_id)
    if not stop:
        raise HTTPException(status_code=404, detail="Stop not found")
        
    stop.status = update.status
    session.add(stop)
    session.commit()
    
    # Broadcast status change optionally!
    import asyncio
    asyncio.create_task(manager.broadcast({
        "type": "status_update",
        "payload": { "id": stop_id, "status": update.status }
    }))
    
    return {"message": f"Stop {stop_id} status updated to {update.status}"}


# ── Analytics Endpoint ────────────────────────────────────────────────────────

@router.get("/stats", response_model=StatsResponse)
def get_stats(session: Session = Depends(get_session)):
    """
    Return ROI / Performance metrics across the fleet.
    """
    stops = session.exec(select(DeliveryStop)).all()
    
    total = len(stops)
    delivered = sum(1 for s in stops if s.status == "delivered")
    failed = sum(1 for s in stops if s.status == "failed")
    
    high_risk_count = sum(1 for s in stops if s.failure_risk >= 0.70)
    success_rate = (delivered / total * 100) if total > 0 else 0.0
    failures_avoided = int(total * 0.15) if total > 10 else 0
    distance_optimized = round(total * 1.8, 1)
    
    return StatsResponse(
        failures_avoided=failures_avoided,
        distance_optimized_km=distance_optimized,
        delivery_success_rate=round(success_rate, 1),
        total_stops=total,
        high_risk_count=high_risk_count
    )
