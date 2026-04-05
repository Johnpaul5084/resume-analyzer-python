import React, { useState, useEffect, useRef } from 'react';
import { resumeAPI, autoApplyAPI } from '../api';
import {
    Zap, ExternalLink, Copy, Check, Search, MapPin, Building2,
    Briefcase, Loader2, AlertTriangle, Send, Globe, ChevronDown,
    ChevronRight, FileText, Sparkles, Clock, DollarSign, CheckCircle2,
    ArrowUpRight, Shield, RefreshCw, Filter
} from 'lucide-react';

const PLATFORM_ICONS = {
    linkedin: '💼', indeed: '🔍', glassdoor: '🏢', naukri: '🇮🇳',
    monster: '👾', wellfound: '🚀', dice: '🎲', internshala: '🎓',
    instahyre: '⚡', simplyhired: '📋', foundit: '🔎', hirist: '💻',
};

export default function AutoApply() {
    const [resumes, setResumes] = useState([]);
    const [selectedResumeId, setSelectedResumeId] = useState(null);
    const [resumeData, setResumeData] = useState(null);
    const [targetRole, setTargetRole] = useState('');
    const [location, setLocation] = useState('India');
    const [loading, setLoading] = useState(true);
    const [searching, setSearching] = useState(false);
    const [results, setResults] = useState(null);
    const [error, setError] = useState(null);
    const [copiedCover, setCopiedCover] = useState(false);
    const [showCoverLetter, setShowCoverLetter] = useState(false);
    const [filterPlatform, setFilterPlatform] = useState('all');
    const [appliedJobs, setAppliedJobs] = useState(new Set());

    const resultsRef = useRef(null);

    useEffect(() => {
        (async () => {
            try {
                const res = await resumeAPI.getAll();
                setResumes(res.data);
                if (res.data.length > 0) {
                    setSelectedResumeId(res.data[0].id);
                    const d = await resumeAPI.getById(res.data[0].id);
                    setResumeData(d.data);
                    if (d.data?.predicted_role && d.data.predicted_role !== 'Analyzing...')
                        setTargetRole(d.data.predicted_role);
                }
            } catch (e) { console.error(e); }
            finally { setLoading(false); }
        })();
    }, []);

    const handleResumeChange = async (id) => {
        setSelectedResumeId(id);
        try {
            const d = await resumeAPI.getById(id);
            setResumeData(d.data);
            if (d.data?.predicted_role && d.data.predicted_role !== 'Analyzing...')
                setTargetRole(d.data.predicted_role);
        } catch (e) { console.error(e); }
    };

    const searchJobs = async () => {
        if (!targetRole.trim()) return alert('Enter a target role');
        if (!resumeData) return;
        const text = resumeData.content_text || resumeData.content || '';
        if (!text.trim()) return alert('Resume content is empty.');

        setSearching(true); setError(null); setResults(null);
        try {
            const res = await autoApplyAPI.searchAndApply(text, targetRole, location);
            setResults(res.data);
            setTimeout(() => resultsRef.current?.scrollIntoView({ behavior: 'smooth' }), 300);
        } catch (e) {
            console.error(e);
            setError(e.response?.data?.error || e.message || 'Search failed.');
        } finally { setSearching(false); }
    };

    const markApplied = (idx) => {
        setAppliedJobs(prev => {
            const next = new Set(prev);
            next.has(idx) ? next.delete(idx) : next.add(idx);
            return next;
        });
    };

    const copyCoverLetter = () => {
        if (results?.cover_letter) {
            navigator.clipboard.writeText(results.cover_letter);
            setCopiedCover(true);
            setTimeout(() => setCopiedCover(false), 2000);
        }
    };

    if (loading) return (
        <div className="flex items-center justify-center min-h-[60vh]">
            <div className="flex flex-col items-center gap-4">
                <div className="animate-spin w-12 h-12 border-4 border-indigo-600 border-t-transparent rounded-full" />
                <p className="text-[10px] font-black text-slate-500 uppercase tracking-widest animate-pulse">
                    Loading Auto-Apply Engine
                </p>
            </div>
        </div>
    );

    if (!resumes.length) return (
        <div className="glass-card p-20 text-center max-w-2xl mx-auto mt-12">
            <Send size={56} className="text-indigo-400 mx-auto mb-6" />
            <h2 className="text-3xl font-black text-white mb-3 tracking-tighter">Upload a Resume First</h2>
            <p className="text-slate-500 text-sm mb-8">Auto-Apply needs a resume to find matching jobs.</p>
            <a href="/upload" className="btn-primary px-10 py-4 text-xs tracking-widest">UPLOAD RESUME</a>
        </div>
    );

    return (
        <div className="space-y-8">
            {/* ── HEADER ── */}
            <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
                <div>
                    <h1 className="text-4xl md:text-5xl font-black bg-gradient-to-r from-white via-emerald-200 to-cyan-300 bg-clip-text text-transparent tracking-tighter">
                        Auto-Apply Engine
                    </h1>
                    <p className="text-slate-500 font-bold uppercase text-[10px] tracking-widest mt-1">
                        One click → 12 Platforms → Real Jobs → AI Cover Letter → Apply
                    </p>
                </div>
                <select value={selectedResumeId || ''} onChange={(e) => handleResumeChange(Number(e.target.value))}
                    className="bg-white/5 border border-white/10 rounded-xl px-4 py-2.5 text-sm text-white font-bold outline-none focus:ring-2 focus:ring-emerald-600/20 appearance-none cursor-pointer min-w-[200px]">
                    {resumes.map(r => <option key={r.id} value={r.id} className="bg-slate-900 text-white">{r.title}</option>)}
                </select>
            </div>

            {/* ── SEARCH CONFIG ── */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                <div className="glass-card p-6">
                    <label className="block text-[10px] font-black uppercase tracking-widest text-emerald-400 mb-2">
                        🎯 Target Role
                    </label>
                    <input type="text" value={targetRole} onChange={(e) => setTargetRole(e.target.value)}
                        placeholder="e.g. Full Stack Developer"
                        className="w-full p-4 bg-black/40 border-2 border-emerald-500/30 rounded-xl text-sm text-white font-bold focus:ring-2 focus:ring-emerald-500/40 outline-none placeholder-slate-600" />
                </div>
                <div className="glass-card p-6">
                    <label className="block text-[10px] font-black uppercase tracking-widest text-emerald-400 mb-2">
                        📍 Location
                    </label>
                    <input type="text" value={location} onChange={(e) => setLocation(e.target.value)}
                        placeholder="e.g. Bangalore, Remote"
                        className="w-full p-4 bg-black/40 border-2 border-emerald-500/30 rounded-xl text-sm text-white font-bold focus:ring-2 focus:ring-emerald-500/40 outline-none placeholder-slate-600" />
                </div>
                <div className="glass-card p-6 flex items-end">
                    <button onClick={searchJobs} disabled={searching || !targetRole.trim()}
                        className="w-full px-6 py-4 bg-gradient-to-r from-emerald-600 to-cyan-600 text-white rounded-xl font-black uppercase tracking-[0.2em] text-xs shadow-[0_0_30px_rgba(16,185,129,0.3)] hover:shadow-[0_0_50px_rgba(16,185,129,0.5)] transition-all disabled:opacity-40 disabled:cursor-not-allowed flex items-center justify-center gap-3">
                        {searching ? <><Loader2 size={16} className="animate-spin" /> Searching...</> : <><Search size={16} /> Search & Generate</>}
                    </button>
                </div>
            </div>

            {/* ── PLATFORM BADGES ── */}
            <div className="glass-card p-6">
                <div className="flex items-center gap-3 mb-4">
                    <Globe size={16} className="text-cyan-400" />
                    <span className="text-[10px] font-black uppercase tracking-widest text-cyan-400">
                        Supported Platforms — Apply Across All
                    </span>
                </div>
                <div className="flex flex-wrap gap-2">
                    {Object.entries(PLATFORM_ICONS).map(([id, icon]) => (
                        <span key={id}
                            className="px-3 py-1.5 bg-white/5 border border-white/10 rounded-lg text-[10px] font-bold text-slate-400 flex items-center gap-1.5 hover:bg-white/10 transition-all">
                            <span className="text-sm">{icon}</span>
                            {id.charAt(0).toUpperCase() + id.slice(1)}
                        </span>
                    ))}
                </div>
            </div>

            {error && (
                <div className="bg-rose-500/10 border border-rose-500/20 p-5 rounded-xl flex items-start gap-3 text-rose-400 text-sm font-bold">
                    <AlertTriangle size={18} className="flex-shrink-0 mt-0.5" /><span>{error}</span>
                </div>
            )}

            {/* ══════════ RESULTS ══════════ */}
            {results && (
                <div ref={resultsRef} className="space-y-8 animate-fade-in">

                    {/* ── APPLY TIPS ── */}
                    {results.apply_tips && (
                        <div className="glass-card p-6">
                            <h3 className="text-sm font-black text-white flex items-center gap-2 mb-3">
                                <Sparkles size={16} className="text-amber-400" /> AI Apply Strategy
                            </h3>
                            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-2">
                                {results.apply_tips.map((tip, i) => (
                                    <p key={i} className="text-[11px] text-slate-400 font-medium bg-white/5 px-3 py-2 rounded-lg">{tip}</p>
                                ))}
                            </div>
                        </div>
                    )}

                    {/* ── RESUME KEYWORDS ── */}
                    {results.resume_keywords?.length > 0 && (
                        <div className="flex items-center gap-3 flex-wrap">
                            <span className="text-[10px] font-black text-slate-500 uppercase tracking-widest">Your Key Skills:</span>
                            {results.resume_keywords.map((kw, i) => (
                                <span key={i} className="px-3 py-1 bg-emerald-600/10 border border-emerald-500/20 rounded-full text-[10px] font-bold text-emerald-400">
                                    {kw}
                                </span>
                            ))}
                        </div>
                    )}

                    {/* ── PLATFORM QUICK-APPLY LINKS ── */}
                    {results.platform_links?.length > 0 && (
                        <div className="space-y-4">
                            <h2 className="text-xl font-black text-white tracking-tight flex items-center gap-3">
                                <Globe size={20} className="text-cyan-400" /> Quick Apply — 12 Platforms
                            </h2>
                            <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-3">
                                {results.platform_links.map((p) => (
                                    <a key={p.platform_id} href={p.apply_url} target="_blank" rel="noopener noreferrer"
                                        className="group glass-card p-4 hover:bg-white/10 transition-all flex flex-col gap-2 cursor-pointer border border-white/5 hover:border-emerald-500/30">
                                        <div className="flex items-center gap-2">
                                            <span className="text-xl">{p.icon}</span>
                                            <span className="text-xs font-black text-white">{p.name}</span>
                                            <ArrowUpRight size={12} className="text-slate-600 ml-auto group-hover:text-emerald-400 transition-colors" />
                                        </div>
                                        <p className="text-[10px] text-slate-500 font-medium line-clamp-2">{p.description}</p>
                                        <div className="flex items-center gap-2 mt-auto">
                                            {p.supports_easy_apply && (
                                                <span className="text-[8px] font-black px-2 py-0.5 bg-emerald-600/20 text-emerald-400 rounded-full uppercase tracking-wider">
                                                    Easy Apply
                                                </span>
                                            )}
                                            <span className="text-[8px] font-bold text-slate-600 uppercase">{p.regions?.join(', ')}</span>
                                        </div>
                                    </a>
                                ))}
                            </div>
                        </div>
                    )}

                    {/* ── AI COVER LETTER ── */}
                    {results.cover_letter && (
                        <div className="glass-card overflow-hidden">
                            <div className="p-4 border-b border-white/5 bg-violet-500/5 flex items-center justify-between cursor-pointer"
                                onClick={() => setShowCoverLetter(!showCoverLetter)}>
                                <div className="flex items-center gap-2">
                                    <FileText size={16} className="text-violet-400" />
                                    <span className="text-sm font-black text-white">AI-Generated Cover Letter</span>
                                    <span className="text-[9px] font-bold px-2 py-0.5 bg-violet-600/20 text-violet-400 rounded-full uppercase tracking-wider">
                                        Ready to Use
                                    </span>
                                </div>
                                <div className="flex items-center gap-2">
                                    <button onClick={(e) => { e.stopPropagation(); copyCoverLetter(); }}
                                        className="px-3 py-1.5 bg-violet-600/10 border border-violet-500/20 hover:bg-violet-600 rounded-lg text-[10px] font-black uppercase tracking-widest text-violet-400 hover:text-white flex items-center gap-1.5 transition-all">
                                        {copiedCover ? <><Check size={12} /> Copied!</> : <><Copy size={12} /> Copy</>}
                                    </button>
                                    <ChevronDown size={16} className={`text-slate-500 transition-transform ${showCoverLetter ? 'rotate-180' : ''}`} />
                                </div>
                            </div>
                            {showCoverLetter && (
                                <div className="p-6">
                                    <p className="text-sm text-slate-300 whitespace-pre-line leading-relaxed font-medium">{results.cover_letter}</p>
                                </div>
                            )}
                        </div>
                    )}

                    {/* ── REAL JOB LISTINGS ── */}
                    {results.real_jobs?.length > 0 && (
                        <div className="space-y-4">
                            <div className="flex items-center justify-between">
                                <h2 className="text-xl font-black text-white tracking-tight flex items-center gap-3">
                                    <Briefcase size={20} className="text-emerald-400" />
                                    Live Jobs — {results.real_jobs.length} Found
                                    <span className="text-[9px] font-bold px-2 py-0.5 bg-emerald-600/20 text-emerald-400 rounded-full uppercase tracking-wider">
                                        Real-Time
                                    </span>
                                </h2>
                                <div className="flex items-center gap-2 text-[10px] font-black text-slate-500 uppercase tracking-widest">
                                    <CheckCircle2 size={12} className="text-emerald-500" />
                                    {appliedJobs.size} Applied
                                </div>
                            </div>

                            <div className="space-y-3">
                                {results.real_jobs.map((job, idx) => (
                                    <div key={idx}
                                        className={`glass-card p-5 transition-all ${appliedJobs.has(idx) ? 'border-emerald-500/30 bg-emerald-500/5' : 'hover:bg-white/5'}`}>
                                        <div className="flex flex-col md:flex-row md:items-start justify-between gap-4">
                                            <div className="flex-1 space-y-2">
                                                <div className="flex items-start gap-3">
                                                    <div className="w-10 h-10 bg-gradient-to-br from-indigo-600/30 to-violet-600/30 rounded-xl flex items-center justify-center flex-shrink-0">
                                                        <Building2 size={18} className="text-indigo-400" />
                                                    </div>
                                                    <div className="flex-1">
                                                        <h3 className="text-sm font-black text-white tracking-tight">{job.title}</h3>
                                                        <p className="text-xs font-bold text-indigo-400">{job.company}</p>
                                                    </div>
                                                </div>

                                                <div className="flex flex-wrap gap-3 text-[10px] font-bold text-slate-500">
                                                    <span className="flex items-center gap-1"><MapPin size={10} /> {job.location}</span>
                                                    <span className="flex items-center gap-1"><DollarSign size={10} /> {job.salary}</span>
                                                    <span className="flex items-center gap-1"><Clock size={10} /> {job.posted}</span>
                                                    <span className="flex items-center gap-1"><Briefcase size={10} /> {job.job_type}</span>
                                                    {job.is_remote && (
                                                        <span className="px-2 py-0.5 bg-emerald-600/20 text-emerald-400 rounded-full uppercase tracking-wider">Remote</span>
                                                    )}
                                                </div>

                                                {job.description && (
                                                    <p className="text-[11px] text-slate-500 font-medium line-clamp-2 leading-relaxed">{job.description}</p>
                                                )}
                                            </div>

                                            <div className="flex items-center gap-2 flex-shrink-0">
                                                <button onClick={() => markApplied(idx)}
                                                    className={`px-3 py-2 rounded-lg text-[10px] font-black uppercase tracking-widest border transition-all flex items-center gap-1.5 ${
                                                        appliedJobs.has(idx) ? 'border-emerald-500/40 bg-emerald-600/20 text-emerald-400' : 'border-white/10 text-slate-500 hover:border-amber-500/30 hover:text-amber-400'
                                                    }`}>
                                                    {appliedJobs.has(idx) ? <><CheckCircle2 size={12} /> Applied</> : <><Shield size={12} /> Mark Applied</>}
                                                </button>
                                                {job.apply_link && job.apply_link !== '#' ? (
                                                    <a href={job.apply_link} target="_blank" rel="noopener noreferrer"
                                                        className="px-5 py-2 bg-gradient-to-r from-emerald-600 to-cyan-600 text-white rounded-lg text-[10px] font-black uppercase tracking-widest flex items-center gap-1.5 hover:shadow-[0_0_20px_rgba(16,185,129,0.3)] transition-all">
                                                        <ExternalLink size={12} /> Apply Now
                                                    </a>
                                                ) : (
                                                    <a href={`https://www.linkedin.com/jobs/search/?keywords=${encodeURIComponent(job.title + ' ' + job.company)}`}
                                                        target="_blank" rel="noopener noreferrer"
                                                        className="px-5 py-2 bg-gradient-to-r from-blue-600 to-indigo-600 text-white rounded-lg text-[10px] font-black uppercase tracking-widest flex items-center gap-1.5 hover:shadow-[0_0_20px_rgba(37,99,235,0.3)] transition-all">
                                                        <ExternalLink size={12} /> Find on LinkedIn
                                                    </a>
                                                )}
                                            </div>
                                        </div>
                                        {job.apply_platform && (
                                            <div className="mt-2 text-[9px] font-bold text-slate-600 uppercase tracking-widest">
                                                via {job.apply_platform}
                                            </div>
                                        )}
                                    </div>
                                ))}
                            </div>
                        </div>
                    )}

                    {/* ── COMPLETION BANNER ── */}
                    <div className="bg-gradient-to-r from-emerald-600/10 via-cyan-600/10 to-blue-600/10 border border-emerald-500/20 p-8 rounded-2xl text-center space-y-4">
                        <CheckCircle2 size={40} className="text-emerald-400 mx-auto" />
                        <h3 className="text-xl font-black text-white tracking-tight">
                            Auto-Apply Ready — {results.platform_links?.length || 12} Platforms Connected
                        </h3>
                        <p className="text-slate-400 text-sm font-medium max-w-2xl mx-auto">
                            Found <strong className="text-white">{results.real_jobs?.length || 0} real jobs</strong> for
                            <strong className="text-emerald-400"> {targetRole}</strong> in <strong className="text-cyan-400">{location}</strong>.
                            Apply across LinkedIn, Indeed, Glassdoor, Naukri, Monster, Wellfound, Dice, Internshala, Instahyre,
                            SimplyHired, Foundit, and Hirist — all from one place.
                        </p>
                        <p className="text-[10px] text-slate-600 font-bold uppercase tracking-widest">
                            AI Cover Letter Generated • {appliedJobs.size} Tracked • Zero Platform Fees
                        </p>
                        <button onClick={searchJobs}
                            className="px-6 py-3 bg-white/5 border border-white/10 rounded-xl text-[10px] font-black uppercase tracking-widest text-slate-400 hover:bg-emerald-600/10 hover:text-emerald-400 transition-all flex items-center gap-2 mx-auto">
                            <RefreshCw size={12} /> Search Again
                        </button>
                    </div>
                </div>
            )}
        </div>
    );
}
