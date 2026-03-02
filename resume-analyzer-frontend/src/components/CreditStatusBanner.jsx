import React, { useState, useEffect, useCallback } from 'react';
import { creditAPI } from '../api';
import { AlertTriangle, Clock, Zap, X, RefreshCcw, ChevronDown, ChevronUp } from 'lucide-react';

const API_LABELS = {
    gemini: { name: 'Gemini AI', color: 'from-blue-500 to-cyan-400', icon: '🧠' },
    openai: { name: 'OpenAI GPT', color: 'from-emerald-500 to-green-400', icon: '🤖' },
    serpapi: { name: 'SerpAPI Jobs', color: 'from-orange-500 to-amber-400', icon: '🔍' },
};

export default function CreditStatusBanner() {
    const [creditData, setCreditData] = useState(null);
    const [dismissed, setDismissed] = useState(false);
    const [expanded, setExpanded] = useState(false);
    const [loading, setLoading] = useState(false);
    const [errorTriggered, setErrorTriggered] = useState(false);

    const fetchCredits = useCallback(async () => {
        try {
            setLoading(true);
            const res = await creditAPI.getStatus();
            setCreditData(res.data);
        } catch (err) {
            console.warn('Credit status fetch failed:', err);
        } finally {
            setLoading(false);
        }
    }, []);

    // Poll credits every 60 seconds
    useEffect(() => {
        fetchCredits();
        const interval = setInterval(fetchCredits, 60000);
        return () => clearInterval(interval);
    }, [fetchCredits]);

    // Also refetch when a credit-exhaustion event is fired from the axios interceptor
    useEffect(() => {
        const handler = () => {
            setErrorTriggered(true);
            setDismissed(false);
            fetchCredits();
        };
        window.addEventListener('api-credits-exhausted', handler);
        return () => window.removeEventListener('api-credits-exhausted', handler);
    }, [fetchCredits]);

    // Don't render if no data or user dismissed
    if (!creditData || dismissed) return null;

    const { credits, any_exhausted, exhausted_apis, reset_info } = creditData;

    // Don't show banner if nothing is exhausted and no error triggered
    if (!any_exhausted && !errorTriggered) return null;

    // If we had an error trigger but credits aren't actually exhausted, don't show
    if (!any_exhausted) return null;

    return (
        <div className="relative overflow-hidden">
            {/* Main Banner */}
            <div className="relative bg-gradient-to-r from-amber-900/40 via-orange-900/30 to-red-900/40 backdrop-blur-xl border border-amber-500/30 rounded-2xl mx-4 mt-4 shadow-[0_0_40px_rgba(245,158,11,0.15)]">
                {/* Animated shimmer overlay */}
                <div className="absolute inset-0 overflow-hidden rounded-2xl pointer-events-none">
                    <div className="absolute inset-0 bg-gradient-to-r from-transparent via-amber-400/5 to-transparent animate-shimmer" />
                </div>

                {/* Close button */}
                <button
                    onClick={() => setDismissed(true)}
                    className="absolute top-4 right-4 p-1.5 rounded-lg bg-white/5 hover:bg-white/10 text-slate-400 hover:text-white transition-all z-10"
                    title="Dismiss"
                >
                    <X size={14} />
                </button>

                <div className="p-5 pr-12">
                    {/* Top Row */}
                    <div className="flex items-center gap-3 mb-3">
                        <div className="relative">
                            <div className="w-10 h-10 bg-amber-500/20 rounded-xl flex items-center justify-center border border-amber-500/30">
                                <AlertTriangle size={20} className="text-amber-400" />
                            </div>
                            <div className="absolute -top-1 -right-1 w-3 h-3 bg-amber-500 rounded-full animate-pulse" />
                        </div>
                        <div>
                            <h3 className="text-sm font-black text-amber-300 tracking-wide uppercase">
                                Daily Credit Limit Reached
                            </h3>
                            <p className="text-xs text-amber-200/60 font-medium">
                                {exhausted_apis.join(', ')} {exhausted_apis.length === 1 ? 'has' : 'have'} exceeded today's free-tier quota
                            </p>
                        </div>
                    </div>

                    {/* Reset Timer */}
                    <div className="flex items-center gap-6 mb-3">
                        <div className="flex items-center gap-2 bg-white/5 px-4 py-2.5 rounded-xl border border-white/10">
                            <Clock size={16} className="text-cyan-400" />
                            <span className="text-sm font-bold text-white">
                                {reset_info?.reset_message || 'Credits reset at midnight'}
                            </span>
                        </div>
                        <button
                            onClick={fetchCredits}
                            disabled={loading}
                            className="flex items-center gap-1.5 text-xs font-bold text-slate-400 hover:text-white transition-colors"
                        >
                            <RefreshCcw size={12} className={loading ? 'animate-spin' : ''} />
                            Refresh
                        </button>
                    </div>

                    {/* Friendly Message */}
                    <p className="text-xs text-slate-300/80 font-medium leading-relaxed mb-2">
                        💡 <span className="text-amber-200/90">Don't worry!</span> Your AI features will automatically restore
                        when credits reset at midnight. Come back tomorrow for a fresh set of credits.
                        Features using exhausted APIs will use smart fallback responses in the meantime.
                    </p>

                    {/* Expand/Collapse Details */}
                    <button
                        onClick={() => setExpanded(!expanded)}
                        className="flex items-center gap-1.5 text-[11px] font-black text-indigo-400 hover:text-indigo-300 uppercase tracking-widest transition-colors"
                    >
                        {expanded ? <ChevronUp size={14} /> : <ChevronDown size={14} />}
                        {expanded ? 'Hide' : 'View'} Credit Details
                    </button>
                </div>

                {/* Expanded Credit Cards */}
                {expanded && credits && (
                    <div className="px-5 pb-5 grid grid-cols-1 sm:grid-cols-3 gap-3">
                        {Object.entries(credits).map(([api, info]) => {
                            const meta = API_LABELS[api] || { name: api, color: 'from-slate-500 to-slate-400', icon: '⚡' };
                            const percentage = info.percentage_used || 0;
                            const isExhausted = info.exhausted;

                            return (
                                <div
                                    key={api}
                                    className={`relative overflow-hidden rounded-xl border p-4 transition-all duration-300 ${isExhausted
                                            ? 'bg-red-950/40 border-red-500/30 shadow-[0_0_20px_rgba(239,68,68,0.1)]'
                                            : 'bg-white/5 border-white/10'
                                        }`}
                                >
                                    <div className="flex items-center justify-between mb-3">
                                        <div className="flex items-center gap-2">
                                            <span className="text-lg">{meta.icon}</span>
                                            <span className="text-xs font-black text-white uppercase tracking-wide">{meta.name}</span>
                                        </div>
                                        {isExhausted && (
                                            <span className="text-[9px] font-black text-red-400 bg-red-500/20 px-2 py-0.5 rounded-full uppercase tracking-widest animate-pulse">
                                                Exhausted
                                            </span>
                                        )}
                                        {!isExhausted && (
                                            <span className="text-[9px] font-black text-emerald-400 bg-emerald-500/20 px-2 py-0.5 rounded-full uppercase tracking-widest">
                                                Active
                                            </span>
                                        )}
                                    </div>

                                    {/* Progress Bar */}
                                    <div className="w-full h-2 bg-white/10 rounded-full overflow-hidden mb-2">
                                        <div
                                            className={`h-full rounded-full transition-all duration-700 bg-gradient-to-r ${isExhausted ? 'from-red-500 to-rose-400' : meta.color
                                                }`}
                                            style={{ width: `${Math.min(percentage, 100)}%` }}
                                        />
                                    </div>

                                    <div className="flex justify-between text-[10px] font-bold">
                                        <span className="text-slate-400">
                                            {info.used_today} / {info.daily_limit} used
                                        </span>
                                        <span className={isExhausted ? 'text-red-400' : 'text-emerald-400'}>
                                            {info.remaining} left
                                        </span>
                                    </div>
                                </div>
                            );
                        })}
                    </div>
                )}
            </div>

            {/* CSS for shimmer animation */}
            <style>{`
                @keyframes shimmer {
                    0% { transform: translateX(-100%); }
                    100% { transform: translateX(100%); }
                }
                .animate-shimmer {
                    animation: shimmer 3s ease-in-out infinite;
                }
            `}</style>
        </div>
    );
}
