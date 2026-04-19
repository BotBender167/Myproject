export type RiskLabel = 'Low' | 'Medium' | 'High'

export interface DeliveryStop {
    id: number
    name: string
    address: string
    latitude: number
    longitude: number
    status: string
    area_type: string
}

export interface EnrichedStop extends DeliveryStop {
    traffic_density: number
    weather_condition: string
    ambient_light: string
    failure_risk: number
    risk_reason?: string
    risk_label?: RiskLabel
    recommendation?: string
}

export interface PredictRequest {
    weather_score: number
    traffic_score: number
    history_score: number
    time_of_day: number
    area_type: string
}

export interface PredictResponse {
    risk_score: number
    risk_label: RiskLabel
    risk_reason: string
    recommendation?: string
}

export interface StatsResponse {
    failures_avoided: number
    distance_optimized_km: number
    delivery_success_rate: number
    total_stops: number
    high_risk_count: number
}

// ── Feed Protocol ─────────────────────────────────────────────────────────────

export interface FeedEvent {
    id: string
    timestamp: Date
    message: string
    severity: 'info' | 'warn' | 'error' | 'success' | 'alert'
}
