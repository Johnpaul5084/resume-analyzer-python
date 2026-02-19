# 🚀 Step-by-Step Supabase Setup Guide

## Why Supabase?
- ✅ 100% Free
- ✅ Never expires (unlike Render's 90-day DB)
- ✅ No credit card needed
- ✅ PostgreSQL (same as your current DB)
- ✅ Built-in authentication, storage, and real-time
- ✅ 500 MB storage free (more than enough)

---

## Step 1: Create a Supabase Account

1. Open your browser and go to: **https://supabase.com**
2. Click **"Start your project"**
3. Sign up with your **GitHub account** (students use this — it's instant)
4. You'll see the Supabase Dashboard

---

## Step 2: Create Your Project

1. Click **"New Project"**
2. Fill in:
   - **Name:** `resume-analyzer-phoenix`
   - **Database Password:** Create a strong password (write it down!)
   - **Region:** Select your nearest region (e.g., `South Asia (Mumbai)`)
3. Click **"Create new project"**
4. Wait 1-2 minutes for the project to initialize

---

## Step 3: Get Your Connection String

1. In your Supabase project dashboard, click **"Project Settings"** (gear icon on left)
2. Click **"Database"** tab
3. Scroll down to **"Connection string"**
4. Click the **"URI"** tab
5. Copy the connection string — it looks like:
   ```
   postgresql://postgres:[YOUR-PASSWORD]@db.abcdefghij.supabase.co:5432/postgres
   ```

---

## Step 4: Update Your .env File

Open `d:\4-2\resume-analyzer-python\resume-analyzer-backend\.env`

Replace:
```
POSTGRES_SERVER=localhost
POSTGRES_USER=postgres
POSTGRES_PASSWORD=password
POSTGRES_DB=resume_analyzer_ai
```

With:
```
DATABASE_URL=postgresql://postgres:[YOUR-PASSWORD]@db.YOURPROJECTID.supabase.co:5432/postgres
```

**Example:**
```env
DATABASE_URL=postgresql://postgres:mysecretpassword@db.abcdefgh.supabase.co:5432/postgres
```

---

## Step 5: Run Database Migration

Run these commands in order:

```bash
cd d:\4-2\resume-analyzer-python\resume-analyzer-backend

# Activate virtual environment (Windows)
venv\Scripts\activate

# Run the migration (this creates all tables in Supabase)
python supabase_migrate.py
```

---

## Step 6: Verify Migration

1. Go to your Supabase Dashboard
2. Click **"Table Editor"** on the left
3. You should see these tables:
   - `users`
   - `resumes`
   - `job_descriptions`

---

## Step 7: Restart Your Backend

```bash
# With Supabase configured, start the backend
python -m uvicorn app.main:app --reload
```

The backend will now use **Supabase PostgreSQL** instead of local SQLite!

---

## ✅ After Setup - Free Limits (More Than Enough)

| Resource | Free Limit | Your Usage |
|----------|-----------|------------|
| Database Size | 500 MB | ~5 MB |
| API Requests | 50,000/month | Low |
| Storage | 1 GB | < 100 MB |
| Auth Users | 50,000 | Students only |

**You can store 10,000+ resumes before hitting any limit!** 🎉

---

## 🚀 For Render Deployment (After Local Testing)

In Render's environment variables, add:
```
DATABASE_URL = your-supabase-postgresql-url
```

That's it! No code changes needed — Render will automatically use Supabase.
