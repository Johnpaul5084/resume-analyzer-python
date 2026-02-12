# 🐛 Signup Error - Debugging Guide

## Issue
Getting "An error occurred" when clicking "Create Account" during signup.

## ✅ Fixes Applied

### 1. Backend (auth.py)
- Added `db.refresh(user)` after commit to load server-generated fields
- Added try-catch block with better error handling
- Added rollback on error

### 2. Frontend (Login.jsx)
- Enhanced error messages to show:
  - Server errors with details
  - Network connection errors
  - Generic errors with message
- Added console.error for debugging

## 🔍 How to Debug

### Step 1: Open Browser Console
1. Open http://localhost:3000
2. Press **F12** to open Developer Tools
3. Go to **Console** tab
4. Try to signup again
5. Look for error messages in red

### Step 2: Check Network Tab
1. In Developer Tools, go to **Network** tab
2. Try to signup again
3. Look for the POST request to `/api/v1/signup`
4. Click on it to see:
   - **Request**: What data was sent
   - **Response**: What the server returned
   - **Status Code**: Should be 201 for success

### Step 3: Check Backend Logs
Look at the terminal where `uvicorn` is running for error messages.

## 🎯 Common Issues & Solutions

### Issue 1: "Cannot connect to server"
**Cause**: Backend not running or wrong port  
**Solution**: 
- Check if backend is running on port 8000
- Run: `curl http://127.0.0.1:8000/`
- Should return: `{"message":"Welcome to Resume Analyzer AI API..."}`

### Issue 2: CORS Error
**Cause**: Frontend can't access backend due to CORS policy  
**Solution**: Already configured in `app/core/config.py`
```python
BACKEND_CORS_ORIGINS = [
    "http://localhost:3000",
    "http://localhost:8080",
    "http://127.0.0.1:3000"
]
```

### Issue 3: Database Error
**Cause**: SQLite database file permissions or corruption  
**Solution**:
```bash
# Delete and recreate database
cd resume-analyzer-backend
del resume_analyzer.db  # or rm on Linux/Mac
python -c "from app.db.session import engine; from app.models.all_models import Base; Base.metadata.create_all(bind=engine)"
```

### Issue 4: Validation Error
**Cause**: Missing or invalid fields  
**Solution**: Ensure all fields are filled:
- Email: Valid email format
- Password: At least 1 character
- Full Name: At least 1 character

### Issue 5: "User already exists"
**Cause**: Email already registered  
**Solution**: Use a different email or delete the database

## 🧪 Manual API Test

Test the signup endpoint directly:

```python
import requests

response = requests.post(
    "http://127.0.0.1:8000/api/v1/signup",
    json={
        "email": "test123@example.com",
        "password": "password123",
        "full_name": "Test User"
    }
)

print(f"Status: {response.status_code}")
print(f"Response: {response.json()}")
```

Expected response (201):
```json
{
  "id": 1,
  "email": "test123@example.com",
  "full_name": "Test User",
  "is_active": true,
  "created_at": "2026-02-09T16:08:00.123456"
}
```

## 📋 Checklist

- [ ] Backend is running (check terminal)
- [ ] Frontend is running (check terminal)
- [ ] Browser console shows no errors
- [ ] Network tab shows 201 response
- [ ] All form fields are filled
- [ ] Email is in valid format
- [ ] Using a new email (not already registered)

## 🔧 Quick Fix Steps

1. **Restart Backend**:
   ```bash
   # Stop the current backend (Ctrl+C)
   cd resume-analyzer-backend
   python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
   ```

2. **Restart Frontend**:
   ```bash
   # Stop the current frontend (Ctrl+C)
   cd resume-analyzer-frontend
   npm run dev
   ```

3. **Clear Browser Cache**:
   - Press Ctrl+Shift+Delete
   - Clear cached images and files
   - Reload page (Ctrl+F5)

4. **Try Again**:
   - Use a fresh email
   - Fill all fields
   - Click "Create Account"

## 📞 What to Report

If still not working, please share:
1. **Browser console error** (screenshot or copy text)
2. **Network tab response** (what the server returned)
3. **Backend terminal output** (any error messages)

## ✨ Expected Behavior

When signup works correctly:
1. Click "Create Account"
2. See "Processing..." button
3. Automatically logged in
4. Redirected to Dashboard
5. See welcome message

---

**The fixes have been applied. Please try signing up again and check the browser console (F12) for detailed error messages!**
