"""
LinkedIn Integration API Endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel, EmailStr
from datetime import datetime

from app.api.deps import get_current_user, get_db
from app.models.user import User
from app.models.application import Application
from app.services.linkedin_service import LinkedInService
from app.schemas.linkedin import (
    LinkedInLoginRequest,
    LinkedInLoginResponse,
    JobSearchRequest,
    JobSearchResponse,
    AutoApplyRequest,
    AutoApplyResponse,
    CoverLetterRequest,
    CoverLetterResponse
)

router = APIRouter()

# In-memory storage for LinkedIn sessions (use Redis in production)
linkedin_sessions = {}


@router.post("/connect", response_model=LinkedInLoginResponse)
def connect_linkedin(
    request: LinkedInLoginRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Connect user's LinkedIn account
    
    This endpoint logs into LinkedIn and stores the session for future use.
    """
    try:
        linkedin_service = LinkedInService()
        result = linkedin_service.login_to_linkedin(request.email, request.password)
        
        if result['success']:
            # Store session for this user
            linkedin_sessions[current_user.id] = {
                'cookies': result['cookies'],
                'connected_at': datetime.now().isoformat()
            }
            
            # Update user's LinkedIn connection status in DB
            current_user.linkedin_connected = True
            current_user.linkedin_email = request.email
            db.commit()
            
            return LinkedInLoginResponse(
                success=True,
                message="Successfully connected to LinkedIn",
                connected_at=datetime.now()
            )
        else:
            raise HTTPException(status_code=400, detail=result['message'])
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error connecting to LinkedIn: {str(e)}")


@router.post("/search-jobs", response_model=JobSearchResponse)
def search_jobs(
    request: JobSearchRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Search for jobs on LinkedIn
    
    Returns a list of job postings matching the search criteria.
    """
    try:
        # Check if user is connected to LinkedIn
        if current_user.id not in linkedin_sessions:
            raise HTTPException(
                status_code=400,
                detail="Please connect your LinkedIn account first"
            )
        
        linkedin_service = LinkedInService()
        
        # Restore session cookies
        linkedin_service._init_driver()
        for cookie in linkedin_sessions[current_user.id]['cookies']:
            linkedin_service.driver.add_cookie(cookie)
        
        # Search for jobs
        jobs = linkedin_service.search_jobs(
            keywords=request.keywords,
            location=request.location,
            experience_level=request.experience_level,
            job_type=request.job_type,
            max_results=request.max_results
        )
        
        linkedin_service.close()
        
        return JobSearchResponse(
            success=True,
            jobs=jobs,
            total_found=len(jobs)
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error searching jobs: {str(e)}")


@router.post("/auto-apply", response_model=AutoApplyResponse)
def auto_apply(
    request: AutoApplyRequest,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Automatically apply to jobs on LinkedIn
    
    This is a background task that will apply to jobs matching the criteria.
    """
    try:
        # Check if user is connected to LinkedIn
        if current_user.id not in linkedin_sessions:
            raise HTTPException(
                status_code=400,
                detail="Please connect your LinkedIn account first"
            )
        
        # Get user's resume data
        resume = db.query(Resume).filter(
            Resume.user_id == current_user.id,
            Resume.id == request.resume_id
        ).first()
        
        if not resume:
            raise HTTPException(status_code=404, detail="Resume not found")
        
        # Prepare resume data for application
        resume_data = {
            'text': resume.text,
            'email': current_user.email,
            'phone': current_user.phone or '',
            'first_name': current_user.full_name.split()[0] if current_user.full_name else '',
            'last_name': ' '.join(current_user.full_name.split()[1:]) if current_user.full_name else '',
            'location': request.location or '',
            'linkedin_url': current_user.linkedin_url or '',
            'website': current_user.website or ''
        }
        
        # Start auto-apply in background
        background_tasks.add_task(
            run_auto_apply,
            user_id=current_user.id,
            resume_data=resume_data,
            search_params=request.dict(),
            db=db
        )
        
        return AutoApplyResponse(
            success=True,
            message=f"Auto-apply started. Will apply to up to {request.max_applications} jobs.",
            status="in_progress"
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error starting auto-apply: {str(e)}")


@router.post("/generate-cover-letter", response_model=CoverLetterResponse)
def generate_cover_letter(
    request: CoverLetterRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Generate a personalized cover letter using AI
    """
    try:
        # Get user's resume
        resume = db.query(Resume).filter(
            Resume.user_id == current_user.id,
            Resume.id == request.resume_id
        ).first()
        
        if not resume:
            raise HTTPException(status_code=404, detail="Resume not found")
        
        linkedin_service = LinkedInService()
        cover_letter = linkedin_service.generate_cover_letter(
            job_title=request.job_title,
            company=request.company,
            resume_text=resume.text
        )
        
        return CoverLetterResponse(
            success=True,
            cover_letter=cover_letter,
            job_title=request.job_title,
            company=request.company
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating cover letter: {str(e)}")


@router.get("/applications")
def get_applications(
    skip: int = 0,
    limit: int = 50,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get user's job applications
    """
    try:
        applications = db.query(Application).filter(
            Application.user_id == current_user.id
        ).order_by(Application.applied_at.desc()).offset(skip).limit(limit).all()
        
        return {
            'success': True,
            'applications': applications,
            'total': db.query(Application).filter(Application.user_id == current_user.id).count()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching applications: {str(e)}")


@router.get("/applications/stats")
def get_application_stats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get statistics about user's applications
    """
    try:
        total_applications = db.query(Application).filter(
            Application.user_id == current_user.id
        ).count()
        
        successful_applications = db.query(Application).filter(
            Application.user_id == current_user.id,
            Application.status == 'applied'
        ).count()
        
        failed_applications = db.query(Application).filter(
            Application.user_id == current_user.id,
            Application.status == 'failed'
        ).count()
        
        # Get applications by date (last 30 days)
        from datetime import timedelta
        thirty_days_ago = datetime.now() - timedelta(days=30)
        recent_applications = db.query(Application).filter(
            Application.user_id == current_user.id,
            Application.applied_at >= thirty_days_ago
        ).count()
        
        return {
            'success': True,
            'stats': {
                'total_applications': total_applications,
                'successful': successful_applications,
                'failed': failed_applications,
                'last_30_days': recent_applications,
                'success_rate': (successful_applications / total_applications * 100) if total_applications > 0 else 0
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching stats: {str(e)}")


@router.delete("/disconnect")
def disconnect_linkedin(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Disconnect user's LinkedIn account
    """
    try:
        # Remove session
        if current_user.id in linkedin_sessions:
            del linkedin_sessions[current_user.id]
        
        # Update user
        current_user.linkedin_connected = False
        current_user.linkedin_email = None
        db.commit()
        
        return {
            'success': True,
            'message': 'LinkedIn account disconnected'
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error disconnecting: {str(e)}")


# Background task function
def run_auto_apply(user_id: int, resume_data: dict, search_params: dict, db: Session):
    """
    Background task to run auto-apply
    """
    try:
        linkedin_service = LinkedInService()
        
        # Restore session
        if user_id in linkedin_sessions:
            linkedin_service._init_driver()
            for cookie in linkedin_sessions[user_id]['cookies']:
                linkedin_service.driver.add_cookie(cookie)
        
        # Search for jobs
        jobs = linkedin_service.search_jobs(
            keywords=search_params['keywords'],
            location=search_params.get('location', ''),
            experience_level=search_params.get('experience_level', ''),
            job_type=search_params.get('job_type', ''),
            max_results=search_params.get('max_results', 25)
        )
        
        # Auto-apply to jobs
        results = linkedin_service.auto_apply_batch(
            jobs=jobs,
            resume_data=resume_data,
            max_applications=search_params.get('max_applications', 20),
            generate_cover_letters=search_params.get('generate_cover_letters', True)
        )
        
        # Save applications to database
        for app_result in results['applications']:
            application = Application(
                user_id=user_id,
                job_title=app_result['job']['title'],
                company=app_result['job']['company'],
                location=app_result['job']['location'],
                job_url=app_result['job']['link'],
                status='applied' if app_result['result']['success'] else 'failed',
                applied_at=datetime.now(),
                platform='linkedin'
            )
            db.add(application)
        
        db.commit()
        linkedin_service.close()
        
    except Exception as e:
        print(f"Error in auto-apply background task: {e}")
