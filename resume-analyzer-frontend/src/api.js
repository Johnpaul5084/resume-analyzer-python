import axios from 'axios';

// API Configuration
// In production (Vercel), VITE_API_URL should be set to Railway backend URL
// Example: https://your-backend.railway.app
export const getApiBaseUrl = () => {
    let envUrl = import.meta.env.VITE_API_URL;

    // If VITE_API_URL is set (Production)
    if (envUrl) {
        envUrl = envUrl.replace(/\/$/, "");
        if (!envUrl.startsWith('http')) {
            envUrl = `https://${envUrl}`;
        }
        const fullUrl = envUrl.endsWith('/api/v1') ? envUrl : `${envUrl}/api/v1`;
        return fullUrl.replace(/\/$/, "");
    }

    // Local Development: Use Vite Proxy
    // Vite config redirects /api to backend (http://localhost:8080)
    console.log("AI Resume Analyzer Frontend: Using Proxy connection.");
    return '/api/v1';
};

const api = axios.create({
    baseURL: getApiBaseUrl(),
    timeout: 120000, // 120s timeout to handle cold starts (especially on Render Free Tier)
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

        // Check for credit exhaustion (any error where the message mentions "credit limit")
        if (error.response && error.response.data) {
            const errMsg = typeof error.response.data === 'string'
                ? error.response.data
                : JSON.stringify(error.response.data);

            if (errMsg.toLowerCase().includes('credit limit') ||
                errMsg.toLowerCase().includes('daily limit reached') ||
                errMsg.toLowerCase().includes('resets at midnight')) {
                // Dispatch a custom event so the CreditStatusBanner can react
                window.dispatchEvent(new CustomEvent('api-credits-exhausted', {
                    detail: {
                        message: errMsg,
                        timestamp: Date.now()
                    }
                }));
            }
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
    chat: (question, resumeId = null, chatHistory = null) => api.post('/ai-mentor/chat', { question, resume_id: resumeId, chat_history: chatHistory }),
    getInsight: (resumeText, skills, targetRole = null) =>
        api.post('/ai-mentor/insight', {
            resume_text: resumeText,
            skills: skills,
            target_role: targetRole
        }),
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

// 🏢 Company ATS Simulator API (UNIQUE)
export const companyAtsAPI = {
    scoreAll: (resumeText, targetRole = 'Software Engineer', companies = null) =>
        api.post('/ai-rewrite/company-ats', { resume_text: resumeText, target_role: targetRole, companies }),
    scoreSingle: (resumeText, companyId, targetRole = 'Software Engineer') =>
        api.post('/ai-rewrite/company-ats/single', { resume_text: resumeText, company_id: companyId, target_role: targetRole }),
    listCompanies: () =>
        api.get('/ai-rewrite/company-ats/companies'),
};

// 📝 Self-Contained Resume Builder (OUR OWN TECHNOLOGY — NO OVERLEAF)
export const resumeBuilderAPI = {
    build: (resumeText, templateId = 'classic', targetRole = 'Software Engineer') =>
        api.post('/ai-rewrite/build-resume', { resume_text: resumeText, template_id: templateId, target_role: targetRole }),
    getTemplates: () =>
        api.get('/ai-rewrite/templates'),
    exportLatex: (resumeText, templateId = 'classic', targetRole = 'Software Engineer') =>
        api.post('/ai-rewrite/latex', { resume_text: resumeText, template_id: templateId, target_role: targetRole }),
};

// 🎯 AI Interview Prep Engine (UNIQUE)
export const interviewPrepAPI = {
    generate: (resumeText, targetRole = 'Software Engineer') =>
        api.post('/ai-rewrite/interview-prep', { resume_text: resumeText, target_role: targetRole }),
};

// 📊 Resume Strength Radar (UNIQUE)
export const strengthRadarAPI = {
    analyze: (resumeText, targetRole = 'Software Engineer') =>
        api.post('/ai-rewrite/strength-radar', { resume_text: resumeText, target_role: targetRole }),
};

// ⚡ Full Pipeline API (OUR OWN TECH — does everything in one call)
export const pipelineAPI = {
    run: (resumeText, targetRole, templateId = 'classic', companies = null, mode = 'ATS') =>
        api.post('/ai-rewrite/pipeline', { resume_text: resumeText, target_role: targetRole, template_id: templateId, companies, mode }, { timeout: 180000 }),
};

// 🚀 Auto-Apply Engine (12+ PLATFORMS — UNIQUE)
export const autoApplyAPI = {
    searchAndApply: (resumeText, targetRole, location = 'India', maxJobs = 10) =>
        api.post('/ai-rewrite/auto-apply', { resume_text: resumeText, target_role: targetRole, location, max_jobs: maxJobs }, { timeout: 120000 }),
    applyLinks: (resumeText, targetRole, location = 'India', platforms = null) =>
        api.post('/ai-rewrite/apply-links', { resume_text: resumeText, target_role: targetRole, location, platforms }),
    getPlatforms: () =>
        api.get('/ai-rewrite/platforms'),
};

// Credit Status API
export const creditAPI = {
    getStatus: () => api.get('/advanced/api-credits'),
    quickCheck: () => api.get('/advanced/credits-check'),
};

export default api;
