# Resume Analyzer AI - Setup & Deployment Guide

## 🚀 Quick Start (Development)

### Backend Setup

1. **Navigate to backend directory:**
```bash
cd resume-analyzer-backend
```

2. **Create and activate virtual environment:**
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

3. **Install dependencies:**
```bash
pip install -r requirements.txt
```

4. **Download spaCy model:**
```bash
python -m spacy download en_core_web_sm
```

5. **Setup PostgreSQL database:**
```sql
CREATE DATABASE resume_analyzer_ai;
```

6. **Configure environment variables:**
Edit `.env` file with your credentials:
```env
POSTGRES_SERVER=localhost
POSTGRES_USER=postgres
POSTGRES_PASSWORD=your_password
POSTGRES_DB=resume_analyzer_ai
SECRET_KEY=generate-a-secure-key
GEMINI_API_KEY=your-gemini-api-key
```

7. **Run the backend:**
```bash
uvicorn app.main:app --reload
```

Backend runs on: **http://localhost:8000**
API Docs: **http://localhost:8000/docs**

---

### Frontend Setup

1. **Navigate to frontend directory:**
```bash
cd resume-analyzer-frontend
```

2. **Install dependencies:**
```bash
npm install
```

3. **Run development server:**
```bash
npm run dev
```

Frontend runs on: **http://localhost:3000**

---

## 🌐 Cloud Deployment

### Option 1: Render (Free Tier)

#### Backend Deployment

1. Create account on [Render.com](https://render.com)
2. Click "New +" → "Web Service"
3. Connect your GitHub repository
4. Configure:
   - **Name:** resume-analyzer-backend
   - **Environment:** Python 3
   - **Build Command:** `pip install -r requirements.txt && python -m spacy download en_core_web_sm`
   - **Start Command:** `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
   - **Instance Type:** Free

5. Add Environment Variables:
   - `POSTGRES_SERVER` (from Render PostgreSQL)
   - `POSTGRES_USER`
   - `POSTGRES_PASSWORD`
   - `POSTGRES_DB`
   - `SECRET_KEY`
   - `GEMINI_API_KEY`

#### Database Setup (Render PostgreSQL)

1. Click "New +" → "PostgreSQL"
2. Name: `resume-analyzer-db`
3. Copy connection details to backend environment variables

#### Frontend Deployment

1. Click "New +" → "Static Site"
2. Connect repository
3. Configure:
   - **Build Command:** `npm install && npm run build`
   - **Publish Directory:** `dist`
4. Add environment variable:
   - `VITE_API_URL=https://your-backend-url.onrender.com/api/v1`

---

### Option 2: Railway (Alternative)

1. Visit [Railway.app](https://railway.app)
2. Create new project
3. Add PostgreSQL database
4. Deploy backend from GitHub
5. Deploy frontend as static site

---

## 🔑 Getting API Keys

### Google Gemini API (Free)

1. Visit [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Click "Get API Key"
3. Create new API key
4. Copy and add to `.env` as `GEMINI_API_KEY`

---

## 📦 Docker Deployment

### Build and Run Backend

```bash
cd resume-analyzer-backend
docker build -t resume-analyzer-backend .
docker run -p 8000:8000 --env-file .env resume-analyzer-backend
```

### Docker Compose (Full Stack)

Create `docker-compose.yml`:

```yaml
version: '3.8'

services:
  db:
    image: postgres:14
    environment:
      POSTGRES_DB: resume_analyzer_ai
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: password
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data

  backend:
    build: ./resume-analyzer-backend
    ports:
      - "8000:8000"
    depends_on:
      - db
    environment:
      POSTGRES_SERVER: db
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: password
      POSTGRES_DB: resume_analyzer_ai
      SECRET_KEY: your-secret-key
      GEMINI_API_KEY: your-api-key

  frontend:
    build: ./resume-analyzer-frontend
    ports:
      - "3000:3000"
    depends_on:
      - backend

volumes:
  postgres_data:
```

Run:
```bash
docker-compose up
```

---

## 🧪 Testing the Application

1. **Open frontend:** http://localhost:3000
2. **Create account:** Click "Sign Up"
3. **Upload resume:** PDF, DOCX, or TXT
4. **View analysis:** Check ATS score and recommendations
5. **Test API:** Visit http://localhost:8000/docs

---

## 🎓 For College Presentation

### Demo Flow

1. **Show Login/Signup** - User authentication
2. **Upload Resume** - With job description
3. **View ATS Score** - Explain ML scoring components
4. **Show Breakdown** - Keywords, grammar, relevance
5. **Job Recommendations** - Real-time matching
6. **Explain Architecture** - FastAPI + React + PostgreSQL
7. **Show Code** - Highlight ML/AI components

### Key Technical Points

- **Machine Learning:** spaCy NER, TF-IDF, Cosine Similarity
- **AI Integration:** Google Gemini for text generation
- **Security:** JWT authentication, password hashing
- **Scalability:** Docker, cloud deployment
- **Modern Stack:** FastAPI (async), React (hooks)

---

## 🐛 Common Issues

### Backend won't start
- Check PostgreSQL is running
- Verify `.env` credentials
- Ensure spaCy model is downloaded

### Frontend can't connect to backend
- Check CORS settings in `app/core/config.py`
- Verify backend is running on port 8000
- Update proxy in `vite.config.js` if needed

### Database errors
- Ensure database exists: `CREATE DATABASE resume_analyzer_ai;`
- Check connection string in `.env`

---

## 📊 Project Metrics

- **Lines of Code:** ~3000+
- **API Endpoints:** 10+
- **ML Models:** spaCy, TF-IDF, LanguageTool
- **Technologies:** 15+
- **Deployment:** Cloud-ready

---

**Good luck with your B.Tech project! 🎓**
