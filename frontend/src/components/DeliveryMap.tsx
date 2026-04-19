import { useEffect, useRef } from 'react'
import { MapContainer, TileLayer, Marker, Popup, useMap } from 'react-leaflet'
import { divIcon } from 'leaflet'
import 'leaflet/dist/leaflet.css'
import type { EnrichedStop, RiskLabel } from '@/types'

// ── Interfaces ────────────────────────────────────────────────────────────────

interface Props {
    stops: EnrichedStop[]
    center?: [number, number]
    zoom?: number
}

// ── Risk colour logic ─────────────────────────────────────────────────────────

function markerColor(riskLabel?: RiskLabel, status?: string): string {
    if (status === 'delivered') return '#6b7280'   // Dim Grey
    if (status === 'failed') return '#374151'      // Dark Steel
    if (riskLabel === 'High') return '#ef4444'     // Pulsing Red
    return '#f59e0b'                               // Amber (Pending / Normal Risk = custom Amber Icon)
}

function buildSvgIcon(color: string, isHigh: boolean): string {
    const ringOpacity = isHigh ? '0.35' : '0'
    const glowStd = isHigh ? '5' : '2.5'

    return `
    <svg xmlns="http://www.w3.org/2000/svg" width="32" height="42" viewBox="0 0 32 42">
      <defs>
        <filter id="glow-${color.replace('#', '')}">
          <feGaussianBlur stdDeviation="${glowStd}" result="blur"/>
          <feMerge><feMergeNode in="blur"/><feMergeNode in="SourceGraphic"/></feMerge>
        </filter>
      </defs>
      <!-- Outer pulsing ring for high-risk nodes (Amber Icon equivalent) -->
      <circle cx="16" cy="16" r="15" fill="${color}" opacity="${ringOpacity}"/>
      <path d="M16 0C7.163 0 0 7.163 0 16c0 10.667 16 26 16 26S32 26.667 32 16C32 7.163 24.837 0 16 0z"
            fill="${color}" opacity="0.95" filter="url(#glow-${color.replace('#', '')})"/>
      <circle cx="16" cy="16" r="5.5" fill="#111111" opacity="0.9"/>
      ${isHigh ? `<circle cx="16" cy="16" r="2.5" fill="${color}" opacity="0.8"/>` : ''}
    </svg>
  `
}

// ── Auto-Pan Controller ───────────────────────────────────────────────────────
// Inner component that uses react-leaflet's useMap() hook.
// Watches the stops array; when a new stop is prepended (latest = stops[0]),
// it calls map.flyTo() to smoothly pan & zoom to that coordinate.

function AutoPanController({ stops }: { stops: EnrichedStop[] }) {
    const map = useMap()
    const prevCountRef = useRef(stops.length)

    useEffect(() => {
        const prevCount = prevCountRef.current
        prevCountRef.current = stops.length

        // Only fly when a new stop was ADDED (count grew), not on initial load
        if (stops.length > prevCount && stops.length > 0) {
            const newest = stops[0]  // stops are prepended, so index 0 is the latest
            console.log(`[MAP] flyTo new deployment: [${newest.latitude}, ${newest.longitude}]`)
            map.flyTo(
                [newest.latitude, newest.longitude],
                14,                    // zoom level 14 — street level with context
                { animate: true, duration: 1.5 }
            )
        }
    }, [stops, map])

    return null  // Pure behaviour component — renders nothing
}

// ── DeliveryMap ───────────────────────────────────────────────────────────────

export default function DeliveryMap({ stops, center, zoom = 13 }: Props) {

    // Auto-center on Patiala or mean of stops
    const defaultCenter: [number, number] = center ?? (stops.length > 0
        ? [
            stops.reduce((s, p) => s + p.latitude, 0) / stops.length,
            stops.reduce((s, p) => s + p.longitude, 0) / stops.length,
        ]
        : [30.3398, 76.3869]  // Patiala, Punjab
    )

    return (
        <MapContainer
            center={defaultCenter}
            zoom={zoom}
            style={{ width: '100%', height: '100%', minHeight: '340px' }}
            className=""
            zoomControl={false}
            attributionControl={false}
        >
            {/* CartoDB Dark-Matter tile layer */}
            <TileLayer
                url="https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png"
                maxZoom={19}
            />

            {/* Auto-pan to newest stop on every new webhook ingestion */}
            <AutoPanController stops={stops} />

            {/* Dynamic markers — maps over stops (activeDeployments via parent) */}
            {stops.map((stop) => {
                const color = markerColor(stop.risk_label, stop.status)
                const isHigh = stop.status === 'pending' && stop.risk_label === 'High'
                const svgStr = buildSvgIcon(color, isHigh)

                // Custom Amber Icon for high-risk nodes (isHigh = amber + pulse ring)
                const icon = divIcon({
                    html: svgStr,
                    className: 'animated-marker',
                    iconSize: [32, 42],
                    iconAnchor: [16, 42],
                    popupAnchor: [0, -44],
                })

                return (
                    <Marker
                        key={stop.id}
                        position={[stop.latitude, stop.longitude]}
                        icon={icon}
                    >
                        <Popup className="sentinel-popup" maxWidth={260}>
                            <div style={{ padding: '4px 0px', minWidth: 200 }}>
                                <p className="text-slate-200 font-mono text-[11px] mb-2 uppercase tracking-wide border-b border-[#222] pb-1">
                                    {stop.name}
                                </p>
                                <p className="text-[#6b7280] text-[10px] mb-3 leading-tight">
                                    {stop.address}
                                </p>

                                <div className="flex gap-2 mb-2">
                                    <span className={
                                        stop.status === 'delivered' ? 'badge-on-track' :
                                        stop.status === 'failed' ? 'badge-failed' : 'badge-pending'
                                    }>
                                        {stop.status}
                                    </span>
                                    {stop.risk_label === "High" && stop.status === 'pending' && (
                                        <span className="badge-high">HIGH RISK</span>
                                    )}
                                </div>

                                <div className="space-y-1 mb-2 bg-[#111111] p-1.5 border border-[#333333]">
                                    {stop.traffic_density > 0 && (
                                        <div className="flex justify-between text-[9px] font-mono text-steel-400">
                                            <span>traffic:</span>
                                            <span style={{ color: stop.traffic_density > 0.6 ? '#ef4444' : '#f59e0b' }}>
                                                {stop.traffic_density.toFixed(2)}
                                            </span>
                                        </div>
                                    )}
                                    {stop.weather_condition && (
                                        <div className="flex justify-between text-[9px] font-mono text-steel-400">
                                            <span>weather:</span>
                                            <span style={{ color: stop.weather_condition === 'Storm' ? '#ef4444' : '#f59e0b' }}>
                                                {stop.weather_condition}
                                            </span>
                                        </div>
                                    )}
                                </div>

                                {stop.risk_reason && (
                                    <p className="text-[9px] text-[#ef4444] bg-[#2e0909] border border-red-500/30 p-1.5 font-mono">
                                        ⚠ {stop.risk_reason.toUpperCase()}
                                    </p>
                                )}
                            </div>
                        </Popup>
                    </Marker>
                )
            })}
        </MapContainer>
    )
}
