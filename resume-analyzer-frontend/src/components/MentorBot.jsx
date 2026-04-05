import React, { useState, useRef, useEffect } from 'react';
import { Send, User, Bot, X, Calendar, Map, Target, Briefcase, ChevronRight, BarChart3, TrendingUp, Zap, RefreshCw } from 'lucide-react';
import { mentorAPI, resumeAPI } from '../api';

export default function MentorBot({ resumeId, inline = false }) {
    const [isOpen, setIsOpen] = useState(false);
    const [activeTab, setActiveTab] = useState('chat');
    const [messages, setMessages] = useState([
        { role: 'assistant', content: "Initialization complete. I am your AI Career Mentor — powered by Gemini AI. Ask me about interview prep, skill roadmaps, career paths, or resume optimization. How shall we begin?" }
    ]);
    const [input, setInput] = useState('');
    const [loading, setLoading] = useState(false);
    const [mentorData, setMentorData] = useState(null);
    const chatEndRef = useRef(null);

    // Auto-scroll to latest message
    useEffect(() => {
        chatEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    }, [messages, loading]);

    const handleSend = async () => {
        if (!input.trim() || loading) return;
        const userMessage = { role: 'user', content: input };
        const newMessages = [...messages, userMessage];
        setMessages(newMessages);
        setInput('');
        setLoading(true);
        try {
            // Send chat history for contextual conversations
            const historyForBackend = newMessages
                .filter(m => m.role === 'user' || m.role === 'assistant')
                .slice(-10) // Last 10 messages for context
                .map(m => ({ role: m.role, content: m.content }));

            const response = await mentorAPI.chat(input, resumeId, historyForBackend);
            setMessages(prev => [...prev, { role: 'assistant', content: response.data.reply }]);
        } catch (err) {
            const errMsg = err.response?.data?.detail || "Neural link interrupted. Please retry.";
            setMessages(prev => [...prev, { role: 'assistant', content: `⚠️ ${errMsg}` }]);
        } finally {
            setLoading(false);
        }
    };

    const runAIIntelligence = async () => {
        setLoading(true);
        try {
            const res = await resumeAPI.getById(resumeId);
            const resumeText = res.data.content_text || res.data.content || '';
            const skills = res.data.key_strengths || res.data.analysis?.key_strengths || [];
            const targetRole = res.data.predicted_role || '';
            const insight = await mentorAPI.getInsight(resumeText, skills, targetRole);
            setMentorData(insight.data);
            setActiveTab('intel');
        } catch (err) {
            console.error(err);
        } finally {
            setLoading(false);
        }
    };

    const quickPrompts = [
        "How do I prepare for FAANG interviews?",
        "What skills should I learn in 2026?",
        "Suggest portfolio project ideas",
        "Create a 6-month career roadmap",
    ];

    // ─────────────────────────────────────────────────────────
    // CHAT VIEW (shared between inline and sidebar)
    // ─────────────────────────────────────────────────────────
    const renderChat = () => (
        <div className="flex flex-col h-full">
            <div className="flex-1 p-6 space-y-6 overflow-y-auto custom-scrollbar">
                {messages.map((m, idx) => (
                    <div key={idx} className={`flex ${m.role === 'user' ? 'justify-end' : 'justify-start'} animate-fade-in`}>
                        <div className={`flex items-start gap-3 max-w-[85%] ${m.role === 'user' ? 'flex-row-reverse' : ''}`}>
                            <div className={`w-8 h-8 rounded-xl flex items-center justify-center flex-shrink-0 ${m.role === 'user' ? 'bg-white/10' : 'bg-indigo-600/30'}`}>
                                {m.role === 'user' ? <User size={14} className="text-white" /> : <Bot size={14} className="text-indigo-400" />}
                            </div>
                            <div className={`p-4 rounded-2xl text-sm leading-relaxed ${m.role === 'user'
                                ? 'bg-white text-black font-semibold rounded-br-sm shadow-xl'
                                : 'bg-white/5 text-slate-300 border border-white/10 rounded-tl-sm'
                            }`} style={{ whiteSpace: 'pre-wrap' }}>
                                {m.content}
                            </div>
                        </div>
                    </div>
                ))}
                {loading && (
                    <div className="flex items-start gap-3">
                        <div className="w-8 h-8 rounded-xl flex items-center justify-center bg-indigo-600/30">
                            <Bot size={14} className="text-indigo-400" />
                        </div>
                        <div className="flex gap-1.5 p-4 bg-white/5 rounded-2xl border border-white/10">
                            <div className="w-2 h-2 bg-indigo-500 rounded-full animate-bounce" style={{ animationDelay: '0ms' }}></div>
                            <div className="w-2 h-2 bg-indigo-500 rounded-full animate-bounce" style={{ animationDelay: '150ms' }}></div>
                            <div className="w-2 h-2 bg-indigo-500 rounded-full animate-bounce" style={{ animationDelay: '300ms' }}></div>
                        </div>
                    </div>
                )}
                <div ref={chatEndRef} />
            </div>

            {/* Quick Prompts — show only when just the welcome message */}
            {messages.length <= 1 && (
                <div className="px-6 pb-4">
                    <p className="text-[10px] font-black text-slate-600 uppercase tracking-widest mb-3 px-1">Quick Start</p>
                    <div className="grid grid-cols-2 gap-2">
                        {quickPrompts.map((q, i) => (
                            <button
                                key={i}
                                onClick={() => { setInput(q); }}
                                className="text-left text-[11px] text-slate-400 font-semibold px-4 py-3 rounded-xl bg-white/5 border border-white/5 hover:bg-indigo-600/10 hover:border-indigo-500/20 hover:text-indigo-300 transition-all"
                            >
                                {q}
                            </button>
                        ))}
                    </div>
                </div>
            )}

            <div className="p-5 bg-black/40 border-t border-white/5 flex gap-3">
                <input
                    type="text"
                    value={input}
                    onChange={(e) => setInput(e.target.value)}
                    onKeyDown={(e) => e.key === 'Enter' && handleSend()}
                    placeholder="Ask your AI mentor anything..."
                    className="flex-1 bg-white/5 border border-white/10 rounded-xl px-5 py-3.5 text-sm text-white focus:ring-2 focus:ring-indigo-600/20 font-medium placeholder-slate-600 outline-none transition-all"
                    disabled={loading}
                />
                <button
                    onClick={handleSend}
                    disabled={loading || !input.trim()}
                    className="bg-indigo-600 text-white p-3.5 rounded-xl hover:bg-indigo-500 transition-all active:scale-95 shadow-lg shadow-indigo-600/20 disabled:opacity-40 disabled:cursor-not-allowed"
                >
                    <Send size={18} />
                </button>
            </div>
        </div>
    );

    // ─────────────────────────────────────────────────────────
    // INTEL VIEW
    // ─────────────────────────────────────────────────────────
    const renderIntel = () => (
        <div className="p-8 space-y-8">
            {!mentorData ? (
                <div className="flex flex-col items-center justify-center py-16 text-center space-y-6">
                    <div className="w-20 h-20 bg-indigo-500/10 rounded-full flex items-center justify-center text-indigo-400 animate-pulse border border-indigo-500/20">
                        <Target size={40} />
                    </div>
                    <div className="space-y-3">
                        <h4 className="font-black text-2xl text-white tracking-tighter uppercase">Initialize Intel Scan</h4>
                        <p className="text-slate-500 text-sm max-w-xs font-medium">Analyze your profile against market demand patterns using AI.</p>
                    </div>
                    <button onClick={runAIIntelligence} className="w-full max-w-sm py-4 bg-white text-black rounded-2xl font-black uppercase tracking-widest text-[10px] flex items-center justify-center gap-3 shadow-2xl hover:bg-indigo-600 hover:text-white transition-all">
                        {loading ? <div className="animate-spin w-4 h-4 border-2 border-slate-900 border-t-indigo-600 rounded-full"></div> : <Zap size={16} />}
                        Run Analysis
                    </button>
                </div>
            ) : (
                <div className="space-y-8 animate-fade-in">
                    <div className="glass-card p-1 border-indigo-500/10">
                        <div className="bg-slate-900/60 p-8 rounded-xl flex flex-col items-center text-center">
                            <p className="text-[10px] font-black uppercase tracking-[0.4em] text-indigo-400 mb-4">Market Projection</p>
                            <h4 className="text-4xl font-black tracking-tighter text-white mb-2">{mentorData.market_demand}</h4>
                            <p className="text-slate-500 text-sm font-black uppercase tracking-widest">{mentorData.recommended_role}</p>

                            <div className="w-full h-px bg-white/5 my-6"></div>

                            <div className="flex justify-between w-full">
                                <div className="text-left">
                                    <p className="text-[10px] font-black text-slate-600 uppercase mb-1">Growth</p>
                                    <span className="text-xl font-black text-emerald-400">{mentorData.growth_score}/10</span>
                                </div>
                                <div className="text-center">
                                    <p className="text-[10px] font-black text-slate-600 uppercase mb-1">Salary Range</p>
                                    <span className="text-xl font-black text-amber-400">{mentorData.salary_range}</span>
                                </div>
                                <div className="text-right">
                                    <p className="text-[10px] font-black text-slate-600 uppercase mb-1">Domain</p>
                                    <span className="text-sm font-black text-indigo-400">{mentorData.domain}</span>
                                </div>
                            </div>
                        </div>
                    </div>

                    {/* Missing Skills */}
                    {mentorData.missing_skills && mentorData.missing_skills.length > 0 && (
                        <div className="space-y-3">
                            <p className="text-[10px] font-black text-rose-400 uppercase tracking-widest px-1">Skill Gaps to Address</p>
                            <div className="flex flex-wrap gap-2">
                                {mentorData.missing_skills.map((skill, i) => (
                                    <span key={i} className="px-3 py-1.5 bg-rose-500/10 border border-rose-500/20 text-rose-400 text-xs font-bold rounded-lg">
                                        {skill}
                                    </span>
                                ))}
                            </div>
                        </div>
                    )}

                    <div className="bg-indigo-600/10 p-6 rounded-2xl border border-indigo-500/20 flex gap-4">
                        <Bot className="text-indigo-400 flex-shrink-0 mt-1" size={24} />
                        <p className="text-sm text-slate-300 font-medium leading-relaxed italic">
                            "{mentorData.mentor_advice}"
                        </p>
                    </div>

                    <button onClick={runAIIntelligence} className="w-full py-3 bg-white/5 border border-white/10 rounded-xl text-[10px] font-black uppercase tracking-widest text-slate-400 hover:bg-indigo-600/10 hover:text-indigo-400 transition-all flex items-center justify-center gap-2">
                        <RefreshCw size={12} /> Refresh Analysis
                    </button>
                </div>
            )}
        </div>
    );

    // ─────────────────────────────────────────────────────────
    // ROADMAP VIEW
    // ─────────────────────────────────────────────────────────
    const renderRoadmap = () => (
        <div className="p-8">
            {!mentorData ? (
                <div className="flex flex-col items-center justify-center py-16 text-center space-y-6">
                    <div className="w-20 h-20 bg-emerald-500/10 rounded-full flex items-center justify-center text-emerald-400 border border-emerald-500/20">
                        <Map size={40} />
                    </div>
                    <h4 className="font-black text-2xl text-white tracking-tighter uppercase">Generate Roadmap</h4>
                    <p className="text-slate-500 text-sm max-w-xs">AI will create a personalized 6-month career trajectory based on your profile.</p>
                    <button onClick={runAIIntelligence} className="w-full max-w-sm py-4 bg-white text-black rounded-2xl font-black uppercase tracking-widest text-[10px]">Generate Trajectory</button>
                </div>
            ) : (
                <div className="space-y-6 animate-fade-in">
                    <div className="flex items-center justify-between mb-2">
                        <h4 className="font-black uppercase tracking-widest text-[10px] text-slate-500">6-Month AI Roadmap</h4>
                        <span className="text-[10px] bg-indigo-500/20 text-indigo-400 px-3 py-1 rounded-full font-black uppercase">AI Generated</span>
                    </div>
                    <div className="bg-white/5 p-8 rounded-2xl border border-white/10 text-slate-300 font-medium whitespace-pre-line leading-loose text-sm selection:bg-indigo-500/40 custom-scrollbar overflow-y-auto max-h-[500px]">
                        {mentorData.dynamic_roadmap}
                    </div>
                </div>
            )}
        </div>
    );

    // ─────────────────────────────────────────────────────────
    // SKILL GRAPH VIEW
    // ─────────────────────────────────────────────────────────
    const renderGraph = () => (
        <div className="p-8 h-full flex flex-col">
            {!mentorData ? (
                <div className="flex-1 flex flex-col items-center justify-center text-center space-y-6">
                    <div className="w-20 h-20 bg-purple-500/10 rounded-full flex items-center justify-center text-purple-400 border border-purple-500/20">
                        <BarChart3 size={40} />
                    </div>
                    <h4 className="font-black text-2xl text-white tracking-tighter uppercase">Skill Graph</h4>
                    <p className="text-slate-500 text-sm max-w-xs">Visualize your skill coverage vs. market requirements.</p>
                    <button onClick={runAIIntelligence} className="w-full max-w-sm py-4 bg-white text-black rounded-2xl font-black uppercase tracking-widest text-[10px]">Generate Graph</button>
                </div>
            ) : (
                <div className="space-y-6 animate-fade-in">
                    {mentorData.skill_graph ? (
                        <div className="glass-card p-3 border-white/10 overflow-hidden">
                            <div className="bg-white rounded-2xl overflow-hidden p-4">
                                <img src={`data:image/png;base64,${mentorData.skill_graph}`} alt="Skill Graph" className="w-full h-auto brightness-[0.9] contrast-[1.1]" />
                            </div>
                        </div>
                    ) : (
                        <div className="bg-white/5 p-8 rounded-2xl border border-white/10 text-center">
                            <p className="text-slate-400 text-sm">Skill graph could not be generated. Run the intel scan first.</p>
                        </div>
                    )}
                    <div className="grid grid-cols-3 gap-3">
                        <div className="bg-emerald-500/10 p-4 rounded-2xl border border-emerald-500/20 text-center">
                            <div className="w-3 h-3 bg-emerald-500 rounded-full mx-auto mb-2 shadow-[0_0_8px_rgba(16,185,129,0.5)]"></div>
                            <span className="text-[10px] font-black uppercase text-emerald-400 tracking-widest">Mastered</span>
                        </div>
                        <div className="bg-rose-500/10 p-4 rounded-2xl border border-rose-500/20 text-center">
                            <div className="w-3 h-3 bg-rose-500 rounded-full mx-auto mb-2 shadow-[0_0_8px_rgba(244,63,94,0.5)]"></div>
                            <span className="text-[10px] font-black uppercase text-rose-400 tracking-widest">Gap</span>
                        </div>
                        <div className="bg-indigo-500/10 p-4 rounded-2xl border border-indigo-500/20 text-center">
                            <div className="w-3 h-3 bg-indigo-500 rounded-full mx-auto mb-2 shadow-[0_0_8px_rgba(99,102,241,0.5)]"></div>
                            <span className="text-[10px] font-black uppercase text-indigo-400 tracking-widest">Target</span>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );

    // ─────────────────────────────────────────────────────────
    // TAB BAR (shared)
    // ─────────────────────────────────────────────────────────
    const tabBar = (
        <div className="flex p-2 bg-black/20 gap-1.5 overflow-x-auto no-scrollbar border-b border-white/5">
            {[
                { id: 'chat', label: 'Chat', icon: <Bot size={13} /> },
                { id: 'intel', label: 'Intel', icon: <Target size={13} /> },
                { id: 'roadmap', label: 'Roadmap', icon: <Map size={13} /> },
                { id: 'graph', label: 'Skills', icon: <BarChart3 size={13} /> }
            ].map(tab => (
                <button
                    key={tab.id}
                    onClick={() => setActiveTab(tab.id)}
                    className={`whitespace-nowrap flex items-center gap-2 px-4 py-2.5 rounded-lg text-[10px] font-black uppercase tracking-widest transition-all ${activeTab === tab.id ? 'bg-indigo-600 text-white shadow-lg' : 'text-slate-500 hover:bg-white/5 hover:text-slate-300'}`}
                >
                    {tab.icon} {tab.label}
                </button>
            ))}
        </div>
    );

    // ─────────────────────────────────────────────────────────
    // RENDER: Inline Mode (for CareerMentor page)
    // ─────────────────────────────────────────────────────────
    if (inline) {
        return (
            <div className="flex flex-col h-full">
                {tabBar}
                <div className="flex-1 overflow-y-auto custom-scrollbar">
                    {activeTab === 'chat' && renderChat()}
                    {activeTab === 'intel' && renderIntel()}
                    {activeTab === 'roadmap' && renderRoadmap()}
                    {activeTab === 'graph' && renderGraph()}
                </div>
            </div>
        );
    }

    // ─────────────────────────────────────────────────────────
    // RENDER: Floating Sidebar Mode (default)
    // ─────────────────────────────────────────────────────────
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
                        AI Mentor
                    </span>
                </div>
            </button>

            {/* AI Mentor Sidebar */}
            {isOpen && (
                <div className="fixed top-0 right-0 w-[480px] h-full bg-slate-950/80 backdrop-blur-2xl border-l border-white/10 flex flex-col z-[100] animate-in slide-in-from-right duration-500 shadow-[-40px_0_60px_rgba(0,0,0,0.5)]">
                    <div className="p-6 border-b border-white/5 flex justify-between items-center bg-white/5">
                        <div className="flex items-center gap-4">
                            <div className="bg-indigo-600 p-2.5 rounded-xl shadow-[0_0_15px_rgba(79,70,229,0.4)]">
                                <Bot size={24} className="text-white" />
                            </div>
                            <div>
                                <h3 className="font-black text-xl tracking-tighter text-white">AI MENTOR</h3>
                                <div className="flex items-center gap-2 mt-0.5">
                                    <span className="w-1.5 h-1.5 bg-emerald-500 rounded-full animate-pulse"></span>
                                    <span className="text-[10px] text-slate-400 font-bold uppercase tracking-widest">Gemini AI Active</span>
                                </div>
                            </div>
                        </div>
                        <button onClick={() => setIsOpen(false)} className="hover:bg-white/10 p-2.5 rounded-xl transition-all text-slate-500 hover:text-white">
                            <X size={20} />
                        </button>
                    </div>

                    {tabBar}

                    <div className="flex-1 overflow-hidden flex flex-col">
                        {activeTab === 'chat' && renderChat()}
                        {activeTab === 'intel' && renderIntel()}
                        {activeTab === 'roadmap' && <div className="flex-1 overflow-y-auto custom-scrollbar">{renderRoadmap()}</div>}
                        {activeTab === 'graph' && <div className="flex-1 overflow-y-auto custom-scrollbar">{renderGraph()}</div>}
                    </div>

                    <div className="p-4 bg-black/40 text-center border-t border-white/5">
                        <span className="text-[9px] font-black text-slate-600 uppercase tracking-[0.4em]">AI Resume Analyzer • Powered by Gemini</span>
                    </div>
                </div>
            )}
        </>
    );
}
