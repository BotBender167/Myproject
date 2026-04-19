from typing import Optional
from sqlmodel import Field, SQLModel


# ── Database Table Models ─────────────────────────────────────────────────────

class DeliveryStop(SQLModel, table=True):
    """Represents a physical delivery stop stored in the database."""

    __tablename__ = "delivery_stops"

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True, max_length=128)
    address: str = Field(max_length=256)
    latitude: float
    longitude: float
    status: str = Field(default="pending", max_length=32)   # pending | delivered | failed
    area_type: str = Field(default="residential", max_length=32)  # residential | commercial | industrial
    risk_reason: Optional[str] = Field(default=None, max_length=256)
    
    # Enriched Fields
    traffic_density: float = Field(default=0.0)
    weather_condition: str = Field(default="Clear", max_length=32)
    ambient_light: str = Field(default="Daylight", max_length=32)
    failure_risk: float = Field(default=0.0)
    recommendation: Optional[str] = Field(default=None, max_length=256)


class HistoricalDelivery(SQLModel, table=True):
    """Stores a large dataset of past deliveries for location-based risk context."""
    
    __tablename__ = "historical_deliveries"

    id: Optional[int] = Field(default=None, primary_key=True)
    stop_id: str = Field(index=True, max_length=64)
    lat: float = Field(index=True)  # Indexed for bounding-box/proximity queries
    lng: float = Field(index=True)
    weather_at_time: str = Field(max_length=32)
    traffic_level: float
    was_successful: bool


# ── Request / Response Schemas (non-table) ────────────────────────────────────

class PredictRequest(SQLModel):
    """Payload sent by the client to request a delivery risk prediction manually (legacy behavior)."""

    weather_score: float = Field(ge=0.0, le=1.0, description="Simulated weather severity (0=good, 1=bad)")
    traffic_score: float = Field(ge=0.0, le=1.0, description="Current traffic congestion (0=clear, 1=gridlock)")
    history_score: float = Field(ge=0.0, le=1.0, description="Historical delay rate for this route (0=never, 1=always)")
    time_of_day: int = Field(default=12, ge=0, le=23, description="Hour of day (0-23) for risk calculation")
    area_type: str = Field(default="residential", description="Zone type: residential | commercial | industrial")


class PredictResponse(SQLModel):
    """ML prediction result returned to the client."""

    risk_score: float = Field(ge=0.0, le=1.0, description="Weighted composite risk (0=safe, 1=critical)")
    risk_label: str = Field(description="Human-readable label: Low | Medium | High")
    risk_reason: str = Field(description="Primary driver of the risk score")
    recommendation: Optional[str] = Field(default=None, description="Strategic operation guideline")


class EnrichedStop(SQLModel):
    """DeliveryStop enriched dynamically for the frontend."""

    id: int
    name: str
    address: str
    latitude: float
    longitude: float
    status: str
    area_type: str
    traffic_density: float
    weather_condition: str
    ambient_light: str
    failure_risk: float
    risk_reason: Optional[str] = None
    risk_label: Optional[str] = None
    recommendation: Optional[str] = None


class StopCreate(SQLModel):
    """Payload for creating a new delivery stop."""

    name: str = Field(max_length=128)
    address: str = Field(max_length=256)
    latitude: float
    longitude: float
    status: str = Field(default="pending", max_length=32)
    area_type: str = Field(default="residential", max_length=32)


class StopStatusUpdate(SQLModel):
    """Payload for updating delivery stop status."""

    status: str = Field(description="New status: pending | delivered | failed")


class StatsResponse(SQLModel):
    """Platform performance / ROI metrics."""

    failures_avoided: int
    distance_optimized_km: float
    delivery_success_rate: float
    total_stops: int
    high_risk_count: int

class WebhookZomatoOrder(SQLModel):
    """Incoming Zomato webhook payload."""
    
    order_id: str
    delivery_address: str
    timestamp: str
    lat: float
    lng: float
