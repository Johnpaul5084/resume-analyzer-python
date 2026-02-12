# 🚀 DEPLOYMENT - STEP BY STEP GUIDE

## ✅ Prerequisites Installed Successfully!

- ✅ Node.js v22.19.0
- ✅ npm 10.9.3
- ✅ Git 2.50.0
- ✅ Vercel CLI
- ✅ Railway CLI

---

## 🎨 PART 1: DEPLOY FRONTEND TO VERCEL (5 minutes)

### Step 1: Navigate to Frontend Directory
```bash
cd d:\4-2\resume-analyzer-python\resume-analyzer-frontend
```

### Step 2: Install Dependencies
```bash
npm install
```

### Step 3: Build the Frontend
```bash
npm run build
```
This creates an optimized production build in the `dist` folder.

### Step 4: Login to Vercel
```bash
vercel login
```
- This will open your browser
- Login with GitHub, GitLab, or Email
- Return to terminal after login

### Step 5: Deploy to Production
```bash
vercel --prod
```

**Answer the prompts:**
```
? Set up and deploy "d:\4-2\resume-analyzer-python\resume-analyzer-frontend"? [Y/n] Y
? Which scope do you want to deploy to? [Your Account]
? Link to existing project? [y/N] N
? What's your project's name? resume-analyzer
? In which directory is your code located? ./
? Want to modify these settings? [y/N] N
```

**🎉 RESULT:** You'll get a URL like:
```
✅ Production: https://resume-analyzer-xyz.vercel.app
```

**SAVE THIS URL!** You'll need it later.

---

## 🔧 PART 2: DEPLOY BACKEND TO RAILWAY (5 minutes)

### Step 1: Navigate to Backend Directory
```bash
cd d:\4-2\resume-analyzer-python\resume-analyzer-backend
```

### Step 2: Login to Railway
```bash
railway login
```
- This will open your browser
- Login with GitHub
- Return to terminal after login

### Step 3: Initialize Railway Project
```bash
railway init
```

**Answer the prompts:**
```
? Create a new project or link to an existing one? Create new project
? Enter project name: resume-analyzer-backend
? Select a team: [Your Account]
```

### Step 4: Deploy to Railway
```bash
railway up
```

This will:
- Upload your code
- Detect Python
- Install dependencies
- Start the server

**🎉 RESULT:** You'll get a URL like:
```
✅ Deployed: https://resume-analyzer-backend-production.up.railway.app
```

**SAVE THIS URL!** You'll need it next.

### Step 5: Add PostgreSQL Database (Recommended)
```bash
railway add
```

Select: **PostgreSQL**

This creates a production database for your app.

### Step 6: Generate Domain (Make it Public)
```bash
railway domain
```

This generates a public URL for your backend.

---

## 🔐 PART 3: CONFIGURE ENVIRONMENT VARIABLES

### For Railway (Backend):

1. Go to https://railway.app/dashboard
2. Click on your `resume-analyzer-backend` project
3. Click on the service (Python app)
4. Go to **Variables** tab
5. Click **+ New Variable**

Add these variables:

```bash
GEMINI_API_KEY=your_gemini_api_key_here
SECRET_KEY=your_super_secret_random_key
DATABASE_URL=[auto-filled if you added PostgreSQL]
BACKEND_CORS_ORIGINS=["https://your-frontend.vercel.app"]
```

**To generate a secure SECRET_KEY:**
```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

6. Click **Deploy** to restart with new variables

---

## 🔄 PART 4: UPDATE FRONTEND WITH BACKEND URL

### Step 1: Update API Configuration

Open: `resume-analyzer-frontend/src/api.js`

Update the baseURL:
```javascript
const api = axios.create({
  baseURL: 'https://your-backend.railway.app/api/v1',  // Replace with your Railway URL
  headers: {
    'Content-Type': 'application/json',
  },
});
```

### Step 2: Redeploy Frontend
```bash
cd d:\4-2\resume-analyzer-python\resume-analyzer-frontend
vercel --prod
```

---

## ✅ PART 5: VERIFY DEPLOYMENT

### Test Backend:
1. Open: `https://your-backend.railway.app/docs`
2. You should see the API documentation (Swagger UI)
3. Try the `/` endpoint - should return welcome message

### Test Frontend:
1. Open: `https://your-frontend.vercel.app`
2. You should see the login/signup page
3. Try creating an account
4. Try uploading a resume

### Test Full Integration:
1. Signup → Login → Upload Resume → View Results
2. Check browser console for errors (F12)
3. Verify all features work

---

## 🎯 YOUR LIVE URLS

**Frontend (Vercel):**
```
https://your-app.vercel.app
```

**Backend (Railway):**
```
https://your-backend.railway.app
```

**API Documentation:**
```
https://your-backend.railway.app/docs
```

---

## 🐛 TROUBLESHOOTING

### Issue: "CORS Error" in browser console
**Solution:**
1. Go to Railway dashboard
2. Add environment variable:
   ```
   BACKEND_CORS_ORIGINS=["https://your-frontend.vercel.app"]
   ```
3. Redeploy backend

### Issue: "Network Error" when calling API
**Solution:**
1. Check if backend is running: Visit `/docs` endpoint
2. Verify API URL in frontend `api.js`
3. Check Railway logs: `railway logs`

### Issue: Backend deployment fails
**Solution:**
1. Check Railway logs for errors
2. Verify `requirements.txt` is correct
3. Ensure Python version is 3.11
4. Try: `railway logs --tail`

### Issue: Database connection error
**Solution:**
1. Make sure you added PostgreSQL in Railway
2. Check if `DATABASE_URL` is set in environment variables
3. Railway auto-provides this when you add PostgreSQL

---

## 📊 DEPLOYMENT CHECKLIST

- [ ] Frontend deployed to Vercel
- [ ] Backend deployed to Railway
- [ ] PostgreSQL database added
- [ ] Environment variables configured
- [ ] CORS settings updated
- [ ] Frontend API URL updated
- [ ] Frontend redeployed with new API URL
- [ ] Backend is accessible at `/docs`
- [ ] Frontend loads without errors
- [ ] Can create account
- [ ] Can login
- [ ] Can upload resume
- [ ] Can view ATS score
- [ ] All features working

---

## 🎓 FOR YOUR PRESENTATION

**Share these URLs:**

**Live Application:**
```
https://your-app.vercel.app
```

**API Documentation:**
```
https://your-backend.railway.app/docs
```

**GitHub Repository:**
```
https://github.com/yourusername/resume-analyzer
```

---

## 💰 COST

**Free Tier (Perfect for B.Tech Project):**
- Vercel: FREE (100GB bandwidth)
- Railway: $5 credit/month (enough for demo)
- **Total: ~$0-5/month**

**Paid Tier (If you need more):**
- Vercel Pro: $20/month
- Railway: ~$10-20/month
- **Total: ~$30-40/month**

---

## 🚀 QUICK COMMANDS REFERENCE

```bash
# Frontend Deployment
cd resume-analyzer-frontend
vercel login
vercel --prod

# Backend Deployment
cd resume-analyzer-backend
railway login
railway init
railway up
railway add  # Add PostgreSQL
railway domain  # Generate public URL

# View Logs
railway logs
railway logs --tail

# Redeploy
vercel --prod  # Frontend
railway up     # Backend
```

---

## 🎉 CONGRATULATIONS!

Your Resume Analyzer is now:
- ✅ **Live on the internet**
- ✅ **Accessible from anywhere**
- ✅ **Running on professional infrastructure**
- ✅ **Secured with HTTPS**
- ✅ **Ready for your presentation**

**You can now share your live app with:**
- Professors
- Recruiters
- Friends
- Portfolio visitors
- Anyone in the world!

---

## 📞 NEED HELP?

**Documentation:**
- Vercel: https://vercel.com/docs
- Railway: https://docs.railway.app

**Common Issues:**
- Check `DEPLOYMENT_INSTRUCTIONS.md`
- View Railway logs: `railway logs`
- Check Vercel logs in dashboard

**Support:**
- Vercel Discord: https://vercel.com/discord
- Railway Discord: https://discord.gg/railway

---

**Your project is LIVE! Time to celebrate! 🎉🚀**
