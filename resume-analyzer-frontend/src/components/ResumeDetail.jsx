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
    const [recsLoading, setRecsLoading] = useState(false);

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
        } else if (resume && resume.predicted_role !== "Analyzing..." && recommendations.length === 0) {
            // Once analysis is done, if we haven't fetched real recs yet, do it now
            fetchRecommendations();
        }
        return () => clearInterval(interval);
    }, [resume, recommendations.length]);

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
        setRecsLoading(true);
        try {
            const response = await jobAPI.getRecommendations(id);
            setRecommendations(response.data);
        } catch (err) {
            console.error('Error fetching recommendations:', err);
        } finally {
            setRecsLoading(false);
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
            <div className="space-y-10">
                <div className="flex items-center gap-6">
                    <h2 className="text-3xl font-black tracking-tighter text-white">Market Opportunities</h2>
                    <div className="h-px flex-1 bg-white/5"></div>
                    <span className="text-[9px] font-black text-indigo-400 uppercase tracking-widest px-3 py-1 bg-indigo-500/10 rounded-full border border-indigo-500/20">
                        {resume.predicted_role || 'All Roles'}
                    </span>
                </div>

                {recommendations.length > 0 ? (
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
                        {recommendations.map((rec, idx) => {
                            // Extract portal links from improvement_suggestions
                            const linkedinLink = rec.improvement_suggestions?.find(s => s.includes('linkedin'))?.split('LinkedIn: ')[1]
                                || rec.apply_link;
                            const indeedLink = rec.improvement_suggestions?.find(s => s.includes('indeed'))?.split('Indeed: ')[1];
                            const naukriLink = rec.improvement_suggestions?.find(s => s.includes('naukri'))?.split('Naukri: ')[1];

                            return (
                                <div key={idx} className="glass-card p-8 hover:border-indigo-500/50 group transition-all duration-300 flex flex-col gap-5">
                                    {/* Header */}
                                    <div className="flex justify-between items-start">
                                        <div className="flex-1 min-w-0">
                                            <h3 className="font-black text-white text-base leading-tight mb-1 truncate">{rec.title}</h3>
                                            <p className="text-indigo-400 font-bold text-[10px] uppercase tracking-widest">{rec.company}</p>
                                        </div>
                                        <span className="ml-3 shrink-0 text-[10px] font-black bg-emerald-500/10 text-emerald-400 px-3 py-1 rounded-full uppercase tracking-tighter border border-emerald-500/20">
                                            {rec.match_percentage?.toFixed(0)}% Fit
                                        </span>
                                    </div>

                                    {/* Meta */}
                                    <div className="flex flex-wrap gap-2">
                                        {rec.location && (
                                            <span className="text-[9px] font-bold text-slate-400 bg-white/5 px-3 py-1 rounded-full border border-white/5">
                                                📍 {rec.location}
                                            </span>
                                        )}
                                        {rec.salary_range && rec.salary_range !== 'Competitive' && (
                                            <span className="text-[9px] font-bold text-emerald-400 bg-emerald-500/5 px-3 py-1 rounded-full border border-emerald-500/10">
                                                💰 {rec.salary_range}
                                            </span>
                                        )}
                                        {rec.posted_date && (
                                            <span className="text-[9px] font-bold text-slate-500 bg-white/5 px-3 py-1 rounded-full border border-white/5">
                                                🕐 {rec.posted_date}
                                            </span>
                                        )}
                                    </div>

                                    {/* Apply Buttons */}
                                    <div className="flex flex-col gap-2 mt-auto">
                                        {linkedinLink && (
                                            <button
                                                onClick={() => window.open(linkedinLink, '_blank')}
                                                className="w-full py-3 bg-blue-600/10 border border-blue-500/20 text-blue-400 hover:bg-blue-600 hover:text-white hover:border-blue-500 rounded-xl font-black uppercase tracking-widest text-[9px] transition-all"
                                            >
                                                🔗 Apply on LinkedIn
                                            </button>
                                        )}
                                        <div className="grid grid-cols-2 gap-2">
                                            {indeedLink && (
                                                <button
                                                    onClick={() => window.open(indeedLink, '_blank')}
                                                    className="py-2 bg-white/5 border border-white/5 text-slate-400 hover:bg-indigo-600/30 hover:text-white rounded-xl font-black uppercase tracking-widest text-[9px] transition-all"
                                                >
                                                    Indeed
                                                </button>
                                            )}
                                            {naukriLink && (
                                                <button
                                                    onClick={() => window.open(naukriLink, '_blank')}
                                                    className="py-2 bg-white/5 border border-white/5 text-slate-400 hover:bg-indigo-600/30 hover:text-white rounded-xl font-black uppercase tracking-widest text-[9px] transition-all"
                                                >
                                                    Naukri
                                                </button>
                                            )}
                                        </div>
                                    </div>
                                </div>
                            );
                        })}
                    </div>
                ) : recsLoading ? (
                    <div className="glass-card p-12 text-center text-slate-500 italic text-sm">
                        Synchronizing with live markets for <span className="text-indigo-400 font-bold">{resume.predicted_role}</span>…
                    </div>
                ) : (
                    <div className="glass-card p-12 text-center text-slate-500 italic text-sm">
                        No specific live opportunities found for <span className="text-white font-bold">{resume.predicted_role}</span>. <br />
                        Try adjusting your alignment context.
                    </div>
                )}
            </div>

        </div>
    );
}
