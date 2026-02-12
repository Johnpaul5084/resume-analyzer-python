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
    Recommend jobs from the internal database based on resume content.
    (This simulates a "Real-time AI Job Matching" feature)
    """
    resume = db.query(Resume).filter(Resume.id == resume_id, Resume.owner_id == current_user.id).first()
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")
    
    # Simple logic: find jobs in DB and calculate match scores on the fly
    # In production: Use vector database (pgvector / Pinecone) for semantic search
    
    # --- Real-Time Job Search Integration ---
    from app.core.config import settings
    from app.services.realtime_job_service import RealTimeJobService
    
    recommendations = []
    
    # Try fetching real-time jobs first if API key is set
    if settings.SERPAPI_API_KEY:
        try:
            query = resume.predicted_role if resume.predicted_role and resume.predicted_role != "Analyzing..." else "Software Engineer"
            real_time_jobs = RealTimeJobService.search_jobs(query)
            
            if real_time_jobs:
                for job in real_time_jobs:
                    # Calculate match score against real-time job description
                    score_data = ATSScoringService.calculate_match_score(resume.content_text, job['description_text'])
                    
                    if score_data['ats_score'] > 0: # Include all for now, sort later
                        rec = {
                            "job_id": 0, # External job
                            "match_percentage": score_data['ats_score'],
                            "missing_skills": score_data['missing_keywords'][:5],
                            "improvement_suggestions": [f"Apply for {job['title']} at {job['company']}"],
                            "title": job['title'],
                            "company": job['company'],
                            "location": job['location'],
                            "salary_range": job.get('salary_range', 'Competitive'),
                            "posted_date": job.get('posted_date', 'Recently'),
                            "apply_link": job.get('apply_link'),
                            "logo": job.get('logo')
                        }
                        recommendations.append(rec)
        except Exception as e:
            print(f"Real-time job fetch failed: {e}")
            # Fallback to DB
            pass
            
    # Fallback to DB if no recommendations from API
    if not recommendations:
        all_jobs = db.query(JobDescription).all() 
        for job in all_jobs:
            score_data = ATSScoringService.calculate_match_score(resume.content_text, job.description_text)
            if score_data['ats_score'] > 30: 
                rec = {
                    "job_id": job.id,
                    "match_percentage": score_data['ats_score'],
                    "missing_skills": score_data['missing_keywords'][:5],
                    "improvement_suggestions": [f"Apply for {job.title} at {job.company}"],
                    "title": job.title,
                    "company": job.company,
                    "location": job.location,
                    "salary_range": job.salary_range,
                    "posted_date": job.posted_date,
                    "apply_link": None, # Internal jobs don't have links
                    "logo": None
                }
                recommendations.append(rec)

    # Sort by match percentage
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
