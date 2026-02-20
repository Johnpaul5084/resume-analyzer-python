import React, { useState } from 'react';
import { Send, User, Bot, X, Calendar } from 'lucide-react';
import { careerGuruAPI } from '../api';

export default function CareerGuru({ resumeId }) {
    const [isOpen, setIsOpen] = useState(false);
    const [messages, setMessages] = useState([
        { role: 'assistant', content: "Hello! I'm your AI Career Guru. How can I help you with your career goals today?" }
    ]);
    const [input, setInput] = useState('');
    const [loading, setLoading] = useState(false);
    const [showRoadmapModal, setShowRoadmapModal] = useState(false);
    const [targetRole, setTargetRole] = useState('');
    const [roadmap, setRoadmap] = useState(null);

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
            console.error('Chat error:', err);
            setMessages(prev => [...prev, { role: 'assistant', content: "I'm having trouble connecting to the network. Please try again later." }]);
        } finally {
            setLoading(false);
        }
    };

    const handleGenerateRoadmap = async () => {
        if (!targetRole.trim()) return;
        setLoading(true);
        try {
            const response = await careerGuruAPI.getRoadmap(targetRole, resumeId);
            setRoadmap(response.data);
        } catch (err) {
            console.error('Roadmap error:', err);
        } finally {
            setLoading(false);
        }
    };

    return (
        <>
            {/* Floating Chat Button */}
            <button
                onClick={() => setIsOpen(true)}
                className="fixed bottom-8 right-8 bg-gradient-to-r from-blue-600 to-indigo-600 text-white p-4 rounded-full shadow-2xl hover:scale-110 transition-transform z-50 group"
            >
                <div className="flex items-center gap-2">
                    <Bot size={28} />
                    <span className="max-w-0 overflow-hidden group-hover:max-w-xs transition-all duration-300 font-bold">Career Guru</span>
                </div>
            </button>

            {/* Chat Window */}
            {isOpen && (
                <div className="fixed bottom-24 right-8 w-96 h-[600px] bg-white rounded-2xl shadow-2xl border border-gray-100 flex flex-col z-50 overflow-hidden animate-in slide-in-from-bottom-5">
                    {/* Header */}
                    <div className="bg-gradient-to-r from-blue-600 to-indigo-600 p-4 text-white flex justify-between items-center">
                        <div className="flex items-center gap-3">
                            <div className="bg-white/20 p-2 rounded-lg">
                                <Bot size={20} />
                            </div>
                            <div>
                                <h3 className="font-bold">AI Career Guru</h3>
                                <p className="text-xs text-blue-100 flex items-center gap-1">
                                    <span className="w-2 h-2 bg-green-400 rounded-full animate-pulse"></span>
                                    Ask anything about your career
                                </p>
                            </div>
                        </div>
                        <button onClick={() => setIsOpen(false)} className="hover:bg-white/10 p-1 rounded-md transition-colors">
                            <X size={20} />
                        </button>
                    </div>

                    {/* Quick Actions */}
                    <div className="p-3 bg-gray-50 border-b flex gap-2 overflow-x-auto no-scrollbar">
                        <button
                            onClick={() => setShowRoadmapModal(true)}
                            className="text-xs flex-shrink-0 bg-blue-100 text-blue-700 px-3 py-1.5 rounded-full font-bold hover:bg-blue-200 transition-colors flex items-center gap-1"
                        >
                            <Calendar size={14} />
                            Generate Roadmap
                        </button>
                    </div>

                    {/* Messages */}
                    <div className="flex-1 overflow-y-auto p-4 space-y-4 bg-gray-50">
                        {messages.map((m, idx) => (
                            <div key={idx} className={`flex ${m.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                                <div className={`flex gap-3 max-w-[85%] ${m.role === 'user' ? 'flex-row-reverse' : ''}`}>
                                    <div className={`w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0 ${m.role === 'user' ? 'bg-blue-600' : 'bg-indigo-600'}`}>
                                        {m.role === 'user' ? <User size={16} className="text-white" /> : <Bot size={16} className="text-white" />}
                                    </div>
                                    <div className={`p-3 rounded-2xl text-sm shadow-sm ${m.role === 'user'
                                            ? 'bg-blue-600 text-white rounded-tr-none'
                                            : 'bg-white text-gray-800 border border-gray-100 rounded-tl-none'
                                        }`}>
                                        {m.content}
                                    </div>
                                </div>
                            </div>
                        ))}
                        {loading && (
                            <div className="flex justify-start">
                                <div className="flex gap-3">
                                    <div className="w-8 h-8 rounded-full bg-indigo-600 flex items-center justify-center">
                                        <Bot size={16} className="text-white" />
                                    </div>
                                    <div className="p-3 rounded-2xl bg-white border border-gray-100 shadow-sm">
                                        <div className="flex gap-1">
                                            <div className="w-1.5 h-1.5 bg-gray-400 rounded-full animate-bounce"></div>
                                            <div className="w-1.5 h-1.5 bg-gray-400 rounded-full animate-bounce delay-75"></div>
                                            <div className="w-1.5 h-1.5 bg-gray-400 rounded-full animate-bounce delay-150"></div>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        )}
                    </div>

                    {/* Input */}
                    <div className="p-4 border-t bg-white">
                        <div className="flex gap-2">
                            <input
                                type="text"
                                value={input}
                                onChange={(e) => setInput(e.target.value)}
                                onKeyPress={(e) => e.key === 'Enter' && handleSend()}
                                placeholder="Type your question..."
                                className="flex-1 bg-gray-50 border-none rounded-xl px-4 py-2.5 text-sm focus:ring-2 focus:ring-blue-500"
                            />
                            <button
                                onClick={handleSend}
                                className="bg-blue-600 text-white p-2.5 rounded-xl hover:bg-blue-700 transition-colors shadow-lg"
                                disabled={loading}
                            >
                                <Send size={20} />
                            </button>
                        </div>
                    </div>
                </div>
            )}

            {/* Roadmap Modal */}
            {showRoadmapModal && (
                <div className="fixed inset-0 bg-black/50 backdrop-blur-sm z-[60] flex items-center justify-center p-4">
                    <div className="bg-white rounded-3xl w-full max-w-lg overflow-hidden shadow-2xl animate-in zoom-in-95 duration-200">
                        <div className="p-6 bg-gradient-to-r from-blue-600 to-indigo-600 text-white flex justify-between items-center">
                            <div>
                                <h2 className="text-2xl font-bold">Personalized Roadmap 🚀</h2>
                                <p className="text-blue-100 text-sm">Step-by-step path to your dream role</p>
                            </div>
                            <button onClick={() => setShowRoadmapModal(false)} className="hover:bg-white/10 p-1 rounded-full transition-colors">
                                <X size={24} />
                            </button>
                        </div>

                        <div className="p-6">
                            {!roadmap ? (
                                <div className="space-y-4">
                                    <div>
                                        <label className="block text-sm font-bold text-gray-700 mb-2">TARGET JOB ROLE</label>
                                        <input
                                            type="text"
                                            value={targetRole}
                                            onChange={(e) => setTargetRole(e.target.value)}
                                            placeholder="e.g. Senior Full Stack Engineer, Data Scientist"
                                            className="w-full bg-gray-50 border-gray-200 rounded-xl px-4 py-3 focus:ring-2 focus:ring-blue-500 transition-shadow"
                                        />
                                    </div>
                                    <button
                                        onClick={handleGenerateRoadmap}
                                        className="w-full bg-blue-600 text-white py-3 rounded-xl font-bold hover:bg-blue-700 transition-all flex items-center justify-center gap-2"
                                        disabled={loading || !targetRole}
                                    >
                                        {loading ? <div className="animate-spin w-5 h-5 border-2 border-white/30 border-t-white rounded-full"></div> : 'Generate Career Path'}
                                    </button>
                                </div>
                            ) : (
                                <div className="space-y-6">
                                    {roadmap.steps?.map((step, i) => (
                                        <div key={i} className="flex gap-4 relative">
                                            {i !== roadmap.steps.length - 1 && <div className="absolute left-6 top-10 bottom-0 w-0.5 bg-blue-100"></div>}
                                            <div className="w-12 h-12 rounded-2xl bg-blue-600 text-white flex items-center justify-center font-bold text-lg flex-shrink-0 shadow-lg shadow-blue-200">
                                                {i + 1}
                                            </div>
                                            <div className="flex-1 pb-4">
                                                <h4 className="font-bold text-gray-800 text-lg leading-tight">{step.Goal || step['Goal Name']}</h4>
                                                <p className="text-sm text-gray-600 mt-1 mb-2 font-medium">⏳ {step.Time || step['Estimated Time']}</p>
                                                <div className="flex flex-wrap gap-2 mb-2">
                                                    {(step.Skills || step['Skills to Learn'])?.split(',').map((s, j) => (
                                                        <span key={j} className="text-[10px] px-2 py-0.5 bg-indigo-50 text-indigo-700 rounded-md font-bold border border-indigo-100 uppercase">
                                                            {s.trim()}
                                                        </span>
                                                    ))}
                                                </div>
                                                <div className="text-xs bg-gray-50 p-2 rounded-lg text-gray-500 border border-gray-100">
                                                    📚 Resource: <span className="text-blue-600 font-bold">{step.Resource || step['One Free Resource']}</span>
                                                </div>
                                            </div>
                                        </div>
                                    ))}
                                    <button
                                        onClick={() => setRoadmap(null)}
                                        className="w-full py-2 text-gray-500 font-bold text-sm hover:text-gray-700 transition-colors"
                                    >
                                        Build another roadmap
                                    </button>
                                </div>
                            )}
                        </div>
                    </div>
                </div>
            )}
        </>
    );
}
