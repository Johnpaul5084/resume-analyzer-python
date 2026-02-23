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
        <div className="min-h-screen p-8">
            <div className="max-w-7xl mx-auto">
                {/* Header */}
                <div className="flex justify-between items-center mb-8">
                    <div>
                        <h1 className="text-4xl font-bold text-gray-800 mb-2">IRIS: Resume Intelligence</h1>
                        <p className="text-gray-600">Advanced AI-Powered Role Fit & Semantic Analysis Engine</p>
                    </div>
                    <button onClick={handleLogout} className="btn-secondary flex items-center gap-2">
                        <LogOut size={18} />
                        Logout
                    </button>
                </div>

                {/* Upload Card */}
                <div className="card mb-8 bg-gradient-to-r from-blue-600 to-indigo-600 text-white hover:shadow-2xl cursor-pointer"
                    onClick={() => navigate('/upload')}>
                    <div className="flex items-center gap-4">
                        <div className="bg-white/20 p-4 rounded-lg">
                            <Upload size={32} />
                        </div>
                        <div>
                            <h2 className="text-2xl font-bold mb-1">Upload New Resume</h2>
                            <p className="text-blue-100">Get instant ATS score and AI-powered feedback</p>
                        </div>
                    </div>
                </div>

                {/* Resumes Grid */}
                {loading ? (
                    <div className="text-center py-12">
                        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
                        <p className="text-gray-600 mt-4">Loading resumes...</p>
                    </div>
                ) : resumes.length === 0 ? (
                    <div className="card text-center py-12">
                        <FileText size={48} className="mx-auto text-gray-400 mb-4" />
                        <h3 className="text-xl font-semibold text-gray-700 mb-2">No resumes yet</h3>
                        <p className="text-gray-600">Upload your first resume to get started!</p>
                    </div>
                ) : (
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                        {resumes.map((resume) => (
                            <div
                                key={resume.id}
                                className="card cursor-pointer hover:scale-105 transition-transform"
                                onClick={() => navigate(`/resume/${resume.id}`)}
                            >
                                <div className="flex items-start justify-between mb-4">
                                    <div className="flex items-center gap-3">
                                        <div className="bg-blue-100 p-3 rounded-lg">
                                            <FileText className="text-blue-600" size={24} />
                                        </div>
                                        <div>
                                            <h3 className="font-semibold text-gray-800">{resume.title}</h3>
                                            <p className="text-sm text-gray-500">{resume.file_type?.toUpperCase()}</p>
                                        </div>
                                    </div>
                                </div>

                                <div className="flex items-center justify-between">
                                    <div>
                                        <p className="text-sm text-gray-600 mb-1">ATS Score</p>
                                        <div className="flex items-center gap-2">
                                            <span className={`score-badge ${getScoreColor(resume.ats_score)}`}>
                                                {resume.ats_score?.toFixed(1) || 0}%
                                            </span>
                                            <TrendingUp size={16} className="text-green-600" />
                                        </div>
                                    </div>
                                    <div className="text-right">
                                        <p className="text-xs text-gray-500">
                                            {new Date(resume.created_at).toLocaleDateString()}
                                        </p>
                                    </div>
                                </div>
                            </div>
                        ))}
                    </div>
                )}
            </div>
        </div>
    );
}
