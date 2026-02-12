# Resume Analyzer AI - Python Stack

A comprehensive **Resume Analyzer** built with **Python (FastAPI)** backend and **React** frontend. This project features **ATS scoring**, **AI-powered resume rewriting**, **job matching**, and **user authentication**.

---

## 🎯 **Key Features**

### ✅ **Implemented**
1. **User Authentication** - JWT-based login/signup
2. **Resume Upload & Parsing** - PDF, DOCX, TXT support
3. **ATS Scoring Engine** - ML-based scoring with:
   - Keyword matching (TF-IDF + spaCy)
   - Grammar checking (LanguageTool)
   - Relevance scoring (Cosine Similarity)
   - Structure analysis
4. **AI Resume Rewriting** - Google Gemini API integration
5. **Job Matching** - Real-time job recommendations
6. **Modern UI** - React + Tailwind CSS with animations
7. **Cloud-Ready** - Dockerized for easy deployment

---

## 📁 **Project Structure**

```
resume-analyzer-python/
├── resume-analyzer-backend/     # FastAPI Backend
│   ├── app/
│   │   ├── api/endpoints/       # REST API routes
│   │   ├── core/                # Config & Security
│   │   ├── db/                  # Database setup
│   │   ├── models/              # SQLAlchemy models
│   │   ├── schemas/             # Pydantic schemas
│   │   ├── services/            # Business logic (ML/AI)
│   │   └── main.py              # App entry point
│   ├── requirements.txt
│   ├── Dockerfile
│   └── .env
│
├── resume-analyzer-frontend/    # React Frontend
│   ├── src/
│   │   ├── components/          # UI components
│   │   ├── api.js               # API client
│   │   ├── App.jsx              # Main app
│   │   └── main.jsx
│   ├── package.json
│   └── vite.config.js
│
└── PROJECT_SUMMARY.md
```

---

## 🚀 **Quick Start**

### **Prerequisites**
- Python 3.10+
- Node.js 18+
- PostgreSQL 14+

### **1. Backend Setup**

```bash
cd resume-analyzer-backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Download spaCy model
python -m spacy download en_core_web_sm

# Setup database
# Create PostgreSQL database: resume_analyzer_ai

# Configure .env file
# Edit .env with your database credentials and API keys

# Run server
uvicorn app.main:app --reload
```

Backend will run on: **http://localhost:8000**
API Docs: **http://localhost:8000/docs**

### **2. Frontend Setup**

```bash
cd resume-analyzer-frontend

# Install dependencies
npm install

# Run dev server
npm run dev
```

Frontend will run on: **http://localhost:3000**

---

## 🔧 **Technology Stack**

| Layer | Technology |
|-------|-----------|
| **Backend** | FastAPI, Python 3.10+ |
| **Database** | PostgreSQL + SQLAlchemy |
| **ML/NLP** | spaCy, scikit-learn, LanguageTool |
| **AI** | Google Gemini API |
| **Frontend** | React 18, Vite, Tailwind CSS |
| **Auth** | JWT (python-jose + passlib) |
| **Deployment** | Docker, Render/Railway ready |

---

## 📊 **API Endpoints**

### **Authentication**
- `POST /api/v1/login/access-token` - Login
- `POST /api/v1/signup` - Register

### **Resumes**
- `POST /api/v1/resumes/upload` - Upload & analyze resume
- `GET /api/v1/resumes/` - List user resumes
- `GET /api/v1/resumes/{id}` - Get resume details

### **Jobs**
- `POST /api/v1/jobs/match/{resume_id}` - Match resume to job
- `GET /api/v1/jobs/recommendations/{resume_id}` - Get job recommendations

---

## 🎓 **B.Tech Final Year Project Highlights**

### **Machine Learning Components**
1. **NLP-based Keyword Extraction** - Using spaCy NER and TF-IDF
2. **Semantic Similarity** - Cosine similarity for job matching
3. **Grammar Analysis** - LanguageTool integration
4. **AI Text Generation** - Gemini API for resume rewriting

### **Real-Time Features**
- Live ATS score calculation
- Instant job recommendations
- AI-powered feedback

### **Production-Ready**
- JWT authentication
- Docker containerization
- Cloud deployment ready (Render/Railway)
- RESTful API design
- Comprehensive error handling

---

## 🌐 **Deployment Guide**

### **Option 1: Render (Recommended)**

**Backend:**
1. Create new Web Service on Render
2. Connect GitHub repo
3. Set build command: `pip install -r requirements.txt`
4. Set start command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
5. Add environment variables from `.env`

**Frontend:**
1. Create Static Site on Render
2. Build command: `npm install && npm run build`
3. Publish directory: `dist`

**Database:**
- Use Render PostgreSQL or Supabase free tier

### **Option 2: Docker**

```bash
# Build and run with Docker
docker build -t resume-analyzer-backend ./resume-analyzer-backend
docker run -p 8000:8000 resume-analyzer-backend
```

---

## 📝 **Environment Variables**

Create `.env` file in `resume-analyzer-backend/`:

```env
POSTGRES_SERVER=localhost
POSTGRES_USER=postgres
POSTGRES_PASSWORD=your_password
POSTGRES_DB=resume_analyzer_ai

SECRET_KEY=your-secret-key-here
GEMINI_API_KEY=your-gemini-api-key

# Optional
AWS_ACCESS_KEY_ID=
AWS_SECRET_ACCESS_KEY=
AWS_S3_BUCKET=
```

---

## 🎨 **UI Features**

- **Modern Design** - Gradient backgrounds, glassmorphism
- **Responsive** - Mobile-friendly
- **Animations** - Smooth transitions and loading states
- **Charts** - Visual ATS score breakdown (Recharts)
- **Dark Mode Ready** - Tailwind CSS utilities

---

## 🔐 **Security Features**

- Password hashing (bcrypt)
- JWT token authentication
- CORS protection
- SQL injection prevention (SQLAlchemy ORM)
- File upload validation

---

## 📈 **Future Enhancements**

- [ ] Email notifications (SMTP integration)
- [ ] Rate limiting (Redis)
- [ ] Resume templates library
- [ ] Bulk resume analysis
- [ ] Admin dashboard
- [ ] Analytics & reporting

---

## 🐛 **Troubleshooting**

**Issue:** `ModuleNotFoundError: No module named 'spacy'`
```bash
pip install spacy
python -m spacy download en_core_web_sm
```

**Issue:** Database connection error
- Ensure PostgreSQL is running
- Check `.env` credentials
- Create database: `CREATE DATABASE resume_analyzer_ai;`

**Issue:** CORS errors
- Update `BACKEND_CORS_ORIGINS` in `app/core/config.py`

---

## 👨‍💻 **For College Project Presentation**

### **Key Points to Highlight:**

1. **Machine Learning Integration**
   - NLP for text analysis
   - TF-IDF vectorization
   - Cosine similarity for matching

2. **AI-Powered Features**
   - Gemini API for intelligent rewriting
   - Real-time job recommendations

3. **Full-Stack Development**
   - RESTful API design
   - Modern React frontend
   - Database design & optimization

4. **Production Deployment**
   - Cloud-hosted application
   - Docker containerization
   - Scalable architecture

---

## 📄 **License**

MIT License - Free for educational and commercial use

---

## 🙏 **Acknowledgments**

- **spaCy** - NLP library
- **LanguageTool** - Grammar checking
- **Google Gemini** - AI text generation
- **FastAPI** - Modern Python web framework

---

**Built with ❤️ for B.Tech Final Year Project**
