# 🚀 QUICK DEPLOY REFERENCE CARD

## Copy-Paste Commands (Windows)

### FRONTEND DEPLOYMENT (Vercel)
```bash
cd d:\4-2\resume-analyzer-python\resume-analyzer-frontend
vercel login
vercel --prod
```

### BACKEND DEPLOYMENT (Railway)
```bash
cd d:\4-2\resume-analyzer-python\resume-analyzer-backend
railway login
railway init
railway up
railway add
```

### VIEW LOGS
```bash
railway logs
railway logs --tail
```

### REDEPLOY
```bash
# Frontend
cd d:\4-2\resume-analyzer-python\resume-analyzer-frontend
vercel --prod

# Backend
cd d:\4-2\resume-analyzer-python\resume-analyzer-backend
railway up
```

---

## Environment Variables (Railway Dashboard)

```
GEMINI_API_KEY=your_gemini_api_key
SECRET_KEY=your_random_secret_key
DATABASE_URL=postgresql://... (auto-filled)
BACKEND_CORS_ORIGINS=["https://your-app.vercel.app"]
```

---

## Generate Secret Key
```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

---

## Test URLs

```
Frontend:  https://your-app.vercel.app
Backend:   https://your-backend.railway.app
API Docs:  https://your-backend.railway.app/docs
```

---

## Troubleshooting

**CORS Error:**
- Add frontend URL to BACKEND_CORS_ORIGINS in Railway

**Network Error:**
- Check if backend is running at /docs
- Verify API URL in frontend/src/api.js

**Build Failed:**
- Check logs: `railway logs`
- Verify requirements.txt

---

## Documentation Files

- **START HERE:** `DEPLOY_NOW.md`
- **Detailed Guide:** `DEPLOYMENT_INSTRUCTIONS.md`
- **Visual Guide:** `DEPLOYMENT_VISUAL_GUIDE.md`
- **Ready Check:** `DEPLOYMENT_READY.md`

---

## Support

- Vercel: https://vercel.com/docs
- Railway: https://docs.railway.app

---

**Total Time: 10 minutes**
**Total Cost: $0-5/month**

🎉 **You got this!**
