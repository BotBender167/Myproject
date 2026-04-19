import { useState } from 'react'
import {
    X,
    MapPin,
    AlertTriangle,
    CheckCircle2,
    Clock,
    Bike,
    Navigation,
    Package,
} from 'lucide-react'
import api from '@/lib/api'
import type { EnrichedStop } from '@/types'

// ── Props ─────────────────────────────────────────────────────────────────────

interface Props {
    stop: EnrichedStop
    onClose: () => void
    onStatusUpdate: (stopId: number, newStatus: string) => void
}

// ── Rider Focus Mode ──────────────────────────────────────────────────────────

export default function RiderFocusMode({ stop, onClose, onStatusUpdate }: Props) {
    const [loading, setLoading] = useState<'complete' | 'fail' | null>(null)
    const [error, setError] = useState<string | null>(null)

    const riskColor =
        stop.risk_label === 'High' ? '#ef4444' :
        stop.risk_label === 'Medium' ? '#f59e0b' : '#3b82f6'

    const updateStatus = async (status: 'delivered' | 'failed') => {
        setLoading(status === 'delivered' ? 'complete' : 'fail')
        setError(null)
        try {
            await api.patch(`/api/stops/${stop.id}/status`, { status })
            onStatusUpdate(stop.id, status)
            onClose()
        } catch (err: unknown) {
            const msg = err instanceof Error ? err.message : 'Failed to update status'
            setError(msg)
        } finally {
            setLoading(null)
        }
    }

    return (
        <div className="rider-focus-overlay">
            {/* Close */}
            <button
                onClick={onClose}
                className="absolute top-5 right-5 w-9 h-9 rounded-xl bg-slate-800/60
                    border border-slate-700/50 flex items-center justify-center
                    text-slate-400 hover:text-white hover:border-slate-500/50 transition-all"
                aria-label="Close Rider Focus Mode"
            >
                <X className="w-4 h-4" />
            </button>

            {/* Mode label */}
            <div className="flex items-center gap-2 mb-8">
                <div className="w-8 h-8 rounded-xl bg-blue-500/15 border border-blue-500/30
                    flex items-center justify-center">
                    <Bike className="w-4 h-4 text-blue-400" />
                </div>
                <div>
                    <p className="text-xs text-blue-400 font-semibold tracking-widest uppercase">Rider Focus Mode</p>
                    <p className="text-[10px] text-slate-600">Active Delivery</p>
                </div>
            </div>

            {/* Main card */}
            <div className="w-full max-w-md glass-blue p-8 rounded-2xl space-y-6">

                {/* Stop name */}
                <div className="text-center space-y-2">
                    <div className="w-14 h-14 rounded-2xl mx-auto mb-3 flex items-center justify-center"
                        style={{ background: `${riskColor}15`, border: `1px solid ${riskColor}30` }}>
                        <Package className="w-7 h-7" style={{ color: riskColor }} />
                    </div>
                    <h1 className="text-2xl font-bold text-white">{stop.name}</h1>
                    <div className="flex items-center justify-center gap-1.5 text-slate-400 text-sm">
                        <MapPin className="w-3.5 h-3.5" />
                        <span>{stop.address}</span>
                    </div>
                </div>

                {/* Divider */}
                <div className="h-px bg-slate-800/60" />

                {/* Risk info */}
                <div className="space-y-3">
                    {/* Risk badge row */}
                    <div className="flex items-center justify-between px-4 py-3 rounded-xl bg-slate-900/60 border border-slate-800/40">
                        <div className="flex items-center gap-2 text-slate-400 text-sm">
                            <AlertTriangle className="w-3.5 h-3.5" />
                            <span>Risk Level</span>
                        </div>
                        <div className="flex items-center gap-2">
                            <span className="font-mono text-xs text-slate-500">
                                {stop.risk_score !== undefined ? `${(stop.risk_score * 100).toFixed(0)}%` : '—'}
                            </span>
                            <span
                                className="px-2.5 py-0.5 rounded-full text-xs font-bold"
                                style={{ background: `${riskColor}18`, color: riskColor, border: `1px solid ${riskColor}35` }}
                            >
                                {stop.risk_label ?? 'Unknown'}
                            </span>
                        </div>
                    </div>

                    {/* Risk reason */}
                    {stop.risk_reason && (
                        <div className="flex items-start gap-2.5 px-4 py-3 rounded-xl bg-slate-900/40 border border-slate-800/30">
                            <AlertTriangle className="w-3.5 h-3.5 mt-0.5 shrink-0" style={{ color: riskColor }} />
                            <div>
                                <p className="text-[10px] text-slate-600 uppercase tracking-wider mb-0.5">Why High Risk</p>
                                <p className="text-sm text-slate-300">{stop.risk_reason}</p>
                            </div>
                        </div>
                    )}

                    {/* Area & coords */}
                    <div className="flex gap-2">
                        <div className="flex-1 flex items-center gap-2 px-3 py-2.5 rounded-xl bg-slate-900/40 border border-slate-800/30">
                            <Navigation className="w-3.5 h-3.5 text-slate-500" />
                            <div>
                                <p className="text-[10px] text-slate-600">Area Type</p>
                                <p className="text-xs text-slate-300 capitalize">{stop.area_type}</p>
                            </div>
                        </div>
                        <div className="flex-1 flex items-center gap-2 px-3 py-2.5 rounded-xl bg-slate-900/40 border border-slate-800/30">
                            <Clock className="w-3.5 h-3.5 text-slate-500" />
                            <div>
                                <p className="text-[10px] text-slate-600">Status</p>
                                <p className="text-xs text-slate-300 capitalize">{stop.status}</p>
                            </div>
                        </div>
                    </div>
                </div>

                {/* Error */}
                {error && (
                    <div className="rounded-lg bg-red-500/8 border border-red-500/20 px-3 py-2 text-xs text-red-400">
                        {error}
                    </div>
                )}

                {/* CTA Buttons */}
                {stop.status === 'pending' ? (
                    <div className="grid grid-cols-2 gap-3">
                        {/* Mark Complete */}
                        <button
                            id={`btn-complete-${stop.id}`}
                            onClick={() => updateStatus('delivered')}
                            disabled={loading !== null}
                            className="flex items-center justify-center gap-2 py-4 rounded-2xl
                                text-base font-bold text-white transition-all duration-200
                                disabled:opacity-50 active:scale-95"
                            style={{
                                background: 'linear-gradient(135deg, #059669, #10b981)',
                                boxShadow: '0 4px 24px rgba(16,185,129,0.3)',
                            }}
                        >
                            {loading === 'complete' ? (
                                <span className="w-4 h-4 border-2 border-white/40 border-t-white rounded-full animate-spin" />
                            ) : (
                                <CheckCircle2 className="w-5 h-5" />
                            )}
                            Delivered
                        </button>

                        {/* Mark Failed */}
                        <button
                            id={`btn-fail-${stop.id}`}
                            onClick={() => updateStatus('failed')}
                            disabled={loading !== null}
                            className="flex items-center justify-center gap-2 py-4 rounded-2xl
                                text-base font-bold transition-all duration-200
                                border border-red-500/30 bg-red-500/10 text-red-400
                                hover:bg-red-500/15 hover:border-red-400/40
                                disabled:opacity-50 active:scale-95"
                        >
                            {loading === 'fail' ? (
                                <span className="w-4 h-4 border-2 border-red-400/40 border-t-red-400 rounded-full animate-spin" />
                            ) : (
                                <AlertTriangle className="w-5 h-5" />
                            )}
                            Failed
                        </button>
                    </div>
                ) : (
                    <div className="text-center py-4">
                        <p className="text-sm text-slate-500">
                            This stop is already marked as{' '}
                            <span className={stop.status === 'delivered' ? 'text-emerald-400' : 'text-red-400'}>
                                {stop.status}
                            </span>.
                        </p>
                    </div>
                )}
            </div>

            {/* Geo coords */}
            <p className="mt-4 text-[10px] font-mono text-slate-700">
                {stop.latitude.toFixed(5)}, {stop.longitude.toFixed(5)}
            </p>
        </div>
    )
}
