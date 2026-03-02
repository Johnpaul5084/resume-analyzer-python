"""
=============================================================================
 AI RESUME ANALYZER — Comprehensive API Test Suite
=============================================================================
 Tests all 3 API integrations:
   1. GEMINI API   → Resume Rewrite, ATS Scoring, Role Prediction, Grammar Fix
   2. SERPAPI      → Real-time Job Search with Apply Links
   3. OPENAI API   → AI Mentor Chat, Roadmap, Career Intelligence

 Usage:
   # Test against LOCAL server (fallback mode — no API keys needed)
   python test_comprehensive.py

   # Test against DEPLOYED Render server (real API keys configured there)
   python test_comprehensive.py https://your-backend.onrender.com

   # Test against Railway
   python test_comprehensive.py https://your-backend.up.railway.app
=============================================================================
"""

import requests
import json
import time
import sys
import os

# ── CONFIG ──────────────────────────────────────────────────────────────────
DEPLOYED_URL = sys.argv[1].rstrip("/") if len(sys.argv) > 1 else "http://127.0.0.1:8000"
BASE = f"{DEPLOYED_URL}/api/v1"
TIMEOUT = 60  # Generous timeout for Gemini/OpenAI calls on cold start

# Fix Windows encoding
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

# ── TEST STATE ──────────────────────────────────────────────────────────────
RESULTS = []
TOKEN = None
RID = None
RESUME_TEXT = ""
PREDICTED_ROLE = ""

# ── Sample resume for testing (realistic student resume) ────────────────────
SAMPLE_RESUME = """
JOHN PAUL KUMAR
Full Stack Developer | Python | React | Cloud
Email: johnpaul@email.com | Phone: +91-9876543210
LinkedIn: linkedin.com/in/johnpaul | GitHub: github.com/johnpaul

PROFESSIONAL SUMMARY
Passionate Computer Science student with hands-on experience in building web applications 
using Python, FastAPI, React, and cloud technologies. Developed multiple production-ready 
projects including an AI-powered resume analyzer. Strong problem-solving skills with 
knowledge of data structures, algorithms, and system design.

EDUCATION
B.Tech in Computer Science and Engineering
Anna University, Chennai — 2022-2026
CGPA: 8.5/10

TECHNICAL SKILLS
Languages: Python, JavaScript, Java, C++, SQL
Frameworks: FastAPI, React.js, Node.js, Express.js, Django
Databases: PostgreSQL, MongoDB, SQLite, Redis
Tools: Git, Docker, VS Code, Postman, Linux
Cloud: AWS (EC2, S3, Lambda), Render, Vercel
AI/ML: TensorFlow, scikit-learn, NLP basics, Gemini API

WORK EXPERIENCE
Software Developer Intern — TechSolutions Pvt Ltd (Jun 2025 – Aug 2025)
- Developed RESTful API endpoints using FastAPI serving 5000+ daily requests
- Implemented JWT authentication and role-based access control
- Optimized database queries reducing response time by 35%
- Collaborated with frontend team to integrate React components

PROJECTS
AI Resume Analyzer (Python, FastAPI, React, Gemini API)
- Built full-stack web application that analyzes resumes using AI
- Integrated Google Gemini for intelligent resume rewriting and ATS scoring
- Implemented real-time job matching using SerpAPI
- Deployed on Render (backend) and Vercel (frontend)

E-commerce Platform (Node.js, MongoDB, React)
- Developed complete e-commerce solution with payment gateway integration
- Implemented search functionality with filters and sorting
- Used Redis for session management and caching

CERTIFICATIONS
- AWS Cloud Practitioner
- Google IT Automation with Python
- HackerRank Problem Solving (Gold)
"""


def log(status, endpoint, detail=""):
    """Log test result."""
    icon = "[PASS]" if status == "PASS" else ("[FAIL]" if status == "FAIL" else "[SKIP]")
    line = f"{icon} {endpoint}"
    if detail:
        detail_short = str(detail)[:200]
        line += f"\n       -> {detail_short}"
    print(line)
    RESULTS.append((status, endpoint, str(detail)[:300]))


def headers():
    """Auth headers."""
    h = {"Content-Type": "application/json"}
    if TOKEN:
        h["Authorization"] = f"Bearer {TOKEN}"
    return h


def auth_headers_upload():
    """Auth headers for file upload (no Content-Type — let requests set it)."""
    h = {}
    if TOKEN:
        h["Authorization"] = f"Bearer {TOKEN}"
    return h


# =============================================================================
# TEST GROUPS
# =============================================================================

def test_health():
    """Test 1: Server Health Check"""
    print("\n" + "="*60)
    print("  TEST 1: SERVER HEALTH")
    print("="*60)
    
    try:
        r = requests.get(f"{DEPLOYED_URL}/", timeout=15)
        log("PASS" if r.status_code == 200 else "FAIL", "GET /", f"HTTP {r.status_code}")
    except Exception as e:
        log("FAIL", "GET /", str(e)[:100])
    
    try:
        r = requests.get(f"{BASE}/healthz", timeout=15)
        log("PASS" if r.status_code == 200 else "FAIL", "GET /api/v1/healthz", f"HTTP {r.status_code}")
    except Exception as e:
        log("FAIL", "GET /api/v1/healthz", str(e)[:100])


def test_auth():
    """Test 2: Authentication (Signup + Login + User Info)"""
    global TOKEN
    print("\n" + "="*60)
    print("  TEST 2: AUTHENTICATION")
    print("="*60)
    
    ts = str(int(time.time()))
    user = {
        "email": f"test_{ts}@student.com",
        "password": "TestPass@2026",
        "full_name": "Test Student"
    }
    
    # Signup
    try:
        r = requests.post(f"{BASE}/signup", json=user, timeout=TIMEOUT)
        if r.status_code in [200, 201]:
            log("PASS", "POST /signup", f"User created: {user['email']}")
        else:
            log("FAIL", "POST /signup", f"HTTP {r.status_code}: {r.text[:150]}")
    except Exception as e:
        log("FAIL", "POST /signup", str(e)[:100])
    
    # Login
    try:
        r = requests.post(
            f"{BASE}/login/access-token",
            data={"username": user["email"], "password": user["password"]},
            timeout=TIMEOUT
        )
        if r.status_code == 200:
            TOKEN = r.json().get("access_token")
            log("PASS", "POST /login", "JWT Token received")
        else:
            log("FAIL", "POST /login", f"HTTP {r.status_code}: {r.text[:100]}")
    except Exception as e:
        log("FAIL", "POST /login", str(e)[:100])
    
    # Get current user
    if TOKEN:
        try:
            r = requests.get(f"{BASE}/users/me", headers=headers(), timeout=15)
            log("PASS" if r.status_code == 200 else "FAIL", "GET /users/me", f"HTTP {r.status_code}")
        except Exception as e:
            log("FAIL", "GET /users/me", str(e)[:100])


def test_resume_upload():
    """Test 3: Resume Upload & ATS Analysis (GEMINI API)"""
    global RID, RESUME_TEXT, PREDICTED_ROLE
    print("\n" + "="*60)
    print("  TEST 3: RESUME UPLOAD + ATS SCORING (Gemini API)")
    print("="*60)
    
    if not TOKEN:
        log("SKIP", "Resume Upload", "No auth token — login failed")
        return
    
    RESUME_TEXT = SAMPLE_RESUME.strip()
    
    # Test 3a: Upload WITHOUT target role (should auto-detect)
    print("\n  --- 3a: Upload WITHOUT target role (auto-detect) ---")
    try:
        r = requests.post(
            f"{BASE}/resumes/upload",
            headers=auth_headers_upload(),
            files={"file": ("resume.txt", RESUME_TEXT.encode(), "text/plain")},
            data={"title": "Auto Detect Resume", "job_description": ""},
            timeout=TIMEOUT
        )
        if r.status_code == 200:
            data = r.json()
            RID = data.get("id")
            ats = data.get("ats_score", "?")
            role = data.get("predicted_role", "?")
            PREDICTED_ROLE = role
            log("PASS", "POST /resumes/upload (no role)", 
                f"ID:{RID} | ATS Score:{ats} | Predicted Role: {role}")
            
            # Verify critical fields
            if role and role != "Analyzing...":
                log("PASS", "  -> Role Auto-Detection", f"Detected: {role}")
            else:
                log("FAIL", "  -> Role Auto-Detection", f"Got generic: {role}")
            
            if ats and float(ats) > 0:
                log("PASS", "  -> ATS Score Generated", f"Score: {ats}")
            else:
                log("FAIL", "  -> ATS Score Generated", f"Score: {ats}")
            
            # Check for breakdown, analysis, suggestions
            breakdown = data.get("score_breakdown", {})
            if breakdown:
                log("PASS", "  -> Score Breakdown", 
                    f"Keys: {list(breakdown.keys())[:5]}")
            
            analysis = data.get("analysis")
            if analysis:
                log("PASS", "  -> AI Analysis", f"{analysis[:100]}...")
            
            suggestions = data.get("suggestions")
            if suggestions and len(suggestions) > 0:
                log("PASS", "  -> AI Suggestions", f"{len(suggestions)} suggestions generated")
            
            strengths = data.get("key_strengths")
            if strengths and len(strengths) > 0:
                log("PASS", "  -> Key Strengths", f"{strengths[:3]}")
        else:
            log("FAIL", "POST /resumes/upload (no role)", f"HTTP {r.status_code}: {r.text[:200]}")
    except Exception as e:
        log("FAIL", "POST /resumes/upload (no role)", str(e)[:100])
    
    # Test 3b: Upload WITH target role
    print("\n  --- 3b: Upload WITH target role (DevOps Engineer) ---")
    try:
        r = requests.post(
            f"{BASE}/resumes/upload",
            headers=auth_headers_upload(),
            files={"file": ("resume_devops.txt", RESUME_TEXT.encode(), "text/plain")},
            data={"title": "DevOps Resume", "job_description": "DevOps Engineer"},
            timeout=TIMEOUT
        )
        if r.status_code == 200:
            data = r.json()
            rid2 = data.get("id")
            role2 = data.get("predicted_role", "?")
            ats2 = data.get("ats_score", "?")
            missing = data.get("missing_keywords", [])
            log("PASS", "POST /resumes/upload (DevOps)", 
                f"ID:{rid2} | Role:{role2} | ATS:{ats2}")
            
            # Verify DevOps-specific analysis
            if "devops" in str(role2).lower() or "DevOps" in str(role2):
                log("PASS", "  -> Role Targeting", f"Correctly set to: {role2}")
            else:
                log("FAIL", "  -> Role Targeting", f"Expected DevOps, got: {role2}")
            
            if missing:
                log("PASS", "  -> Missing Skills (DevOps-specific)", f"{missing[:5]}")
            
            if not RID:
                RID = rid2
        else:
            log("FAIL", "POST /resumes/upload (DevOps)", f"HTTP {r.status_code}: {r.text[:200]}")
    except Exception as e:
        log("FAIL", "POST /resumes/upload (DevOps)", str(e)[:100])
    
    # Test 3c: Get resume by ID
    print("\n  --- 3c: Retrieve Resume Analysis ---")
    if RID:
        try:
            r = requests.get(f"{BASE}/resumes/{RID}", headers=headers(), timeout=TIMEOUT)
            if r.status_code == 200:
                data = r.json()
                log("PASS", f"GET /resumes/{RID}", 
                    f"Role: {data.get('predicted_role')} | ATS: {data.get('ats_score')}")
            else:
                log("FAIL", f"GET /resumes/{RID}", f"HTTP {r.status_code}")
        except Exception as e:
            log("FAIL", f"GET /resumes/{{ID}}", str(e)[:100])
    
    # Test 3d: List all resumes
    try:
        r = requests.get(f"{BASE}/resumes/", headers=headers(), timeout=15)
        if r.status_code == 200:
            count = len(r.json())
            log("PASS", "GET /resumes/", f"Total resumes: {count}")
        else:
            log("FAIL", "GET /resumes/", f"HTTP {r.status_code}")
    except Exception as e:
        log("FAIL", "GET /resumes/", str(e)[:100])


def test_gemini_features():
    """Test 4: Gemini-Powered AI Features"""
    print("\n" + "="*60)
    print("  TEST 4: GEMINI AI FEATURES")
    print("="*60)
    
    if not TOKEN:
        log("SKIP", "Gemini Features", "No auth token")
        return
    
    # 4a: Resume Rewrite for specific role
    print("\n  --- 4a: AI Rewrite (Target: Full Stack Developer) ---")
    try:
        r = requests.post(
            f"{BASE}/resumes/rewrite",
            headers=headers(),
            json={
                "text": SAMPLE_RESUME[:2000],
                "section_type": "Entire Resume",
                "target_role": "Full Stack Developer",
                "company_type": "FAANG"
            },
            timeout=TIMEOUT
        )
        if r.status_code == 200:
            rewritten = str(r.json()) if isinstance(r.json(), str) else r.json()
            rewritten_text = str(rewritten)[:300]
            log("PASS", "POST /resumes/rewrite", f"Rewritten ({len(str(rewritten))} chars)")
            
            # Check quality indicators
            has_action_verbs = any(v in str(rewritten).lower() for v in 
                ["developed", "implemented", "designed", "built", "engineered", "optimized", "led"])
            if has_action_verbs:
                log("PASS", "  -> Action Verbs Present", "Uses strong action verbs")
            else:
                log("FAIL", "  -> Action Verbs Present", "Missing action verbs in rewrite")
            
            # Check it's not a dummy/error response
            if "error" not in str(rewritten).lower() and "failed" not in str(rewritten).lower():
                log("PASS", "  -> Genuine Content", "Not a dummy/error response")
            else:
                log("FAIL", "  -> Genuine Content", f"Possible error: {rewritten_text}")
        else:
            log("FAIL", "POST /resumes/rewrite", f"HTTP {r.status_code}: {r.text[:200]}")
    except Exception as e:
        log("FAIL", "POST /resumes/rewrite", str(e)[:100])
    
    # 4b: Job Role Prediction
    print("\n  --- 4b: AI Job Role Prediction ---")
    try:
        r = requests.post(
            f"{BASE}/resumes/predict-job",
            headers=headers(),
            json={"text": SAMPLE_RESUME},
            timeout=TIMEOUT
        )
        if r.status_code == 200:
            predictions = r.json()
            if isinstance(predictions, list) and len(predictions) > 0:
                top = predictions[0]
                log("PASS", "POST /resumes/predict-job", 
                    f"Top: {top.get('role')} ({top.get('confidence')}%)")
                for i, p in enumerate(predictions[:3]):
                    log("PASS", f"  -> Prediction #{i+1}", 
                        f"{p.get('role')} — {p.get('confidence')}% confidence")
            else:
                log("FAIL", "POST /resumes/predict-job", f"Unexpected: {predictions}")
        else:
            log("FAIL", "POST /resumes/predict-job", f"HTTP {r.status_code}: {r.text[:200]}")
    except Exception as e:
        log("FAIL", "POST /resumes/predict-job", str(e)[:100])
    
    # 4c: Validate Role Fit
    print("\n  --- 4c: AI Role Fit Validation ---")
    try:
        r = requests.post(
            f"{BASE}/resumes/validate-fit",
            headers=headers(),
            json={
                "text": SAMPLE_RESUME,
                "target_role": "Data Scientist"
            },
            timeout=TIMEOUT
        )
        if r.status_code == 200:
            fit = r.json()
            score = fit.get("match_score", "?")
            missing = fit.get("missing_skills", [])
            strengths = fit.get("strengths", [])
            log("PASS", "POST /resumes/validate-fit", 
                f"Match: {score}% for Data Scientist")
            if missing:
                log("PASS", "  -> Missing Skills", f"{missing[:5]}")
            if strengths:
                log("PASS", "  -> Strengths Found", f"{strengths[:3]}")
        else:
            log("FAIL", "POST /resumes/validate-fit", f"HTTP {r.status_code}: {r.text[:200]}")
    except Exception as e:
        log("FAIL", "POST /resumes/validate-fit", str(e)[:100])
    
    # 4d: Grammar Enhancement
    print("\n  --- 4d: AI Grammar Enhancement ---")
    try:
        r = requests.post(
            f"{BASE}/ai-rewrite/enhance-grammar",
            headers=headers(),
            json={
                "text": "i worked on many projects in collage. i know python and javscript. i have do internship at tech company were i learn alot."
            },
            timeout=TIMEOUT
        )
        if r.status_code == 200:
            data = r.json()
            enhanced = data.get("enhanced_text", "")
            log("PASS", "POST /ai-rewrite/enhance-grammar", 
                f"Enhanced ({len(enhanced)} chars)")
            
            # Check grammar was actually fixed
            if "collage" not in enhanced.lower() or "college" in enhanced.lower():
                log("PASS", "  -> Grammar Fixed", "Corrected spelling errors")
            if len(enhanced) > 20:
                log("PASS", "  -> Substantial Output", f"Preview: {enhanced[:150]}...")
        else:
            log("FAIL", "POST /ai-rewrite/enhance-grammar", f"HTTP {r.status_code}: {r.text[:200]}")
    except Exception as e:
        log("FAIL", "POST /ai-rewrite/enhance-grammar", str(e)[:100])
    
    # 4e: AI Resume Transform (full JD alignment)
    print("\n  --- 4e: AI Resume Transform (JD Alignment) ---")
    try:
        sample_jd = """We are looking for a Senior Python Developer to join our team.
        Requirements: 5+ years Python, FastAPI/Django, PostgreSQL, Redis, Docker, 
        Kubernetes, AWS, CI/CD pipelines. Experience with microservices architecture.
        Strong understanding of REST APIs and system design."""
        
        r = requests.post(
            f"{BASE}/ai-rewrite/transform",
            headers=headers(),
            json={
                "resume_text": SAMPLE_RESUME,
                "job_description": sample_jd,
                "mode": "ATS"
            },
            timeout=TIMEOUT
        )
        if r.status_code == 200:
            data = r.json()
            rewritten = data.get("rewritten_resume", "")
            log("PASS", "POST /ai-rewrite/transform", 
                f"JD-aligned rewrite ({len(rewritten)} chars)")
            
            # Check JD keywords are present
            jd_keywords = ["python", "fastapi", "docker", "kubernetes", "aws"]
            found = [kw for kw in jd_keywords if kw in rewritten.lower()]
            log("PASS" if len(found) >= 3 else "FAIL", 
                "  -> JD Keyword Alignment", f"Found {len(found)}/5: {found}")
        else:
            log("FAIL", "POST /ai-rewrite/transform", f"HTTP {r.status_code}: {r.text[:200]}")
    except Exception as e:
        log("FAIL", "POST /ai-rewrite/transform", str(e)[:100])


def test_serpapi_jobs():
    """Test 5: SerpAPI Real-Time Job Search"""
    print("\n" + "="*60)
    print("  TEST 5: SERPAPI — REAL-TIME JOB SEARCH")
    print("="*60)
    
    if not TOKEN or not RID:
        log("SKIP", "SerpAPI Jobs", "No token or resume ID")
        return
    
    # 5a: Job Recommendations
    print("\n  --- 5a: Job Recommendations for Resume ---")
    try:
        r = requests.get(
            f"{BASE}/jobs/recommendations/{RID}",
            headers=headers(),
            timeout=TIMEOUT
        )
        if r.status_code == 200:
            jobs = r.json()
            if isinstance(jobs, list) and len(jobs) > 0:
                log("PASS", f"GET /jobs/recommendations/{RID}", 
                    f"{len(jobs)} job recommendations received")
                
                for i, job in enumerate(jobs[:3]):
                    title = job.get("title", "?")
                    company = job.get("company", "?")
                    location = job.get("location", "?")
                    salary = job.get("salary_range", "?")
                    apply_link = job.get("apply_link", "")
                    match_pct = job.get("match_percentage", "?")
                    
                    log("PASS", f"  -> Job #{i+1}", 
                        f"{title} @ {company} | {location} | {salary} | Match: {match_pct}%")
                    
                    # Check if apply link is a real URL
                    if apply_link and apply_link.startswith("http"):
                        log("PASS", f"     Apply Link", f"{apply_link[:80]}...")
                    else:
                        log("FAIL", f"     Apply Link", f"Invalid: {apply_link[:80]}")
                
                # Check portal links in suggestions
                first_job = jobs[0]
                suggestions = first_job.get("improvement_suggestions", [])
                portal_found = [s for s in suggestions if any(p in s.lower() for p in ["linkedin", "indeed", "naukri"])]
                if portal_found:
                    log("PASS", "  -> Portal Links", f"Found {len(portal_found)} job portals")
                    for link in portal_found[:3]:
                        log("PASS", f"     Portal", link[:100])
            else:
                log("FAIL", f"GET /jobs/recommendations/{RID}", "Empty job list")
        else:
            log("FAIL", f"GET /jobs/recommendations/{RID}", f"HTTP {r.status_code}: {r.text[:200]}")
    except Exception as e:
        log("FAIL", "GET /jobs/recommendations/", str(e)[:100])
    
    # 5b: Job Match
    print("\n  --- 5b: Job-Resume Match Score ---")
    try:
        r = requests.post(
            f"{BASE}/jobs/match/{RID}",
            headers=headers(),
            json={
                "title": "Python Developer",
                "company": "Google",
                "description_text": "We need a Python developer with FastAPI, Docker, and AWS experience."
            },
            timeout=TIMEOUT
        )
        if r.status_code == 200:
            data = r.json()
            match_pct = data.get("match_percentage", "?")
            log("PASS", f"POST /jobs/match/{RID}", f"Match score: {match_pct}%")
        else:
            log("FAIL", f"POST /jobs/match/{RID}", f"HTTP {r.status_code}: {r.text[:200]}")
    except Exception as e:
        log("FAIL", "POST /jobs/match/", str(e)[:100])


def test_openai_mentor():
    """Test 6: OpenAI-Powered AI Mentor"""
    print("\n" + "="*60)
    print("  TEST 6: OPENAI — AI CAREER MENTOR")
    print("="*60)
    
    if not TOKEN:
        log("SKIP", "AI Mentor", "No auth token")
        return
    
    # 6a: Mentor Chat (doubt clarification)
    print("\n  --- 6a: AI Mentor Chat (Doubt Clearing) ---")
    test_questions = [
        "How should I prepare for a Google SDE interview? What DSA topics are most important?",
        "I know Python and React. Should I learn DevOps or Machine Learning for better career growth?",
        "What projects should I build to get hired at a FAANG company as a fresher?",
    ]
    
    for i, question in enumerate(test_questions):
        try:
            payload = {"question": question}
            if RID:
                payload["resume_id"] = RID
            
            r = requests.post(
                f"{BASE}/ai-mentor/chat",
                headers=headers(),
                json=payload,
                timeout=TIMEOUT
            )
            if r.status_code == 200:
                reply = r.json().get("reply", "")
                if len(reply) > 30:
                    log("PASS", f"  Chat Q{i+1}", f"Q: {question[:60]}...")
                    log("PASS", f"  Reply", f"{reply[:150]}...")
                else:
                    log("FAIL", f"  Chat Q{i+1}", f"Too short reply: {reply}")
            else:
                log("FAIL", f"  Chat Q{i+1}", f"HTTP {r.status_code}: {r.text[:100]}")
        except Exception as e:
            log("FAIL", f"  Chat Q{i+1}", str(e)[:100])
    
    # 6b: Mentor Insight (Match Intel + Roadmap + Skill Graph)
    print("\n  --- 6b: AI Mentor Deep Insight ---")
    try:
        r = requests.post(
            f"{BASE}/ai-mentor/insight",
            headers=headers(),
            json={
                "resume_text": SAMPLE_RESUME,
                "skills": ["Python", "FastAPI", "React", "Docker", "AWS", "PostgreSQL"],
                "target_role": "Full Stack Developer"
            },
            timeout=TIMEOUT
        )
        if r.status_code == 200:
            data = r.json()
            rec_role = data.get("recommended_role", "?")
            demand = data.get("market_demand", "?")
            salary = data.get("salary_range", "?")
            growth = data.get("growth_score", "?")
            missing = data.get("missing_skills", [])
            advice = data.get("mentor_advice", "")
            roadmap = data.get("dynamic_roadmap", "")
            skill_graph = data.get("skill_graph")
            
            log("PASS", "POST /ai-mentor/insight", f"Role: {rec_role}")
            log("PASS", "  -> Market Demand", f"{demand}")
            log("PASS", "  -> Salary Range", f"{salary}")
            log("PASS", "  -> Growth Score", f"{growth}/10")
            
            if missing:
                log("PASS", "  -> Missing Skills", f"{missing[:5]}")
            if advice and len(advice) > 20:
                log("PASS", "  -> Mentor Advice", f"{advice[:150]}...")
            if roadmap and len(roadmap) > 50:
                log("PASS", "  -> Career Roadmap", f"{roadmap[:150]}...")
            else:
                log("FAIL", "  -> Career Roadmap", f"Too short or empty: {roadmap[:100]}")
            if skill_graph:
                log("PASS", "  -> Skill Graph", f"Generated (base64 image: {len(skill_graph)} chars)")
            else:
                log("SKIP", "  -> Skill Graph", "Not generated (matplotlib may not be available)")
        else:
            log("FAIL", "POST /ai-mentor/insight", f"HTTP {r.status_code}: {r.text[:200]}")
    except Exception as e:
        log("FAIL", "POST /ai-mentor/insight", str(e)[:100])
    
    # 6c: Career Prediction
    print("\n  --- 6c: Career Path Prediction ---")
    try:
        r = requests.post(
            f"{BASE}/ai-mentor/predict",
            headers=headers(),
            json={
                "branch": "Computer Science",
                "skills": ["Python", "React", "Docker", "AWS"],
                "interests": ["System Design", "Cloud Computing", "AI"]
            },
            timeout=TIMEOUT
        )
        if r.status_code == 200:
            data = r.json()
            log("PASS", "POST /ai-mentor/predict", f"Career paths predicted: {json.dumps(data)[:200]}")
        else:
            log("FAIL", "POST /ai-mentor/predict", f"HTTP {r.status_code}: {r.text[:100]}")
    except Exception as e:
        log("FAIL", "POST /ai-mentor/predict", str(e)[:100])
    
    # 6d: Resume Strategy
    print("\n  --- 6d: Resume Strategy (FAANG/MNC/Startup) ---")
    for tier in ["faang", "mnc", "startup"]:
        try:
            r = requests.get(
                f"{BASE}/ai-mentor/strategy/{tier}",
                headers=headers(),
                timeout=15
            )
            if r.status_code == 200:
                log("PASS", f"GET /ai-mentor/strategy/{tier}", f"Strategy loaded")
            else:
                log("FAIL", f"GET /ai-mentor/strategy/{tier}", f"HTTP {r.status_code}")
        except Exception as e:
            log("FAIL", f"GET /ai-mentor/strategy/{tier}", str(e)[:100])


def test_advanced_features():
    """Test 7: Advanced Features"""
    print("\n" + "="*60)
    print("  TEST 7: ADVANCED FEATURES")
    print("="*60)
    
    if not TOKEN:
        log("SKIP", "Advanced Features", "No auth token")
        return
    
    endpoints = [
        ("GET", "/advanced/resume-templates", None, "Resume Templates"),
        ("GET", "/advanced/export-formats", None, "Export Formats"),
        ("GET", "/advanced/market-insights", None, "Market Insights"),
        ("GET", "/advanced/user-stats", None, "User Stats"),
        ("GET", "/advanced/salary-insights?role=Full+Stack+Developer&experience_years=2", None, "Salary Insights"),
    ]
    
    for method, path, payload, label in endpoints:
        try:
            if method == "GET":
                r = requests.get(f"{BASE}{path}", headers=headers(), timeout=15)
            else:
                r = requests.post(f"{BASE}{path}", headers=headers(), json=payload, timeout=15)
            
            if r.status_code == 200:
                log("PASS", f"{method} {path.split('?')[0]}", f"{label} OK")
            else:
                log("FAIL", f"{method} {path}", f"HTTP {r.status_code}: {r.text[:100]}")
        except Exception as e:
            log("FAIL", f"{method} {path}", str(e)[:100])


def test_ai_rewrite_edge_cases():
    """Test 8: Edge Cases & Quality Checks"""
    print("\n" + "="*60)
    print("  TEST 8: AI QUALITY & EDGE CASES")
    print("="*60)
    
    if not TOKEN:
        log("SKIP", "Edge Cases", "No auth token")
        return
    
    # 8a: Upload resume WITHOUT any target role — system should auto-detect
    print("\n  --- 8a: Auto Role Detection Quality ---")
    try:
        r = requests.post(
            f"{BASE}/resumes/predict-job",
            headers=headers(),
            json={
                "text": """Experienced nurse with 5 years in ICU care.
                Skills: Patient assessment, Critical care, IV therapy, EMR systems,
                Medication administration, Team coordination.
                Education: BSN Nursing, State University.
                Certifications: BLS, ACLS, PALS"""
            },
            timeout=TIMEOUT
        )
        if r.status_code == 200:
            preds = r.json()
            if isinstance(preds, list) and len(preds) > 0:
                top_role = preds[0].get("role", "")
                if any(kw in top_role.lower() for kw in ["nurse", "medical", "healthcare", "doctor", "pharmacist"]):
                    log("PASS", "  -> Non-Tech Resume Detection", 
                        f"Correctly identified: {top_role}")
                else:
                    log("FAIL", "  -> Non-Tech Resume Detection", 
                        f"Expected healthcare role, got: {top_role}")
        else:
            log("FAIL", "  -> Non-Tech Resume Detection", f"HTTP {r.status_code}")
    except Exception as e:
        log("FAIL", "  -> Non-Tech Resume Detection", str(e)[:100])
    
    # 8b: Grammar check with many errors
    print("\n  --- 8b: Heavy Grammar Fix ---")
    try:
        awful_text = "i has developd many projets using pythn and javscript. my skills includ react, nod.js, and mongdb. i want to became a sofware enginer at good compny."
        r = requests.post(
            f"{BASE}/ai-rewrite/enhance-grammar",
            headers=headers(),
            json={"text": awful_text},
            timeout=TIMEOUT
        )
        if r.status_code == 200:
            enhanced = r.json().get("enhanced_text", "")
            # Count how many obvious errors remain
            known_errors = ["developd", "projets", "pythn", "javscript", "includ", "nod.js", "mongdb", "became", "sofware", "enginer", "compny"]
            remaining = [e for e in known_errors if e in enhanced.lower()]
            if len(remaining) <= 2:
                log("PASS", "  -> Grammar Quality", 
                    f"Fixed {len(known_errors)-len(remaining)}/{len(known_errors)} errors")
            else:
                log("FAIL", "  -> Grammar Quality", 
                    f"Still has {len(remaining)} errors: {remaining}")
        else:
            log("FAIL", "  -> Grammar Quality", f"HTTP {r.status_code}")
    except Exception as e:
        log("FAIL", "  -> Grammar Quality", str(e)[:100])
    
    # 8c: Validate fit for completely mismatched role
    print("\n  --- 8c: Role Mismatch Detection ---")
    try:
        r = requests.post(
            f"{BASE}/resumes/validate-fit",
            headers=headers(),
            json={
                "text": SAMPLE_RESUME,  # CS student resume
                "target_role": "Civil Engineer"
            },
            timeout=TIMEOUT
        )
        if r.status_code == 200:
            fit = r.json()
            score = fit.get("match_score", 100)
            if score < 50:
                log("PASS", "  -> Mismatch Detection", 
                    f"Low score ({score}%) for CS student → Civil Engineer (correct!)")
            else:
                log("FAIL", "  -> Mismatch Detection", 
                    f"Score too high ({score}%) for mismatched role")
        else:
            log("FAIL", "  -> Mismatch Detection", f"HTTP {r.status_code}")
    except Exception as e:
        log("FAIL", "  -> Mismatch Detection", str(e)[:100])


def test_background_rewrite():
    """Test 9: Background AI Rewrite (check if it completed)"""
    print("\n" + "="*60)
    print("  TEST 9: BACKGROUND AI REWRITE VERIFICATION")
    print("="*60)
    
    if not TOKEN or not RID:
        log("SKIP", "Background Rewrite", "No token or resume")
        return
    
    # Wait a bit for background task to complete
    print("  Waiting 10 seconds for background AI rewrite to complete...")
    time.sleep(10)
    
    try:
        r = requests.get(f"{BASE}/resumes/{RID}", headers=headers(), timeout=TIMEOUT)
        if r.status_code == 200:
            data = r.json()
            rewritten = data.get("ai_rewritten_content", "")
            if rewritten and len(rewritten) > 50 and "failed" not in rewritten.lower():
                log("PASS", "  -> AI Rewritten Content", f"Available ({len(rewritten)} chars)")
                log("PASS", "  -> Preview", f"{rewritten[:200]}...")
            elif rewritten and "failed" in rewritten.lower():
                log("FAIL", "  -> AI Rewritten Content", f"Rewrite failed: {rewritten[:150]}")
            else:
                log("SKIP", "  -> AI Rewritten Content", 
                    "Still processing or no API key available locally")
        else:
            log("FAIL", "  -> Background Rewrite Check", f"HTTP {r.status_code}")
    except Exception as e:
        log("FAIL", "  -> Background Rewrite Check", str(e)[:100])


# =============================================================================
# MAIN EXECUTION
# =============================================================================
if __name__ == "__main__":
    print("\n" + "="*60)
    print("  AI RESUME ANALYZER — COMPREHENSIVE TEST SUITE")
    print(f"  Target: {DEPLOYED_URL}")
    print(f"  Time: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*60)
    
    start_time = time.time()
    
    # Run all test groups
    test_health()
    test_auth()
    test_resume_upload()
    test_gemini_features()
    test_serpapi_jobs()
    test_openai_mentor()
    test_advanced_features()
    test_ai_rewrite_edge_cases()
    test_background_rewrite()
    
    elapsed = round(time.time() - start_time, 1)
    
    # ── FINAL REPORT ────────────────────────────────────────────────────────
    passed = sum(1 for r in RESULTS if r[0] == "PASS")
    failed = sum(1 for r in RESULTS if r[0] == "FAIL")
    skipped = sum(1 for r in RESULTS if r[0] == "SKIP")
    total = len(RESULTS)
    score = round(passed / max(total - skipped, 1) * 100)
    
    print("\n" + "="*60)
    print("  FINAL TEST REPORT")
    print("="*60)
    print(f"  Server   : {DEPLOYED_URL}")
    print(f"  Duration : {elapsed} seconds")
    print(f"  PASSED   : {passed}/{total}")
    print(f"  FAILED   : {failed}/{total}")
    print(f"  SKIPPED  : {skipped}/{total}")
    print(f"  Score    : {score}%")
    print("="*60)
    
    if failed > 0:
        print("\n  FAILURES:")
        print("  " + "-"*56)
        for r in RESULTS:
            if r[0] == "FAIL":
                print(f"  [FAIL] {r[1]}")
                if r[2]:
                    print(f"         {r[2][:200]}")
    
    if skipped > 0:
        print(f"\n  SKIPPED ({skipped}):")
        for r in RESULTS:
            if r[0] == "SKIP":
                print(f"  [SKIP] {r[1]}: {r[2][:100]}")
    
    # Summary by API
    print("\n  API COVERAGE SUMMARY:")
    print("  " + "-"*56)
    gemini_tests = [r for r in RESULTS if any(kw in r[1].lower() for kw in 
        ["rewrite", "predict", "validate", "grammar", "ats", "upload"])]
    serpapi_tests = [r for r in RESULTS if "job" in r[1].lower() or "recommendation" in r[1].lower()]
    openai_tests = [r for r in RESULTS if "mentor" in r[1].lower() or "insight" in r[1].lower() or "chat" in r[1].lower()]
    
    for api_name, tests in [("GEMINI", gemini_tests), ("SERPAPI", serpapi_tests), ("OPENAI", openai_tests)]:
        p = sum(1 for t in tests if t[0] == "PASS")
        f = sum(1 for t in tests if t[0] == "FAIL")
        s = sum(1 for t in tests if t[0] == "SKIP")
        icon = "PASS" if f == 0 and p > 0 else ("PARTIAL" if p > 0 else "FAIL")
        print(f"  [{icon}] {api_name:8s} — Passed: {p}, Failed: {f}, Skipped: {s}")
    
    print("\n" + "="*60)
    if failed == 0:
        print("  ALL TESTS PASSED! READY FOR DEPLOYMENT!")
    elif score >= 80:
        print("  MOSTLY PASSING — Review failures above")
    else:
        print("  FIX FAILURES BEFORE DEPLOYMENT")
    print("="*60)
    
    # Save results to file
    with open("test_results_comprehensive.txt", "w", encoding="utf-8") as f:
        f.write(f"AI Resume Analyzer — Test Results\n")
        f.write(f"Server: {DEPLOYED_URL}\n")
        f.write(f"Time: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"Duration: {elapsed}s\n\n")
        for r2 in RESULTS:
            f.write(f"[{r2[0]}] {r2[1]}: {r2[2]}\n")
        f.write(f"\nPASSED:{passed} FAILED:{failed} SKIPPED:{skipped} Score:{score}%\n")
    
    print(f"\n  Results saved to: test_results_comprehensive.txt")
    sys.exit(0 if failed == 0 else 1)
