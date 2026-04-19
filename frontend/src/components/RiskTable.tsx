import { useState } from 'react'
import {
    ArrowUpDown,
    MapPin,
    AlertTriangle,
    CheckCircle2,
    Clock,
    Bike,
} from 'lucide-react'
import type { EnrichedStop, RiskLabel } from '@/types'
import RiderView from '@/components/RiderView'

// ── Helpers ───────────────────────────────────────────────────────────────────

function riskBadge(label?: RiskLabel) {
    if (!label) return <span className="badge-pending">—</span>
    if (label === 'High') return <span className="badge-high"><AlertTriangle className="w-3 h-3" />High Risk</span>
    if (label === 'Medium') return <span className="badge-delayed"><Clock className="w-3 h-3" />Medium</span>
    return <span className="badge-on-track"><CheckCircle2 className="w-3 h-3" />Low</span>
}

function statusBadge(status: string) {
    if (status === 'delivered') return <span className="badge-on-track"><CheckCircle2 className="w-3 h-3" />Delivered</span>
    if (status === 'failed') return <span className="badge-failed"><AlertTriangle className="w-3 h-3" />Failed</span>
    return <span className="badge-pending"><Clock className="w-3 h-3" />Pending</span>
}

function RiskReasonTag({ reason, label }: { reason?: string; label?: RiskLabel }) {
    if (!reason) return <span className="text-steel-600 font-mono text-[9px] uppercase tracking-wider">—</span>
    const cls =
        label === 'High' ? 'risk-tag risk-tag-high' :
        label === 'Medium' ? 'risk-tag risk-tag-medium' : 'risk-tag'
    return <span className={cls} title={reason}>{reason}</span>
}

type SortKey = 'name' | 'status' | 'risk_score' | 'id'
type SortDir = 'asc' | 'desc'

// ── RiskTable ─────────────────────────────────────────────────────────────────

interface Props {
    stops: EnrichedStop[]
    loading?: boolean
    onStatusUpdate?: (stopId: number, newStatus: string) => void
}

export default function RiskTable({ stops, loading, onStatusUpdate }: Props) {
    const [sortKey, setSortKey] = useState<SortKey>('id')
    const [sortDir, setSortDir] = useState<SortDir>('asc')
    const [focusStop, setFocusStop] = useState<EnrichedStop | null>(null)

    function handleSort(key: SortKey) {
        if (sortKey === key) setSortDir((d) => (d === 'asc' ? 'desc' : 'asc'))
        else { setSortKey(key); setSortDir('asc') }
    }

    const sorted = [...stops].sort((a, b) => {
        let cmp = 0
        if (sortKey === 'id') cmp = a.id - b.id
        else if (sortKey === 'name') cmp = a.name.localeCompare(b.name)
        else if (sortKey === 'status') cmp = a.status.localeCompare(b.status)
        else if (sortKey === 'risk_score') cmp = (a.risk_score ?? -1) - (b.risk_score ?? -1)
        return sortDir === 'asc' ? cmp : -cmp
    })

    function SortBtn({ col }: { col: SortKey }) {
        return (
            <button
                id={`sort-${col}`}
                onClick={() => handleSort(col)}
                className="inline-flex items-center gap-1 hover:text-amber-400 transition-colors"
                aria-label="Sort Column"
            >
                <ArrowUpDown className="w-3 h-3 opacity-50" />
            </button>
        )
    }

    const handleFocusClose = () => setFocusStop(null)
    const handleStatusUpdate = (stopId: number, newStatus: string) => {
        onStatusUpdate?.(stopId, newStatus)
        setFocusStop(null)
    }

    return (
        <>
            {/* Rider Focus Overlay Upgrade */}
            {focusStop && (
                <RiderView
                    stop={focusStop}
                    onClose={handleFocusClose}
                    onStatusUpdate={handleStatusUpdate}
                />
            )}

            <div className="overflow-hidden border border-[#333333] bg-[#111111] rounded-none">
                <table className="cyber-table">
                    <thead>
                        <tr>
                            <th className="w-14">
                                <span className="flex items-center gap-1"># <SortBtn col="id" /></span>
                            </th>
                            <th>
                                <span className="flex items-center gap-1">Stop <SortBtn col="name" /></span>
                            </th>
                            <th className="hidden md:table-cell">Address</th>
                            <th>
                                <span className="flex items-center gap-1">Status <SortBtn col="status" /></span>
                            </th>
                            <th>
                                <span className="flex items-center gap-1">Risk <SortBtn col="risk_score" /></span>
                            </th>
                            <th className="hidden lg:table-cell">Why?</th>
                            <th className="w-16">Deploy</th>
                        </tr>
                    </thead>
                    <tbody>
                        {loading && (
                            <tr>
                                <td colSpan={7} className="text-center py-12">
                                    <div className="flex flex-col items-center gap-3">
                                        <div className="w-5 h-5 border-2 border-[#333333] border-t-amber-500 rounded-full animate-spin" />
                                        <span className="text-steel-600 text-[10px] font-mono tracking-widest uppercase">Fetching DB...</span>
                                    </div>
                                </td>
                            </tr>
                        )}
                        {!loading && sorted.length === 0 && (
                            <tr>
                                <td colSpan={7} className="text-center py-12">
                                    <div className="flex flex-col items-center gap-2 text-steel-700">
                                        <MapPin className="w-6 h-6 text-[#222222]" />
                                        <p className="text-sm font-mono tracking-widest uppercase text-steel-600">No active orders</p>
                                        <p className="text-[10px]">Awaiting webhook transmission.</p>
                                    </div>
                                </td>
                            </tr>
                        )}
                        {!loading && sorted.map((stop) => (
                            <tr key={stop.id}>
                                <td>
                                    <span className="font-mono text-[10px] text-steel-600">#{stop.id}</span>
                                </td>
                                <td>
                                    <div className="flex items-center gap-2">
                                        <div className="w-7 h-7 bg-[#1a1205] border border-amber-500/20 flex flex-col items-center justify-center shrink-0">
                                            <MapPin className="w-3.5 h-3.5 text-amber-500" />
                                        </div>
                                        <div>
                                            <p className="font-mono text-slate-300 text-xs font-semibold uppercase tracking-wide">{stop.name}</p>
                                            <p className="text-[9px] font-mono text-steel-500 tracking-widest uppercase">{stop.area_type}</p>
                                        </div>
                                    </div>
                                </td>
                                <td className="hidden md:table-cell">
                                    <span className="font-mono text-steel-500 text-[10px] uppercase tracking-wider">{stop.address}</span>
                                </td>
                                <td>{statusBadge(stop.status)}</td>
                                <td>
                                    <div className="flex items-center gap-1.5">
                                        {riskBadge(stop.risk_label)}
                                        {stop.risk_score !== undefined && (
                                            <span className="text-[9px] font-mono text-steel-500 bg-[#0f0f0f] border border-[#222] px-1 py-0.5">
                                                {(stop.risk_score * 100).toFixed(0)}%
                                            </span>
                                        )}
                                    </div>
                                </td>
                                <td className="hidden lg:table-cell">
                                    <RiskReasonTag reason={stop.risk_reason} label={stop.risk_label} />
                                </td>
                                <td>
                                    <button
                                        id={`btn-focus-${stop.id}`}
                                        onClick={() => setFocusStop(stop)}
                                        className="w-8 h-8 border border-[#333333] bg-[#0a0a0a] flex items-center justify-center text-steel-500 hover:text-amber-500 hover:border-amber-500 transition-all duration-200"
                                        title="Open Rider View"
                                    >
                                        <Bike className="w-3.5 h-3.5" />
                                    </button>
                                </td>
                            </tr>
                        ))}
                    </tbody>
                </table>

                {/* Footer */}
                {!loading && sorted.length > 0 && (
                    <div className="px-4 py-2.5 bg-[#0a0a0a] border-t border-[#333333]
                        text-[9px] uppercase tracking-widest text-steel-500 font-mono flex justify-between">
                        <span>{sorted.length} stops logged</span>
                        <span>
                            <span className="text-red-500/80">{sorted.filter((s) => s.risk_label === 'High').length} HIGH</span>  //{' '}
                            <span className="text-amber-500/80">{sorted.filter((s) => s.risk_label === 'Medium').length} MED</span> //{' '}
                            <span className="text-slate-500/80">{sorted.filter((s) => s.risk_label === 'Low').length} LOW</span>
                        </span>
                    </div>
                )}
            </div>
        </>
    )
}
