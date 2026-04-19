import { useState, useEffect } from 'react'
import {
    X, Navigation, AlertTriangle, CheckCircle2, Clock, MapPin, 
    AlertOctagon, CloudLightning, Activity
} from 'lucide-react'
import api from '@/lib/api'
import type { EnrichedStop } from '@/types'
import { MapContainer, TileLayer, Marker, Popup } from 'react-leaflet'
import { divIcon } from 'leaflet'

interface Props {
    stop: EnrichedStop
    onClose: () => void
    onStatusUpdate: (stopId: number, newStatus: string) => void
}

export default function RiderView({ stop, onClose, onStatusUpdate }: Props) {
    const [loading, setLoading] = useState<'complete' | 'fail' | null>(null)
    const [error, setError] = useState<string | null>(null)
    const [reportModalOpen, setReportModalOpen] = useState(false)
    
    // Automatic Rerouting Effect State
    const [weatherSeverity, setWeatherSeverity] = useState(stop.weather_condition)
    const [isOptimizing, setIsOptimizing] = useState(false)

    // Simulate weather worsening and automatic reroute after 10 seconds viewing
    useEffect(() => {
        if (stop.status !== 'pending' || weatherSeverity === 'Storm') return
        
        const timer = setTimeout(() => {
            setWeatherSeverity('Storm')
            setIsOptimizing(true)
            
            // "Optimizing" blocks UI for 3 seconds then clears
            setTimeout(() => {
                setIsOptimizing(false)
            }, 3000)
            
        }, 8000) // 8 seconds in RiderView triggers a simulated storm shift
        
        return () => clearTimeout(timer)
    }, [stop.status, weatherSeverity])

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

    const markerSvg = `
    <svg xmlns="http://www.w3.org/2000/svg" width="28" height="36" viewBox="0 0 28 36">
      <path d="M14 0C6.268 0 0 6.268 0 14c0 9.333 14 22 14 22S28 23.333 28 14C28 6.268 21.732 0 14 0z" fill="#f59e0b" opacity="0.95"/>
      <circle cx="14" cy="14" r="5" fill="#111111" opacity="0.9"/>
    </svg>`

    const icon = divIcon({
        html: markerSvg,
        className: '',
        iconSize: [28, 36],
        iconAnchor: [14, 36]
    })

    return (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4" style={{ background: 'rgba(8,8,8,0.92)', backdropFilter: 'blur(8px)' }}>
            
            {/* Optimizing Overlay */}
            {isOptimizing && (
                <div className="absolute inset-0 z-[60] flex flex-col items-center justify-center bg-[#080808]/80 backdrop-blur-md">
                    <CloudLightning className="w-16 h-16 text-amber-500 mb-4 animate-pulse" />
                    <h2 className="text-xl font-bold text-amber-400 font-mono tracking-widest uppercase">Severe Weather Shift</h2>
                    <p className="text-steel-400 mt-2 font-mono text-xs animate-pulse">Calculating alternative route constraints...</p>
                </div>
            )}

            {/* Close */}
            <button
                onClick={onClose}
                disabled={isOptimizing}
                className="absolute top-6 right-6 w-10 h-10 bg-[#111111] border border-steel flex items-center justify-center text-steel-400 hover:text-amber-500 hover:border-amber-500 transition-all z-[55] disabled:opacity-0"
                aria-label="Close Rider View"
            >
                <X className="w-5 h-5" />
            </button>

            {/* Main Window */}
            <div className="w-full max-w-5xl h-[85vh] flex flex-col lg:flex-row border border-[#333333] shadow-2xl relative">
                
                {/* Left side: Maps Context */}
                <div className="flex-1 bg-[#0a0a0a] relative border-r border-[#333333]">
                    <div className="absolute top-4 left-4 z-[400] bg-[#080808]/90 border border-amber-500/30 px-3 py-1.5 backdrop-blur font-mono text-[10px] text-amber-400 uppercase tracking-widest flex items-center gap-2 shadow-glow-amber-sm">
                        <Navigation className="w-3 h-3" />
                        Live Routing
                    </div>
                    <MapContainer
                        center={[stop.latitude, stop.longitude]}
                        zoom={15}
                        style={{ width: '100%', height: '100%' }}
                        zoomControl={false}
                        attributionControl={false}
                    >
                        <TileLayer url="https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png" maxZoom={19} />
                        <Marker position={[stop.latitude, stop.longitude]} icon={icon} />
                    </MapContainer>
                </div>

                {/* Right side: Execution Pane */}
                <div className="w-full lg:w-[400px] shrink-0 bg-[#0f0f0f] flex flex-col pt-8 pb-6 px-6">
                    
                    <div className="mb-8">
                        <h1 className="text-2xl font-bold text-slate-200 mb-2">{stop.name}</h1>
                        <div className="flex items-start gap-2 text-steel-400 text-xs">
                            <MapPin className="w-3.5 h-3.5 mt-0.5 shrink-0" />
                            <span>{stop.address}</span>
                        </div>
                    </div>

                    {/* Environment Metrics */}
                    <div className="grid grid-cols-2 gap-3 mb-6">
                        <div className="border border-[#222222] bg-[#141414] p-3">
                            <p className="text-[10px] text-steel-500 uppercase tracking-widest mb-1.5">Current Status</p>
                            <p className={`font-mono text-xs uppercase ${stop.status === 'delivered' ? 'text-steel-400' : 'text-amber-400'}`}>
                                {stop.status}
                            </p>
                        </div>
                        <div className={`border p-3 transition-all ${weatherSeverity === 'Storm' ? 'border-amber-500/40 bg-[#1a1205]' : 'border-[#222222] bg-[#141414]'}`}>
                            <p className="text-[10px] text-steel-500 uppercase tracking-widest mb-1.5 flex justify-between">
                                Weather <CloudLightning className="w-3 h-3" />
                            </p>
                            <p className={`font-mono text-xs uppercase ${weatherSeverity === 'Storm' ? 'text-amber-500' : 'text-slate-300'}`}>
                                {weatherSeverity}
                            </p>
                        </div>
                    </div>

                    {/* Risk Reason if high */}
                    {stop.risk_reason && stop.risk_label === "High" && (
                        <div className="flex gap-3 mb-4 p-4 border border-red-500/30 bg-[#2e0909]">
                            <AlertOctagon className="w-6 h-6 text-red-500" />
                            <div>
                                <p className="text-[10px] text-red-400 uppercase tracking-widest">Active Hazard Report</p>
                                <p className="text-xs text-red-100 font-mono mt-1">{stop.risk_reason}</p>
                            </div>
                        </div>
                    )}

                    {/* Recommendation Engine Tag */}
                    {stop.recommendation && (
                        <div className="flex gap-3 mb-6 p-4 border border-amber-500/30 bg-[#2d1b05]">
                            <Activity className="w-6 h-6 text-amber-500" />
                            <div>
                                <p className="text-[10px] text-amber-400 uppercase tracking-widest">Strategic Recommendation</p>
                                <p className="text-xs text-amber-100 font-mono mt-1">{stop.recommendation}</p>
                            </div>
                        </div>
                    )}

                    <div className="mt-auto space-y-3">
                        {error && <div className="text-[10px] uppercase tracking-widest text-[#ef4444] font-mono mb-2">{error}</div>}

                        {stop.status === 'pending' ? (
                            <>
                                <button
                                    onClick={() => updateStatus('delivered')}
                                    disabled={loading !== null || isOptimizing}
                                    className="w-full flex items-center justify-center gap-2 py-4 bg-[#111111] border-2 border-[#333333] hover:border-amber-500 hover:text-amber-400 text-slate-300 font-bold uppercase tracking-widest text-xs transition-colors disabled:opacity-50"
                                >
                                    {loading === 'complete' ? 'Confirming...' : <><CheckCircle2 className="w-4 h-4" /> Drop-off Complete</>}
                                </button>
                                
                                <div className="flex gap-2">
                                    <button
                                        onClick={() => updateStatus('failed')}
                                        disabled={loading !== null || isOptimizing}
                                        className="flex-1 py-3 bg-[#111111] border border-[#222222] hover:border-red-500/50 hover:bg-[#1a0a0a] text-steel-400 hover:text-red-400 font-mono text-[10px] uppercase tracking-widest transition-colors disabled:opacity-50"
                                    >
                                        {loading === 'fail' ? '...' : 'Mark Failed'}
                                    </button>
                                    <button
                                        onClick={() => setReportModalOpen(true)}
                                        disabled={loading !== null || isOptimizing}
                                        className="flex-1 py-3 bg-[#111111] border border-[#222222] hover:bg-[#151515] text-steel-400 font-mono text-[10px] uppercase tracking-widest transition-colors disabled:opacity-50 flex justify-center items-center gap-1.5"
                                    >
                                        <AlertTriangle className="w-3.5 h-3.5" /> Report Issue
                                    </button>
                                </div>
                            </>
                        ) : (
                            <div className="text-center py-6 border border-[#222] bg-[#111111]">
                                <CheckCircle2 className="w-8 h-8 text-steel-600 mx-auto mb-2" />
                                <p className="text-xs text-steel-400 font-mono uppercase tracking-widest">Route Inactive</p>
                            </div>
                        )}
                    </div>
                </div>
            </div>

            {/* Report Modal */}
            {reportModalOpen && (
                <div className="absolute inset-0 z-[60] bg-black/80 backdrop-blur-sm flex items-center justify-center p-4">
                    <div className="w-full max-w-sm bg-[#111111] border border-amber-500/50 shadow-glow-amber-sm p-6">
                        <h3 className="text-amber-500 font-bold uppercase tracking-widest text-sm mb-4">Transmission Alert</h3>
                        <p className="text-steel-400 text-xs font-mono mb-6">Dispatch has been notified of an exception at these coordinates. Support pipeline open.</p>
                        <button 
                            onClick={() => setReportModalOpen(false)}
                            className="w-full py-2 bg-[#1a1205] border border-amber-500/30 text-amber-500 text-xs font-bold uppercase tracking-widest hover:bg-amber-500 hover:text-black transition-colors"
                        >
                            Acknowledge
                        </button>
                    </div>
                </div>
            )}

        </div>
    )
}
