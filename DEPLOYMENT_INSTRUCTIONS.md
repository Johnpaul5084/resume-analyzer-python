# 🚀 DEPLOYMENT IN PROGRESS!

## Step-by-Step Deployment Guide

### Prerequisites Check ✅

Before we deploy, let's make sure everything is ready:

1. **Node.js installed** (for Vercel CLI)
2. **Git initialized** (for Railway)
3. **Environment variables ready** (GEMINI_API_KEY, SECRET_KEY)

---

## 🎨 STEP 1: Deploy Frontend to Vercel

### Option A: Using Vercel CLI (Recommended)

```bash
# 1. Install Vercel CLI globally
npm install -g vercel

# 2. Navigate to frontend directory
cd d:\4-2\resume-analyzer-python\resume-analyzer-frontend

# 3. Login to Vercel (will open browser)
vercel login

# 4. Deploy to production
vercel --prod
```

**Follow the prompts:**
- Set up and deploy? **Yes**
- Which scope? **Your account**
- Link to existing project? **No**
- What's your project's name? **resume-analyzer** (or your choice)
- In which directory is your code located? **./**
- Want to override the settings? **No**

**Result:** You'll get a URL like `https://resume-analyzer-xyz.vercel.app`

### Option B: Using Vercel Dashboard (Alternative)

1. Go to https://vercel.com
2. Sign up/Login with GitHub
3. Click "Add New Project"
4. Import your GitHub repository (you'll need to push to GitHub first)
5. Configure:
   - Framework Preset: **Vite**
   - Build Command: `npm run build`
   - Output Directory: `dist`
6. Click "Deploy"

---

## 🔧 STEP 2: Deploy Backend to Railway

### Option A: Using Railway CLI (Recommended)

```bash
# 1. Install Railway CLI
npm install -g @railway/cli

# 2. Navigate to backend directory
cd d:\4-2\resume-analyzer-python\resume-analyzer-backend

# 3. Login to Railway
railway login

# 4. Initialize project
railway init

# Follow prompts:
# - Create new project? Yes
# - Project name? resume-analyzer-backend

# 5. Deploy
railway up

# 6. Add PostgreSQL database (optional but recommended)
railway add

# Select: PostgreSQL
```

**Result:** You'll get a URL like `https://resume-analyzer-backend.up.railway.app`

### Option B: Using Railway Dashboard (Alternative)

1. Go to https://railway.app
2. Sign up/Login with GitHub
3. Click "New Project"
4. Select "Deploy from GitHub repo"
5. Connect your repository
6. Select the backend folder
7. Railway will auto-detect Python and deploy

---

## 🔐 STEP 3: Configure Environment Variables

### For Railway (Backend):

In Railway dashboard:
1. Click on your project
2. Go to "Variables" tab
3. Add these variables:

```bash
GEMINI_API_KEY=your_gemini_api_key_here
SECRET_KEY=your_super_secret_key_here_change_this
DATABASE_URL=postgresql://... (auto-provided if you added PostgreSQL)
BACKEND_CORS_ORIGINS=["https://your-frontend.vercel.app"]
```

**Generate a secure SECRET_KEY:**
```bash
# Run this in Python:
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

### For Vercel (Frontend):

In Vercel dashboard:
1. Go to your project
2. Click "Settings" → "Environment Variables"
3. Add:

```bash
VITE_API_URL=https://your-backend.railway.app/api/v1
```

---

## 🔄 STEP 4: Update Frontend API Configuration

After backend is deployed, update the API URL in frontend:

**File:** `resume-analyzer-frontend/src/api.js`

```javascript
const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'https://your-backend.railway.app/api/v1'
});
```

Then redeploy frontend:
```bash
cd d:\4-2\resume-analyzer-python\resume-analyzer-frontend
vercel --prod
```

---

## ✅ STEP 5: Verify Deployment

### Test Backend:
```bash
# Check if backend is live
curl https://your-backend.railway.app/

# Check API docs
# Open in browser: https://your-backend.railway.app/docs
```

### Test Frontend:
```bash
# Open in browser
https://your-frontend.vercel.app
```

### Test Full Flow:
1. Open frontend URL
2. Create account
3. Login
4. Upload resume
5. View ATS score
6. Check if everything works!

---

## 🐛 Troubleshooting

### Issue: Frontend can't connect to backend
**Solution:**
- Check CORS settings in backend
- Verify API URL in frontend
- Check Railway logs: `railway logs`

### Issue: Backend deployment fails
**Solution:**
- Check requirements.txt
- Verify Python version (3.11)
- Check Railway logs for errors
- Ensure all dependencies are compatible

### Issue: Database errors
**Solution:**
- Add PostgreSQL in Railway
- Update DATABASE_URL in environment variables
- Restart the service

### Issue: Build fails
**Solution:**
```bash
# Frontend: Clear cache and rebuild
cd resume-analyzer-frontend
rm -rf node_modules dist
npm install
npm run build

# Backend: Check dependencies
cd resume-analyzer-backend
pip install -r requirements.txt
```

---

## 📊 Post-Deployment Checklist

- [ ] Frontend is live and accessible
- [ ] Backend is live and accessible
- [ ] API docs are accessible (/docs)
- [ ] Database is connected
- [ ] Environment variables are set
- [ ] CORS is configured correctly
- [ ] User can signup/login
- [ ] Resume upload works
- [ ] ATS scoring works
- [ ] AI rewriting works
- [ ] No console errors

---

## 🎯 Quick Deploy Commands Summary

```bash
# FRONTEND (Vercel)
cd d:\4-2\resume-analyzer-python\resume-analyzer-frontend
npm install -g vercel
vercel login
vercel --prod

# BACKEND (Railway)
cd d:\4-2\resume-analyzer-python\resume-analyzer-backend
npm install -g @railway/cli
railway login
railway init
railway up
railway add  # Add PostgreSQL
```

---

## 🌐 Alternative: Quick Deploy with GitHub

If you prefer using GitHub:

1. **Push to GitHub:**
```bash
cd d:\4-2\resume-analyzer-python
git init
git add .
git commit -m "Initial commit - Resume Analyzer"
git remote add origin https://github.com/yourusername/resume-analyzer.git
git push -u origin main
```

2. **Deploy Frontend:**
   - Go to Vercel.com
   - Click "Import Project"
   - Select your GitHub repo
   - Select `resume-analyzer-frontend` folder
   - Deploy!

3. **Deploy Backend:**
   - Go to Railway.app
   - Click "New Project" → "Deploy from GitHub"
   - Select your repo
   - Select `resume-analyzer-backend` folder
   - Deploy!

---

## 💰 Cost Breakdown

### Free Tier (Recommended for B.Tech Project):
- **Vercel:** Free (100GB bandwidth, unlimited projects)
- **Railway:** $5/month credit (enough for small projects)
- **Total:** ~$0-5/month

### Paid Tier (For Production):
- **Vercel Pro:** $20/month (better performance)
- **Railway:** ~$10-20/month (based on usage)
- **Total:** ~$30-40/month

---

## 🎓 For Your Presentation

**Share these URLs:**
- **Live App:** https://your-app.vercel.app
- **API Docs:** https://your-backend.railway.app/docs
- **GitHub:** https://github.com/yourusername/resume-analyzer

**Demo Script:**
1. "Here's my live application deployed on Vercel and Railway"
2. "Let me create an account and upload a resume"
3. "Watch as the AI analyzes and scores the resume"
4. "Here's the ATS score breakdown and improvement suggestions"
5. "The backend API is fully documented at /docs"

---

## 🚀 You're Live!

Once deployed, your application will be:
- ✅ Accessible from anywhere in the world
- ✅ Running on professional cloud infrastructure
- ✅ Automatically scaled based on traffic
- ✅ Backed up and monitored
- ✅ Using HTTPS (secure)
- ✅ Fast and reliable

**Congratulations! Your B.Tech project is now live! 🎉**

---

## 📞 Need Help?

**Vercel Documentation:** https://vercel.com/docs
**Railway Documentation:** https://docs.railway.app
**Deployment Issues:** Check logs in respective dashboards

**Common Commands:**
```bash
# View Railway logs
railway logs

# Redeploy Vercel
vercel --prod

# Check Railway status
railway status
```

---

**Ready to deploy? Let's go! 🚀**
