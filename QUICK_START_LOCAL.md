# ⚡ QUICK START - Run Locally

## 🚀 EASIEST WAY (One Command)

### Run Both Backend + Frontend:

```powershell
cd d:\4-2\resume-analyzer-python
.\run-app.ps1
```

This will:
- ✅ Open backend in one window
- ✅ Open frontend in another window
- ✅ Install dependencies automatically
- ✅ Start both servers

**Wait 15 seconds, then open:** http://localhost:5173

---

## 🔧 MANUAL WAY (Two Terminals)

### Terminal 1 - Backend:

```powershell
cd d:\4-2\resume-analyzer-python
.\run-backend.ps1
```

**Backend URL:** http://127.0.0.1:8000
**API Docs:** http://127.0.0.1:8000/docs

### Terminal 2 - Frontend:

```powershell
cd d:\4-2\resume-analyzer-python
.\run-frontend.ps1
```

**Frontend URL:** http://localhost:5173

---

## ✅ TESTING CHECKLIST

### 1. Test Signup
- Go to http://localhost:5173
- Click "Sign Up"
- Email: test@example.com
- Password: Test123!
- Name: Test User
- Click "Sign Up"

### 2. Test Login
- Email: test@example.com
- Password: Test123!
- Click "Login"

### 3. Test Resume Upload
- Click "Upload Resume"
- Select a PDF or DOCX file
- Wait for analysis (10-30 seconds)
- Check ATS score

### 4. Verify Output
- [ ] ATS score displays (0-100)
- [ ] Score breakdown shows
- [ ] Recommendations appear
- [ ] Job suggestions display
- [ ] No errors in browser console (F12)

---

## 🐛 TROUBLESHOOTING

### Backend won't start:
```powershell
cd d:\4-2\resume-analyzer-python\resume-analyzer-backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### Frontend won't start:
```powershell
cd d:\4-2\resume-analyzer-python\resume-analyzer-frontend
npm install
npm run dev
```

### Port already in use:
```powershell
# Kill process on port 8000
netstat -ano | findstr :8000
taskkill /PID <PID> /F
```

---

## 📊 EXPECTED RESULTS

### Good ATS Score (70-90):
- Resume has relevant keywords
- Good formatting
- Clear sections
- No major grammar issues

### Poor ATS Score (30-50):
- Missing keywords
- Poor formatting
- Grammar errors
- Incomplete sections

---

## 🎯 ACCURACY CHECK

1. **Upload IT resume** → Should suggest IT jobs
2. **Upload Medical resume** → Should suggest Medical jobs
3. **Upload resume with typos** → Should detect errors
4. **Upload well-formatted resume** → Should get high score

---

## 📸 SCREENSHOTS FOR PRESENTATION

Take screenshots of:
- [ ] Login page
- [ ] Dashboard
- [ ] Resume upload
- [ ] ATS score results
- [ ] API documentation

---

## ✅ SUCCESS INDICATORS

**Everything works when:**
- ✅ Backend runs without errors
- ✅ Frontend loads correctly
- ✅ Can signup and login
- ✅ Can upload resume
- ✅ ATS score is reasonable
- ✅ No errors in console

---

## 🚀 AFTER TESTING

Once local testing is successful:

1. ✅ **You know the app works!**
2. ✅ **Deploy to Railway/Render**
3. ✅ **Test deployed version**
4. ✅ **Prepare presentation**

---

**Ready? Run `.\run-app.ps1` and test! 🧪**
