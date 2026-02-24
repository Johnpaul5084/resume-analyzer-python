import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { resumeAPI } from '../api';
import { Upload, FileText, TrendingUp, LogOut } from 'lucide-react';

export default function Dashboard() {
    const [resumes, setResumes] = useState([]);
    const [loading, setLoading] = useState(true);
    const navigate = useNavigate();

    useEffect(() => {
        fetchResumes();
    }, []);

    const fetchResumes = async () => {
        try {
            const response = await resumeAPI.getAll();
            setResumes(response.data);
        } catch (err) {
            console.error('Error fetching resumes:', err);
            if (err.response?.status === 401) {
                navigate('/');
            }
        } finally {
            setLoading(false);
        }
    };

    const handleLogout = () => {
        localStorage.removeItem('access_token');
        navigate('/');
    };

    const getScoreColor = (score) => {
        if (score >= 80) return 'bg-green-100 text-green-800';
        if (score >= 60) return 'bg-yellow-100 text-yellow-800';
        return 'bg-red-100 text-red-800';
    };

    return (
        <div className="min-h-screen p-8 bg-slate-950 text-slate-100">
            <div className="max-w-7xl mx-auto">
                {/* Header */}
                <div className="flex justify-between items-center mb-12">
                    <div>
                        <h1 className="text-5xl font-black bg-gradient-to-r from-white via-indigo-200 to-slate-500 bg-clip-text text-transparent mb-2">
                            AI Intelligence Suite
                        </h1>
                        <div className="flex items-center gap-3">
                            <span className="h-1 w-12 bg-indigo-500 rounded-full"></span>
                            <p className="text-slate-400 font-medium tracking-widest uppercase text-xs">Command Center</p>
                        </div>
                    </div>
                    <button onClick={handleLogout} className="btn-secondary group flex items-center gap-2 px-4 py-2 text-sm">
                        <LogOut size={16} className="group-hover:translate-x-1 transition-transform" />
                        Disconnect
                    </button>
                </div>

                <div className="space-y-12">
                    {/* Header / Intro */}
                    <div className="relative">
                        <div className="absolute -left-12 top-1/2 -translate-y-1/2 w-1 bg-indigo-600 h-16 rounded-full"></div>
                        <h1 className="text-6xl font-black bg-gradient-to-r from-white via-indigo-200 to-slate-500 bg-clip-text text-transparent tracking-tighter mb-4">
                            Command Center
                        </h1>
                        <p className="text-slate-400 font-medium tracking-wide max-w-2xl px-1 uppercase text-[10px] letter-spacing-[0.2em]">
                            Synchronized Resume Intelligence & Neural Alignment Matrix
                        </p>
                    </div>

                    {/* Upload Action */}
                    <div className="glass-card p-1 border border-white/5 overflow-hidden cursor-pointer group hover:scale-[1.005] transition-all duration-500"
                        onClick={() => navigate('/upload')}>
                        <div className="bg-gradient-to-r from-indigo-600/10 via-blue-600/10 to-transparent p-10 rounded-2xl flex items-center justify-between">
                            <div className="flex items-center gap-8">
                                <div className="bg-indigo-600 p-6 rounded-2xl shadow-[0_0_30px_rgba(79,70,229,0.3)] group-hover:rotate-6 transition-transform">
                                    <Upload size={36} className="text-white" />
                                </div>
                                <div>
                                    <h2 className="text-3xl font-black text-white mb-2">Initialize Profile Analysis</h2>
                                    <p className="text-slate-400 text-sm font-medium tracking-wide">Ready for deep semantic scanning and role alignment.</p>
                                </div>
                            </div>
                        </div>
                    </div>

                    {/* Resume Feed */}
                    <div className="space-y-8">
                        <div className="flex items-center gap-4">
                            <h2 className="text-xs font-black uppercase tracking-[0.3em] text-slate-500">Neural History Feed</h2>
                            <div className="h-px flex-1 bg-white/5 font-bold tracking-widest text-[10px] text-slate-800">---------------------------------</div>
                        </div>

                        {loading ? (
                            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
                                {[1, 2, 3].map(i => (
                                    <div key={i} className="glass-card h-64 animate-pulse-slow"></div>
                                ))}
                            </div>
                        ) : resumes.length > 0 ? (
                            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
                                {resumes.map((resume) => (
                                    <div
                                        key={resume.id}
                                        className="glass-card p-8 cursor-pointer group hover:border-indigo-500/50 transition-all duration-500 flex flex-col h-full bg-white/5 border border-white/5 backdrop-blur-sm"
                                        onClick={() => navigate(`/resume/${resume.id}`)}
                                    >
                                        <div className="flex justify-between items-start mb-10">
                                            <div className="bg-white/5 p-4 rounded-2xl border border-white/5 group-hover:bg-indigo-600/20 group-hover:border-indigo-500/30 transition-all">
                                                <FileText className="text-slate-400 group-hover:text-indigo-400" size={28} />
                                            </div>
                                            {resume.ats_score && (
                                                <div className="text-right">
                                                    <p className="text-[10px] font-black text-slate-500 uppercase tracking-tighter mb-1">ATS Intel</p>
                                                    <span className={`text-2xl font-black ${resume.ats_score > 70 ? 'text-emerald-400' : 'text-amber-400'}`}>
                                                        {resume.ats_score.toFixed(0)}%
                                                    </span>
                                                </div>
                                            )}
                                        </div>

                                        <h3 className="text-xl font-black text-white mb-3 group-hover:text-indigo-400 transition-colors line-clamp-1">
                                            {resume.title}
                                        </h3>
                                        <div className="mt-auto pt-6 border-t border-white/5 flex items-center justify-between">
                                            <span className="text-[10px] font-bold text-slate-500 uppercase tracking-widest">
                                                v1.{new Date(resume.created_at).getDate()}
                                            </span>
                                            <span className="text-xs font-black text-indigo-400 opacity-0 group-hover:opacity-100 transition-opacity">
                                                EXECUTE ANALYZE →
                                            </span>
                                        </div>
                                    </div>
                                ))}
                            </div>
                        ) : (
                            <div className="glass-card p-20 text-center">
                                <div className="bg-white/5 w-20 h-20 rounded-3xl flex items-center justify-center mx-auto mb-6 border border-white/5 text-slate-600">
                                    <FileText size={40} />
                                </div>
                                <h3 className="text-2xl font-black text-white mb-2 tracking-tight">No Active Profiles Detected</h3>
                                <p className="text-slate-500 text-sm max-w-sm mx-auto font-medium">Upload your first resume to initialize the neural career intelligence suite.</p>
                                <button onClick={() => navigate('/upload')} className="btn-primary mt-8 px-10 py-5 text-xs tracking-widest">
                                    INITIATE SYSTEM
                                </button>
                            </div>
                        )}
                    </div>
                </div>
            </div>
        </div>
    );
}
