import React, { useState, useEffect, useRef } from 'react';
import { resumeAPI, companyAtsAPI, rewriteAPI, resumeBuilderAPI, interviewPrepAPI, strengthRadarAPI } from '../api';
import { Zap, Building2, Download, Copy, Check, ChevronRight, AlertTriangle, Sparkles, FileText, RefreshCw, CheckCircle2, Loader2, MessageSquareText, Radar, Eye, EyeOff, ChevronDown, HelpCircle } from 'lucide-react';
import html2pdf from 'html2pdf.js';

const STEP_COLORS = {
    pending: 'bg-white/5 border-white/10 text-slate-600',
    active: 'bg-indigo-600/20 border-indigo-500/40 text-indigo-400 animate-pulse',
    done: 'bg-emerald-600/20 border-emerald-500/40 text-emerald-400',
};

const COMPANY_COLORS = {
    google: { bg: 'from-blue-600/20 to-blue-500/5', border: 'border-blue-500/30', text: 'text-blue-400' },
    amazon: { bg: 'from-orange-600/20 to-orange-500/5', border: 'border-orange-500/30', text: 'text-orange-400' },
    microsoft: { bg: 'from-cyan-600/20 to-cyan-500/5', border: 'border-cyan-500/30', text: 'text-cyan-400' },
    meta: { bg: 'from-blue-700/20 to-blue-600/5', border: 'border-blue-600/30', text: 'text-blue-300' },
    tcs: { bg: 'from-red-600/20 to-red-500/5', border: 'border-red-500/30', text: 'text-red-400' },
    infosys: { bg: 'from-violet-600/20 to-violet-500/5', border: 'border-violet-500/30', text: 'text-violet-400' },
    wipro: { bg: 'from-purple-600/20 to-purple-500/5', border: 'border-purple-500/30', text: 'text-purple-400' },
};

const TEMPLATES = [
    { id: 'classic', name: 'Classic', icon: '📄', color: 'border-slate-500/30' },
    { id: 'modern', name: 'Modern', icon: '💎', color: 'border-blue-500/30' },
    { id: 'academic', name: 'Academic', icon: '🎓', color: 'border-purple-500/30' },
    { id: 'minimal', name: 'Minimal', icon: '⚡', color: 'border-emerald-500/30' },
    { id: 'executive', name: 'Executive', icon: '👔', color: 'border-rose-500/30' },
];

// ── SVG Radar Chart Component ──
function RadarChart({ dimensions }) {
    if (!dimensions) return null;
    const labels = Object.keys(dimensions);
    const values = Object.values(dimensions);
    const n = labels.length;
    const cx = 120, cy = 120, R = 90;

    const angleFor = (i) => (Math.PI * 2 * i) / n - Math.PI / 2;
    const pointAt = (i, r) => {
        const a = angleFor(i);
        return [cx + r * Math.cos(a), cy + r * Math.sin(a)];
    };

    const gridLevels = [0.25, 0.5, 0.75, 1.0];

    return (
        <svg viewBox="0 0 240 240" className="w-full max-w-[280px] mx-auto">
            {/* Grid lines */}
            {gridLevels.map(level => (
                <polygon key={level} points={Array.from({ length: n }, (_, i) => pointAt(i, R * level).join(',')).join(' ')}
                    fill="none" stroke="rgba(255,255,255,0.06)" strokeWidth="1" />
            ))}
            {/* Axes */}
            {labels.map((_, i) => {
                const [x, y] = pointAt(i, R);
                return <line key={i} x1={cx} y1={cy} x2={x} y2={y} stroke="rgba(255,255,255,0.05)" strokeWidth="1" />;
            })}
            {/* Data polygon */}
            <polygon
                points={values.map((v, i) => pointAt(i, R * (v / 100)).join(',')).join(' ')}
                fill="rgba(99,102,241,0.15)" stroke="rgba(99,102,241,0.7)" strokeWidth="2"
            />
            {/* Data points */}
            {values.map((v, i) => {
                const [x, y] = pointAt(i, R * (v / 100));
                return <circle key={i} cx={x} cy={y} r="3" fill="#6366f1" />;
            })}
            {/* Labels */}
            {labels.map((label, i) => {
                const [x, y] = pointAt(i, R + 18);
                const short = label.split(' ').map(w => w[0]).join('');
                return (
                    <text key={i} x={x} y={y} textAnchor="middle" dominantBaseline="middle"
                        className="fill-slate-400 text-[7px] font-bold uppercase">
                        {short}
                    </text>
                );
            })}
        </svg>
    );
}

export default function SmartPipeline() {
    const [resumes, setResumes] = useState([]);
    const [selectedResumeId, setSelectedResumeId] = useState(null);
    const [resumeData, setResumeData] = useState(null);
    const [targetRole, setTargetRole] = useState('');
    const [selectedTemplate, setSelectedTemplate] = useState('classic');
    const [selectedCompanies, setSelectedCompanies] = useState(['google', 'amazon', 'microsoft', 'tcs', 'infosys']);
    const [loading, setLoading] = useState(true);

    // Pipeline state
    const [running, setRunning] = useState(false);
    const [step, setStep] = useState(0);
    const [atsResults, setAtsResults] = useState(null);
    const [rewriteResult, setRewriteResult] = useState(null);
    const [resumeHtml, setResumeHtml] = useState(null);
    const [interviewPrep, setInterviewPrep] = useState(null);
    const [strengthData, setStrengthData] = useState(null);
    const [error, setError] = useState(null);
    const [copied, setCopied] = useState(false);
    const [downloading, setDownloading] = useState(false);
    const [showPreview, setShowPreview] = useState(true);
    const [activeTab, setActiveTab] = useState('preview');

    const resultsRef = useRef(null);
    const previewRef = useRef(null);

    useEffect(() => {
        (async () => {
            try {
                const res = await resumeAPI.getAll();
                setResumes(res.data);
                if (res.data.length > 0) {
                    setSelectedResumeId(res.data[0].id);
                    const d = await resumeAPI.getById(res.data[0].id);
                    setResumeData(d.data);
                    if (d.data?.predicted_role && d.data.predicted_role !== 'Analyzing...') setTargetRole(d.data.predicted_role);
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
            if (d.data?.predicted_role && d.data.predicted_role !== 'Analyzing...') setTargetRole(d.data.predicted_role);
        } catch (e) { console.error(e); }
    };

    const toggleCompany = (c) => setSelectedCompanies(prev => prev.includes(c) ? prev.filter(x => x !== c) : [...prev, c]);

    const scoreColor = (s) => s >= 75 ? 'text-emerald-400' : s >= 50 ? 'text-amber-400' : 'text-rose-400';
    const barColor = (s) => s >= 75 ? 'bg-emerald-500' : s >= 50 ? 'bg-amber-500' : 'bg-rose-500';

    // ── RUN PIPELINE ──
    const runPipeline = async () => {
        if (!targetRole.trim()) return alert('Enter a target role');
        if (!resumeData) return;
        const text = resumeData.content_text || resumeData.content || '';
        if (!text.trim()) return alert('Resume content is empty.');

        setRunning(true); setError(null);
        setAtsResults(null); setRewriteResult(null); setResumeHtml(null);
        setInterviewPrep(null); setStrengthData(null);

        try {
            // Step 1: ATS
            setStep(1);
            const ats = await companyAtsAPI.scoreAll(text, targetRole, selectedCompanies);
            setAtsResults(ats.data);

            // Step 2: Grammar + Rewrite
            setStep(2);
            const grammar = await rewriteAPI.enhanceGrammar(text);
            const enhanced = grammar.data.enhanced_text || text;
            setStep(3);
            const rw = await rewriteAPI.transform(enhanced, targetRole, 'ATS');
            setRewriteResult(rw.data.rewritten_resume);

            // Step 4: Build Resume (OUR OWN HTML TEMPLATE)
            setStep(4);
            const build = await resumeBuilderAPI.build(rw.data.rewritten_resume || text, selectedTemplate, targetRole);
            if (build.data?.success) setResumeHtml(build.data.resume_html);

            // Step 5: Interview Prep + Strength Radar (concurrent)
            setStep(5);
            const [intv, str] = await Promise.all([
                interviewPrepAPI.generate(text, targetRole),
                strengthRadarAPI.analyze(text, targetRole),
            ]);
            if (intv.data?.success) setInterviewPrep(intv.data.interview_prep);
            if (str.data?.success) setStrengthData(str.data);

            setStep(6);
            setTimeout(() => resultsRef.current?.scrollIntoView({ behavior: 'smooth' }), 300);
        } catch (e) {
            console.error(e);
            setError(e.response?.data?.error || e.message || 'Pipeline failed.');
        } finally { setRunning(false); }
    };

    // ── DOWNLOAD PDF (from HTML) ──
    const downloadPDF = async () => {
        if (!resumeHtml) return;
        setDownloading(true);
        const container = document.createElement('div');
        container.innerHTML = resumeHtml;
        try {
            const title = resumeData?.title || 'Resume';
            await html2pdf().set({
                margin: 0,
                filename: `${title.replace(/[^a-z0-9]/gi, '_')}_${targetRole.replace(/[^a-z0-9]/gi, '_')}.pdf`,
                image: { type: 'jpeg', quality: 0.98 },
                html2canvas: { scale: 2, useCORS: true },
                jsPDF: { unit: 'mm', format: 'a4', orientation: 'portrait' }
            }).from(container).save();
        } catch (e) { console.error(e); }
        finally { setDownloading(false); }
    };

    const copyRewrite = () => {
        if (rewriteResult) {
            navigator.clipboard.writeText(rewriteResult);
            setCopied(true);
            setTimeout(() => setCopied(false), 2000);
        }
    };

    if (loading) return (
        <div className="flex items-center justify-center min-h-[60vh]">
            <div className="flex flex-col items-center gap-4">
                <div className="animate-spin w-12 h-12 border-4 border-indigo-600 border-t-transparent rounded-full" />
                <p className="text-[10px] font-black text-slate-500 uppercase tracking-widest animate-pulse">Initializing Pipeline</p>
            </div>
        </div>
    );

    if (!resumes.length) return (
        <div className="glass-card p-20 text-center max-w-2xl mx-auto mt-12">
            <Zap size={56} className="text-indigo-400 mx-auto mb-6" />
            <h2 className="text-3xl font-black text-white mb-3 tracking-tighter">Upload a Resume First</h2>
            <p className="text-slate-500 text-sm mb-8">The AI Pipeline needs a resume to analyze.</p>
            <a href="/upload" className="btn-primary px-10 py-4 text-xs tracking-widest">UPLOAD RESUME</a>
        </div>
    );

    return (
        <div className="space-y-8">
            {/* ── HEADER ── */}
            <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
                <div>
                    <h1 className="text-4xl md:text-5xl font-black bg-gradient-to-r from-white via-indigo-200 to-violet-300 bg-clip-text text-transparent tracking-tighter">
                        AI Smart Pipeline
                    </h1>
                    <p className="text-slate-500 font-bold uppercase text-[10px] tracking-widest mt-1">
                        ATS Score → Grammar → Rewrite → Resume Build → Interview Prep → Download
                    </p>
                </div>
                <select value={selectedResumeId || ''} onChange={(e) => handleResumeChange(Number(e.target.value))}
                    className="bg-white/5 border border-white/10 rounded-xl px-4 py-2.5 text-sm text-white font-bold outline-none focus:ring-2 focus:ring-indigo-600/20 appearance-none cursor-pointer min-w-[200px]">
                    {resumes.map(r => <option key={r.id} value={r.id} className="bg-slate-900 text-white">{r.title}</option>)}
                </select>
            </div>

            {/* ── CONFIG PANEL ── */}
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                {/* Role */}
                <div className="glass-card p-6">
                    <label className="block text-[10px] font-black uppercase tracking-widest text-indigo-400 mb-2">🎯 Target Role</label>
                    <input type="text" value={targetRole} onChange={(e) => setTargetRole(e.target.value)}
                        placeholder="e.g. DevOps Engineer, Data Scientist"
                        className="w-full p-4 bg-black/40 border-2 border-indigo-500/30 rounded-xl text-sm text-white font-bold focus:ring-2 focus:ring-indigo-500/40 outline-none placeholder-slate-600" />
                </div>
                {/* Companies */}
                <div className="glass-card p-6">
                    <label className="block text-[10px] font-black uppercase tracking-widest text-indigo-400 mb-3">🏢 Companies</label>
                    <div className="flex flex-wrap gap-2">
                        {Object.keys(COMPANY_COLORS).map(c => (
                            <button key={c} onClick={() => toggleCompany(c)}
                                className={`px-3 py-1.5 rounded-lg text-[10px] font-black uppercase tracking-wider transition-all border ${
                                    selectedCompanies.includes(c) ? `${COMPANY_COLORS[c].border} ${COMPANY_COLORS[c].text} bg-white/10` : 'border-white/5 text-slate-600'
                                }`}>{c.charAt(0).toUpperCase() + c.slice(1)}</button>
                        ))}
                    </div>
                </div>
                {/* Template */}
                <div className="glass-card p-6">
                    <label className="block text-[10px] font-black uppercase tracking-widest text-indigo-400 mb-3">📝 Resume Template</label>
                    <div className="grid grid-cols-5 gap-2">
                        {TEMPLATES.map(t => (
                            <button key={t.id} onClick={() => setSelectedTemplate(t.id)}
                                className={`p-2 rounded-lg border text-center transition-all ${selectedTemplate === t.id ? 'border-indigo-500/50 bg-indigo-600/10' : `border-white/5 bg-white/5`}`}>
                                <span className="text-lg">{t.icon}</span>
                                <p className="text-[8px] font-bold mt-1 text-white">{t.name}</p>
                            </button>
                        ))}
                    </div>
                </div>
            </div>

            {/* ── RUN BUTTON ── */}
            <div className="flex justify-center">
                <button onClick={runPipeline} disabled={running || !targetRole.trim()}
                    className="group px-12 py-5 bg-gradient-to-r from-indigo-600 via-violet-600 to-indigo-600 bg-[length:200%_100%] animate-gradient-x text-white rounded-2xl font-black uppercase tracking-[0.3em] text-xs shadow-[0_0_40px_rgba(79,70,229,0.3)] hover:shadow-[0_0_60px_rgba(79,70,229,0.5)] transition-all disabled:opacity-40 disabled:cursor-not-allowed flex items-center gap-4">
                    {running ? <><Loader2 size={18} className="animate-spin" /> Processing...</> : <><Zap size={18} /> Run Full Pipeline</>}
                </button>
            </div>

            {/* ── PIPELINE STEPS ── */}
            {(running || step > 0) && (
                <div className="flex items-center justify-center gap-2 flex-wrap">
                    {[{s:1,l:'ATS',i:<Building2 size={12}/>},{s:2,l:'Grammar',i:<FileText size={12}/>},{s:3,l:'Rewrite',i:<Sparkles size={12}/>},{s:4,l:'Resume',i:<Eye size={12}/>},{s:5,l:'Interview',i:<MessageSquareText size={12}/>}].map((x,i) => {
                        const status = step > x.s ? 'done' : step === x.s ? 'active' : 'pending';
                        return (
                            <React.Fragment key={x.s}>
                                {i > 0 && <div className={`w-6 h-px ${step > x.s ? 'bg-emerald-500/40' : 'bg-white/10'}`}/>}
                                <div className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg border text-[9px] font-black uppercase tracking-widest ${STEP_COLORS[status]}`}>
                                    {status === 'done' ? <CheckCircle2 size={12}/> : status === 'active' ? <Loader2 size={12} className="animate-spin"/> : x.i}
                                    {x.l}
                                </div>
                            </React.Fragment>
                        );
                    })}
                </div>
            )}

            {error && (
                <div className="bg-rose-500/10 border border-rose-500/20 p-5 rounded-xl flex items-start gap-3 text-rose-400 text-sm font-bold">
                    <AlertTriangle size={18} className="flex-shrink-0 mt-0.5" /><span>{error}</span>
                </div>
            )}

            {/* ══════════ RESULTS ══════════ */}
            {(atsResults || rewriteResult || resumeHtml) && (
                <div ref={resultsRef} className="space-y-8 animate-fade-in">

                    {/* ── ATS SCORES ── */}
                    {atsResults?.company_scores && (
                        <div className="space-y-4">
                            <div className="flex items-center justify-between">
                                <h2 className="text-xl font-black text-white tracking-tight flex items-center gap-3">
                                    <Building2 size={20} className="text-indigo-400" /> Company ATS Scores
                                </h2>
                                {atsResults.summary && (
                                    <div className="flex items-center gap-4">
                                        <span className="text-[10px] font-black text-slate-500 uppercase tracking-widest">
                                            Avg: <span className={`text-lg ${scoreColor(atsResults.summary.average_score)}`}>{atsResults.summary.average_score}</span>/100
                                        </span>
                                    </div>
                                )}
                            </div>
                            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                                {Object.entries(atsResults.company_scores).map(([cid, data]) => {
                                    const col = COMPANY_COLORS[cid] || COMPANY_COLORS.google;
                                    const sc = data.final_score || 0;
                                    const meta = data.company_meta || {};
                                    return (
                                        <div key={cid} className={`bg-gradient-to-br ${col.bg} border ${col.border} rounded-xl p-5 space-y-3`}>
                                            <div className="flex items-center justify-between">
                                                <div className="flex items-center gap-2">
                                                    <span className="text-lg">{meta.logo_emoji || '🏢'}</span>
                                                    <h3 className={`font-black text-sm uppercase tracking-widest ${col.text}`}>{meta.name || cid}</h3>
                                                </div>
                                                <span className={`text-2xl font-black ${scoreColor(sc)}`}>{sc}</span>
                                            </div>
                                            <div className="w-full h-2 bg-black/20 rounded-full overflow-hidden">
                                                <div className={`h-full rounded-full transition-all duration-1000 ${barColor(sc)}`} style={{ width: `${sc}%` }} />
                                            </div>
                                            <p className={`text-[10px] font-black uppercase tracking-widest ${sc >= 70 ? 'text-emerald-400' : sc >= 45 ? 'text-amber-400' : 'text-rose-400'}`}>
                                                {data.verdict || (sc >= 70 ? 'Strong Match ✅' : sc >= 45 ? 'Needs Improvement ⚠️' : 'Likely Rejected ❌')}
                                            </p>
                                            {data.top_improvements?.slice(0, 2).map((imp, i) => (
                                                <p key={i} className="text-[10px] text-slate-400 font-medium flex items-start gap-1.5">
                                                    <ChevronRight size={10} className="text-indigo-500 mt-0.5 flex-shrink-0" /> {imp}
                                                </p>
                                            ))}
                                        </div>
                                    );
                                })}
                            </div>
                        </div>
                    )}

                    {/* ── RESUME PREVIEW + BEFORE/AFTER + DOWNLOAD ── */}
                    {(resumeHtml || rewriteResult) && (
                        <div className="space-y-4">
                            <div className="flex items-center justify-between">
                                <h2 className="text-xl font-black text-white tracking-tight flex items-center gap-3">
                                    <Sparkles size={20} className="text-violet-400" /> Built Resume
                                    <span className="text-[10px] font-bold bg-violet-500/20 text-violet-400 px-3 py-1 rounded-full uppercase tracking-widest">{selectedTemplate}</span>
                                </h2>
                                <div className="flex items-center gap-2">
                                    {['preview', 'comparison', 'rewrite'].map(tab => (
                                        <button key={tab} onClick={() => setActiveTab(tab)}
                                            className={`px-4 py-2 rounded-lg text-[10px] font-black uppercase tracking-widest transition-all border ${
                                                activeTab === tab ? 'border-indigo-500/40 bg-indigo-600/10 text-indigo-400' : 'border-white/5 text-slate-600 hover:text-slate-400'
                                            }`}>{tab === 'preview' ? '📄 Preview' : tab === 'comparison' ? '↔ Compare' : '✍️ Text'}</button>
                                    ))}
                                </div>
                            </div>

                            {/* Preview Tab — LIVE RENDERED RESUME */}
                            {activeTab === 'preview' && resumeHtml && (
                                <div className="glass-card overflow-hidden">
                                    <div className="p-3 border-b border-white/5 bg-emerald-500/5 flex items-center justify-between">
                                        <div className="flex items-center gap-2">
                                            <div className="w-2 h-2 bg-emerald-500 rounded-full animate-pulse" />
                                            <span className="text-[10px] font-black uppercase tracking-widest text-emerald-400">Live Resume Preview — Our Own Engine</span>
                                        </div>
                                        <div className="flex gap-2">
                                            <button onClick={downloadPDF} disabled={downloading}
                                                className="px-4 py-1.5 bg-emerald-600/20 border border-emerald-500/30 hover:bg-emerald-600 rounded-lg text-[10px] font-black uppercase tracking-widest text-emerald-400 hover:text-white flex items-center gap-1.5 transition-all disabled:opacity-50">
                                                {downloading ? <Loader2 size={12} className="animate-spin"/> : <Download size={12}/>}
                                                {downloading ? 'Generating...' : 'Download PDF'}
                                            </button>
                                            <button onClick={copyRewrite}
                                                className="px-4 py-1.5 bg-indigo-600/10 border border-indigo-500/20 hover:bg-indigo-600 rounded-lg text-[10px] font-black uppercase tracking-widest text-indigo-400 hover:text-white flex items-center gap-1.5 transition-all">
                                                {copied ? <><Check size={12}/> Copied!</> : <><Copy size={12}/> Copy Text</>}
                                            </button>
                                        </div>
                                    </div>
                                    <div className="bg-slate-100 p-6 flex justify-center">
                                        <div ref={previewRef} className="shadow-2xl bg-white" style={{ width: '800px', minHeight: '400px' }}
                                            dangerouslySetInnerHTML={{ __html: resumeHtml }} />
                                    </div>
                                </div>
                            )}

                            {/* Comparison Tab */}
                            {activeTab === 'comparison' && (
                                <div className="glass-card overflow-hidden">
                                    <div className="grid grid-cols-2 divide-x divide-white/5">
                                        <div>
                                            <div className="p-3 border-b border-white/5 bg-rose-500/5 flex items-center gap-2">
                                                <div className="w-2 h-2 bg-rose-500 rounded-full" />
                                                <span className="text-[10px] font-black uppercase tracking-widest text-rose-400">Original</span>
                                            </div>
                                            <div className="p-5 max-h-[400px] overflow-y-auto custom-scrollbar">
                                                <p className="text-[11px] text-slate-500 whitespace-pre-line leading-relaxed font-medium">
                                                    {(resumeData?.content_text || resumeData?.content || '').slice(0, 3000)}
                                                </p>
                                            </div>
                                        </div>
                                        <div>
                                            <div className="p-3 border-b border-white/5 bg-emerald-500/5 flex items-center gap-2">
                                                <div className="w-2 h-2 bg-emerald-500 rounded-full" />
                                                <span className="text-[10px] font-black uppercase tracking-widest text-emerald-400">AI Optimized</span>
                                            </div>
                                            <div className="p-5 max-h-[400px] overflow-y-auto custom-scrollbar">
                                                <p className="text-[11px] text-slate-300 whitespace-pre-line leading-relaxed font-medium">
                                                    {rewriteResult || 'Processing...'}
                                                </p>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            )}

                            {/* Raw Text Tab */}
                            {activeTab === 'rewrite' && rewriteResult && (
                                <div className="glass-card p-6">
                                    <p className="text-xs text-slate-300 whitespace-pre-line leading-relaxed font-medium">{rewriteResult}</p>
                                </div>
                            )}
                        </div>
                    )}

                    {/* ── STRENGTH RADAR + INTERVIEW PREP ── */}
                    {(strengthData || interviewPrep) && (
                        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">

                            {/* Strength Radar */}
                            {strengthData && (
                                <div className="glass-card p-6 space-y-4">
                                    <h3 className="text-lg font-black text-white tracking-tight flex items-center gap-2">
                                        <Radar size={18} className="text-indigo-400" /> Resume Strength Radar
                                    </h3>
                                    <RadarChart dimensions={strengthData.dimensions} />
                                    <div className="grid grid-cols-2 gap-2">
                                        {strengthData.dimensions && Object.entries(strengthData.dimensions).map(([dim, score]) => (
                                            <div key={dim} className="flex items-center justify-between bg-white/5 px-3 py-2 rounded-lg">
                                                <span className="text-[10px] font-bold text-slate-400 truncate">{dim}</span>
                                                <span className={`text-sm font-black ${scoreColor(score)}`}>{score}</span>
                                            </div>
                                        ))}
                                    </div>
                                    <div className="bg-indigo-600/5 border border-indigo-500/10 p-4 rounded-xl">
                                        <div className="flex items-center justify-between mb-2">
                                            <span className="text-[10px] font-black text-indigo-400 uppercase tracking-widest">Overall</span>
                                            <span className={`text-2xl font-black ${scoreColor(strengthData.overall_score)}`}>{strengthData.overall_score}/100</span>
                                        </div>
                                        <p className="text-[10px] text-slate-400 font-medium">{strengthData.one_line_verdict}</p>
                                        <div className="flex gap-4 mt-2 text-[9px] font-bold">
                                            <span className="text-emerald-400">💪 Strongest: {strengthData.strongest}</span>
                                            <span className="text-amber-400">⚠️ Weakest: {strengthData.weakest}</span>
                                        </div>
                                    </div>
                                </div>
                            )}

                            {/* Interview Prep */}
                            {interviewPrep && (
                                <div className="glass-card p-6 space-y-4 max-h-[600px] overflow-y-auto custom-scrollbar">
                                    <h3 className="text-lg font-black text-white tracking-tight flex items-center gap-2">
                                        <MessageSquareText size={18} className="text-amber-400" /> AI Interview Prep
                                    </h3>

                                    {[
                                        { key: 'technical_questions', title: '🔧 Technical', color: 'text-blue-400' },
                                        { key: 'behavioral_questions', title: '🧠 Behavioral', color: 'text-violet-400' },
                                        { key: 'role_specific_questions', title: '🎯 Role-Specific', color: 'text-emerald-400' },
                                    ].map(({ key, title, color }) => (
                                        <div key={key}>
                                            <p className={`text-[10px] font-black uppercase tracking-widest mb-2 ${color}`}>{title}</p>
                                            {(interviewPrep[key] || []).map((q, i) => (
                                                <div key={i} className="bg-white/5 rounded-lg p-3 mb-2">
                                                    <p className="text-xs text-white font-bold mb-1 flex items-start gap-2">
                                                        <HelpCircle size={12} className="flex-shrink-0 mt-0.5 text-indigo-400" />
                                                        {q.question}
                                                    </p>
                                                    <p className="text-[10px] text-slate-400 font-medium ml-5">💡 {q.tip}</p>
                                                </div>
                                            ))}
                                        </div>
                                    ))}

                                    {interviewPrep.resume_red_flags?.length > 0 && (
                                        <div>
                                            <p className="text-[10px] font-black uppercase tracking-widest mb-2 text-rose-400">⚠️ Potential Red Flags</p>
                                            {interviewPrep.resume_red_flags.map((f, i) => (
                                                <p key={i} className="text-[10px] text-rose-400/80 font-medium flex items-start gap-2 mb-1">
                                                    <AlertTriangle size={10} className="flex-shrink-0 mt-0.5" /> {f}
                                                </p>
                                            ))}
                                        </div>
                                    )}
                                </div>
                            )}
                        </div>
                    )}

                    {/* ── COMPLETE BANNER ── */}
                    {step >= 6 && (
                        <div className="bg-gradient-to-r from-emerald-600/10 via-indigo-600/10 to-violet-600/10 border border-emerald-500/20 p-8 rounded-2xl text-center space-y-4">
                            <CheckCircle2 size={40} className="text-emerald-400 mx-auto" />
                            <h3 className="text-xl font-black text-white tracking-tight">Pipeline Complete — All Built In-House</h3>
                            <p className="text-slate-400 text-sm font-medium max-w-lg mx-auto">
                                Resume analyzed by {selectedCompanies.length} company ATS systems, grammar-enhanced, AI-rewritten for <strong className="text-white">{targetRole}</strong>, rendered with our <strong className="text-indigo-400">{selectedTemplate}</strong> template, interview questions generated, and strength analyzed.
                            </p>
                            <p className="text-[10px] text-slate-600 font-bold uppercase tracking-widest">Zero external dependencies • Our own technology • Download-ready</p>
                            <button onClick={runPipeline} className="px-6 py-3 bg-white/5 border border-white/10 rounded-xl text-[10px] font-black uppercase tracking-widest text-slate-400 hover:bg-indigo-600/10 hover:text-indigo-400 transition-all flex items-center gap-2 mx-auto">
                                <RefreshCw size={12} /> Re-run Pipeline
                            </button>
                        </div>
                    )}
                </div>
            )}
        </div>
    );
}
