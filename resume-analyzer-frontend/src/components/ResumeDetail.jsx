import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { resumeAPI, jobAPI } from '../api';
import { RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis, Radar, ResponsiveContainer, Tooltip } from 'recharts';
import { FileText, TrendingUp, AlertCircle, Briefcase, ArrowLeft } from 'lucide-react';
import MentorBot from './MentorBot';

export default function ResumeDetail() {
    const { id } = useParams();
    const navigate = useNavigate();
    const [resume, setResume] = useState(null);
    const [recommendations, setRecommendations] = useState([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        fetchResumeDetails();
        fetchRecommendations();
    }, [id]);

    // Auto-refresh if analyzing
    useEffect(() => {
        let interval;
        if (resume && resume.predicted_role === "Analyzing...") {
            interval = setInterval(() => {
                fetchResumeDetails();
            }, 5000); // Poll every 5s
        }
        return () => clearInterval(interval);
    }, [resume]);

    const fetchResumeDetails = async () => {
        try {
            const response = await resumeAPI.getById(id);
            setResume(response.data);
        } catch (err) {
            console.error('Error fetching resume:', err);
        } finally {
            setLoading(false);
        }
    };

    const fetchRecommendations = async () => {
        try {
            const response = await jobAPI.getRecommendations(id);
            setRecommendations(response.data);
        } catch (err) {
            console.error('Error fetching recommendations:', err);
        }
    };

    if (loading) {
        return (
            <div className="min-h-screen flex items-center justify-center">
                <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
            </div>
        );
    }

    if (!resume) {
        return (
            <div className="min-h-screen flex items-center justify-center">
                <div className="text-center">
                    <AlertCircle size={48} className="mx-auto text-red-500 mb-4" />
                    <h2 className="text-2xl font-bold text-gray-800">Resume not found</h2>
                </div>
            </div>
        );
    }

    const scoreData = resume.score_breakdown ? [
        { subject: 'Semantic Similarity', A: resume.score_breakdown.semantic_similarity || 0, fullMark: 100 },
        { subject: 'Skill Coverage', A: resume.score_breakdown.skill_coverage || 0, fullMark: 100 },
        { subject: 'Experience Depth', A: resume.score_breakdown.experience_depth || 0, fullMark: 100 },
        { subject: 'ATS Format', A: resume.score_breakdown.ats_format_score || 0, fullMark: 100 },
        { subject: 'Market Fit', A: resume.score_breakdown.market_readiness || 0, fullMark: 100 },
    ] : [];

    const getScoreColor = (score) => {
        if (score >= 80) return 'text-green-600';
        if (score >= 60) return 'text-yellow-600';
        return 'text-red-600';
    };

    return (
        <div className="space-y-12">
            {/* Action Bar */}
            <div className="flex items-center justify-between border-b border-white/5 pb-8">
                <div>
                    <h1 className="text-4xl font-black tracking-tighter bg-gradient-to-r from-white to-slate-400 bg-clip-text text-transparent">
                        {resume.title}
                    </h1>
                    <p className="text-slate-500 font-bold uppercase text-[10px] tracking-[0.2em] mt-1">
                        Neural Signature Detected: {new Date(resume.created_at).toLocaleDateString()}
                    </p>
                </div>
                <div className="flex gap-4">
                    <button onClick={() => navigate('/dashboard')} className="px-6 py-3 rounded-xl bg-white/5 border border-white/10 text-xs font-black uppercase tracking-widest hover:bg-white/10 transition-all">
                        ← Exit Node
                    </button>
                    <button onClick={() => navigate(`/optimizer/${id}`)} className="px-6 py-3 rounded-xl bg-indigo-600 text-white text-xs font-black uppercase tracking-widest hover:bg-indigo-700 shadow-[0_0_20px_rgba(79,70,229,0.3)] transition-all">
                        Optimize Matrix
                    </button>
                </div>
            </div>

            {/* Core Metrics Grid */}
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
                {/* ATS Score Card */}
                <div className="glass-card p-1">
                    <div className="bg-slate-900/50 p-8 rounded-2xl h-full flex flex-col items-center justify-center text-center">
                        <p className="text-[10px] font-black text-slate-500 uppercase tracking-[0.3em] mb-4">ATS Alignment</p>
                        <div className={`text-7xl font-black tracking-tighter mb-2 ${getScoreColor(resume.ats_score)}`}>
                            {resume.ats_score?.toFixed(0)}<span className="text-3xl ml-1">%</span>
                        </div>
                        <p className="text-xs font-bold text-slate-400 leading-relaxed uppercase tracking-tighter">
                            Semantic Match Probability
                        </p>
                    </div>
                </div>

                {/* Radar Chart */}
                <div className="lg:col-span-2 glass-card p-8">
                    <h2 className="text-xs font-black uppercase tracking-[0.3em] text-slate-500 mb-8 px-2">Skill Surface Analysis</h2>
                    {scoreData.length > 0 ? (
                        <div className="h-[300px]">
                            <ResponsiveContainer width="100%" height="100%">
                                <RadarChart cx="50%" cy="50%" outerRadius="80%" data={scoreData}>
                                    <PolarGrid stroke="#334155" />
                                    <PolarAngleAxis dataKey="subject" tick={{ fill: '#94a3b8', fontSize: 10, fontWeight: 800 }} />
                                    <PolarRadiusAxis angle={30} domain={[0, 100]} tick={false} axisLine={false} />
                                    <Radar
                                        name="AI Analysis"
                                        dataKey="A"
                                        stroke="#6366f1"
                                        fill="#6366f1"
                                        fillOpacity={0.3}
                                        strokeWidth={3}
                                    />
                                    <Tooltip
                                        contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', borderRadius: '12px' }}
                                        itemStyle={{ color: '#818cf8', fontWeight: 'bold' }}
                                    />
                                </RadarChart>
                            </ResponsiveContainer>
                        </div>
                    ) : (
                        <div className="flex items-center justify-center h-[300px] text-slate-600 italic">Computing Metrics...</div>
                    )}
                </div>
            </div>

            {/* Detailed Intelligence */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-10">
                {/* Gaps */}
                <div className="glass-card p-10 border-l-4 border-l-rose-500/50">
                    <h2 className="text-xl font-black uppercase tracking-widest text-slate-200 mb-8 flex items-center gap-4">
                        <span className="p-2 bg-rose-500/10 rounded-lg"><TrendingUp className="text-rose-400" size={20} /></span>
                        Critical Deficiencies
                    </h2>
                    <div className="flex flex-wrap gap-3">
                        {resume.missing_keywords?.slice(0, 12).map((keyword, idx) => (
                            <span key={idx} className="px-4 py-2 bg-rose-500/5 border border-rose-500/10 text-rose-400 rounded-xl text-[10px] font-black uppercase tracking-widest">
                                - {keyword}
                            </span>
                        ))}
                    </div>
                </div>

                {/* Role Alignment */}
                <div className="glass-card p-10 border-l-4 border-l-emerald-500/50">
                    <h2 className="text-xl font-black uppercase tracking-widest text-slate-200 mb-8 flex items-center gap-4">
                        <span className="p-2 bg-emerald-500/10 rounded-lg"><TrendingUp className="text-emerald-400" size={20} /></span>
                        Target Projections
                    </h2>
                    <div className="bg-white/5 p-8 rounded-3xl border border-white/5 mb-6">
                        <p className="text-[10px] font-black text-indigo-400 uppercase tracking-widest mb-2">Neural Prediction</p>
                        <div className="text-4xl font-black tracking-tighter text-white uppercase italic">
                            {resume.predicted_role}
                        </div>
                    </div>
                </div>
            </div>

            {/* Market Recommendations Section */}
            {recommendations.length > 0 && (
                <div className="space-y-10">
                    <div className="flex items-center gap-6">
                        <h2 className="text-3xl font-black tracking-tighter text-white">Market Opportunities</h2>
                        <div className="h-px flex-1 bg-white/5"></div>
                    </div>
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
                        {recommendations.map((rec, idx) => (
                            <div key={idx} className="glass-card p-8 hover:border-indigo-500/50 group transition-all duration-300">
                                <div className="flex justify-between items-start mb-6">
                                    <div>
                                        <h3 className="font-black text-white text-lg leading-none mb-2">{rec.title}</h3>
                                        <p className="text-indigo-400 font-bold text-[10px] uppercase tracking-widest">{rec.company}</p>
                                    </div>
                                    <span className="text-[10px] font-black bg-emerald-500/10 text-emerald-500 px-3 py-1 rounded-full uppercase tracking-tighter">
                                        {rec.match_percentage.toFixed(0)}% Fit
                                    </span>
                                </div>
                                <button
                                    onClick={() => rec.apply_link && window.open(rec.apply_link, '_blank')}
                                    className="w-full py-4 bg-white/5 text-slate-400 rounded-2xl font-black uppercase tracking-widest text-[10px] border border-white/5 group-hover:bg-indigo-600 group-hover:text-white group-hover:border-indigo-500 transition-all"
                                >
                                    Initiate Protocol
                                </button>
                            </div>
                        ))}
                    </div>
                </div>
            )}
        </div>
    );
}
