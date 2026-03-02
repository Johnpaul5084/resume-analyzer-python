from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pathlib import Path
from app.api import dependencies as deps
from app.db.session import get_db
from app.models.all_models import Resume, JobDescription, User
from app.schemas.all_schemas import JobMatchResult, JobDescriptionCreate
from typing import List
import urllib.parse
import os
import logging
import requests

logger = logging.getLogger(__name__)
router = APIRouter()


# ─────────────────────────────────────────────────────────────────────────────
# Real apply links for job portal searches
# ─────────────────────────────────────────────────────────────────────────────
def _portal_links(role: str, company: str = "", location: str = "India"):
    q      = urllib.parse.quote_plus(f"{role} {company}".strip())
    role_q = urllib.parse.quote_plus(role)
    slug   = role.lower().replace(" ", "-")
    return {
        "linkedin":  f"https://www.linkedin.com/jobs/search/?keywords={q}&location={urllib.parse.quote_plus(location)}&f_TPR=r2592000",
        "indeed":    f"https://in.indeed.com/jobs?q={q}&l={urllib.parse.quote_plus(location)}",
        "naukri":    f"https://www.naukri.com/{slug}-jobs",
        "glassdoor": f"https://www.glassdoor.co.in/Jobs/{slug}-jobs-SRCH_KO0,{len(role)}.htm",
    }


# ─────────────────────────────────────────────────────────────────────────────
# SerpAPI — fetch REAL live job listings
# ─────────────────────────────────────────────────────────────────────────────
def _serpapi_jobs(role: str, location: str = "India", num: int = 8) -> list:
    """
    Calls SerpAPI Google Jobs endpoint.
    Returns list of real live job dicts.
    """
    from dotenv import load_dotenv, dotenv_values
    load_dotenv(Path(__file__).resolve().parent.parent.parent.parent / ".env", override=True)

    api_key = os.getenv("SERPAPI_API_KEY", "") or dotenv_values(Path(__file__).resolve().parent.parent.parent.parent / ".env").get("SERPAPI_API_KEY")
    if not api_key:
        raise ValueError("SERPAPI_API_KEY not set")

    params = {
        "engine":   "google_jobs",
        "q":        f"{role} jobs in {location}",
        "hl":       "en",
        "gl":       "in",     # Google India
        "api_key":  api_key,
    }
    resp = requests.get("https://serpapi.com/search", params=params, timeout=15)
    resp.raise_for_status()
    data = resp.json()

    jobs = []
    for item in data.get("jobs_results", [])[:num]:
        # Extract salary if available
        salary = ""
        for ext in (item.get("job_highlights") or []):
            if "Salary" in ext.get("title", "") or "Pay" in ext.get("title", ""):
                items = ext.get("items", [])
                if items:
                    salary = items[0]
                    break

        apply_link = ""
        # Try to get the direct apply link
        for opt in (item.get("apply_options") or []):
            if opt.get("link"):
                apply_link = opt["link"]
                break

        jobs.append({
            "title":        item.get("title", role),
            "company":      item.get("company_name", ""),
            "location":     item.get("location", location),
            "salary_range": salary or "Competitive",
            "posted_date":  item.get("detected_extensions", {}).get("posted_at", "Recently"),
            "apply_link":   apply_link,
            "description":  (item.get("description") or "")[:300],
        })

    return jobs


# ─────────────────────────────────────────────────────────────────────────────
# Curated role-specific fallback (used when SerpAPI unavailable)
# ─────────────────────────────────────────────────────────────────────────────
_ROLE_JOBS = {
    "java": [
        {"title": "Java Full Stack Developer",   "company": "Infosys",          "location": "Bangalore",  "salary_range": "8-18 LPA"},
        {"title": "Senior Java Developer",        "company": "TCS",              "location": "Hyderabad",  "salary_range": "12-22 LPA"},
        {"title": "Java Backend Engineer",        "company": "Wipro",            "location": "Pune",       "salary_range": "10-20 LPA"},
        {"title": "Spring Boot Developer",        "company": "HCL",              "location": "Chennai",    "salary_range": "9-16 LPA"},
        {"title": "Java Microservices Architect", "company": "Accenture",        "location": "Bangalore",  "salary_range": "18-32 LPA"},
        {"title": "Full Stack Java Engineer",     "company": "Capgemini",        "location": "Mumbai",     "salary_range": "10-18 LPA"},
    ],
    "devops": [
        {"title": "DevOps Engineer",              "company": "Amazon India",     "location": "Hyderabad",  "salary_range": "12-22 LPA"},
        {"title": "Senior DevOps Engineer",       "company": "Google India",     "location": "Bangalore",  "salary_range": "20-40 LPA"},
        {"title": "Cloud DevOps Engineer",        "company": "Microsoft",        "location": "Hyderabad",  "salary_range": "18-35 LPA"},
        {"title": "SRE / DevOps Specialist",      "company": "Flipkart",         "location": "Bangalore",  "salary_range": "15-28 LPA"},
        {"title": "Platform Engineer (K8s)",      "company": "Paytm",            "location": "Noida",      "salary_range": "14-25 LPA"},
        {"title": "DevOps Lead",                  "company": "Publicis Sapient", "location": "Gurugram",   "salary_range": "22-38 LPA"},
    ],
    "data": [
        {"title": "Data Scientist",               "company": "IBM India",        "location": "Bangalore",  "salary_range": "12-22 LPA"},
        {"title": "ML Engineer",                  "company": "Swiggy",           "location": "Bangalore",  "salary_range": "15-28 LPA"},
        {"title": "AI/ML Developer",              "company": "TCS",              "location": "Hyderabad",  "salary_range": "10-20 LPA"},
        {"title": "Data Analyst",                 "company": "Deloitte",         "location": "Pune",       "salary_range": "8-16 LPA"},
        {"title": "Senior Data Engineer",         "company": "Walmart Labs",     "location": "Bangalore",  "salary_range": "18-32 LPA"},
        {"title": "NLP Research Engineer",        "company": "Freshworks",       "location": "Chennai",    "salary_range": "14-24 LPA"},
    ],
    "python": [
        {"title": "Python Developer",             "company": "Zoho",             "location": "Chennai",    "salary_range": "8-16 LPA"},
        {"title": "Senior Python Engineer",       "company": "Freshworks",       "location": "Bangalore",  "salary_range": "14-26 LPA"},
        {"title": "Backend Python Developer",     "company": "Swiggy",           "location": "Bangalore",  "salary_range": "12-22 LPA"},
        {"title": "Django/FastAPI Developer",     "company": "Mphasis",          "location": "Pune",       "salary_range": "9-18 LPA"},
        {"title": "Python Full Stack Engineer",   "company": "LTIMindtree",      "location": "Hyderabad",  "salary_range": "10-20 LPA"},
        {"title": "Python Data Engineer",         "company": "Capgemini",        "location": "Mumbai",     "salary_range": "11-19 LPA"},
    ],
    "react": [
        {"title": "React Developer",              "company": "Infosys",          "location": "Bangalore",  "salary_range": "8-18 LPA"},
        {"title": "Senior Frontend Engineer",     "company": "Groww",            "location": "Bangalore",  "salary_range": "15-28 LPA"},
        {"title": "React / Next.js Developer",    "company": "Razorpay",         "location": "Bangalore",  "salary_range": "14-25 LPA"},
        {"title": "UI Engineer (React)",          "company": "Accenture",        "location": "Hyderabad",  "salary_range": "10-20 LPA"},
        {"title": "Full Stack React Developer",   "company": "Wipro",            "location": "Pune",       "salary_range": "12-22 LPA"},
        {"title": "Frontend Architect",           "company": "KPMG India",       "location": "Mumbai",     "salary_range": "20-35 LPA"},
    ],
    "android": [
        {"title": "Android Developer",            "company": "Paytm",            "location": "Noida",      "salary_range": "9-18 LPA"},
        {"title": "Senior Android Engineer",      "company": "Flipkart",         "location": "Bangalore",  "salary_range": "15-28 LPA"},
        {"title": "Kotlin Developer",             "company": "Swiggy",           "location": "Bangalore",  "salary_range": "12-22 LPA"},
        {"title": "Mobile Developer (Android)",   "company": "Razorpay",         "location": "Bangalore",  "salary_range": "14-26 LPA"},
        {"title": "Android SDK Engineer",         "company": "Samsung India",    "location": "Noida",      "salary_range": "10-20 LPA"},
        {"title": "Lead Android Developer",       "company": "Ola",              "location": "Bangalore",  "salary_range": "20-35 LPA"},
    ],
    "cloud": [
        {"title": "Cloud Architect",              "company": "AWS India",        "location": "Hyderabad",  "salary_range": "25-50 LPA"},
        {"title": "Azure Cloud Engineer",         "company": "Microsoft India",  "location": "Hyderabad",  "salary_range": "18-35 LPA"},
        {"title": "GCP Solutions Engineer",       "company": "Google India",     "location": "Bangalore",  "salary_range": "22-40 LPA"},
        {"title": "Cloud DevOps Engineer",        "company": "Infosys",          "location": "Bangalore",  "salary_range": "12-24 LPA"},
        {"title": "Cloud Platform Engineer",      "company": "Cognizant",        "location": "Chennai",    "salary_range": "14-26 LPA"},
        {"title": "Multi-Cloud Consultant",       "company": "Deloitte",         "location": "Pune",       "salary_range": "20-38 LPA"},
    ],
}

def _curated_jobs(role: str, base_score: float) -> list:
    rl = role.lower()
    for key, jobs in _ROLE_JOBS.items():
        if key in rl:
            return [{**j, "match_score": round(max(base_score - i * 3, 60), 1)} for i, j in enumerate(jobs)]
    # Generic fallback
    generic = [
        {"title": f"{role} Engineer",         "company": "TCS",       "location": "Bangalore", "salary_range": "10-20 LPA"},
        {"title": f"Senior {role} Specialist","company": "Accenture", "location": "Hyderabad", "salary_range": "14-26 LPA"},
        {"title": f"{role} Developer",        "company": "Infosys",   "location": "Pune",      "salary_range": "9-18 LPA"},
        {"title": f"Lead {role} Engineer",    "company": "Cognizant", "location": "Chennai",   "salary_range": "16-28 LPA"},
        {"title": f"{role} Consultant",       "company": "IBM India", "location": "Mumbai",    "salary_range": "18-32 LPA"},
        {"title": f"Junior {role} Developer", "company": "HCL",       "location": "Noida",     "salary_range": "5-10 LPA"},
    ]
    return [{**j, "match_score": round(max(base_score - i * 3, 60), 1)} for i, j in enumerate(generic)]


# ─────────────────────────────────────────────────────────────────────────────
# Build final result object for each job
# ─────────────────────────────────────────────────────────────────────────────
def _build_result(idx: int, job: dict, base_score: float) -> dict:
    title    = job.get("title", "Engineer")
    company  = job.get("company", "")
    location = job.get("location", "India")
    links    = _portal_links(title, company, location)

    # Prefer the real direct link from SerpAPI; fall back to LinkedIn search
    apply_link = job.get("apply_link") or links["linkedin"]

    match_score = float(job.get("match_score", max(base_score - idx * 3, 60)))

    return {
        "job_id":           idx + 1,
        "match_percentage": round(match_score, 1),
        "missing_skills":   [],
        "improvement_suggestions": [
            f"LinkedIn: {links['linkedin']}",
            f"Indeed: {links['indeed']}",
            f"Naukri: {links['naukri']}",
        ],
        "title":        title,
        "company":      company,
        "location":     location,
        "salary_range": job.get("salary_range", "Competitive"),
        "posted_date":  job.get("posted_date", "Recently posted"),
        "apply_link":   apply_link,
        "logo":         None,
    }


# ─────────────────────────────────────────────────────────────────────────────
# Endpoints
# ─────────────────────────────────────────────────────────────────────────────
@router.get("/recommendations/{resume_id}", response_model=List[JobMatchResult])
def recommend_jobs(
    resume_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.get_current_user),
):
    """
    Returns real live job recommendations using SerpAPI (primary).
    Falls back to curated role-specific list if SerpAPI is unavailable.
    """
    resume = db.query(Resume).filter(
        Resume.id == resume_id,
        Resume.owner_id == current_user.id
    ).first()
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")

    role       = (resume.predicted_role or "Software Engineer").strip()
    base_score = resume.ats_score or 70

    raw_jobs: list = []

    # ── Primary: SerpAPI live search ─────────────────────────────────────────
    from dotenv import load_dotenv, dotenv_values
    load_dotenv(Path(__file__).resolve().parent.parent.parent.parent / ".env", override=True)
    serp_key = os.getenv("SERPAPI_API_KEY", "") or dotenv_values(Path(__file__).resolve().parent.parent.parent.parent / ".env").get("SERPAPI_API_KEY")

    if serp_key:
        try:
            logger.info(f"Fetching SerpAPI jobs for role: {role}")
            raw_jobs = _serpapi_jobs(role, location="India", num=8)
            logger.info(f"SerpAPI returned {len(raw_jobs)} jobs")
        except Exception as e:
            logger.warning(f"SerpAPI failed: {e} — using curated fallback")

    # ── Fallback: curated role-specific list ─────────────────────────────────
    if not raw_jobs:
        logger.info(f"Using curated jobs for role: {role}")
        raw_jobs = _curated_jobs(role, base_score)

    results = [_build_result(i, job, base_score) for i, job in enumerate(raw_jobs[:8])]
    results.sort(key=lambda x: x["match_percentage"], reverse=True)
    return results


@router.post("/match/{resume_id}")
def match_job_to_resume(
    resume_id: int,
    job_desc: JobDescriptionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.get_current_user),
):
    resume = db.query(Resume).filter(
        Resume.id == resume_id, Resume.owner_id == current_user.id
    ).first()
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")
    return {"match_percentage": 75, "missing_skills": [], "improvement_suggestions": []}


@router.post("/")
def create_job(
    job_in: JobDescriptionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.get_current_user),
):
    db_job = JobDescription(
        title=job_in.title,
        company=job_in.company,
        description_text=job_in.description_text,
        required_skills={},
    )
    db.add(db_job)
    db.commit()
    return job_in
