from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.api import dependencies as deps
from app.db.session import get_db
from app.models.all_models import Resume, JobDescription, User
from app.schemas.all_schemas import JobMatchResult, JobDescriptionCreate
from app.services.ats_scoring_service import ATSScoringService
from typing import List

router = APIRouter()

@router.post("/match/{resume_id}", response_model=JobMatchResult)
def match_job_to_resume(
    resume_id: int,
    job_desc: JobDescriptionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.get_current_user),
):
    """
    Match a resume against a specific job description provided by the user (or scraped).
    Returns a detailed match analysis.
    """
    resume = db.query(Resume).filter(Resume.id == resume_id, Resume.owner_id == current_user.id).first()
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")
        
    # Analyze
    result = ATSScoringService.calculate_score(resume.content_text, job_desc.description_text)
    
    # Generate suggestions
    suggestions = []
    if result['missing_keywords']:
        suggestions.append(f"Add missing keywords: {', '.join(result['missing_keywords'][:5])}")
    
    if result['breakdown']['structure_score'] < 70:
        suggestions.append("Improve resume structure and formatting.")

    return {
        "match_percentage": result['ats_score'],
        "missing_skills": result['missing_keywords'],
        "improvement_suggestions": suggestions
    }

@router.get("/recommendations/{resume_id}", response_model=List[JobMatchResult])
def recommend_jobs(
    resume_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.get_current_user),
):
    """
    Recommend jobs based on resume content. Uses curated job pool when DB is empty.
    """
    resume = db.query(Resume).filter(Resume.id == resume_id, Resume.owner_id == current_user.id).first()
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")

    from app.core.config import settings

    recommendations = []

    # Try real-time jobs if SerpAPI key is set
    if settings.SERPAPI_API_KEY:
        try:
            from app.services.realtime_job_service import RealTimeJobService
            query = resume.predicted_role if resume.predicted_role and resume.predicted_role != "Analyzing..." else "Software Engineer"
            real_time_jobs = RealTimeJobService.search_jobs(query)
            for job in real_time_jobs or []:
                score_data = ATSScoringService.calculate_match_score(resume.content_text, job.get('description_text', ''))
                ats = score_data.get('ats_score', 65)
                recommendations.append({
                    "job_id": 0,
                    "match_percentage": ats,
                    "missing_skills": [],
                    "improvement_suggestions": [f"Apply for {job.get('title','Role')} at {job.get('company','Company')}"],
                    "title": job.get('title', 'Software Engineer'),
                    "company": job.get('company', 'Tech Company'),
                    "location": job.get('location', 'India'),
                    "salary_range": job.get('salary_range', 'Competitive'),
                    "posted_date": job.get('posted_date', 'Recently'),
                    "apply_link": job.get('apply_link'),
                    "logo": job.get('logo'),
                })
        except Exception as e:
            print(f"Real-time job fetch failed: {e}")

    # Try DB jobs
    if not recommendations:
        all_jobs = db.query(JobDescription).all()
        for job in all_jobs:
            score_data = ATSScoringService.calculate_match_score(resume.content_text, job.description_text)
            ats = score_data.get('ats_score', 65)
            if ats > 30:
                recommendations.append({
                    "job_id": job.id,
                    "match_percentage": ats,
                    "missing_skills": [],
                    "improvement_suggestions": [f"Apply for {job.title} at {job.company}"],
                    "title": job.title,
                    "company": job.company,
                    "location": getattr(job, 'location', 'India'),
                    "salary_range": getattr(job, 'salary_range', 'Competitive'),
                    "posted_date": getattr(job, 'posted_date', 'Recently'),
                    "apply_link": None,
                    "logo": None,
                })

    # Curated fallback when no DB jobs and no real-time jobs
    if not recommendations:
        ats = resume.ats_score or 65
        role = resume.predicted_role or "Software Engineer"
        curated = [
            {"title": "Software Engineer", "company": "Google India", "location": "Hyderabad", "salary_range": "20-35 LPA"},
            {"title": "Python Developer", "company": "Amazon", "location": "Bangalore", "salary_range": "18-30 LPA"},
            {"title": "Full Stack Developer", "company": "Microsoft", "location": "Hyderabad", "salary_range": "16-28 LPA"},
            {"title": "Backend Engineer", "company": "Flipkart", "location": "Bangalore", "salary_range": "15-25 LPA"},
            {"title": "Data Engineer", "company": "Walmart Labs", "location": "Bangalore", "salary_range": "14-22 LPA"},
        ]
        for i, job in enumerate(curated):
            recommendations.append({
                "job_id": -(i+1),
                "match_percentage": round(max(ats - i*3, 55), 1),
                "missing_skills": [],
                "improvement_suggestions": [f"Tailor your resume for {job['title']} role"],
                "title": job["title"],
                "company": job["company"],
                "location": job["location"],
                "salary_range": job["salary_range"],
                "posted_date": "Recently",
                "apply_link": None,
                "logo": None,
            })

    recommendations.sort(key=lambda x: x["match_percentage"], reverse=True)
    return recommendations[:15]

@router.post("/", response_model=JobDescriptionCreate)
def create_job(
    job_in: JobDescriptionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.get_current_user),
):
    """
    Add a new job description to the system (Recruiter role or Admin).
    """
    # Simply add to DB for now
    db_job = JobDescription(
        title=job_in.title,
        company=job_in.company,
        description_text=job_in.description_text,
        required_skills={} # Parse skills if needed
    )
    db.add(db_job)
    db.commit()
    return job_in
