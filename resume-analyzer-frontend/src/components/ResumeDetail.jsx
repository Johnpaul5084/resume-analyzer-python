import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { resumeAPI, jobAPI } from '../api';
import { PieChart, Pie, Cell, ResponsiveContainer, Legend, Tooltip } from 'recharts';
import { FileText, TrendingUp, AlertCircle, Briefcase, ArrowLeft } from 'lucide-react';
import CareerGuru from './CareerGuru';

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
        { name: 'Keywords', value: resume.score_breakdown.keywords_match || 0, color: '#3b82f6' },
        { name: 'Grammar', value: resume.score_breakdown.grammar_score || 0, color: '#10b981' },
        { name: 'Relevance', value: resume.score_breakdown.relevance_score || 0, color: '#f59e0b' },
        { name: 'Structure', value: resume.score_breakdown.structure_score || 0, color: '#8b5cf6' },
    ] : [];

    const getScoreColor = (score) => {
        if (score >= 80) return 'text-green-600';
        if (score >= 60) return 'text-yellow-600';
        return 'text-red-600';
    };

    return (
        <div className="min-h-screen p-8">
            <div className="max-w-7xl mx-auto">
                <button onClick={() => navigate('/dashboard')} className="btn-secondary mb-6 flex items-center gap-2">
                    <ArrowLeft size={18} />
                    Back to Dashboard
                </button>

                {/* Header */}
                <div className="card mb-8">
                    <div className="flex items-start justify-between">
                        <div className="flex items-center gap-4">
                            <div className="bg-blue-100 p-4 rounded-lg">
                                <FileText className="text-blue-600" size={32} />
                            </div>
                            <div>
                                <h1 className="text-3xl font-bold text-gray-800">{resume.title}</h1>
                                <p className="text-gray-600">Uploaded on {new Date(resume.created_at).toLocaleDateString()}</p>
                            </div>
                        </div>
                        <div className="text-right">
                            <p className="text-sm text-gray-600 mb-2">Overall ATS Score</p>
                            <div className={`text-5xl font-bold ${getScoreColor(resume.ats_score)}`}>
                                {resume.ats_score?.toFixed(1)}%
                            </div>
                        </div>
                    </div>
                </div>

                <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
                    {/* Score Breakdown */}
                    <div className="card">
                        <h2 className="text-2xl font-bold text-gray-800 mb-6">Score Breakdown</h2>
                        {scoreData.length > 0 ? (
                            <ResponsiveContainer width="100%" height={300}>
                                <PieChart>
                                    <Pie
                                        data={scoreData}
                                        cx="50%"
                                        cy="50%"
                                        labelLine={false}
                                        label={({ name, value }) => `${name}: ${value.toFixed(1)}%`}
                                        outerRadius={80}
                                        fill="#8884d8"
                                        dataKey="value"
                                    >
                                        {scoreData.map((entry, index) => (
                                            <Cell key={`cell-${index}`} fill={entry.color} />
                                        ))}
                                    </Pie>
                                    <Tooltip />
                                </PieChart>
                            </ResponsiveContainer>
                        ) : (
                            <p className="text-gray-500">No breakdown data available</p>
                        )}

                        <div className="mt-6 space-y-3">
                            {scoreData.map((item) => (
                                <div key={item.name} className="flex items-center justify-between">
                                    <div className="flex items-center gap-2">
                                        <div className="w-4 h-4 rounded" style={{ backgroundColor: item.color }}></div>
                                        <span className="font-medium text-gray-700">{item.name}</span>
                                    </div>
                                    <span className="font-bold" style={{ color: item.color }}>
                                        {item.value.toFixed(1)}%
                                    </span>
                                </div>
                            ))}
                        </div>
                    </div>

                    {/* Missing Keywords */}
                    <div className="card">
                        <h2 className="text-2xl font-bold text-gray-800 mb-6">Missing Keywords</h2>
                        {resume.missing_keywords && resume.missing_keywords.length > 0 ? (
                            <div className="flex flex-wrap gap-2">
                                {resume.missing_keywords.slice(0, 15).map((keyword, idx) => (
                                    <span
                                        key={idx}
                                        className="px-3 py-1 bg-red-100 text-red-700 rounded-full text-sm font-medium"
                                    >
                                        {keyword}
                                    </span>
                                ))}
                            </div>
                        ) : (
                            <p className="text-gray-500">No missing keywords detected</p>
                        )}

                        <div className="mt-6 p-4 bg-blue-50 rounded-lg">
                            <p className="text-sm text-blue-800">
                                💡 <strong>Tip:</strong> Add these keywords naturally to your resume to improve your ATS score
                            </p>
                        </div>
                    </div>
                </div>

                {/* AI Insights Section */}
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mt-8">
                    {/* Job Prediction */}
                    <div className="card bg-gradient-to-br from-indigo-50 to-purple-50 border-indigo-100">
                        <h2 className="text-2xl font-bold text-indigo-900 mb-4 flex items-center gap-2">
                            <TrendingUp className="text-indigo-600" />
                            Predicted Job Role
                        </h2>

                        <div className="mb-6">
                            <p className="text-gray-600 mb-1">Based on your skills, you seem best fit for:</p>
                            <div className="text-3xl font-bold text-indigo-700">
                                {resume.predicted_role || "General Role"}
                            </div>
                        </div>

                        <h3 className="font-semibold text-indigo-800 mb-3">Matching MNC Job Openings (Mock):</h3>
                        <div className="space-y-3">
                            {resume.matching_jobs && resume.matching_jobs.map((job, idx) => (
                                <div key={idx} className="bg-white p-3 rounded-lg shadow-sm border border-indigo-100 hover:border-indigo-300 transition-colors">
                                    <div className="flex justify-between items-start">
                                        <div>
                                            <h4 className="font-bold text-gray-800">{job.role}</h4>
                                            <p className="text-sm text-indigo-600 font-medium">{job.company}</p>
                                        </div>
                                        <span className="text-xs px-2 py-1 bg-green-100 text-green-700 rounded-full font-bold">
                                            {job.confidence ? job.confidence.toFixed(0) : 0}% Match
                                        </span>
                                    </div>
                                    <div className="flex justify-between mt-2 text-xs text-gray-500">
                                        <span>📍 {job.location || "Remote"}</span>
                                        <span>💰 {job.salary || "$100k"}</span>
                                        <span>🕒 {job.posted || "Just now"}</span>
                                    </div>
                                </div>
                            ))}
                            {(!resume.matching_jobs || resume.matching_jobs.length === 0) && (
                                <p className="text-gray-500 italic">No job predictions available.</p>
                            )}
                        </div>
                    </div>

                    {/* AI Rewrite */}
                    <div className="card border-green-100 bg-gradient-to-br from-green-50 to-emerald-50">
                        <div className="flex justify-between items-center mb-4">
                            <h2 className="text-2xl font-bold text-green-900 flex items-center gap-2">
                                <Briefcase className="text-green-600" />
                                MNC-Ready Optimized Version
                            </h2>
                            <button
                                onClick={() => {
                                    const element = document.createElement("a");
                                    const file = new Blob([resume.ai_rewritten_content], { type: 'text/plain' });
                                    element.href = URL.createObjectURL(file);
                                    element.download = "optimized_resume.txt";
                                    document.body.appendChild(element);
                                    element.click();
                                    document.body.removeChild(element);
                                }}
                                className="text-sm bg-green-100 text-green-700 px-3 py-1 rounded-md hover:bg-green-200 transition-colors font-medium border border-green-200"
                                disabled={!resume.ai_rewritten_content}
                            >
                                Download
                            </button>
                        </div>

                        <div className="bg-white p-4 rounded-lg shadow-inner h-96 overflow-y-auto border border-green-200">
                            {resume.ai_rewritten_content ? (
                                <div className="prose prose-sm max-w-none text-gray-700 whitespace-pre-wrap">
                                    {resume.ai_rewritten_content}
                                </div>
                            ) : (
                                <div className="text-center py-10 text-gray-400">
                                    AI is generating your optimized resume... (or failed to generate)
                                </div>
                            )}
                        </div>
                        <p className="mt-2 text-xs text-green-700 text-center">
                            *Auto-generated by AI based on MNC standards for {resume.predicted_role}
                        </p>
                    </div>
                </div>

                {/* Job Recommendations */}
                {recommendations.length > 0 && (
                    <div className="card mt-8">
                        <h2 className="text-2xl font-bold text-gray-800 mb-6 flex items-center gap-2">
                            <Briefcase className="text-blue-600" />
                            Job Recommendations
                        </h2>
                        <div className="space-y-4">
                            {recommendations.map((rec, idx) => (
                                <div key={idx} className="p-4 border border-gray-200 rounded-lg hover:border-blue-500 hover:shadow-md transition-all bg-white">
                                    <div className="flex justify-between items-start mb-3">
                                        <div className="flex items-center gap-3">
                                            {rec.logo && (
                                                <img src={rec.logo} alt={rec.company} className="w-12 h-12 object-contain rounded bg-gray-50 p-1" />
                                            )}
                                            <div>
                                                <h3 className="text-lg font-bold text-gray-800">{rec.title}</h3>
                                                <p className="text-blue-600 font-semibold">{rec.company}</p>
                                            </div>
                                        </div>
                                        <div className="text-right">
                                            <span className={`inline-block px-3 py-1 rounded-full text-sm font-bold ${rec.match_percentage >= 80 ? 'bg-green-100 text-green-700' :
                                                rec.match_percentage >= 50 ? 'bg-yellow-100 text-yellow-700' : 'bg-red-100 text-red-700'
                                                }`}>
                                                {rec.match_percentage.toFixed(0)}% Match
                                            </span>
                                        </div>
                                    </div>

                                    <div className="flex flex-wrap gap-4 text-sm text-gray-600 mb-4">
                                        <div className="flex items-center gap-1">
                                            <span>📍 {rec.location || 'Remote'}</span>
                                        </div>
                                        <div className="flex items-center gap-1">
                                            <span>💰 {rec.salary_range || 'Competitive'}</span>
                                        </div>
                                        <div className="flex items-center gap-1">
                                            <span>📅 {rec.posted_date || 'Recently'}</span>
                                        </div>
                                    </div>

                                    {rec.missing_skills && rec.missing_skills.length > 0 && (
                                        <div className="bg-red-50 p-3 rounded-md mb-4">
                                            <p className="text-xs font-bold text-red-700 uppercase tracking-wide mb-2">Missing Skills:</p>
                                            <div className="flex flex-wrap gap-2">
                                                {rec.missing_skills.map((skill, i) => (
                                                    <span key={i} className="text-xs px-2 py-1 bg-white border border-red-200 text-red-600 rounded">
                                                        {skill}
                                                    </span>
                                                ))}
                                            </div>
                                        </div>
                                    )}

                                    <button
                                        onClick={() => {
                                            if (rec.apply_link) {
                                                window.open(rec.apply_link, '_blank');
                                            } else {
                                                alert(`Application simulated for ${rec.title} at ${rec.company}`);
                                            }
                                        }}
                                        className="w-full py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 font-medium transition-colors"
                                    >
                                        Apply Now
                                    </button>
                                </div>
                            ))}
                        </div>
                    </div>
                )}
            </div>
            {/* Phase 3 & 4: AI Career Guru & Roadmap */}
            <CareerGuru resumeId={id} />
        </div>
    );
}
