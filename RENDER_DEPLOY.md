# 🚀 Render Deployment Guide - Phoenix Platform

## Status: READY TO DEPLOY (All 13/13 tests passing locally)

---

## Step 1: Go to Render

1. Open: **https://render.com**
2. Sign in with GitHub
3. Click **"New +"** → **"Web Service"**

---

## Step 2: Connect GitHub Repo

1. Select your repo: **`resume-analyzer-python`**
2. Click **"Connect"**

---

## Step 3: Configure the Service

Fill in these settings:

| Setting | Value |
|---------|-------|
| **Name** | `resume-analyzer-phoenix` |
| **Region** | `Singapore` (closest free region to India) |
| **Branch** | `main` |
| **Root Directory** | `resume-analyzer-backend` |
| **Runtime** | `Python 3` |
| **Build Command** | `pip install -r requirements.txt` |
| **Start Command** | `uvicorn app.main:app --host 0.0.0.0 --port $PORT` |
| **Instance Type** | `Free` |

---

## Step 4: Set Environment Variables

In Render → Your Service → **"Environment"** tab, add these:

```
DATABASE_URL = postgresql://postgres.muwrzwnyilttlwsubwos:Gracious%245084%40@aws-1-ap-southeast-2.pooler.supabase.com:5432/postgres

SECRET_KEY = phoenix-ai-career-platform-2026-super-secret-key-change-in-prod

GEMINI_API_KEY = [Your Gemini API Key from Google AI Studio]

SARVAM_API_KEY = [Your Sarvam API Key - optional]

ALGORITHM = HS256

ACCESS_TOKEN_EXPIRE_MINUTES = 30

PROJECT_NAME = Resume Analyzer AI - Phoenix 2026

API_V1_STR = /api/v1
```

> ⚠️ Get your Gemini API key FREE from: https://aistudio.google.com/apikey

---

## Step 5: Deploy

1. Click **"Create Web Service"**
2. Wait ~5 minutes for first build
3. Your API will be live at:
   ```
   https://resume-analyzer-phoenix.onrender.com
   ```

---

## Step 6: Update Frontend API URL

In your frontend's `.env` or `api.js`, update the base URL:

```javascript
const BASE_URL = "https://resume-analyzer-phoenix.onrender.com/api/v1";
```

---

## Step 7: Verify Deployment

Test your live API:
```
https://resume-analyzer-phoenix.onrender.com/
https://resume-analyzer-phoenix.onrender.com/docs
```

---

## ✅ What's Running in Production

- **Backend**: FastAPI on Render (Free)
- **Database**: Supabase PostgreSQL (Free Forever)
- **AI**: Gemini 2.0 Flash (Free tier - 15 RPM)
- **OCR**: Sarvam AI + Tesseract fallback

## ⚠️ Render Free Tier Notes

- First request after 15 min idle may be slow (cold start ~30s)
- 750 hours/month free (enough for 24/7)
- Auto-deploys whenever you push to GitHub
