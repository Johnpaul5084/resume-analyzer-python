# 🎯 Resume Analyzer - Manual Testing Guide

## ✅ Servers Running
- **Backend**: http://127.0.0.1:8000
- **Frontend**: http://localhost:3000
- **API Docs**: http://127.0.0.1:8000/docs

---

## 📋 Step-by-Step Testing Instructions

### 1. Open the Application
Open your web browser and navigate to:
```
http://localhost:3000
```

### 2. What You Should See
**Login/Signup Page** with:
- Modern gradient background
- Login form (email + password)
- "Sign Up" tab/button to create a new account
- Responsive design with Tailwind CSS styling

### 3. Create a Test Account
Click on "Sign Up" and enter:
- **Email**: test@example.com
- **Password**: password123
- **Full Name**: Test User

### 4. Login
After signup, login with the credentials you just created.

### 5. Dashboard
After login, you should see:
- Navigation menu
- "Upload Resume" button
- List of your uploaded resumes (empty initially)

### 6. Upload a Resume
1. Click "Upload Resume"
2. Select a PDF or DOCX file
3. Enter a title (e.g., "My Software Engineer Resume")
4. Optionally add a job description for better matching
5. Click "Analyze"

### 7. View Analysis Results
After upload, you should see:
- **ATS Score** (0-100)
- **Score Breakdown**:
  - Keywords Score
  - Grammar Score
  - Structure Score
  - Relevance Score
- **Missing Keywords**
- **Parsed Sections** (Skills, Experience, Education, etc.)
- **AI Feedback** (if Gemini API key is configured)

### 8. Job Recommendations
- Click "Get Job Recommendations"
- View matched jobs based on your resume

---

## 🔍 API Testing (Alternative)

If you prefer to test via API directly, open:
```
http://127.0.0.1:8000/docs
```

This opens **Swagger UI** where you can:
1. Test all endpoints interactively
2. See request/response schemas
3. Try authentication flow
4. Upload resumes via API

### Quick API Test:
1. Go to `/api/v1/signup` endpoint
2. Click "Try it out"
3. Enter test user data
4. Click "Execute"
5. Check the response

---

## 🎨 Expected UI Features

### Design Elements:
- ✅ Gradient backgrounds (purple/blue theme)
- ✅ Glassmorphism effects
- ✅ Smooth animations
- ✅ Responsive layout
- ✅ Modern typography
- ✅ Interactive charts (Recharts for score visualization)

### Pages:
1. **Login/Signup** (`/`)
2. **Dashboard** (`/dashboard`)
3. **Upload Resume** (`/upload`)
4. **Resume Detail** (`/resume/:id`)

---

## 🐛 Common Issues & Solutions

### Issue: "Network Error"
**Solution**: Make sure backend is running on port 8000
```bash
# Check if backend is running
curl http://127.0.0.1:8000/
```

### Issue: "Failed to fetch"
**Solution**: Check CORS settings in backend config

### Issue: Login not working
**Solution**: 
1. Check browser console for errors (F12)
2. Verify credentials
3. Check if user was created successfully

### Issue: Resume upload fails
**Solution**:
1. Check file format (PDF, DOCX, TXT only)
2. Check file size (max 16MB)
3. Ensure `uploads/` folder exists

---

## 📊 Testing Checklist

- [ ] Frontend loads at http://localhost:3000
- [ ] Can create a new account
- [ ] Can login with credentials
- [ ] Dashboard displays after login
- [ ] Can navigate to upload page
- [ ] Can upload a resume file
- [ ] ATS score is calculated and displayed
- [ ] Score breakdown shows all components
- [ ] Can view resume details
- [ ] Can get job recommendations
- [ ] Can logout
- [ ] API docs accessible at /docs

---

## 🚀 Next Steps After Testing

1. **Add more test data**: Upload multiple resumes
2. **Test AI rewriting**: Use the Gemini API feature
3. **Test job matching**: Add job descriptions
4. **Customize UI**: Modify colors, fonts, layout
5. **Deploy**: Use Docker or deploy to Render/Railway

---

## 📞 Need Help?

Check the logs:
- **Frontend**: Check browser console (F12 → Console tab)
- **Backend**: Check terminal where uvicorn is running

Both servers should be running without errors!
