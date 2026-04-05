import React, { useState, useEffect } from 'react';
import { resumeAPI } from '../api';
import MentorBot from './MentorBot';
import { Bot, Target, FileText, ChevronRight, Sparkles, TrendingUp, Brain } from 'lucide-react';

export default function CareerMentor() {
    const [resumes, setResumes] = useState([]);
    const [selectedResumeId, setSelectedResumeId] = useState(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const fetchResumes = async () => {
            try {
                const res = await resumeAPI.getAll();
                setResumes(res.data);
                if (res.data.length > 0) {
                    setSelectedResumeId(res.data[0].id);
                }
            } catch (err) {
                console.error(err);
            } finally {
                setLoading(false);
            }
        };
        fetchResumes();
    }, []);

    if (loading) {
        return (
            <div className="flex items-center justify-center min-h-[60vh]">
                <div className="flex flex-col items-center gap-6">
                    <div className="animate-spin w-12 h-12 border-4 border-indigo-600 border-t-transparent rounded-full"></div>
                    <p className="text-[10px] font-black text-slate-500 uppercase tracking-widest animate-pulse">Initializing AI Mentor</p>
                </div>
            </div>
        );
    }

    if (resumes.length === 0) {
        return (
            <div className="glass-card p-20 text-center max-w-2xl mx-auto mt-12">
                <div className="bg-indigo-600/10 w-24 h-24 rounded-[40px] flex items-center justify-center mx-auto mb-8 border border-indigo-500/20 text-indigo-400">
                    <Bot size={48} />
                </div>
                <h2 className="text-4xl font-black text-white mb-4 tracking-tighter uppercase">AI Baseline Required</h2>
                <p className="text-slate-500 text-sm font-medium leading-relaxed mb-10 uppercase tracking-widest">
                    Upload a resume to initialize your AI career mentor session.
                </p>
                <a href="/upload" className="btn-primary px-12 py-5 text-xs tracking-[0.3em]">UPLOAD RESUME</a>
            </div>
        );
    }

    return (
        <div className="space-y-8">
            {/* Header */}
            <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-6">
                <div>
                    <h1 className="text-5xl font-black bg-gradient-to-r from-white via-indigo-200 to-slate-500 bg-clip-text text-transparent tracking-tighter mb-2">
                        Career Mentor
                    </h1>
                    <p className="text-slate-500 font-bold tracking-wide max-w-2xl px-1 uppercase text-[10px] tracking-widest">
                        AI-Powered Career Guidance • Chat, Roadmaps & Skill Analysis
                    </p>
                </div>

                <div className="flex flex-col gap-2">
                    <label className="text-[10px] font-black text-slate-500 uppercase tracking-widest px-1">Active Resume</label>
                    <select
                        value={selectedResumeId || ''}
                        onChange={(e) => setSelectedResumeId(Number(e.target.value))}
                        className="bg-white/5 border border-white/10 rounded-xl px-5 py-3 text-sm text-white font-bold outline-none focus:ring-2 focus:ring-indigo-600/20 transition-all appearance-none cursor-pointer min-w-[260px]"
                    >
                        {resumes.map(r => (
                            <option key={r.id} value={r.id} className="bg-slate-900 text-white font-bold">{r.title}</option>
                        ))}
                    </select>
                </div>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-4 gap-8">
                {/* Left Sidebar — AI Features */}
                <div className="lg:col-span-1 space-y-6">
                    {/* Feature Cards */}
                    <div className="glass-card p-6 border border-indigo-500/10 bg-gradient-to-br from-indigo-600/5 to-transparent">
                        <div className="flex items-center gap-3 mb-6">
                            <div className="bg-indigo-600 p-2.5 rounded-xl shadow-lg">
                                <Brain size={20} className="text-white" />
                            </div>
                            <h3 className="text-xs font-black text-white uppercase tracking-widest">AI Features</h3>
                        </div>
                        <ul className="space-y-3">
                            {[
                                { icon: <Bot size={14} />, label: "Multi-Turn Chat", desc: "Context-aware conversations" },
                                { icon: <Target size={14} />, label: "Match Intel", desc: "Market & profile analysis" },
                                { icon: <TrendingUp size={14} />, label: "AI Roadmap", desc: "Personalized career path" },
                                { icon: <Sparkles size={14} />, label: "Skill Graph", desc: "Visual gap analysis" },
                            ].map((item, i) => (
                                <li key={i} className="flex items-start gap-3 text-slate-400 text-xs font-semibold py-2.5 px-3 rounded-lg hover:bg-white/5 transition-all group cursor-default border border-transparent hover:border-white/5">
                                    <span className="text-indigo-500 mt-0.5">{item.icon}</span>
                                    <div>
                                        <p className="text-white text-[11px] font-black">{item.label}</p>
                                        <p className="text-slate-600 text-[10px]">{item.desc}</p>
                                    </div>
                                </li>
                            ))}
                        </ul>
                    </div>

                    <div className="bg-gradient-to-br from-indigo-600/10 to-purple-600/5 p-6 rounded-2xl border border-indigo-500/10">
                        <p className="text-[10px] font-black text-indigo-400 uppercase tracking-widest mb-3">Powered By</p>
                        <p className="text-sm text-white font-bold mb-1">Google Gemini AI</p>
                        <p className="text-[10px] text-slate-500 font-medium leading-relaxed">
                            Real AI responses — no hardcoded answers. Every chat, roadmap, and analysis is generated live using state-of-the-art AI.
                        </p>
                    </div>

                    <div className="bg-white/5 p-6 rounded-2xl border border-white/5">
                        <p className="text-[10px] font-black text-emerald-400 uppercase tracking-widest mb-3">Tips</p>
                        <ul className="space-y-2 text-[11px] text-slate-400 font-medium">
                            <li className="flex items-start gap-2"><ChevronRight size={10} className="text-emerald-500 mt-1 flex-shrink-0" /> Ask about specific roles or companies</li>
                            <li className="flex items-start gap-2"><ChevronRight size={10} className="text-emerald-500 mt-1 flex-shrink-0" /> Request interview prep for FAANG</li>
                            <li className="flex items-start gap-2"><ChevronRight size={10} className="text-emerald-500 mt-1 flex-shrink-0" /> Get project ideas for your stack</li>
                            <li className="flex items-start gap-2"><ChevronRight size={10} className="text-emerald-500 mt-1 flex-shrink-0" /> Use Match Intel for market fit</li>
                        </ul>
                    </div>
                </div>

                {/* Main Area — Inline MentorBot */}
                <div className="lg:col-span-3 glass-card rounded-2xl border border-white/5 overflow-hidden flex flex-col min-h-[650px]">
                    <div className="p-5 border-b border-white/5 flex items-center gap-4 bg-white/5">
                        <div className="bg-indigo-600 p-2.5 rounded-xl shadow-lg">
                            <Bot size={22} className="text-white" />
                        </div>
                        <div>
                            <h3 className="font-black text-lg text-white tracking-tight">AI CAREER MENTOR</h3>
                            <div className="flex items-center gap-2 mt-0.5">
                                <span className="w-1.5 h-1.5 bg-emerald-500 rounded-full animate-pulse"></span>
                                <span className="text-[10px] text-slate-500 font-bold uppercase tracking-widest">
                                    Active → {resumes.find(r => r.id === selectedResumeId)?.title}
                                </span>
                            </div>
                        </div>
                    </div>
                    {/* Inline MentorBot — full chat experience embedded on page */}
                    <div className="flex-1 flex flex-col">
                        {selectedResumeId && <MentorBot resumeId={selectedResumeId} inline={true} />}
                    </div>
                </div>
            </div>
        </div>
    );
}
