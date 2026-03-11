import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { authAPI, getApiBaseUrl } from '../api';
import { LogIn, UserPlus, AlertTriangle } from 'lucide-react';

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

    const [backendStatus, setBackendStatus] = useState('unknown');
    const [wakeAttempt, setWakeAttempt] = useState(0);

    const checkHealth = async () => {
        setBackendStatus('unknown');
        setWakeAttempt(0);

        const baseUrl = getApiBaseUrl();
        const isProduction = window.location.hostname !== 'localhost' && window.location.hostname !== '127.0.0.1';
        const isBaseUrlDefault = baseUrl === '/api/v1';

        if (isProduction && isBaseUrlDefault) {
            setBackendStatus('misconfigured');
            return;
        }

        // Derive the root URL from the API base URL for the /ping endpoint
        // e.g. "https://xyz.onrender.com/api/v1" -> "https://xyz.onrender.com"
        const rootUrl = baseUrl.replace(/\/api\/v1\/?$/, '');
        const pingUrl = `${rootUrl}/ping`;

        const MAX_RETRIES = 6;       // 6 retries × 15s = 90s max wait
        const RETRY_DELAY_MS = 15000; // 15 seconds between retries
        const PING_TIMEOUT_MS = 12000; // 12 second timeout per attempt

        for (let attempt = 1; attempt <= MAX_RETRIES; attempt++) {
            try {
                const controller = new AbortController();
                const timeoutId = setTimeout(() => controller.abort(), PING_TIMEOUT_MS);

                const response = await fetch(pingUrl, { signal: controller.signal });
                clearTimeout(timeoutId);

                if (response.ok) {
                    // Backend is alive — now do a full health check
                    setBackendStatus('online');
                    console.log(`AI System: Neural link established (attempt ${attempt})`);

                    // Optional: do a background deep health check (non-blocking)
                    try {
                        const deepResp = await fetch(`${baseUrl}/healthz`);
                        if (deepResp.ok) {
                            const data = await deepResp.json();
                            if (data.status === 'degraded') {
                                setBackendStatus('warming up');
                                // Re-check in 15s
                                setTimeout(async () => {
                                    try {
                                        const recheck = await fetch(`${baseUrl}/healthz`);
                                        if (recheck.ok) setBackendStatus('online');
                                    } catch { /* ignore */ }
                                }, 15000);
                            }
                        }
                    } catch { /* deep check failed, but ping succeeded — still online */ }

                    return; // Success — exit retry loop
                } else {
                    throw new Error(`HTTP ${response.status}`);
                }
            } catch (err) {
                const isTimeout = err.name === 'AbortError';
                console.warn(`AI System: Ping attempt ${attempt}/${MAX_RETRIES} failed: ${isTimeout ? 'Timeout' : err.message}`);

                if (attempt === 1) {
                    setBackendStatus('waking up');
                }
                setWakeAttempt(attempt);

                if (attempt < MAX_RETRIES) {
                    // Wait before retrying
                    await new Promise(resolve => setTimeout(resolve, RETRY_DELAY_MS));
                } else {
                    // All retries exhausted
                    setBackendStatus('offline (server sleeping)');
                    console.error('AI System: Backend did not respond after all retries.');
                }
            }
        }
    };

    React.useEffect(() => {
        checkHealth();
    }, []);

    const handleSubmit = async (e) => {
        e.preventDefault();
        setError('');
        setLoading(true);
        console.log('AI System: Initiating sync...', { isLogin, email: formData.email });

        const email = formData.email.trim();
        const password = formData.password;
        const full_name = formData.full_name.trim();

        try {
            if (isLogin) {
                console.log('AI System: Authenticating neural link...');
                const response = await authAPI.login(email, password);
                localStorage.setItem('access_token', response.data.access_token);
                console.log('AI System: Authentication successful.');
                navigate('/dashboard');
            } else {
                console.log('AI System: Committing new neural profile...');
                await authAPI.signup({
                    email: email,
                    password: password,
                    full_name: full_name,
                });
                console.log('AI System: Profile created. Establishing link...');
                // Auto login after signup
                const loginResponse = await authAPI.login(email, password);
                localStorage.setItem('access_token', loginResponse.data.access_token);
                console.log('AI System: Link established.');
                navigate('/dashboard');
            }
        } catch (err) {
            console.error('AI System Error:', err);
            const detail = err.response?.data?.detail;
            const errorMsg = typeof detail === 'string' ? detail :
                (Array.isArray(detail) ? detail[0]?.msg : null) ||
                JSON.stringify(err.response?.data) ||
                err.message || 'Unknown Neural Error';
            setError(errorMsg);
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
                                <span className={`w-1.5 h-1.5 rounded-full ${backendStatus === 'online' ? 'bg-emerald-500 animate-pulse' :
                                    backendStatus.startsWith('offline') ? 'bg-rose-500' :
                                        backendStatus === 'waking up' ? 'bg-amber-400 animate-bounce' :
                                            backendStatus === 'warming up' ? 'bg-sky-400 animate-pulse' :
                                                backendStatus === 'misconfigured' ? 'bg-amber-400 shadow-[0_0_10px_rgba(251,191,36,0.5)]' :
                                                    'bg-indigo-500 animate-ping'
                                    }`}></span>
                                <span className="text-[10px] font-black text-slate-400 uppercase tracking-widest leading-none">
                                    System Status: {
                                        backendStatus === 'unknown' ? 'INITIALIZING...' :
                                            backendStatus === 'waking up' ? `WAKING UP (${wakeAttempt}/6)...` :
                                                backendStatus === 'warming up' ? 'WARMING UP MODELS...' :
                                                    backendStatus.toUpperCase()
                                    }
                                    {backendStatus.startsWith('offline') && (
                                        <button
                                            onClick={(e) => { e.preventDefault(); checkHealth(); }}
                                            className="ml-3 text-indigo-400 hover:text-indigo-300 font-black underline underline-offset-4 transition-colors"
                                        >
                                            RECONNECT
                                        </button>
                                    )}
                                </span>
                            </div>
                        </div>

                        {backendStatus === 'misconfigured' && (
                            <div className="mb-8 p-4 bg-amber-500/10 border border-amber-500/20 rounded-2xl">
                                <p className="text-[10px] font-black text-amber-500 uppercase tracking-widest leading-relaxed">
                                    ⚠️ Connection Warning: VITE_API_URL not detected. Ensure it is set in Vercel to your Render backend URL.
                                </p>
                            </div>
                        )}

                        {/* Switcher */}
                        <div className="grid grid-cols-2 p-1.5 bg-black/40 rounded-3xl mb-10 border border-white/5">
                            <button
                                type="button"
                                onClick={() => setIsLogin(true)}
                                className={`py-4 rounded-2xl text-[10px] font-black uppercase tracking-widest transition-all duration-500 ${isLogin ? 'bg-white text-black shadow-[0_0_20px_rgba(255,255,255,0.1)]' : 'text-slate-500 hover:text-white'}`}
                            >
                                Access
                            </button>
                            <button
                                type="button"
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
