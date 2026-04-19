import { useEffect, useState } from 'react'
import { TrendingUp, ShieldCheck, Navigation, BarChart3, RefreshCw } from 'lucide-react'
import api from '@/lib/api'
import type { StatsResponse } from '@/types'

// ── Animated Counter ──────────────────────────────────────────────────────────

function AnimatedNumber({ value, decimals = 0, suffix = '' }: {
    value: number
    decimals?: number
    suffix?: string
}) {
    const [displayed, setDisplayed] = useState(0)

    useEffect(() => {
        if (value === 0) return
        const duration = 1200
        const steps = 40
        const increment = value / steps
        let current = 0
        const timer = setInterval(() => {
            current += increment
            if (current >= value) {
                setDisplayed(value)
                clearInterval(timer)
            } else {
                setDisplayed(current)
            }
        }, duration / steps)
        return () => clearInterval(timer)
    }, [value])

    return (
        <span>
            {decimals > 0 ? displayed.toFixed(decimals) : Math.round(displayed)}
            {suffix}
        </span>
    )
}

// ── Metric Card ───────────────────────────────────────────────────────────────

function MetricCard({
    label,
    value,
    decimals = 0,
    suffix = '',
    sub,
    icon,
    color,
}: {
    label: string
    value: number
    decimals?: number
    suffix?: string
    sub?: string
    icon: React.ReactNode
    color: string
}) {
    return (
        <div className="flex flex-col gap-2 px-5 py-4 rounded-xl border border-slate-800/50 bg-slate-900/40
            hover:border-blue-500/20 hover:bg-slate-900/60 transition-all duration-200">
            <div className="flex items-center justify-between">
                <p className="text-[10px] text-slate-500 uppercase tracking-widest font-medium">{label}</p>
                <span style={{ color }} className="opacity-75">{icon}</span>
            </div>
            <p className="text-2xl font-bold" style={{ color }}>
                <AnimatedNumber value={value} decimals={decimals} suffix={suffix} />
            </p>
            {sub && <p className="text-[11px] text-slate-600">{sub}</p>}
        </div>
    )
}

// ── Performance Widget ────────────────────────────────────────────────────────

export default function PerformanceWidget() {
    const [stats, setStats] = useState<StatsResponse | null>(null)
    const [loading, setLoading] = useState(true)
    const [error, setError] = useState<string | null>(null)

    const fetchStats = async () => {
        setLoading(true)
        setError(null)
        try {
            const res = await api.get<StatsResponse>('/api/stats')
            setStats(res.data)
        } catch (err: unknown) {
            const msg = err instanceof Error ? err.message : 'Failed to load stats'
            setError(msg)
        } finally {
            setLoading(false)
        }
    }

    useEffect(() => { fetchStats() }, [])

    return (
        <div className="glass p-5 space-y-4">
            {/* Header */}
            <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                    <div className="w-7 h-7 rounded-lg bg-blue-500/10 border border-blue-500/25 flex items-center justify-center">
                        <BarChart3 className="w-3.5 h-3.5 text-blue-400" />
                    </div>
                    <div>
                        <h2 className="text-sm font-semibold text-slate-200">Performance Impact</h2>
                        <p className="text-[10px] text-slate-600">Platform ROI · Live metrics</p>
                    </div>
                </div>
                <button
                    onClick={fetchStats}
                    disabled={loading}
                    className="w-7 h-7 rounded-lg border border-slate-700/50 bg-slate-800/40
                        flex items-center justify-center text-slate-500 hover:text-blue-400
                        hover:border-blue-500/30 transition-all duration-150 disabled:opacity-40"
                    title="Refresh stats"
                >
                    <RefreshCw className={`w-3 h-3 ${loading ? 'animate-spin' : ''}`} />
                </button>
            </div>

            {/* Error state */}
            {error && (
                <div className="rounded-lg bg-red-500/5 border border-red-500/20 px-3 py-2 text-xs text-red-400">
                    {error}
                </div>
            )}

            {/* Metrics grid */}
            {stats && !error ? (
                <div className="grid grid-cols-3 gap-3">
                    <MetricCard
                        label="Failures Avoided"
                        value={stats.failures_avoided}
                        sub="Risk-aware routing"
                        icon={<ShieldCheck className="w-4 h-4" />}
                        color="#3b82f6"
                    />
                    <MetricCard
                        label="Distance Optimized"
                        value={stats.distance_optimized_km}
                        decimals={1}
                        suffix=" km"
                        sub="Saved this session"
                        icon={<Navigation className="w-4 h-4" />}
                        color="#a78bfa"
                    />
                    <MetricCard
                        label="Success Rate"
                        value={stats.delivery_success_rate}
                        decimals={1}
                        suffix="%"
                        sub={`${stats.total_stops} total stops`}
                        icon={<TrendingUp className="w-4 h-4" />}
                        color="#34d399"
                    />
                </div>
            ) : !error && (
                <div className="grid grid-cols-3 gap-3">
                    {[1, 2, 3].map(i => (
                        <div key={i} className="h-20 rounded-xl bg-slate-800/30 animate-pulse" />
                    ))}
                </div>
            )}

            {/* High risk callout */}
            {stats && stats.high_risk_count > 0 && (
                <div className="flex items-center gap-2 rounded-lg bg-red-500/5 border border-red-500/15 px-3 py-2">
                    <span className="w-1.5 h-1.5 rounded-full bg-red-400 animate-pulse shrink-0" />
                    <p className="text-xs text-red-400">
                        <span className="font-semibold">{stats.high_risk_count}</span> high-risk stop{stats.high_risk_count !== 1 ? 's' : ''} require attention
                    </p>
                </div>
            )}
        </div>
    )
}
