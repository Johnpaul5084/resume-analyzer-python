# 🚀 PRODUCTION DEPLOYMENT GUIDE - Railway + Vercel

## ✅ CORS Fixed
## ✅ PostgreSQL Ready
## ✅ Production Configuration Complete

---

## 🎯 STEP 1: Fix CORS (Already Done ✅)

Your `app/main.py` already has proper CORS:

```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Will work with any frontend
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

✅ **Status: COMPLETE**

---

## 🎯 STEP 2: Deploy Backend to Railway

### A. Go to Railway

👉 **https://railway.app**

1. Click **"Login"**
2. Choose **"Login with GitHub"**
3. Authorize Railway

### B. Create New Project

1. Click **"New Project"**
2. Click **"Deploy from GitHub repo"**
3. Select **`resume-analyzer-python`** repository
4. Railway will ask which folder - select **`resume-analyzer-backend`**

**OR** if it doesn't auto-detect:

1. Click **"New Project"**
2. Click **"Empty Project"**
3. Click **"+ New"** → **"GitHub Repo"**
4. Select your repo
5. Set **Root Directory**: `resume-analyzer-backend`

### C. Add Environment Variables

In Railway dashboard:

1. Click on your service (Python app)
2. Go to **"Variables"** tab
3. Click **"+ New Variable"**

Add these:

```bash
GEMINI_API_KEY=your_gemini_api_key_here
SECRET_KEY=your_random_secret_key_here
```

**Generate SECRET_KEY:**
```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

### D. Add PostgreSQL Database

1. In your project, click **"+ New"**
2. Select **"Database"**
3. Choose **"Add PostgreSQL"**

Railway will automatically:
- Create PostgreSQL database
- Set `DATABASE_URL` environment variable
- Connect it to your app

✅ **No manual configuration needed!**

### E. Configure Start Command

1. Go to **"Settings"** tab
2. Find **"Start Command"**
3. Set to:

```bash
uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

### F. Generate Public Domain

1. Go to **"Settings"** tab
2. Find **"Networking"**
3. Click **"Generate Domain"**

You'll get:
```
https://resume-analyzer-backend-production.up.railway.app
```

**SAVE THIS URL!** ⭐

### G. Deploy

Railway will automatically deploy. Wait 3-5 minutes.

### H. Test Backend

Open in browser:
```
https://your-backend.railway.app/docs
```

If Swagger UI loads = **SUCCESS!** ✅

---

## 🎯 STEP 3: Deploy Frontend to Vercel

### A. Go to Vercel

👉 **https://vercel.com**

1. Click **"Login"**
2. Choose **"Continue with GitHub"**
3. Authorize Vercel

### B. Import Project

1. Click **"Add New..."** → **"Project"**
2. Find **`resume-analyzer-python`** repository
3. Click **"Import"**

### C. Configure Project

**Framework Preset:** Vite (should auto-detect)

**Root Directory:** Click **"Edit"** and select:
```
resume-analyzer-frontend
```

**Build Settings:**
- Build Command: `npm run build`
- Output Directory: `dist`
- Install Command: `npm install`

### D. Add Environment Variable

Click **"Environment Variables"**

Add:
```bash
Name:  VITE_API_URL
Value: https://your-backend.railway.app
```

⚠️ **IMPORTANT:** Use your actual Railway URL (without `/api/v1`)

### E. Deploy

Click **"Deploy"**

Wait 2-3 minutes.

You'll get:
```
https://resume-analyzer-xyz.vercel.app
```

**SAVE THIS URL!** ⭐

---

## 🎯 STEP 4: Update Frontend API Configuration

### A. Update api.js

Open: `resume-analyzer-frontend/src/api.js`

Update to:
```javascript
import axios from 'axios';

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL 
    ? `${import.meta.env.VITE_API_URL}/api/v1`
    : 'http://127.0.0.1:8000/api/v1',
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add token to requests
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

export default api;
```

### B. Commit and Push

```bash
git add .
git commit -m "Update API configuration for production"
git push
```

Vercel will auto-deploy the update!

---

## 🎯 STEP 5: Update CORS (Optional but Recommended)

For better security, update Railway environment variables:

Add:
```bash
BACKEND_CORS_ORIGINS=["https://your-frontend.vercel.app"]
```

Replace with your actual Vercel URL.

Then redeploy in Railway.

---

## ✅ VERIFICATION CHECKLIST

### Backend Tests:
- [ ] Open `https://your-backend.railway.app/`
- [ ] Should see: `{"message": "Welcome to Resume Analyzer AI API..."}`
- [ ] Open `https://your-backend.railway.app/docs`
- [ ] Should see Swagger UI
- [ ] Test `/api/v1/signup` endpoint
- [ ] Should work without errors

### Frontend Tests:
- [ ] Open `https://your-frontend.vercel.app`
- [ ] Should see login/signup page
- [ ] Create a test account
- [ ] Should successfully signup
- [ ] Login with test account
- [ ] Should redirect to dashboard
- [ ] Upload a resume
- [ ] Should see ATS score

### Integration Tests:
- [ ] No CORS errors in browser console
- [ ] API calls work from frontend
- [ ] File uploads work
- [ ] AI rewriting works
- [ ] All features functional

---

## 🐛 TROUBLESHOOTING

### Issue: "CORS Error"
**Solution:**
1. Check Railway environment variables
2. Ensure CORS is set to `["*"]` or your Vercel URL
3. Redeploy backend

### Issue: "Network Error"
**Solution:**
1. Check if backend is running: Visit `/docs`
2. Verify `VITE_API_URL` in Vercel
3. Check Railway logs for errors

### Issue: "Database Connection Error"
**Solution:**
1. Ensure PostgreSQL is added in Railway
2. Check if `DATABASE_URL` exists in variables
3. Restart the service

### Issue: "Build Failed" (Frontend)
**Solution:**
1. Check Vercel build logs
2. Ensure `package.json` is correct
3. Try: Clear cache and redeploy

### Issue: "Build Failed" (Backend)
**Solution:**
1. Check Railway logs
2. Ensure `requirements.txt` is correct
3. Verify Python version (3.11)

---

## 📊 YOUR LIVE URLS

After deployment, you'll have:

```
Frontend:  https://resume-analyzer-xyz.vercel.app
Backend:   https://resume-analyzer-backend-production.up.railway.app
API Docs:  https://resume-analyzer-backend-production.up.railway.app/docs
Database:  PostgreSQL on Railway (auto-managed)
```

---

## 🎓 FOR YOUR PRESENTATION

### Opening Statement:
*"I deployed a production-grade AI Resume Analyzer using React, FastAPI, PostgreSQL, Railway, and Vercel."*

### Tech Stack to Mention:
- **Frontend:** React 18 + Vite + Tailwind CSS (Vercel)
- **Backend:** FastAPI + Python 3.11 (Railway)
- **Database:** PostgreSQL (Railway)
- **AI:** Google Gemini API
- **Deployment:** Vercel + Railway
- **Security:** HTTPS, JWT authentication, CORS

### Demo Flow:
1. Show live URL (not localhost!)
2. Create account
3. Upload resume
4. Show ATS score
5. Demonstrate AI rewriting
6. Show job recommendations
7. Open `/docs` to show API
8. Explain architecture

---

## 💰 COST

**Free Tier:**
- Vercel: FREE (100GB bandwidth)
- Railway: $5 credit/month
- **Total: ~$0-5/month**

Perfect for B.Tech project!

---

## 🏆 WHAT YOU'VE BUILT

You now have:
- ✅ **Production-ready** web application
- ✅ **Cloud-hosted** on professional infrastructure
- ✅ **PostgreSQL** database (not SQLite)
- ✅ **AI-powered** features
- ✅ **HTTPS** secure
- ✅ **Scalable** architecture
- ✅ **Globally accessible**

**This is not student-level.**
**This is junior developer level.** 🚀

---

## 📞 SUPPORT

**Railway:**
- Dashboard: https://railway.app/dashboard
- Docs: https://docs.railway.app
- Discord: https://discord.gg/railway

**Vercel:**
- Dashboard: https://vercel.com/dashboard
- Docs: https://vercel.com/docs
- Discord: https://vercel.com/discord

---

## 🎉 CONGRATULATIONS!

Your Resume Analyzer is now:
- ✅ Live on the internet
- ✅ Using production database
- ✅ Deployed on professional platforms
- ✅ Ready for your presentation
- ✅ Shareable with anyone

**Time to celebrate! You did it! 🎊**
