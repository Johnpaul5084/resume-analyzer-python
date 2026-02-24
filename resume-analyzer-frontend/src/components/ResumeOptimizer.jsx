import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { resumeAPI, rewriteAPI } from '../api';
import { Bot, Zap, Sparkles, Wand2, Copy, Check, ArrowLeft, AlertTriangle } from 'lucide-react';

export default function ResumeOptimizer() {
    const { id } = useParams();
    const navigate = useNavigate();
    const [resumeData, setResumeData] = useState(null);
    const [jobDescription, setJobDescription] = useState('');
    const [mode, setMode] = useState('ATS');
    const [rewrittenText, setRewrittenText] = useState('');
    const [loading, setLoading] = useState(false);
    const [copied, setCopied] = useState(false);
    const [warning, setWarning] = useState(null);

    useEffect(() => {
        const fetchResume = async () => {
            try {
                const res = await resumeAPI.getById(id);
                setResumeData(res.data);
            } catch (err) {
                console.error(err);
            }
        };
        fetchResume();
    }, [id]);

    const handleRewrite = async () => {
        if (!jobDescription.trim()) {
            alert('Please provide a job description for targeted rewriting.');
            return;
        }
        setLoading(true);
        setWarning(null);
        try {
            const res = await rewriteAPI.transform(resumeData.content, jobDescription, mode);
            if (res.data.success) {
                setRewrittenText(res.data.rewritten_resume);
                setWarning(res.data.warning);
            } else {
                alert(res.data.error || 'Failed to transform resume.');
            }
        } catch (err) {
            console.error(err);
            alert('Service unavailable. Please check your AI keys.');
        } finally {
            setLoading(false);
        }
    };

    const copyToClipboard = () => {
        navigator.clipboard.writeText(rewrittenText);
        setCopied(true);
        setTimeout(() => setCopied(false), 2000);
    };

    if (!resumeData) return <div className="p-10 text-center">Neural Link Synchronizing...</div>;

    return (
        <div className="space-y-12">
            {/* Action Bar */}
            <div className="flex items-center justify-between border-b border-white/5 pb-8">
                <div>
                    <h1 className="text-4xl font-black tracking-tighter bg-gradient-to-r from-white to-slate-400 bg-clip-text text-transparent">
                        Neural Transformer
                    </h1>
                    <p className="text-slate-500 font-bold uppercase text-[10px] tracking-[0.2em] mt-1">
                        Alignment Matrix: {resumeData.title}
                    </p>
                </div>
                <div className="flex gap-4">
                    <button onClick={() => navigate(-1)} className="px-6 py-3 rounded-xl bg-white/5 border border-white/10 text-xs font-black uppercase tracking-widest hover:bg-white/10 transition-all">
                        ← Analysis Hub
                    </button>
                    <button
                        onClick={handleRewrite}
                        disabled={loading}
                        className="px-8 py-3 rounded-xl bg-indigo-600 text-white text-xs font-black uppercase tracking-widest hover:bg-indigo-700 shadow-[0_0_20px_rgba(79,70,229,0.3)] transition-all disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-3"
                    >
                        {loading && <div className="w-3 h-3 border-2 border-white/20 border-t-white rounded-full animate-spin"></div>}
                        Execute Transformation
                    </button>
                </div>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-10">
                {/* Control Panel */}
                <div className="space-y-8">
                    <div className="glass-card p-10">
                        <label className="block text-[10px] font-black uppercase tracking-[0.3em] text-indigo-400 mb-6 px-1">Target Role Protocol (JD)</label>
                        <textarea
                            className="w-full h-80 p-8 bg-black/40 border border-white/5 rounded-3xl text-sm text-slate-300 focus:ring-2 focus:ring-indigo-500/20 font-medium custom-scrollbar transition-all resize-none"
                            placeholder="Paste the target Job Description to synchronize alignment..."
                            value={jobDescription}
                            onChange={(e) => setJobDescription(e.target.value)}
                        />
                    </div>

                    <div className="glass-card p-10">
                        <label className="block text-[10px] font-black uppercase tracking-[0.3em] text-indigo-400 mb-8 px-1">Transformation Strategy</label>
                        <div className="grid grid-cols-2 gap-6">
                            <button
                                onClick={() => setMode('ATS')}
                                className={`p-8 rounded-3xl border-2 transition-all group flex flex-col gap-4 items-center text-center ${mode === 'ATS' ? 'border-indigo-600 bg-indigo-600/10' : 'border-white/5 bg-white/5 hover:border-white/10'}`}
                            >
                                <Zap size={28} className={mode === 'ATS' ? 'text-indigo-400' : 'text-slate-500 group-hover:text-slate-300'} />
                                <div className="space-y-1">
                                    <span className="font-black text-xs uppercase tracking-widest block">Neural ATS</span>
                                    <span className="text-[9px] font-bold text-slate-500 block uppercase tracking-tighter">Metric-Driven Match</span>
                                </div>
                            </button>
                            <button
                                onClick={() => setMode('Creative')}
                                className={`p-8 rounded-3xl border-2 transition-all group flex flex-col gap-4 items-center text-center ${mode === 'Creative' ? 'border-indigo-600 bg-indigo-600/10' : 'border-white/5 bg-white/5 hover:border-white/10'}`}
                            >
                                <Sparkles size={28} className={mode === 'Creative' ? 'text-indigo-400' : 'text-slate-500 group-hover:text-slate-300'} />
                                <div className="space-y-1">
                                    <span className="font-black text-xs uppercase tracking-widest block">Executive Impact</span>
                                    <span className="text-[9px] font-bold text-slate-500 block uppercase tracking-tighter">Narrative Optimization</span>
                                </div>
                            </button>
                        </div>
                    </div>
                </div>

                {/* Transformer Sandbox */}
                <div className="glass-card p-1 border border-indigo-500/10 h-full min-h-[700px]">
                    <div className="bg-slate-900/40 rounded-xl2 h-full flex flex-col overflow-hidden">
                        <div className="p-8 border-b border-white/5 flex items-center justify-between">
                            <div className="flex items-center gap-4">
                                <div className="w-3 h-3 bg-indigo-500 rounded-full animate-pulse"></div>
                                <h3 className="font-black text-sm uppercase tracking-[0.2em] text-white">Neural Output Buffer</h3>
                            </div>
                            {rewrittenText && (
                                <button
                                    onClick={copyToClipboard}
                                    className="px-4 py-2 bg-indigo-600/10 border border-indigo-500/20 hover:bg-indigo-600 transition-all rounded-xl text-[10px] font-black uppercase tracking-widest text-indigo-400 hover:text-white"
                                >
                                    {copied ? 'Buffer Synchronized' : 'Transfer to Clipboard'}
                                </button>
                            )}
                        </div>

                        <div className="flex-1 p-10 overflow-auto custom-scrollbar">
                            {!rewrittenText && !loading ? (
                                <div className="h-full flex flex-col items-center justify-center text-center space-y-6 opacity-20">
                                    <Bot size={100} className="text-slate-400" />
                                    <p className="text-xs font-black uppercase tracking-[0.4em] text-slate-400">Awaiting Signal...</p>
                                </div>
                            ) : loading ? (
                                <div className="h-full flex flex-col items-center justify-center text-center space-y-8">
                                    <div className="relative">
                                        <div className="w-20 h-20 border-4 border-indigo-600/10 border-t-indigo-500 rounded-full animate-spin"></div>
                                        <Bot size={32} className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 text-indigo-500" />
                                    </div>
                                    <div className="space-y-2">
                                        <p className="text-sm font-black uppercase tracking-[0.3em] text-white animate-pulse">Synthesizing Artifact</p>
                                        <p className="text-[10px] font-bold text-slate-500 uppercase tracking-widest">Applying {mode} alignment protocols</p>
                                    </div>
                                </div>
                            ) : (
                                <div className="space-y-8 animate-fade-in">
                                    {warning && (
                                        <div className="bg-amber-500/5 border border-amber-500/20 p-5 rounded-2xl flex items-start gap-4 text-amber-400 text-xs font-bold leading-relaxed">
                                            <AlertTriangle size={18} className="flex-shrink-0 mt-0.5" />
                                            <span className="leading-5">{warning}</span>
                                        </div>
                                    )}
                                    <div className="text-slate-300 font-medium whitespace-pre-line leading-loose text-sm p-10 bg-white/5 rounded-[40px] border border-white/5 selection:bg-indigo-500/40">
                                        {rewrittenText}
                                    </div>
                                </div>
                            )}
                        </div>

                        <div className="p-6 border-t border-white/5 bg-black/20 text-center">
                            <span className="text-[9px] font-black text-slate-600 uppercase tracking-[0.5em]">AI Resume Analyzer Core v4.2</span>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
}
