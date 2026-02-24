import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { authAPI } from '../api';
import { LogIn, UserPlus } from 'lucide-react';

export default function Login() {
    const [isLogin, setIsLogin] = useState(true);
    const [formData, setFormData] = useState({
        email: '',
        password: '',
        full_name: '',
    });
    const [error, setError] = useState('');
    const [loading, setLoading] = useState(false);
    const navigate = useNavigate();

    const handleSubmit = async (e) => {
        e.preventDefault();
        setError('');
        setLoading(true);

        const email = formData.email.trim();
        const password = formData.password;
        const full_name = formData.full_name.trim();

        try {
            if (isLogin) {
                const response = await authAPI.login(email, password);
                localStorage.setItem('access_token', response.data.access_token);
                navigate('/dashboard');
            } else {
                await authAPI.signup({
                    email: email,
                    password: password,
                    full_name: full_name,
                });
                // Auto login after signup
                const loginResponse = await authAPI.login(email, password);
                localStorage.setItem('access_token', loginResponse.data.access_token);
                navigate('/dashboard');
            }
        } catch (err) {
            console.error('Error during signup/login:', err);
            if (err.response) {
                // Server responded with error
                setError(err.response?.data?.detail || JSON.stringify(err.response?.data) || 'Server error occurred');
            } else if (err.request) {
                // Request made but no response
                setError('Cannot connect to server. Please ensure the backend is running and the API URL is correct.');
            } else {
                // Something else happened
                setError(err.message || 'An error occurred');
            }
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="min-h-screen flex items-center justify-center p-6 bg-slate-950 relative overflow-hidden">
            {/* Background Ambient Effects */}
            <div className="absolute top-1/4 left-1/4 w-[500px] h-[500px] bg-indigo-600/10 rounded-full blur-[120px] animate-pulse-slow"></div>
            <div className="absolute bottom-1/4 right-1/4 w-[500px] h-[500px] bg-blue-600/5 rounded-full blur-[120px] animate-pulse-slow delay-1000"></div>

            <div className="w-full max-w-md relative z-10 transition-all duration-700">
                <div className="glass-card p-1 border border-white/5 relative group overflow-hidden">
                    <div className="bg-slate-900/60 backdrop-blur-3xl p-10 lg:p-12 rounded-[40px]">
                        {/* Header */}
                        <div className="text-center mb-12">
                            <h1 className="text-4xl font-black tracking-tighter bg-gradient-to-r from-white via-indigo-200 to-slate-500 bg-clip-text text-transparent mb-4">
                                AI RESUME ANALYZER
                            </h1>
                            <div className="inline-flex items-center gap-2 px-3 py-1 bg-white/5 border border-white/10 rounded-full">
                                <span className="w-1.5 h-1.5 bg-indigo-500 rounded-full animate-pulse"></span>
                                <span className="text-[10px] font-black text-slate-400 uppercase tracking-widest leading-none">Career Intelligence Suite v4.2</span>
                            </div>
                        </div>

                        {/* Switcher */}
                        <div className="grid grid-cols-2 p-1.5 bg-black/40 rounded-3xl mb-10 border border-white/5">
                            <button
                                onClick={() => setIsLogin(true)}
                                className={`py-4 rounded-2xl text-[10px] font-black uppercase tracking-widest transition-all duration-500 ${isLogin ? 'bg-white text-black shadow-[0_0_20px_rgba(255,255,255,0.1)]' : 'text-slate-500 hover:text-white'}`}
                            >
                                Access
                            </button>
                            <button
                                onClick={() => setIsLogin(false)}
                                className={`py-4 rounded-2xl text-[10px] font-black uppercase tracking-widest transition-all duration-500 ${!isLogin ? 'bg-white text-black shadow-[0_0_20px_rgba(255,255,255,0.1)]' : 'text-slate-500 hover:text-white'}`}
                            >
                                Initialize
                            </button>
                        </div>

                        {/* Form */}
                        <form onSubmit={handleSubmit} className="space-y-6">
                            {!isLogin && (
                                <div className="space-y-3">
                                    <label className="text-[10px] font-black text-slate-500 uppercase tracking-widest px-1">Full Signature</label>
                                    <input
                                        type="text"
                                        className="w-full bg-black/40 border border-white/5 px-6 py-4 rounded-2xl text-sm font-medium text-white focus:ring-1 focus:ring-indigo-600/30 transition-all outline-none"
                                        value={formData.full_name}
                                        onChange={(e) => setFormData({ ...formData, full_name: e.target.value })}
                                        placeholder="Identification Name"
                                        required={!isLogin}
                                    />
                                </div>
                            )}

                            <div className="space-y-3">
                                <label className="text-[10px] font-black text-slate-500 uppercase tracking-widest px-1">Neural Hub Email</label>
                                <input
                                    type="email"
                                    className="w-full bg-black/40 border border-white/5 px-6 py-4 rounded-2xl text-sm font-medium text-white focus:ring-1 focus:ring-indigo-600/30 transition-all outline-none"
                                    value={formData.email}
                                    onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                                    placeholder="name@nexus.com"
                                    required
                                />
                            </div>

                            <div className="space-y-3">
                                <label className="text-[10px] font-black text-slate-500 uppercase tracking-widest px-1">Encryption Key</label>
                                <input
                                    type="password"
                                    className="w-full bg-black/40 border border-white/5 px-6 py-4 rounded-2xl text-sm font-medium text-white focus:ring-1 focus:ring-indigo-600/30 transition-all outline-none"
                                    value={formData.password}
                                    onChange={(e) => setFormData({ ...formData, password: e.target.value })}
                                    placeholder="••••••••"
                                    required
                                />
                            </div>

                            {error && (
                                <div className="bg-rose-500/5 border border-rose-500/20 text-rose-400 p-4 rounded-2xl text-[10px] font-black uppercase tracking-widest animate-shake leading-relaxed">
                                    <AlertTriangle className="inline-block mr-2 mt-[-2px]" size={14} />
                                    {error}
                                </div>
                            )}

                            <button
                                type="submit"
                                className="w-full py-5 bg-indigo-600 hover:bg-indigo-500 text-white rounded-[32px] text-xs font-black uppercase tracking-[0.4em] shadow-[0_0_30px_rgba(79,70,229,0.2)] hover:shadow-[0_0_40px_rgba(79,70,229,0.3)] transition-all transform active:scale-[0.98] mt-4"
                                disabled={loading}
                            >
                                {loading ? (
                                    <div className="flex items-center justify-center gap-3">
                                        <div className="w-4 h-4 border-2 border-white/20 border-t-white rounded-full animate-spin"></div>
                                        <span>Synchronizing</span>
                                    </div>
                                ) : isLogin ? 'Establish Link' : 'Commit Neural Profile'}
                            </button>
                        </form>
                    </div>
                </div>

                {/* Footer Footer */}
                <div className="mt-12 text-center">
                    <p className="text-[10px] font-black text-slate-600 tracking-[0.5em] uppercase">
                        End-to-End Career Intelligence Encryption Active
                    </p>
                </div>
            </div>
        </div>
    );
}
