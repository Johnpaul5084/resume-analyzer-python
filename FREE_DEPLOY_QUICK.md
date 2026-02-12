# ⚡ FREE DEPLOYMENT - QUICK REFERENCE

## 🆓 100% FREE STACK

| Component | Platform | Cost |
|-----------|----------|------|
| Frontend | Vercel | ✅ FREE |
| Backend | Render | ✅ FREE |
| Database | Render PostgreSQL | ✅ FREE |

**Total: $0/month FOREVER!** 🎉

---

## 🚀 DEPLOYMENT STEPS

### STEP 1: Render Backend (5 min)

```
1. https://render.com
2. Sign up with GitHub
3. New + → Web Service
4. Connect resume-analyzer-python repo
5. Root: resume-analyzer-backend
6. Runtime: Python 3
7. Build: pip install -r requirements.txt
8. Start: uvicorn app.main:app --host 0.0.0.0 --port $PORT
9. Instance: FREE
10. Add env vars:
    - GEMINI_API_KEY
    - SECRET_KEY
11. Create Web Service
```

### STEP 2: Render Database (3 min)

```
1. New + → PostgreSQL
2. Name: resume-analyzer-db
3. Instance: FREE
4. Create Database
5. Copy Internal Database URL
6. Add to backend env:
   DATABASE_URL=postgres://...
```

### STEP 3: Vercel Frontend (3 min)

```
1. https://vercel.com
2. Sign up with GitHub
3. Import resume-analyzer-python
4. Root: resume-analyzer-frontend
5. Add env var:
   VITE_API_URL=https://your-backend.onrender.com
6. Deploy
```

---

## ✅ CONFIGURATION

### Backend Start Command:
```bash
uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

### Environment Variables (Render):
```bash
GEMINI_API_KEY=your_key
SECRET_KEY=random_key
DATABASE_URL=postgres://... (from database)
```

### Environment Variables (Vercel):
```bash
VITE_API_URL=https://your-backend.onrender.com
```

---

## 🐛 TROUBLESHOOTING

**Slow first load?**
→ Free tier spins down. Wait 30 sec.

**CORS error?**
→ Already fixed in code ✅

**Database error?**
→ Check DATABASE_URL is set

---

## 🎓 PRESENTATION LINE

**"I deployed a production-grade AI Resume Analyzer using React, FastAPI, and PostgreSQL on Vercel and Render - completely free, with automatic HTTPS and CI/CD."**

---

## 💡 PRO TIP

**Before presenting:**
- Open backend URL 2 min early
- Keeps service awake
- Smooth demo guaranteed!

---

## 📖 FULL GUIDE

See: **`DEPLOY_FREE.md`**

---

**Time: 10-15 minutes**
**Cost: $0/month**
**Skill: Professional level!** 🚀
