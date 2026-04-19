import { useEffect, useRef, useState } from 'react'
import { Radio, Zap, AlertTriangle, CheckCircle2, Info } from 'lucide-react'
import type { FeedEvent, FeedSeverity } from '@/types'

// ── Helpers ───────────────────────────────────────────────────────────────────

let _feedId = 0
function makeId() { return String(++_feedId) }

function severityIcon(s: FeedSeverity) {
    const cls = 'w-3.5 h-3.5 mt-0.5 shrink-0'
    switch (s) {
        case 'error': return <AlertTriangle className={`${cls} text-red-400`} />
        case 'warn': return <Zap className={`${cls} text-amber-400`} />
        case 'success': return <CheckCircle2 className={`${cls} text-emerald-400`} />
        default: return <Info className={`${cls} text-cyan-400`} />
    }
}

function severityColor(s: FeedSeverity) {
    switch (s) {
        case 'error': return 'text-red-300'
        case 'warn': return 'text-amber-300'
        case 'success': return 'text-emerald-300'
        default: return 'text-slate-300'
    }
}

function dotColor(s: FeedSeverity) {
    switch (s) {
        case 'error': return 'bg-red-400'
        case 'warn': return 'bg-amber-400'
        case 'success': return 'bg-emerald-400'
        default: return 'bg-cyan-400'
    }
}

// ── Simulated event bank ──────────────────────────────────────────────────────

const EVENT_POOL: Array<{ message: string; severity: FeedSeverity }> = [
    { message: 'Risk Assessment Complete — Sector 7 flagged HIGH', severity: 'error' },
    { message: 'Route optimisation applied for Stop #14', severity: 'success' },
    { message: 'Weather anomaly detected in Zone B — score elevated', severity: 'warn' },
    { message: 'Heartbeat OK — All backend services nominal', severity: 'info' },
    { message: 'Stop #23 status updated → delivered', severity: 'success' },
    { message: 'Traffic congestion spike: I-95 corridor recalculated', severity: 'warn' },
    { message: 'ML model inference completed in 12ms', severity: 'info' },
    { message: 'Stop #31 marked FAILED — retry queued', severity: 'error' },
    { message: '/api/stops polled — 0 new records', severity: 'info' },
    { message: 'Risk Assessment Complete — Sector 12 ON TRACK', severity: 'success' },
    { message: 'Historical backlog sync in progress…', severity: 'info' },
    { message: 'Stop #9 departure delayed — ETA recalculated', severity: 'warn' },
    { message: 'Fleet GPS ping received — all vehicles reporting', severity: 'success' },
    { message: 'High-priority stop #5 re-routed via alt corridor', severity: 'warn' },
    { message: 'System snapshot saved to audit log', severity: 'info' },
]

// ── Component ─────────────────────────────────────────────────────────────────

interface Props {
    externalEvents?: FeedEvent[]
}

export default function LiveFeed({ externalEvents = [] }: Props) {
    const [events, setEvents] = useState<FeedEvent[]>(() =>
        // Seed with 4 initial events
        EVENT_POOL.slice(0, 4).map((e) => ({
            ...e,
            id: makeId(),
            timestamp: new Date(Date.now() - Math.random() * 60_000),
        }))
    )
    const scrollRef = useRef<HTMLDivElement>(null)

    // Auto-scroll to top when new events arrive
    useEffect(() => {
        if (scrollRef.current) {
            scrollRef.current.scrollTo({ top: 0, behavior: 'smooth' })
        }
    }, [events])

    // Inject external events (e.g. from API fetch)
    useEffect(() => {
        if (externalEvents.length > 0) {
            setEvents((prev) => [...externalEvents, ...prev].slice(0, 80))
        }
    }, [externalEvents])

    // Simulate periodic live events
    useEffect(() => {
        const interval = setInterval(() => {
            const pool = EVENT_POOL[Math.floor(Math.random() * EVENT_POOL.length)]
            const evt: FeedEvent = {
                ...pool,
                id: makeId(),
                timestamp: new Date(),
            }
            setEvents((prev) => [evt, ...prev].slice(0, 80))
        }, 3500)

        return () => clearInterval(interval)
    }, [])

    return (
        <div className="flex flex-col h-full">
            {/* Header */}
            <div className="flex items-center justify-between px-4 py-3 border-b border-slate-800/80">
                <div className="flex items-center gap-2">
                    <Radio className="w-4 h-4 text-cyan-400" />
                    <span className="text-sm font-semibold text-slate-200">Live Operations Feed</span>
                </div>
                <span className="flex items-center gap-1.5 text-xs text-emerald-400">
                    <span className="pulse-dot bg-emerald-400 animate-pulse" />
                    Live
                </span>
            </div>

            {/* Scrollable log */}
            <div
                ref={scrollRef}
                className="flex-1 overflow-y-auto px-3 py-1 space-y-0"
                id="live-feed-scroll"
            >
                {events.map((evt) => (
                    <div key={evt.id} className="feed-item">
                        {severityIcon(evt.severity)}
                        <div className="flex-1 min-w-0">
                            <p className={`text-xs leading-relaxed ${severityColor(evt.severity)}`}>
                                {evt.message}
                            </p>
                            <p className="text-[10px] text-slate-600 font-mono mt-0.5">
                                {evt.timestamp.toLocaleTimeString('en-US', { hour12: false })}
                            </p>
                        </div>
                        <span className={`pulse-dot ${dotColor(evt.severity)} mt-1`} />
                    </div>
                ))}
            </div>

            {/* Footer counter */}
            <div className="px-4 py-2 border-t border-slate-800/80 text-[10px] text-slate-600 font-mono">
                {events.length} events — refreshes every 3.5s
            </div>
        </div>
    )
}
