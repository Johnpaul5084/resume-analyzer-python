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
        <div className="min-h-screen p-8">
            <div className="max-w-3xl mx-auto">
                <button
                    onClick={() => navigate('/dashboard')}
                    className="btn-secondary mb-6"
                >
                    ← Back to Dashboard
                </button>

                <div className="card animate-slide-up">
                    <h1 className="text-3xl font-bold text-gray-800 mb-2">Upload Resume</h1>
                    <p className="text-gray-600 mb-6">Upload your resume for AI-powered ATS analysis</p>

                    <form onSubmit={handleSubmit} className="space-y-6">
                        {/* File Upload */}
                        <div>
                            <label className="block text-sm font-medium text-gray-700 mb-2">
                                Resume File (PDF, DOCX, TXT, JPG, PNG)
                            </label>
                            <div className="border-2 border-dashed border-gray-300 rounded-lg p-8 text-center hover:border-blue-500 transition-colors">
                                <input
                                    type="file"
                                    accept=".pdf,.docx,.doc,.txt,.jpg,.jpeg,.png"
                                    onChange={handleFileChange}
                                    className="hidden"
                                    id="file-upload"
                                />
                                <label htmlFor="file-upload" className="cursor-pointer">
                                    {file ? (
                                        <div className="flex items-center justify-center gap-3">
                                            <CheckCircle className="text-green-600" size={32} />
                                            <div>
                                                <p className="font-semibold text-gray-800">{file.name}</p>
                                                <p className="text-sm text-gray-500">{(file.size / 1024).toFixed(2)} KB</p>
                                            </div>
                                        </div>
                                    ) : (
                                        <div>
                                            <Upload className="mx-auto text-gray-400 mb-3" size={48} />
                                            <p className="text-gray-600 font-medium">Click to upload or drag and drop</p>
                                            <p className="text-sm text-gray-500 mt-1">PDF, DOCX, TXT, or Image (Max 16MB)</p>
                                        </div>
                                    )}
                                </label>
                            </div>
                        </div>

                        {/* Title */}
                        <div>
                            <label className="block text-sm font-medium text-gray-700 mb-2">Resume Title</label>
                            <input
                                type="text"
                                className="input-field"
                                value={title}
                                onChange={(e) => setTitle(e.target.value)}
                                placeholder="e.g., Software Engineer Resume - 2024"
                                required
                            />
                        </div>

                        {/* Job Description (Optional) */}
                        <div>
                            <label className="block text-sm font-medium text-gray-700 mb-2">
                                Target Job Description (Optional)
                            </label>
                            <textarea
                                className="input-field"
                                rows="6"
                                value={jobDescription}
                                onChange={(e) => setJobDescription(e.target.value)}
                                placeholder="Paste the job description here to get tailored analysis..."
                            />
                            <p className="text-sm text-gray-500 mt-2">
                                💡 Adding a job description improves keyword matching and relevance scoring
                            </p>
                        </div>

                        {error && (
                            <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg flex items-center gap-2">
                                <AlertCircle size={20} />
                                {error}
                            </div>
                        )}

                        <button
                            type="submit"
                            className="btn-primary w-full"
                            disabled={uploading}
                        >
                            {uploading ? (
                                <span className="flex items-center justify-center gap-2">
                                    <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white"></div>
                                    Analyzing Resume...
                                </span>
                            ) : (
                                'Upload & Analyze'
                            )}
                        </button>
                    </form>
                </div>
            </div>
        </div>
    );
}
