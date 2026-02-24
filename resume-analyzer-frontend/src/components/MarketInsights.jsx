import React, { useState, useEffect } from 'react';
import { resumeAPI } from '../api';
import { TrendingUp, BarChart3, Target, Zap, Globe, Briefcase, IndianRupee, Clock } from 'lucide-react';

export default function MarketInsights() {
    const [resumes, setResumes] = useState([]);
    const [selectedResumeId, setSelectedResumeId] = useState(null);
    const [loading, setLoading] = useState(true);
    const [marketData, setMarketData] = useState({
        demand_index: 8.4,
        top_roles: ["Backend Developer", "Cloud Engineer", "Python Architect"],
        avg_salary: "12L - 25L per annum",
        trending_skills: ["FastAPI", "Next.js", "Generative AI", "Docker"],
        remote_availability: "45%"
    });

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

    const selectedResume = resumes.find(r => r.id === selectedResumeId);

    if (loading) {
        return (
            <div className="flex items-center justify-center min-h-[60vh]">
                <div className="animate-spin w-12 h-12 border-4 border-indigo-600 border-t-transparent rounded-full"></div>
            </div>
        );
    }

    return (
        <div className="space-y-12">
            <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-6">
                <div>
                    <h1 className="text-6xl font-black bg-gradient-to-r from-white via-indigo-200 to-slate-500 bg-clip-text text-transparent tracking-tighter mb-4">
                        Market Insights
                    </h1>
                    <p className="text-slate-400 font-medium tracking-wide max-w-2xl px-1 uppercase text-[10px] letter-spacing-[0.2em]">
                        Global Intelligence & Industry Demand Vectors
                    </p>
                </div>

                <div className="flex flex-col gap-2">
                    <label className="text-[10px] font-black text-slate-500 uppercase tracking-widest px-1">Active Baseline</label>
                    <select
                        value={selectedResumeId || ''}
                        onChange={(e) => setSelectedResumeId(Number(e.target.value))}
                        className="bg-white/5 border border-white/10 rounded-2xl px-6 py-4 text-sm text-white font-bold outline-none focus:ring-2 focus:ring-indigo-600/20 transition-all appearance-none cursor-pointer min-w-[280px]"
                    >
                        {resumes.length > 0 ? resumes.map(r => (
                            <option key={r.id} value={r.id} className="bg-slate-900 text-white font-bold">{r.title}</option>
                        )) : <option value="">No Resumes Found</option>}
                    </select>
                </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8">
                {[
                    { label: "Demand Index", value: marketData.demand_index + "/10", icon: TrendingUp, color: "text-emerald-400" },
                    { label: "Remote Capacity", value: marketData.remote_availability, icon: Globe, color: "text-blue-400" },
                    { label: "Avg CTC Range", value: marketData.avg_salary, icon: IndianRupee, color: "text-indigo-400" },
                    { label: "Market Tempo", value: "High", icon: Zap, color: "text-amber-400" },
                ].map((stat, i) => (
                    <div key={i} className="glass-card p-8 border border-white/5 bg-white/5 rounded-[40px] hover:border-white/10 transition-all">
                        <stat.icon className={`${stat.color} mb-6`} size={24} />
                        <h4 className="text-2xl font-black text-white">{stat.value}</h4>
                        <p className="text-[10px] font-black text-slate-500 uppercase tracking-widest mt-1">{stat.label}</p>
                    </div>
                ))}
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-12">
                <div className="glass-card p-10 border border-white/5 rounded-[48px] bg-gradient-to-br from-indigo-600/5 to-transparent">
                    <h3 className="text-xl font-black text-white uppercase tracking-widest mb-10 flex items-center gap-4">
                        <BarChart3 className="text-indigo-400" size={24} />
                        Trending Skills in {selectedResume?.predicted_role || "Tech"}
                    </h3>
                    <div className="space-y-6">
                        {marketData.trending_skills.map((skill, i) => (
                            <div key={i} className="flex items-center justify-between group">
                                <span className="text-slate-300 font-bold tracking-wide">{skill}</span>
                                <div className="flex items-center gap-4">
                                    <div className="w-32 h-1.5 bg-white/5 rounded-full overflow-hidden">
                                        <div
                                            className="h-full bg-gradient-to-r from-indigo-600 to-blue-500"
                                            style={{ width: `${95 - i * 15}%` }}
                                        ></div>
                                    </div>
                                    <span className="text-[10px] font-black text-indigo-400 w-8">+{80 - i * 10}%</span>
                                </div>
                            </div>
                        ))}
                    </div>
                    <div className="mt-12 bg-indigo-600/10 p-6 rounded-3xl border border-indigo-500/10">
                        <p className="text-xs text-slate-400 font-medium italic leading-relaxed">
                            "System detected {marketData.trending_skills[0]} as a high-velocity skill vector. Recommended for immediate acquisition."
                        </p>
                    </div>
                </div>

                <div className="glass-card p-10 border border-white/5 rounded-[48px] flex flex-col">
                    <h3 className="text-xl font-black text-white uppercase tracking-widest mb-10 flex items-center gap-4">
                        <Target className="text-blue-400" size={24} />
                        MNC Openings: Recommended Fix
                    </h3>
                    <div className="flex-1 flex flex-col justify-center items-center text-center space-y-6 border-2 border-dashed border-white/5 rounded-[40px] p-8">
                        {selectedResume ? (
                            <>
                                <div className="bg-blue-600/10 p-6 rounded-full">
                                    <Briefcase size={40} className="text-blue-400" />
                                </div>
                                <div>
                                    <h4 className="text-2xl font-black text-white tracking-tight">{selectedResume.predicted_role || "Senior Architect"}</h4>
                                    <p className="text-slate-500 text-sm font-medium uppercase tracking-widest mt-1">Matched Career Path</p>
                                </div>
                                <div className="grid grid-cols-2 gap-4 w-full">
                                    <div className="bg-white/5 p-4 rounded-2xl text-center">
                                        <Clock size={16} className="text-slate-500 mx-auto mb-2" />
                                        <span className="text-[10px] font-black text-slate-300 block">34 Global Jobs</span>
                                    </div>
                                    <div className="bg-white/5 p-4 rounded-2xl text-center">
                                        <Globe size={16} className="text-slate-500 mx-auto mb-2" />
                                        <span className="text-[10px] font-black text-slate-300 block">Hybrid Possible</span>
                                    </div>
                                </div>
                            </>
                        ) : (
                            <p className="text-slate-500 font-bold uppercase tracking-widest text-xs">No Baseline Data Found</p>
                        )}
                    </div>
                </div>
            </div>
        </div>
    );
}
