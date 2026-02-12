# ⚡ DEPLOYMENT QUICK REFERENCE CARD

## ✅ VERIFIED CONFIGURATION

### Backend Structure:
```
resume-analyzer-backend/
 └── app/
      └── main.py  ✅ CONFIRMED
```

### Railway Start Command:
```bash
uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

### CORS Configuration:
```python
✅ ALREADY CORRECT - NO CHANGES NEEDED

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

---

## 🚀 DEPLOYMENT STEPS

### STEP 1: Railway (Backend) - 5 min

```
1. https://railway.app
2. Login with GitHub
3. New Project → Deploy from GitHub
4. Select: resume-analyzer-backend
5. Add PostgreSQL database
6. Add variables:
   - GEMINI_API_KEY
   - SECRET_KEY
7. Set start command:
   uvicorn app.main:app --host 0.0.0.0 --port $PORT
8. Generate domain
9. Test: /docs
```

### STEP 2: Vercel (Frontend) - 3 min

```
1. https://vercel.com
2. Login with GitHub
3. Import project
4. Select: resume-analyzer-frontend
5. Add variable:
   VITE_API_URL = https://your-backend.railway.app
6. Deploy
7. Test: open URL
```

---

## ✅ TEST CHECKLIST

- [ ] Can signup
- [ ] Can login
- [ ] Can upload resume
- [ ] ATS score generates
- [ ] No CORS errors

---

## 🎓 PRESENTATION LINE

**"I built and deployed a production-grade AI Resume Analyzer using React, FastAPI, PostgreSQL, Railway, and Vercel with Google Gemini integration."**

---

## 🐛 TROUBLESHOOTING

**CORS Error?**
→ Already fixed in code ✅

**Network Error?**
→ Check VITE_API_URL in Vercel

**Database Error?**
→ Ensure PostgreSQL added in Railway

---

## 💰 COST

Free Tier: $0-5/month ✅

---

**Total Time: 8-10 minutes**
**Skill Level: Entry-level engineer** 🚀

**NOW GO DEPLOY! 💪**
