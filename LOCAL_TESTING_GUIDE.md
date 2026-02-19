# 🧪 LOCAL TESTING GUIDE

## 🎯 Test Before Deploying

Let's run the application locally to verify everything works correctly.

---

## 📋 PREREQUISITES

- ✅ Python 3.13.7 (Detected)
- ✅ Node.js (for frontend)
- ✅ Git Bash or PowerShell

---

## 🚀 STEP 1: RUN BACKEND (Terminal 1)

### Option A: Using PowerShell Script (Easiest)

I've created a script for you. Just run:

```powershell
cd d:\4-2\resume-analyzer-python
.\run-backend.ps1
```

### Option B: Manual Commands

```bash
# Navigate to backend
cd d:\4-2\resume-analyzer-python\resume-analyzer-backend

# Create virtual environment (if not exists)
python -m venv venv

# Activate virtual environment
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the backend server
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

**Backend will run on:** http://127.0.0.1:8000

**Test it:**
- Open: http://127.0.0.1:8000 → Should show welcome message
- Open: http://127.0.0.1:8000/docs → Should show API documentation

---

## 🎨 STEP 2: RUN FRONTEND (Terminal 2)

### Option A: Using PowerShell Script (Easiest)

Open a **NEW terminal** and run:

```powershell
cd d:\4-2\resume-analyzer-python
.\run-frontend.ps1
```

### Option B: Manual Commands

```bash
# Navigate to frontend
cd d:\4-2\resume-analyzer-python\resume-analyzer-frontend

# Install dependencies (first time only)
npm install

# Run the frontend dev server
npm run dev
```

**Frontend will run on:** http://localhost:5173

**Test it:**
- Open: http://localhost:5173 → Should show the login/signup page

---

## ✅ STEP 3: TEST THE APPLICATION

### 1. **Test Signup**
- Go to http://localhost:5173
- Click "Sign Up" or "Create Account"
- Fill in:
  - Email: test@example.com
  - Password: Test123!
  - Full Name: Test User
- Click "Sign Up"
- Should show success message

### 2. **Test Login**
- Use the credentials you just created
- Email: test@example.com
- Password: Test123!
- Click "Login"
- Should redirect to dashboard

### 3. **Test Resume Upload**
- Click "Upload Resume" or "Analyze Resume"
- Select a PDF or DOCX resume file
- Click "Upload" or "Analyze"
- Wait for processing (10-30 seconds)

### 4. **Test ATS Score**
- After upload, you should see:
  - ✅ ATS Score (0-100)
  - ✅ Score breakdown
  - ✅ Recommendations
  - ✅ Job suggestions

### 5. **Test AI Rewriting** (if Gemini API key is set)
- Click "Rewrite with AI" or similar button
- Should generate improved resume text
- Check if output makes sense

---

## 🔍 WHAT TO CHECK

### Backend Health:
- [ ] Backend starts without errors
- [ ] Can access http://127.0.0.1:8000/docs
- [ ] Database connection works (check terminal logs)
- [ ] No error messages in terminal

### Frontend Health:
- [ ] Frontend starts without errors
- [ ] Can access http://localhost:5173
- [ ] No errors in browser console (F12)
- [ ] UI loads correctly

### Integration:
- [ ] Frontend can connect to backend
- [ ] Signup works
- [ ] Login works
- [ ] Resume upload works
- [ ] ATS scoring works
- [ ] No CORS errors in browser console

---

## 🐛 COMMON ISSUES & FIXES

### Issue: "ModuleNotFoundError"

**Solution:**
```bash
cd resume-analyzer-backend
venv\Scripts\activate
pip install -r requirements.txt
```

### Issue: "Port 8000 already in use"

**Solution:**
```bash
# Find and kill the process using port 8000
netstat -ano | findstr :8000
taskkill /PID <PID_NUMBER> /F

# Or use a different port
uvicorn app.main:app --reload --port 8001
```

### Issue: "npm: command not found"

**Solution:**
- Install Node.js from https://nodejs.org
- Restart terminal after installation

### Issue: "Database connection failed"

**Solution:**
- The app uses SQLite by default for local testing
- No PostgreSQL needed locally
- Database file will be created automatically

### Issue: "CORS error in browser"

**Solution:**
- Ensure backend is running on http://127.0.0.1:8000
- Frontend should auto-detect localhost backend
- Check `resume-analyzer-frontend/src/api.js`

---

## 📊 EXPECTED OUTPUT

### Backend Terminal:
```
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     Started reloader process
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

### Frontend Terminal:
```
VITE v5.0.11  ready in 500 ms

➜  Local:   http://localhost:5173/
➜  Network: use --host to expose
➜  press h to show help
```

### Browser Console (F12):
- No red errors
- May see some warnings (okay)
- Network tab shows successful API calls

---

## 🎯 ACCURACY TESTING

### Test ATS Scoring Accuracy:

1. **Upload a good resume:**
   - Should get score: 70-90
   - Should show relevant keywords found
   - Should suggest improvements

2. **Upload a poor resume:**
   - Should get score: 30-50
   - Should show missing keywords
   - Should suggest major improvements

3. **Upload a resume with typos:**
   - Should detect grammar issues
   - Should suggest corrections

### Test Job Matching:

1. Upload IT resume → Should suggest IT jobs
2. Upload Medical resume → Should suggest Medical jobs
3. Check if job titles match resume content

---

## 📝 TEST CHECKLIST

### Basic Functionality:
- [ ] Backend starts successfully
- [ ] Frontend starts successfully
- [ ] Can create account
- [ ] Can login
- [ ] Can upload resume (PDF)
- [ ] Can upload resume (DOCX)
- [ ] ATS score displays
- [ ] Score breakdown shows

### Advanced Features:
- [ ] AI rewriting works (if API key set)
- [ ] Job recommendations display
- [ ] Can view resume details
- [ ] Can download analyzed resume
- [ ] Multiple resumes can be uploaded

### Performance:
- [ ] Resume upload takes < 30 seconds
- [ ] ATS scoring completes quickly
- [ ] No lag in UI
- [ ] No memory leaks (check Task Manager)

---

## 🔧 DEBUGGING TIPS

### View Backend Logs:
- Watch the backend terminal for errors
- Look for lines starting with `ERROR:` or `WARNING:`

### View Frontend Logs:
- Open browser console (F12)
- Go to "Console" tab
- Look for red errors

### View Network Requests:
- Open browser console (F12)
- Go to "Network" tab
- Watch API calls to backend
- Check for failed requests (red)

### Test API Directly:
- Go to http://127.0.0.1:8000/docs
- Try API endpoints manually
- Test signup, login, upload

---

## 📸 TAKE SCREENSHOTS

For your presentation, capture:
- [ ] Backend running in terminal
- [ ] Frontend running in terminal
- [ ] Login page
- [ ] Dashboard with uploaded resumes
- [ ] ATS score results
- [ ] API documentation page

---

## ✅ SUCCESS CRITERIA

**Everything works when:**
- ✅ Both backend and frontend run without errors
- ✅ Can signup and login
- ✅ Can upload and analyze resume
- ✅ ATS score is reasonable (30-90 range)
- ✅ Job recommendations appear
- ✅ No errors in browser console
- ✅ UI is responsive and looks good

---

## 🚀 AFTER LOCAL TESTING

Once everything works locally:

1. ✅ **Confidence boost** - You know the app works!
2. ✅ **Deploy to Railway/Render** - Follow deployment guides
3. ✅ **Test deployed version** - Same tests as local
4. ✅ **Prepare presentation** - Use screenshots and demo

---

## 💡 PRO TIPS

1. **Keep both terminals open** - Don't close them while testing
2. **Use incognito mode** - Avoids cache issues
3. **Test with real resumes** - More accurate results
4. **Check accuracy** - Does the ATS score make sense?
5. **Note any bugs** - Fix before deploying

---

**Ready to test? Run the scripts or manual commands above! 🧪**
