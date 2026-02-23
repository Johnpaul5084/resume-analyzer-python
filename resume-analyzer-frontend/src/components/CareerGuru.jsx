import React, { useState } from 'react';
import { Send, User, Bot, X, Calendar, Map, Target, Briefcase, ChevronRight, BarChart3, TrendingUp, Zap } from 'lucide-react';
import { careerGuruAPI, careerIntelAPI, resumeAPI } from '../api';

export default function CareerGuru({ resumeId }) {
    const [isOpen, setIsOpen] = useState(false);
    const [activeTab, setActiveTab] = useState('chat'); // 'chat', 'roadmap', 'intel', 'graph'
    const [messages, setMessages] = useState([
        { role: 'assistant', content: "Initialization complete. I am IRIS AI, your Career Intelligence Mentor. How shall we optimize your path today?" }
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
            const response = await careerGuruAPI.chat(input, resumeId);
            setMessages(prev => [...prev, { role: 'assistant', content: response.data.reply }]);
        } catch (err) {
            setMessages(prev => [...prev, { role: 'assistant', content: "Neural link interrupted. Please retry." }]);
        } finally {
            setLoading(false);
        }
    };

    const runIRISIntelligence = async () => {
        setLoading(true);
        try {
            // Fetch resume data first to get text and skills
            const res = await resumeAPI.getById(resumeId);
            const resumeText = res.data.content;
            const skills = res.data.analysis?.key_strengths || [];

            const insight = await careerIntelAPI.getMentorInsight(resumeText, skills);
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
            {/* IRIS Orbital Button */}
            <button
                onClick={() => setIsOpen(true)}
                className="fixed bottom-8 right-8 bg-black text-white p-4 rounded-full shadow-[0_0_30px_rgba(79,70,229,0.3)] hover:scale-110 transition-all z-50 group border border-indigo-500/30"
            >
                <div className="flex items-center gap-2">
                    <div className="relative">
                        <Zap size={28} className="text-indigo-400 group-hover:animate-pulse" />
                        <div className="absolute -top-1 -right-1 w-3 h-3 bg-indigo-500 rounded-full animate-ping"></div>
                    </div>
                    <span className="max-w-0 overflow-hidden group-hover:max-w-xs transition-all duration-300 font-black tracking-tighter uppercase text-sm">IRIS AI Neural</span>
                </div>
            </button>

            {/* Career Intelligence Sidebar */}
            {isOpen && (
                <div className="fixed top-0 right-0 w-[450px] h-full bg-white shadow-[-20px_0_50px_rgba(0,0,0,0.1)] flex flex-col z-[100] animate-in slide-in-from-right duration-300">
                    {/* Dark Header */}
                    <div className="bg-[#050505] p-6 text-white flex justify-between items-start">
                        <div className="flex items-center gap-4">
                            <div className="bg-gradient-to-br from-indigo-500 to-purple-600 p-2.5 rounded-2xl">
                                <Bot size={24} />
                            </div>
                            <div>
                                <h3 className="font-black text-xl tracking-tighter">IRIS CAREER INTELLIGENCE</h3>
                                <div className="flex items-center gap-2">
                                    <span className="text-[10px] bg-indigo-500/20 text-indigo-400 px-2 py-0.5 rounded-full font-bold tracking-widest uppercase">System Online</span>
                                    <span className="text-[10px] text-gray-500 font-bold uppercase tracking-widest">v2.0 Neural Match</span>
                                </div>
                            </div>
                        </div>
                        <button onClick={() => setIsOpen(false)} className="hover:bg-white/10 p-2 rounded-full transition-colors text-gray-500">
                            <X size={24} />
                        </button>
                    </div>

                    {/* High-Tech Tab Navigation */}
                    <div className="flex p-2 bg-gray-100/50 border-b overflow-x-auto no-scrollbar gap-1">
                        {[
                            { id: 'chat', label: 'Mentor Chat', icon: <Bot size={14} /> },
                            { id: 'intel', label: 'Fit Analysis', icon: <Target size={14} /> },
                            { id: 'roadmap', label: 'AI Roadmap', icon: <Map size={14} /> },
                            { id: 'graph', label: 'Skill Graph', icon: <BarChart3 size={14} /> }
                        ].map(tab => (
                            <button
                                key={tab.id}
                                onClick={() => setActiveTab(tab.id)}
                                className={`whitespace-nowrap flex items-center gap-2 px-4 py-2.5 rounded-xl text-[11px] font-black uppercase tracking-widest transition-all ${activeTab === tab.id ? 'bg-black text-white shadow-xl' : 'text-gray-400 hover:bg-gray-200'
                                    }`}
                            >
                                {tab.icon} {tab.label}
                            </button>
                        ))}
                    </div>

                    {/* Content Layer */}
                    <div className="flex-1 overflow-y-auto bg-gray-50/50 custom-scrollbar">
                        {activeTab === 'chat' && (
                            <div className="flex flex-col h-full">
                                <div className="flex-1 p-6 space-y-6 overflow-y-auto">
                                    {messages.map((m, idx) => (
                                        <div key={idx} className={`flex ${m.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                                            <div className={`p-4 rounded-3xl text-sm max-w-[85%] leading-relaxed ${m.role === 'user'
                                                    ? 'bg-black text-white rounded-br-none shadow-lg'
                                                    : 'bg-white text-gray-800 border border-gray-100 rounded-tl-none shadow-sm'
                                                }`}>
                                                {m.content}
                                            </div>
                                        </div>
                                    ))}
                                    {loading && <div className="flex gap-2 p-2"><div className="w-2 h-2 bg-indigo-500 rounded-full animate-bounce"></div><div className="w-2 h-2 bg-indigo-500 rounded-full animate-bounce delay-100"></div></div>}
                                </div>
                                <div className="p-6 bg-white border-t flex gap-3">
                                    <input
                                        type="text"
                                        value={input}
                                        onChange={(e) => setInput(e.target.value)}
                                        onKeyPress={(e) => e.key === 'Enter' && handleSend()}
                                        placeholder="Command IRIS..."
                                        className="flex-1 bg-gray-100 border-none rounded-2xl px-5 py-4 text-sm focus:ring-2 focus:ring-indigo-500/20 font-medium"
                                    />
                                    <button onClick={handleSend} className="bg-black text-white p-4 rounded-2xl hover:bg-gray-800 transition-all active:scale-95 shadow-lg"><Send size={20} /></button>
                                </div>
                            </div>
                        )}

                        {activeTab === 'intel' && (
                            <div className="p-8 space-y-8">
                                {!mentorData ? (
                                    <div className="flex flex-col items-center justify-center py-20 text-center space-y-6">
                                        <div className="w-24 h-24 bg-indigo-50 rounded-full flex items-center justify-center text-indigo-600 animate-pulse"><Target size={48} /></div>
                                        <div>
                                            <h4 className="font-black text-2xl uppercase tracking-tighter">Run Neural Matching</h4>
                                            <p className="text-gray-500 text-sm max-w-xs mx-auto">Analyze your resume against global MNC benchmarks and semantic career paths.</p>
                                        </div>
                                        <button onClick={runIRISIntelligence} className="btn-primary px-8 py-4 rounded-2xl font-black uppercase tracking-widest text-xs flex items-center gap-3">
                                            {loading ? <div className="animate-spin w-4 h-4 border-2 border-white/30 border-t-white rounded-full"></div> : <Zap size={16} />}
                                            Execute Analysis
                                        </button>
                                    </div>
                                ) : (
                                    <div className="space-y-8 animate-in fade-in duration-500">
                                        {/* Market Forecast Card */}
                                        <div className="bg-black p-8 rounded-[40px] text-white shadow-2xl relative overflow-hidden group">
                                            <div className="absolute -right-10 -top-10 w-40 h-40 bg-indigo-500/10 rounded-full blur-3xl group-hover:bg-indigo-500/20 transition-all"></div>
                                            <div className="relative z-10">
                                                <p className="text-[10px] font-black uppercase tracking-[0.3em] text-indigo-400 mb-2">Market Demand Forecast</p>
                                                <div className="flex items-end justify-between">
                                                    <div>
                                                        <h4 className="text-4xl font-black tracking-tighter leading-none">{mentorData.market_demand}</h4>
                                                        <p className="text-gray-400 text-xs mt-2 font-bold uppercase tracking-widest">{mentorData.recommended_role}</p>
                                                    </div>
                                                    <div className="text-right">
                                                        <p className="text-[10px] font-black uppercase text-gray-500 mb-1">Growth Score</p>
                                                        <span className="text-2xl font-black text-indigo-400">{mentorData.growth_score}/10</span>
                                                    </div>
                                                </div>
                                            </div>
                                        </div>

                                        {/* Mentor Advice */}
                                        <div className="bg-indigo-50/50 p-6 rounded-3xl border border-indigo-100 flex gap-4">
                                            <Bot className="text-indigo-600 flex-shrink-0" size={24} />
                                            <p className="text-sm text-indigo-900 font-medium leading-relaxed">{mentorData.mentor_advice}</p>
                                        </div>

                                        {/* Salary Range */}
                                        <div className="flex items-center justify-between p-6 bg-white rounded-3xl border border-gray-100 shadow-sm">
                                            <div className="flex items-center gap-3">
                                                <TrendingUp className="text-green-500" size={24} />
                                                <span className="text-xs font-black uppercase tracking-widest text-gray-400">Target Salary</span>
                                            </div>
                                            <span className="text-xl font-black text-gray-800">{mentorData.salary_range}</span>
                                        </div>
                                    </div>
                                )}
                            </div>
                        )}

                        {activeTab === 'roadmap' && (
                            <div className="p-8 h-full">
                                {!mentorData ? (
                                    <div className="flex flex-col items-center justify-center py-20 text-center space-y-6">
                                        <div className="w-24 h-24 bg-blue-50 rounded-full flex items-center justify-center text-blue-600"><Map size={48} /></div>
                                        <h4 className="font-black text-2xl uppercase tracking-tighter">AI Roadmap Engine</h4>
                                        <button onClick={runIRISIntelligence} className="btn-primary px-8 py-4">Generate Timeline</button>
                                    </div>
                                ) : (
                                    <div className="space-y-6">
                                        <div className="flex items-center justify-between mb-4 px-2">
                                            <h4 className="font-black uppercase tracking-widest text-xs text-gray-400">6-Month Preparation Protocol</h4>
                                            <span className="text-[10px] bg-green-100 text-green-700 px-2 py-0.5 rounded-full font-bold">Optimized</span>
                                        </div>
                                        <div className="prose prose-sm max-w-none text-gray-700 font-medium whitespace-pre-line bg-white p-8 rounded-[40px] border border-gray-100 shadow-sm leading-loose">
                                            {mentorData.dynamic_roadmap}
                                        </div>
                                    </div>
                                )}
                            </div>
                        )}

                        {activeTab === 'graph' && (
                            <div className="p-8 h-full flex flex-col">
                                {!mentorData ? (
                                    <div className="flex-1 flex flex-col items-center justify-center text-center space-y-6">
                                        <div className="w-24 h-24 bg-purple-50 rounded-full flex items-center justify-center text-purple-600"><BarChart3 size={48} /></div>
                                        <h4 className="font-black text-2xl uppercase tracking-tighter">Neural Skill Graph</h4>
                                        <button onClick={runIRISIntelligence} className="btn-primary px-8 py-4">Visualize Skills</button>
                                    </div>
                                ) : (
                                    <div className="space-y-6">
                                        <div className="bg-white p-4 rounded-[40px] border border-gray-100 shadow-xl overflow-hidden">
                                            <img
                                                src={`data:image/png;base64,${mentorData.skill_graph}`}
                                                alt="Skill Graph"
                                                className="w-full h-auto rounded-3xl"
                                            />
                                        </div>
                                        <div className="grid grid-cols-3 gap-3">
                                            <div className="bg-green-50 p-3 rounded-2xl border border-green-100 text-center">
                                                <div className="w-3 h-3 bg-green-500 rounded-full mx-auto mb-1"></div>
                                                <span className="text-[9px] font-black uppercase text-green-700">Existing</span>
                                            </div>
                                            <div className="bg-red-50 p-3 rounded-2xl border border-red-100 text-center">
                                                <div className="w-3 h-3 bg-red-500 rounded-full mx-auto mb-1"></div>
                                                <span className="text-[9px] font-black uppercase text-red-700">Missing</span>
                                            </div>
                                            <div className="bg-gray-100 p-3 rounded-2xl border border-gray-200 text-center">
                                                <div className="w-3 h-3 bg-gray-400 rounded-full mx-auto mb-1"></div>
                                                <span className="text-[9px] font-black uppercase text-gray-500">Advanced</span>
                                            </div>
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
