import React, { useState, useEffect } from 'react';
import { resumeAPI } from '../api';
import MentorBot from './MentorBot';
import { Bot, Target, FileText, ChevronRight } from 'lucide-react';

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
                    // Default to latest
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
                <div className="animate-spin w-12 h-12 border-4 border-indigo-600 border-t-transparent rounded-full"></div>
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
                    You must upload a resume before the AI can initialize your career mentor session.
                </p>
                <a href="/upload" className="btn-primary px-12 py-5 text-xs tracking-[0.3em]">INITIATE UPLOAD</a>
            </div>
        );
    }

    return (
        <div className="space-y-12">
            <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-6">
                <div>
                    <h1 className="text-6xl font-black bg-gradient-to-r from-white via-indigo-200 to-slate-500 bg-clip-text text-transparent tracking-tighter mb-4">
                        Career Mentor
                    </h1>
                    <p className="text-slate-400 font-medium tracking-wide max-w-2xl px-1 uppercase text-[10px] letter-spacing-[0.2em]">
                        Autonomous Guidance & Neural Path Optimization
                    </p>
                </div>

                <div className="flex flex-col gap-2">
                    <label className="text-[10px] font-black text-slate-500 uppercase tracking-widest px-1">Active Baseline</label>
                    <select
                        value={selectedResumeId || ''}
                        onChange={(e) => setSelectedResumeId(Number(e.target.value))}
                        className="bg-white/5 border border-white/10 rounded-2xl px-6 py-4 text-sm text-white font-bold outline-none focus:ring-2 focus:ring-indigo-600/20 transition-all appearance-none cursor-pointer min-w-[280px]"
                    >
                        {resumes.map(r => (
                            <option key={r.id} value={r.id} className="bg-slate-900 text-white font-bold">{r.title}</option>
                        ))}
                    </select>
                </div>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-12">
                {/* Mentor Quick Actions */}
                <div className="lg:col-span-1 space-y-6">
                    <div className="glass-card p-8 border border-indigo-500/10 bg-gradient-to-br from-indigo-600/5 to-transparent rounded-[40px]">
                        <div className="flex items-center gap-4 mb-8">
                            <div className="bg-indigo-600 p-3 rounded-2xl shadow-lg">
                                <Target size={24} className="text-white" />
                            </div>
                            <h3 className="text-sm font-black text-white uppercase tracking-widest">System Protocols</h3>
                        </div>
                        <ul className="space-y-4">
                            {[
                                "Quantifiable Impact Analysis",
                                "Semantic JD Alignment",
                                "Skill Surface Mapping",
                                "MNC Standard Validation"
                            ].map((item, i) => (
                                <li key={i} className="flex items-center gap-3 text-slate-400 text-xs font-bold py-3 px-4 rounded-xl hover:bg-white/5 transition-all group cursor-pointer border border-transparent hover:border-white/5">
                                    <ChevronRight size={14} className="text-indigo-500 group-hover:translate-x-1 transition-transform" />
                                    {item}
                                </li>
                            ))}
                        </ul>
                    </div>

                    <div className="bg-white/5 p-8 rounded-[40px] border border-white/5">
                        <p className="text-[10px] font-black text-indigo-400 uppercase tracking-widest mb-4">AI Advice</p>
                        <p className="text-sm text-slate-400 font-medium leading-relaxed italic">
                            "Quantum analysis recommends a bi-weekly sync of your skill surface to maintain alignment with high-growth market sectors in 2026."
                        </p>
                    </div>
                </div>

                {/* Direct BOT Integration */}
                <div className="lg:col-span-2 relative min-h-[600px] glass-card rounded-[40px] border border-white/5 overflow-hidden flex flex-col">
                    <div className="absolute inset-0 bg-indigo-600/5 opacity-20 pointer-events-none"></div>
                    {/* We re-use some of MentorBot's internal view logic here but adapted for page flow */}
                    <div className="p-8 border-b border-white/5 flex items-center gap-5 bg-white/5">
                        <div className="bg-indigo-600 p-3 rounded-2xl shadow-lg">
                            <Bot size={28} className="text-white" />
                        </div>
                        <div>
                            <h3 className="font-black text-xl text-white tracking-tight">AI NEURAL TERMINAL</h3>
                            <p className="text-[10px] text-slate-500 font-bold uppercase tracking-widest">Active Baseline: {resumes.find(r => r.id === selectedResumeId)?.title}</p>
                        </div>
                    </div>
                    {/* For now, we manually implement a simple chat UI, or we can refactor MentorBot to be a component that can be both Sidebar and Page Content */}
                    <div className="flex-1 flex flex-col p-8 justify-center items-center text-center space-y-8">
                        <div className="bg-white/5 p-10 rounded-[60px] border border-white/5 shadow-2xl max-w-md">
                            <Bot size={64} className="text-indigo-400 mx-auto mb-8 animate-pulse" />
                            <h4 className="text-3xl font-black text-white mb-4 tracking-tighter uppercase">Initialize Mentor</h4>
                            <p className="text-slate-500 text-sm font-medium mb-10 leading-relaxed uppercase tracking-widest">
                                The floating AI orb at the bottom right is your constant companion. Click it to initialize chat, roadmaps, and skill visualizations.
                            </p>
                            <div className="w-12 h-12 bg-indigo-600 rounded-full flex items-center justify-center animate-bounce shadow-[0_0_20px_rgba(79,70,229,0.5)] cursor-pointer">
                                <ChevronRight size={24} className="text-white rotate-90" />
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            {/* Inject the actual floating bot with the selected ID */}
            {selectedResumeId && <MentorBot resumeId={selectedResumeId} />}
        </div>
    );
}
