import axios from 'axios';

// API Configuration
// In production (Vercel), VITE_API_URL should be set to Railway backend URL
// Example: https://your-backend.railway.app
const getApiBaseUrl = () => {
    let envUrl = import.meta.env.VITE_API_URL;

    // If VITE_API_URL is set (Production)
    if (envUrl) {
        envUrl = envUrl.replace(/\/$/, "");
        if (!envUrl.startsWith('http')) {
            envUrl = `https://${envUrl}`;
        }
        return envUrl.endsWith('/api/v1') ? envUrl : `${envUrl}/api/v1`;
    }

    // Local Development: Use Vite Proxy
    // Vite config redirects /api to backend (http://localhost:8080)
    console.log("AI Resume Analyzer Frontend: Using Proxy connection.");
    return '/api/v1';
};

const api = axios.create({
    baseURL: getApiBaseUrl(),
    headers: {
        'Content-Type': 'application/json',
    },
});

// Add token to requests if available
api.interceptors.request.use((config) => {
    const token = localStorage.getItem('access_token');
    if (token) {
        config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
});

// AI System Security Interceptor
api.interceptors.response.use(
    (response) => response,
    (error) => {
        if (error.response && error.response.status === 429) {
            // Rate Limit Triggered
            alert("Security: Neural link throttled. Please wait a minute before sending more AI requests.");
        }
        return Promise.reject(error);
    }
);

// Auth API
export const authAPI = {
    login: (email, password) => {
        const params = new URLSearchParams();
        params.append('username', email);
        params.append('password', password);
        return api.post('/login/access-token', params, {
            headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
        });
    },
    signup: (data) => api.post('/signup', data),
    getCurrentUser: () => api.get('/users/me'),
};

// Resume API
export const resumeAPI = {
    upload: (formData) => api.post('/resumes/upload', formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
    }),
    getAll: () => api.get('/resumes/'),
    getById: (id) => api.get(`/resumes/${id}`),
};

// Job API
export const jobAPI = {
    matchJob: (resumeId, jobDescription) => api.post(`/jobs/match/${resumeId}`, jobDescription),
    getRecommendations: (resumeId) => api.get(`/jobs/recommendations/${resumeId}`),
};

// AI Mentor API (Unified)
export const mentorAPI = {
    chat: (question, resumeId = null) => api.post('/ai-mentor/chat', { question, resume_id: resumeId }),
    getInsight: (resumeText, skills) => api.post('/ai-mentor/insight', { resume_text: resumeText, skills: skills }),
    predict: (profile) => api.post('/ai-mentor/predict', profile),
    getStrategy: (tier) => api.get(`/ai-mentor/strategy/${tier}`),
};

// AI Rewrite API (Advanced Transformer)
export const rewriteAPI = {
    transform: (resumeText, jobDescription, mode = 'ATS') =>
        api.post('/ai-rewrite/transform', { resume_text: resumeText, job_description: jobDescription, mode }),
    enhanceGrammar: (text) =>
        api.post('/ai-rewrite/enhance-grammar', { text }),
};

export default api;
