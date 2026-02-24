import React, { useState } from 'react';
import { Send, User, Bot, X, Calendar, Map, Target, Briefcase, ChevronRight, BarChart3, TrendingUp, Zap } from 'lucide-react';
import { mentorAPI, resumeAPI } from '../api';

export default function MentorBot({ resumeId }) {
    const [isOpen, setIsOpen] = useState(false);
    const [activeTab, setActiveTab] = useState('chat'); // 'chat', 'roadmap', 'intel', 'graph'
    const [messages, setMessages] = useState([
        { role: 'assistant', content: "Initialization complete. I am your AI Career Mentor. How shall we optimize your path today?" }
    ]);
    const [input, setInput] = useState('');
    const [loading, setLoading] = useState(false);
    const [mentorData, setMentorData] = useState(null);

    const handleSend = async () => {
        if (!input.trim()) return;
        const userMessage = { role: 'user', content: input };
        setMessages(prev => [...prev, userMessage]);
        setInput('');
        setLoading(true);
        try {
            const response = await mentorAPI.chat(input, resumeId);
            setMessages(prev => [...prev, { role: 'assistant', content: response.data.reply }]);
        } catch (err) {
            setMessages(prev => [...prev, { role: 'assistant', content: "Neural link interrupted. Please retry." }]);
        } finally {
            setLoading(false);
        }
    };

    const runAIIntelligence = async () => {
        setLoading(true);
        try {
            const res = await resumeAPI.getById(resumeId);
            const resumeText = res.data.content;
            const skills = res.data.analysis?.key_strengths || [];

            const insight = await mentorAPI.getInsight(resumeText, skills);
            setMentorData(insight.data);
            setActiveTab('intel');
        } catch (err) {
            console.error(err);
        } finally {
            setLoading(false);
        }
    };

    return (
        <>
            {/* AI Orbital Button */}
            <button
                onClick={() => setIsOpen(true)}
                className="fixed bottom-8 right-8 bg-indigo-600 text-white p-5 rounded-full shadow-[0_0_40px_rgba(79,70,229,0.4)] hover:scale-110 active:scale-95 transition-all z-50 group border border-white/20"
            >
                <div className="flex items-center gap-3">
                    <div className="relative">
                        <Zap size={24} className="text-white group-hover:animate-pulse" />
                        <div className="absolute -top-1 -right-1 w-2.5 h-2.5 bg-white rounded-full animate-ping"></div>
                    </div>
                    <span className="max-w-0 overflow-hidden group-hover:max-w-xs transition-all duration-500 font-black tracking-[0.2em] uppercase text-[10px] whitespace-nowrap">
                        AI Mentor Active
                    </span>
                </div>
            </button>

            {/* AI Mentor Sidebar */}
            {isOpen && (
                <div className="fixed top-0 right-0 w-[480px] h-full bg-slate-950/80 backdrop-blur-2xl border-l border-white/10 flex flex-col z-[100] animate-in slide-in-from-right duration-500 shadow-[-40px_0_60px_rgba(0,0,0,0.5)]">
                    <div className="p-8 border-b border-white/5 flex justify-between items-center bg-white/5">
                        <div className="flex items-center gap-5">
                            <div className="bg-indigo-600 p-3 rounded-2xl shadow-[0_0_20px_rgba(79,70,229,0.4)]">
                                <Bot size={28} className="text-white" />
                            </div>
                            <div>
                                <h3 className="font-black text-2xl tracking-tighter text-white">AI MENTOR</h3>
                                <div className="flex items-center gap-2 mt-1">
                                    <span className="w-1.5 h-1.5 bg-emerald-500 rounded-full animate-pulse"></span>
                                    <span className="text-[10px] text-slate-400 font-black uppercase tracking-widest">Neural Link Sync: 100%</span>
                                </div>
                            </div>
                        </div>
                        <button onClick={() => setIsOpen(false)} className="hover:bg-white/10 p-3 rounded-2xl transition-all text-slate-500 hover:text-white">
                            <X size={24} />
                        </button>
                    </div>

                    <div className="flex p-3 bg-black/20 gap-2 overflow-x-auto no-scrollbar border-b border-white/5">
                        {[
                            { id: 'chat', label: 'Mentor Chat', icon: <Bot size={14} /> },
                            { id: 'intel', label: 'Match Intel', icon: <Target size={14} /> },
                            { id: 'roadmap', label: 'Roadmap', icon: <Map size={14} /> },
                            { id: 'graph', label: 'Skill Graph', icon: <BarChart3 size={14} /> }
                        ].map(tab => (
                            <button
                                key={tab.id}
                                onClick={() => setActiveTab(tab.id)}
                                className={`whitespace-nowrap flex items-center gap-2 px-5 py-3 rounded-xl text-[10px] font-black uppercase tracking-[0.2em] transition-all ${activeTab === tab.id ? 'bg-indigo-600 text-white shadow-xl' : 'text-slate-500 hover:bg-white/5 hover:text-slate-300'}`}
                            >
                                {tab.icon} {tab.label}
                            </button>
                        ))}
                    </div>

                    <div className="flex-1 overflow-y-auto custom-scrollbar">
                        {activeTab === 'chat' && (
                            <div className="flex flex-col h-full">
                                <div className="flex-1 p-8 space-y-8 overflow-y-auto custom-scrollbar">
                                    {messages.map((m, idx) => (
                                        <div key={idx} className={`flex ${m.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                                            <div className={`p-5 rounded-3xl text-sm max-w-[90%] leading-relaxed ${m.role === 'user' ? 'bg-white text-black font-bold rounded-br-none shadow-xl' : 'bg-white/5 text-slate-300 border border-white/10 rounded-tl-none'}`}>
                                                {m.content}
                                            </div>
                                        </div>
                                    ))}
                                    {loading && (
                                        <div className="flex gap-2 p-4 bg-white/5 w-fit rounded-2xl">
                                            <div className="w-1.5 h-1.5 bg-indigo-500 rounded-full animate-bounce"></div>
                                            <div className="w-1.5 h-1.5 bg-indigo-500 rounded-full animate-bounce delay-100"></div>
                                            <div className="w-1.5 h-1.5 bg-indigo-500 rounded-full animate-bounce delay-200"></div>
                                        </div>
                                    )}
                                </div>
                                <div className="p-8 bg-black/40 border-t border-white/5 flex gap-4">
                                    <input
                                        type="text"
                                        value={input}
                                        onChange={(e) => setInput(e.target.value)}
                                        onKeyPress={(e) => e.key === 'Enter' && handleSend()}
                                        placeholder="Command Mentor..."
                                        className="flex-1 bg-white/5 border border-white/10 rounded-2xl px-6 py-4 text-sm text-white focus:ring-2 focus:ring-indigo-600/20 font-medium placeholder-slate-600 outline-none transition-all"
                                    />
                                    <button onClick={handleSend} className="bg-indigo-600 text-white p-4 rounded-2xl hover:bg-indigo-500 transition-all active:scale-95 shadow-lg shadow-indigo-600/20">
                                        <Send size={20} />
                                    </button>
                                </div>
                            </div>
                        )}

                        {activeTab === 'intel' && (
                            <div className="p-10 space-y-10">
                                {!mentorData ? (
                                    <div className="flex flex-col items-center justify-center py-20 text-center space-y-8">
                                        <div className="w-24 h-24 bg-indigo-500/10 rounded-full flex items-center justify-center text-indigo-400 animate-pulse border border-indigo-500/20">
                                            <Target size={48} />
                                        </div>
                                        <div className="space-y-4">
                                            <h4 className="font-black text-3xl text-white tracking-tighter uppercase">Initialize Intel Scan</h4>
                                            <p className="text-slate-500 text-sm max-w-xs font-medium uppercase tracking-tighter">Synchronize your profile with market demand patterns.</p>
                                        </div>
                                        <button onClick={runAIIntelligence} className="w-full py-5 bg-white text-black rounded-[32px] font-black uppercase tracking-[0.3em] text-[10px] flex items-center justify-center gap-3 shadow-2xl hover:bg-indigo-600 hover:text-white transition-all">
                                            {loading ? <div className="animate-spin w-5 h-5 border-4 border-slate-900 border-t-indigo-600 rounded-full"></div> : <Zap size={18} />}
                                            Establish Neural Match
                                        </button>
                                    </div>
                                ) : (
                                    <div className="space-y-10 animate-fade-in">
                                        <div className="glass-card p-1 border-indigo-500/10">
                                            <div className="bg-slate-900/60 p-10 rounded-xl flex flex-col items-center text-center">
                                                <p className="text-[10px] font-black uppercase tracking-[0.4em] text-indigo-400 mb-6">Market Projection</p>
                                                <h4 className="text-5xl font-black tracking-tighter text-white mb-2">{mentorData.market_demand}</h4>
                                                <p className="text-slate-500 text-sm font-black uppercase tracking-widest">{mentorData.recommended_role}</p>

                                                <div className="w-full h-px bg-white/5 my-8"></div>

                                                <div className="flex justify-between w-full">
                                                    <div className="text-left">
                                                        <p className="text-[10px] font-black text-slate-600 uppercase mb-1">Growth Index</p>
                                                        <span className="text-2xl font-black text-emerald-400">{mentorData.growth_score}/10</span>
                                                    </div>
                                                    <div className="text-right">
                                                        <p className="text-[10px] font-black text-slate-600 uppercase mb-1">Profile Alignment</p>
                                                        <span className="text-2xl font-black text-indigo-400">High-Sync</span>
                                                    </div>
                                                </div>
                                            </div>
                                        </div>
                                        <div className="bg-indigo-600/10 p-8 rounded-[40px] border border-indigo-500/20 flex gap-6">
                                            <Bot className="text-indigo-400 flex-shrink-0" size={32} />
                                            <p className="text-sm text-slate-300 font-medium leading-loose italic">
                                                "{mentorData.mentor_advice}"
                                            </p>
                                        </div>
                                    </div>
                                )}
                            </div>
                        )}

                        {activeTab === 'roadmap' && (
                            <div className="p-10">
                                {!mentorData ? (
                                    <div className="flex flex-col items-center justify-center py-20 text-center space-y-8">
                                        <div className="w-24 h-24 bg-emerald-500/10 rounded-full flex items-center justify-center text-emerald-400 border border-emerald-500/20">
                                            <Map size={48} />
                                        </div>
                                        <h4 className="font-black text-3xl text-white tracking-tighter uppercase">Generate Trajectory</h4>
                                        <button onClick={runAIIntelligence} className="w-full py-5 bg-white text-black rounded-[32px] font-black uppercase tracking-[0.3em] text-[10px]">Initialize Timeline</button>
                                    </div>
                                ) : (
                                    <div className="space-y-8 animate-fade-in">
                                        <div className="flex items-center justify-between mb-2">
                                            <h4 className="font-black uppercase tracking-[0.3em] text-[10px] text-slate-500">6-Month Neural Roadmap</h4>
                                            <span className="text-[10px] bg-indigo-500/20 text-indigo-400 px-3 py-1 rounded-full font-black uppercase">Optimized Path</span>
                                        </div>
                                        <div className="bg-white/5 p-10 rounded-[40px] border border-white/10 text-slate-300 font-medium whitespace-pre-line leading-loose text-sm selection:bg-indigo-500/40">
                                            {mentorData.dynamic_roadmap}
                                        </div>
                                    </div>
                                )}
                            </div>
                        )}

                        {activeTab === 'graph' && (
                            <div className="p-10 h-full flex flex-col">
                                {!mentorData ? (
                                    <div className="flex-1 flex flex-col items-center justify-center text-center space-y-8">
                                        <div className="w-24 h-24 bg-purple-500/10 rounded-full flex items-center justify-center text-purple-400 border border-purple-500/20">
                                            <BarChart3 size={48} />
                                        </div>
                                        <h4 className="font-black text-3xl text-white tracking-tighter uppercase">Skill Surface Graph</h4>
                                        <button onClick={runAIIntelligence} className="w-full py-5 bg-white text-black rounded-[32px] font-black uppercase tracking-[0.3em] text-[10px]">Visualize Topography</button>
                                    </div>
                                ) : (
                                    <div className="space-y-8 animate-fade-in">
                                        <div className="glass-card p-4 border-white/10 overflow-hidden">
                                            <div className="bg-white rounded-[32px] overflow-hidden p-6">
                                                <img src={`data:image/png;base64,${mentorData.skill_graph}`} alt="Skill Graph" className="w-full h-auto brightness-[0.9] contrast-[1.1]" />
                                            </div>
                                        </div>
                                        <div className="grid grid-cols-3 gap-4">
                                            <div className="bg-emerald-500/10 p-5 rounded-3xl border border-emerald-500/20 text-center group transition-all hover:bg-emerald-500/20">
                                                <div className="w-4 h-4 bg-emerald-500 rounded-full mx-auto mb-3 shadow-[0_0_10px_rgba(16,185,129,0.5)]"></div>
                                                <span className="text-[10px] font-black uppercase text-emerald-400 tracking-widest">Mastered</span>
                                            </div>
                                            <div className="bg-rose-500/10 p-5 rounded-3xl border border-rose-500/20 text-center group transition-all hover:bg-rose-500/20">
                                                <div className="w-4 h-4 bg-rose-500 rounded-full mx-auto mb-3 shadow-[0_0_10px_rgba(244,63,94,0.5)]"></div>
                                                <span className="text-[10px] font-black uppercase text-rose-400 tracking-widest">Deficit</span>
                                            </div>
                                            <div className="bg-indigo-500/10 p-5 rounded-3xl border border-indigo-500/20 text-center group transition-all hover:bg-indigo-500/20">
                                                <div className="w-4 h-4 bg-indigo-500 rounded-full mx-auto mb-3 shadow-[0_0_10px_rgba(99,102,241,0.5)]"></div>
                                                <span className="text-[10px] font-black uppercase text-indigo-400 tracking-widest">Target</span>
                                            </div>
                                        </div>
                                    </div>
                                )}
                            </div>
                        )}
                    </div>

                    <div className="p-6 bg-black/40 text-center border-t border-white/5">
                        <span className="text-[9px] font-black text-slate-600 uppercase tracking-[0.5em]">AI Resume Analyzer Intelligence Nexus • Terminal Status 200</span>
                    </div>
                </div>
            )}
        </>
    );
}
