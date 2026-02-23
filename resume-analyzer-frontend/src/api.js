import axios from 'axios';

// API Configuration
// In production (Vercel), VITE_API_URL should be set to Railway backend URL
// Example: https://your-backend.railway.app
const getApiBaseUrl = () => {
    let envUrl = import.meta.env.VITE_API_URL;
    if (envUrl) {
        // Remove trailing slash if present
        envUrl = envUrl.replace(/\/$/, "");

        // Ensure the URL starts with https:// if it's just a domain
        if (!envUrl.startsWith('http')) {
            envUrl = `https://${envUrl}`;
        }

        // Append /api/v1 if not already present
        const baseUrl = envUrl.endsWith('/api/v1') ? envUrl : `${envUrl}/api/v1`;
        console.log("Using API Base URL:", baseUrl);
        return baseUrl;
    }
    // Default to localhost for development
    console.log("Using local API (VITE_API_URL not set)");
    return 'http://127.0.0.1:8000/api/v1';
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

// Career Guru API
export const careerGuruAPI = {
    chat: (question, resumeId = null) => api.post('/career-guru/chat', { question, resume_id: resumeId }),
    getRoadmap: (targetRole, resumeId) => api.post('/career-guru/roadmap', { target_role: targetRole, resume_id: resumeId }),
};

// Career Intelligence API
export const careerIntelAPI = {
    predict: (profile) => api.post('/career-intel/predict-career', profile),
    getRoadmap: (targetRole, months = 6) => api.post('/career-intel/generate-roadmap', { target_role: targetRole, timeline_months: months }),
    getStrategy: (tier) => api.get(`/career-intel/resume-strategy/${tier}`),
};

export default api;
