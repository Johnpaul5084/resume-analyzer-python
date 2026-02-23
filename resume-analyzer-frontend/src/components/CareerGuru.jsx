import React, { useState } from 'react';
import { Send, User, Bot, X, Calendar, Map, Target, Briefcase, ChevronRight } from 'lucide-react';
import { careerGuruAPI, careerIntelAPI } from '../api';

export default function CareerGuru({ resumeId }) {
    const [isOpen, setIsOpen] = useState(false);
    const [activeTab, setActiveTab] = useState('chat'); // 'chat', 'roadmap', 'intel'
    const [messages, setMessages] = useState([
        { role: 'assistant', content: "Welcome to IRIS AI – your Career Intelligence Platform. How can I guide you today?" }
    ]);
    const [input, setInput] = useState('');
    const [loading, setLoading] = useState(false);
    const [targetRole, setTargetRole] = useState('');
    const [roadmap, setRoadmap] = useState(null);
    const [intelResult, setIntelResult] = useState(null);

    const handleSend = async () => {
        if (!input.trim()) return;
        const userMessage = { role: 'user', content: input };
        setMessages(prev => [...prev, userMessage]);
        setInput('');
        setLoading(true);
        try {
            const response = await careerGuruAPI.chat(input, resumeId);
            setMessages(prev => [...prev, { role: 'assistant', content: response.data.reply }]);
        } catch (err) {
            setMessages(prev => [...prev, { role: 'assistant', content: "Connection error. Please try again." }]);
        } finally {
            setLoading(false);
        }
    };

    const handleGenerateRoadmap = async () => {
        if (!targetRole.trim()) return;
        setLoading(true);
        try {
            const response = await careerIntelAPI.getRoadmap(targetRole);
            setRoadmap(response.data);
        } catch (err) {
            console.error(err);
        } finally {
            setLoading(false);
        }
    };

    const runCareerIntel = async () => {
        setLoading(true);
        try {
            const response = await careerIntelAPI.predict({
                branch: "Computer Science",
                skills: ["React", "Python", "FastAPI"],
                interests: ["AI", "Web Dev"]
            });
            setIntelResult(response.data);
        } catch (err) {
            console.error(err);
        } finally {
            setLoading(false);
        }
    };

    return (
        <>
            {/* Floating Chat Button */}
            <button
                onClick={() => setIsOpen(true)}
                className="fixed bottom-8 right-8 bg-black text-white p-4 rounded-full shadow-2xl hover:scale-110 transition-transform z-50 group border border-gray-800"
            >
                <div className="flex items-center gap-2">
                    <div className="relative">
                        <Bot size={28} />
                        <div className="absolute -top-1 -right-1 w-3 h-3 bg-indigo-500 rounded-full animate-pulse border-2 border-black"></div>
                    </div>
                    <span className="max-w-0 overflow-hidden group-hover:max-w-xs transition-all duration-300 font-bold tracking-tight">IRIS AI</span>
                </div>
            </button>

            {/* IRIS Sidebar */}
            {isOpen && (
                <div className="fixed bottom-24 right-8 w-[400px] h-[650px] bg-white rounded-3xl shadow-2xl border border-gray-100 flex flex-col z-50 overflow-hidden animate-in slide-in-from-bottom-5">
                    {/* Premium Header */}
                    <div className="bg-black p-5 text-white flex justify-between items-center">
                        <div className="flex items-center gap-3">
                            <div className="bg-gradient-to-br from-indigo-500 to-purple-600 p-2 rounded-xl">
                                <Bot size={20} />
                            </div>
                            <div>
                                <h3 className="font-black text-lg tracking-tighter uppercase">IRIS Intelligence</h3>
                                <div className="flex items-center gap-1.5">
                                    <div className="w-1.5 h-1.5 bg-green-500 rounded-full"></div>
                                    <span className="text-[10px] text-gray-400 font-bold uppercase tracking-widest">Neural Sync Active</span>
                                </div>
                            </div>
                        </div>
                        <button onClick={() => setIsOpen(false)} className="hover:bg-white/10 p-2 rounded-full transition-colors text-gray-400">
                            <X size={20} />
                        </button>
                    </div>

                    {/* Pro Navigation */}
                    <div className="flex p-1.5 bg-gray-50/50 border-b gap-1">
                        {[
                            { id: 'chat', label: 'AI Coach', icon: <Bot size={14} /> },
                            { id: 'roadmap', label: 'Roadmap', icon: <Map size={14} /> },
                            { id: 'intel', label: 'MNC Intel', icon: <Target size={14} /> }
                        ].map(tab => (
                            <button
                                key={tab.id}
                                onClick={() => setActiveTab(tab.id)}
                                className={`flex-1 flex items-center justify-center gap-2 py-2.5 rounded-xl text-[11px] font-black uppercase tracking-wider transition-all ${activeTab === tab.id ? 'bg-white shadow-sm text-indigo-600 border border-gray-100' : 'text-gray-400 hover:text-gray-600'
                                    }`}
                            >
                                {tab.icon} {tab.label}
                            </button>
                        ))}
                    </div>

                    {/* Main Content Area */}
                    <div className="flex-1 overflow-y-auto bg-gray-50/30">
                        {activeTab === 'chat' && (
                            <div className="flex-col h-full flex">
                                <div className="flex-1 p-5 space-y-4 overflow-y-auto">
                                    {messages.map((m, idx) => (
                                        <div key={idx} className={`flex ${m.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                                            <div className={`p-4 rounded-2xl text-sm max-w-[85%] ${m.role === 'user' ? 'bg-indigo-600 text-white font-medium shadow-lg shadow-indigo-100' : 'bg-white text-gray-800 border border-gray-100 shadow-sm'}`}>
                                                {m.content}
                                            </div>
                                        </div>
                                    ))}
                                    {loading && <div className="animate-pulse flex gap-2"><div className="w-2 h-2 bg-indigo-200 rounded-full"></div><div className="w-2 h-2 bg-indigo-200 rounded-full animate-delay-150"></div></div>}
                                </div>
                                <div className="p-4 bg-white border-t flex gap-2">
                                    <input
                                        type="text"
                                        value={input}
                                        onChange={(e) => setInput(e.target.value)}
                                        onKeyPress={(e) => e.key === 'Enter' && handleSend()}
                                        placeholder="Ask IRIS Career Coach..."
                                        className="flex-1 bg-gray-100 border-none rounded-xl px-4 py-3 text-sm focus:ring-0"
                                    />
                                    <button onClick={handleSend} className="bg-black text-white p-3 rounded-xl hover:bg-gray-800 transition-all"><Send size={20} /></button>
                                </div>
                            </div>
                        )}

                        {activeTab === 'roadmap' && (
                            <div className="p-6 space-y-6 h-full flex flex-col">
                                {!roadmap ? (
                                    <div className="flex-1 flex flex-col justify-center text-center space-y-4">
                                        <div className="bg-indigo-50 w-16 h-16 rounded-3xl flex items-center justify-center mx-auto text-indigo-600"><Map size={32} /></div>
                                        <div>
                                            <h4 className="font-black text-gray-800 uppercase tracking-tighter text-xl">Build Your Career Path</h4>
                                            <p className="text-sm text-gray-500">IRIS generates 6-month specialized preparation timelines.</p>
                                        </div>
                                        <div className="space-y-2">
                                            <input
                                                type="text"
                                                value={targetRole}
                                                onChange={(e) => setTargetRole(e.target.value)}
                                                placeholder="e.g. FAANG Data Scientist"
                                                className="w-full bg-white border border-gray-200 rounded-2xl px-5 py-4 text-sm focus:border-indigo-500 outline-none transition-all shadow-sm"
                                            />
                                            <button onClick={handleGenerateRoadmap} className="w-full bg-indigo-600 text-white py-4 rounded-2xl font-black uppercase tracking-widest text-xs hover:bg-indigo-700 transition-all shadow-lg shadow-indigo-100">Activate Engine</button>
                                        </div>
                                    </div>
                                ) : (
                                    <div className="space-y-4">
                                        {roadmap.map((step, i) => (
                                            <div key={i} className="bg-white p-4 rounded-2xl border border-gray-100 shadow-sm flex gap-4 hover:border-indigo-200 transition-all group">
                                                <div className="w-10 h-10 rounded-xl bg-indigo-50 text-indigo-600 flex items-center justify-center font-black group-hover:bg-indigo-600 group-hover:text-white transition-all">{i + 1}</div>
                                                <div>
                                                    <p className="text-[10px] font-black text-indigo-400 uppercase tracking-widest">{step.period}</p>
                                                    <h5 className="font-bold text-gray-800 text-sm leading-tight mt-0.5">{step.focus}</h5>
                                                </div>
                                            </div>
                                        ))}
                                        <button onClick={() => setRoadmap(null)} className="w-full py-3 text-xs font-black text-gray-400 uppercase tracking-widest hover:text-indigo-600 transition-all">Reset Timeline</button>
                                    </div>
                                )}
                            </div>
                        )}

                        {activeTab === 'intel' && (
                            <div className="p-6 space-y-6">
                                {!intelResult ? (
                                    <button onClick={runCareerIntel} className="w-full aspect-square border-2 border-dashed border-gray-200 rounded-3xl flex flex-col items-center justify-center gap-3 text-gray-400 hover:border-indigo-400 hover:text-indigo-500 transition-all group">
                                        <Target size={40} className="group-hover:scale-110 transition-all" />
                                        <span className="font-black uppercase tracking-widest text-xs">Run MNC Suitability Scan</span>
                                    </button>
                                ) : (
                                    <div className="space-y-6 animate-in fade-in duration-500">
                                        <div className="bg-indigo-600 p-6 rounded-[32px] text-white shadow-xl shadow-indigo-100 relative overflow-hidden">
                                            <div className="absolute -right-4 -top-4 w-24 h-24 bg-white/10 rounded-full blur-2xl"></div>
                                            <p className="text-[10px] font-black uppercase tracking-[0.2em] text-white/60 mb-1">Growth Forecast</p>
                                            <div className="flex items-center justify-between">
                                                <h4 className="text-3xl font-black tracking-tighter">{intelResult.future_growth_score}/10</h4>
                                                <div className="bg-white/20 px-3 py-1 rounded-full text-[10px] font-bold uppercase">{intelResult.risk_level} Risk</div>
                                            </div>
                                        </div>

                                        <div className="space-y-2">
                                            <label className="text-[10px] font-black text-gray-400 uppercase tracking-widest px-1">Top Career Paths</label>
                                            <div className="space-y-2">
                                                {intelResult.recommended_domains.map((d, i) => (
                                                    <div key={i} className="bg-white p-4 rounded-2xl border border-gray-100 flex items-center justify-between hover:translate-x-1 transition-all">
                                                        <span className="font-bold text-gray-700 text-sm">{d}</span>
                                                        <ChevronRight size={14} className="text-gray-300" />
                                                    </div>
                                                ))}
                                            </div>
                                        </div>

                                        <div className="bg-amber-50 p-4 rounded-2xl border border-amber-100">
                                            <p className="text-[10px] font-black text-amber-600 uppercase tracking-widest mb-1 flex items-center gap-2">
                                                <Briefcase size={12} /> MNC FAANG Strategy
                                            </p>
                                            <p className="text-xs text-amber-800 leading-relaxed font-medium">Focus on quantifiable results and system scalability to breach current FAANG entry thresholds.</p>
                                        </div>
                                    </div>
                                )}
                            </div>
                        )}
                    </div>
                </div>
            )}
        </>
    );
}
