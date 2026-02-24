import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { resumeAPI } from '../api';
import { Upload, FileText, AlertCircle, CheckCircle } from 'lucide-react';

export default function UploadResume() {
    const [file, setFile] = useState(null);
    const [title, setTitle] = useState('');
    const [jobDescription, setJobDescription] = useState('');
    const [uploading, setUploading] = useState(false);
    const [error, setError] = useState('');
    const navigate = useNavigate();

    const handleFileChange = (e) => {
        const selectedFile = e.target.files[0];
        if (selectedFile) {
            setFile(selectedFile);
            if (!title) {
                setTitle(selectedFile.name.replace(/\.[^/.]+$/, '')); // Remove extension
            }
        }
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        if (!file) {
            setError('Please select a file');
            return;
        }

        setUploading(true);
        setError('');

        const formData = new FormData();
        formData.append('file', file);
        formData.append('title', title);
        if (jobDescription) {
            formData.append('job_description', jobDescription);
        }

        try {
            const response = await resumeAPI.upload(formData);
            navigate(`/resume/${response.data.id}`);
        } catch (err) {
            setError(err.response?.data?.detail || 'Upload failed');
        } finally {
            setUploading(false);
        }
    };

    return (
        <div className="flex flex-col items-center justify-center py-10">
            <div className="w-full max-w-4xl space-y-12">
                {/* Header Header */}
                <div className="text-center space-y-4">
                    <h1 className="text-6xl font-black bg-gradient-to-r from-white via-indigo-200 to-slate-500 bg-clip-text text-transparent tracking-tighter">
                        Profile Injection
                    </h1>
                    <p className="text-slate-400 font-medium tracking-[0.3em] uppercase text-[10px]">
                        Neural Synthesis Queue • Level 1 Protocol
                    </p>
                </div>

                <div className="glass-card p-1 border border-white/5 relative overflow-hidden group">
                    <div className="bg-slate-900/40 p-12 lg:p-16 rounded-xl2">
                        <form onSubmit={handleSubmit} className="space-y-10">
                            {/* Drop Zone */}
                            <div className="space-y-4">
                                <label className="text-[10px] font-black text-indigo-400 uppercase tracking-widest px-1">Source Interface</label>
                                <div className={`border-2 border-dashed rounded-[40px] p-16 text-center transition-all duration-500 relative overflow-hidden ${file ? 'border-indigo-500/50 bg-indigo-500/10' : 'border-white/5 bg-white/5 hover:bg-white/10 hover:border-indigo-500/20'}`}>
                                    <input
                                        type="file"
                                        accept=".pdf,.docx,.doc,.txt,.jpg,.jpeg,.png"
                                        onChange={handleFileChange}
                                        className="hidden"
                                        id="file-upload"
                                    />
                                    <label htmlFor="file-upload" className="cursor-pointer block relative z-10">
                                        {file ? (
                                            <div className="flex flex-col items-center gap-6 animate-scale-in">
                                                <div className="bg-indigo-600 p-6 rounded-3xl shadow-[0_0_30px_rgba(79,70,229,0.4)]">
                                                    <CheckCircle className="text-white" size={40} />
                                                </div>
                                                <div className="space-y-1">
                                                    <p className="font-black text-white text-2xl tracking-tight">{file.name}</p>
                                                    <p className="text-[10px] text-slate-500 font-bold uppercase tracking-widest">
                                                        {(file.size / 1024).toFixed(0)} KB • Ready for Synchronization
                                                    </p>
                                                </div>
                                            </div>
                                        ) : (
                                            <div className="space-y-8">
                                                <div className="bg-white/5 w-24 h-24 rounded-3xl flex items-center justify-center mx-auto transition-all group-hover:scale-110 border border-white/5">
                                                    <Upload className="text-slate-500 group-hover:text-indigo-400" size={40} />
                                                </div>
                                                <div className="space-y-2">
                                                    <p className="text-white font-black text-xl tracking-tight">Select Professional Core</p>
                                                    <p className="text-slate-500 text-xs font-medium max-w-sm mx-auto uppercase tracking-tighter">
                                                        Drop PDF, DOCX or Image Artifacts
                                                    </p>
                                                </div>
                                            </div>
                                        )}
                                    </label>
                                </div>
                            </div>

                            {/* Inputs */}
                            <div className="grid grid-cols-1 md:grid-cols-2 gap-10">
                                <div className="space-y-4">
                                    <label className="text-[10px] font-black text-indigo-400 uppercase tracking-widest px-1">Identifier Label</label>
                                    <input
                                        type="text"
                                        className="w-full bg-black/40 border border-white/5 px-8 py-5 rounded-3xl text-sm font-medium focus:ring-2 focus:ring-indigo-600/20 transition-all text-white outline-none"
                                        value={title}
                                        onChange={(e) => setTitle(e.target.value)}
                                        placeholder="v1.0 - Core Engine Resume"
                                        required
                                    />
                                </div>
                                <div className="space-y-4">
                                    <label className="text-[10px] font-black text-indigo-400 uppercase tracking-widest px-1">Alignment Context (Optional)</label>
                                    <input
                                        type="text"
                                        className="w-full bg-black/40 border border-white/5 px-8 py-5 rounded-3xl text-sm font-medium focus:ring-2 focus:ring-indigo-600/20 transition-all text-white outline-none"
                                        value={jobDescription}
                                        onChange={(e) => setJobDescription(e.target.value)}
                                        placeholder="Target MNC / Role Context"
                                    />
                                </div>
                            </div>

                            {error && (
                                <div className="bg-rose-500/5 border border-rose-500/20 text-rose-400 px-6 py-5 rounded-2xl flex items-center gap-4 animate-shake">
                                    <AlertCircle size={20} className="shrink-0" />
                                    <p className="text-xs font-black uppercase tracking-widest leading-relaxed">{error}</p>
                                </div>
                            )}

                            <button
                                type="submit"
                                className="w-full py-6 bg-white text-black hover:bg-indigo-600 hover:text-white transition-all rounded-[32px] text-xs font-black uppercase tracking-[0.4em] shadow-2xl disabled:opacity-50"
                                disabled={uploading}
                            >
                                {uploading ? (
                                    <div className="flex items-center justify-center gap-4">
                                        <div className="w-5 h-5 border-4 border-slate-900 border-t-indigo-600 rounded-full animate-spin"></div>
                                        <span>Synchronizing...</span>
                                    </div>
                                ) : (
                                    'Commit to Synthesis'
                                )}
                            </button>
                        </form>
                    </div>
                </div>

                <div className="flex justify-center">
                    <button onClick={() => navigate('/dashboard')} className="text-[10px] font-black text-slate-600 hover:text-indigo-400 uppercase tracking-[0.4em] transition-all">
                        Abort Connection • Return to Hub
                    </button>
                </div>
            </div>
        </div>
    );
}
