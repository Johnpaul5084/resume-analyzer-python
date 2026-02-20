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
        <div className="min-h-screen flex items-center justify-center p-4">
            <div className="card max-w-md w-full animate-fade-in">
                <div className="text-center mb-8">
                    <h1 className="text-4xl font-bold bg-gradient-to-r from-blue-600 to-indigo-600 bg-clip-text text-transparent mb-2">
                        Resume Analyzer AI
                    </h1>
                    <p className="text-gray-600">Optimize your resume with AI-powered insights</p>
                </div>

                <div className="flex gap-2 mb-6">
                    <button
                        onClick={() => setIsLogin(true)}
                        className={`flex-1 py-2 rounded-lg font-semibold transition-all ${isLogin ? 'bg-blue-600 text-white' : 'bg-gray-100 text-gray-600'
                            }`}
                    >
                        <LogIn className="inline mr-2" size={18} />
                        Login
                    </button>
                    <button
                        onClick={() => setIsLogin(false)}
                        className={`flex-1 py-2 rounded-lg font-semibold transition-all ${!isLogin ? 'bg-blue-600 text-white' : 'bg-gray-100 text-gray-600'
                            }`}
                    >
                        <UserPlus className="inline mr-2" size={18} />
                        Sign Up
                    </button>
                </div>

                <form onSubmit={handleSubmit} className="space-y-4">
                    {!isLogin && (
                        <div>
                            <label className="block text-sm font-medium text-gray-700 mb-2">Full Name</label>
                            <input
                                type="text"
                                className="input-field"
                                value={formData.full_name}
                                onChange={(e) => setFormData({ ...formData, full_name: e.target.value })}
                                required={!isLogin}
                            />
                        </div>
                    )}

                    <div>
                        <label className="block text-sm font-medium text-gray-700 mb-2">Email</label>
                        <input
                            type="email"
                            className="input-field"
                            value={formData.email}
                            onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                            required
                        />
                    </div>

                    <div>
                        <label className="block text-sm font-medium text-gray-700 mb-2">Password</label>
                        <input
                            type="password"
                            className="input-field"
                            value={formData.password}
                            onChange={(e) => setFormData({ ...formData, password: e.target.value })}
                            required
                        />
                    </div>

                    {error && (
                        <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg">
                            {error}
                        </div>
                    )}

                    <button type="submit" className="btn-primary w-full" disabled={loading}>
                        {loading ? 'Processing...' : isLogin ? 'Login' : 'Create Account'}
                    </button>
                </form>
            </div>
        </div>
    );
}
