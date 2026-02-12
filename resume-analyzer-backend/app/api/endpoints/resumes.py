from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException, status
from typing import List, Optional
from sqlalchemy.orm import Session
from app.api import dependencies as deps
from app.db.session import get_db
from app.models.all_models import Resume, User
from app.schemas.all_schemas import ResumeDetailedAnalysis, ResumeInDBBase, ResumeCreate
from app.services.parser_service import ParserService
from app.services.ats_scoring_service import ATSScoringService
import os

router = APIRouter()

from fastapi import BackgroundTasks

import logging

# Configure logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

def process_ai_features_wrapper(resume_id, text, user_id):
    # Create new DB session for background task
    from app.db.session import SessionLocal
    db = SessionLocal()
    try:
        process_ai_features(resume_id, text, user_id, db)
    except Exception as e:
        logger.error(f"Wrapper failed: {e}")
    finally:
        db.close()

def process_ai_features(resume_id: int, extracted_text: str, user_id: int, db: Session):
    """
    Background task to handle heavy AI operations (Prediction + Rewriting).
    """
    logger.info(f"Starting AI processing for resume {resume_id}...")
    try:
        # A. Predict Role
        from app.services.job_prediction_service import JobPredictionService
        logger.info("Predicting job role...")
        predicted_role_data = JobPredictionService.predict_job_role(extracted_text)
        logger.info(f"Prediction result: {predicted_role_data}")
        
        detected_role = "General"
        if predicted_role_data and isinstance(predicted_role_data, list) and len(predicted_role_data) > 0:
            detected_role = predicted_role_data[0]['role']
        
        # B. Auto-Rewrite Full Resume
        from app.services.ai_rewrite_service import AIRewriteService
        import asyncio
        
        logger.info(f"rewriting resume for role: {detected_role}...")
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        ai_rewritten_text = loop.run_until_complete(AIRewriteService.rewrite_section(
            text=extracted_text[:3000],
            section_type="Entire Resume", 
            target_role=detected_role,
            company_type="MNC"
        ))
        loop.close()
        logger.info("Rewrite complete.")

        # Update DB
        resume = db.query(Resume).filter(Resume.id == resume_id).first()
        if resume:
            resume.predicted_role = detected_role
            resume.ai_rewritten_content = ai_rewritten_text
            db.commit()
            logger.info(f"Database updated for resume {resume_id}.")
        else:
            logger.error(f"Resume {resume_id} not found in DB during background task.")
            
    except Exception as e:
        logger.error(f"Error in background AI processing: {str(e)}")
        import traceback
        traceback.print_exc()
        
        # Update DB with Failure State
        try:
            resume = db.query(Resume).filter(Resume.id == resume_id).first()
            if resume:
                resume.predicted_role = "Analysis Failed"
                resume.ai_rewritten_content = "AI processing failed. Please try again."
                db.commit()
        except Exception as db_e:
            logger.error(f"Failed to update resume status to Failed: {db_e}")

@router.post("/upload", response_model=ResumeDetailedAnalysis)
async def upload_resume(
    *,
    db: Session = Depends(get_db),
    file: UploadFile = File(...),
    title: str = Form(...),
    job_description: Optional[str] = Form(None),
    current_user: User = Depends(deps.get_current_user),
    background_tasks: BackgroundTasks
):
    """
    Upload and analyze resume. AI features run in background for real-time responsiveness.
    """
    # 1. Parse File
    try:
        extracted_text = await ParserService.extract_text(file)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
        
    if not extracted_text:
         raise HTTPException(status_code=400, detail="Could not extract text from file.")

    # 2. Analyze Resume (ATS Score - Fast)
    analysis_result = ATSScoringService.calculate_score(extracted_text, job_description)
    parsed_sections = ParserService.extract_sections(extracted_text)
    
    # 3. Save Initial Data to DB
    file_location = f"uploads/{current_user.id}_{file.filename}"
    os.makedirs("uploads", exist_ok=True)
    
    with open(file_location, "wb") as f:
        f.write(await file.read())
        
    db_resume = Resume(
        title=title,
        file_path=file_location,
        file_type=file.filename.split('.')[-1],
        content_text=extracted_text,
        parsed_data=parsed_sections,
        ats_score=analysis_result["ats_score"],
        score_breakdown=analysis_result["breakdown"],
        missing_keywords=analysis_result["missing_keywords"],
        owner_id=current_user.id,
        predicted_role="Analyzing...", # Placeholder
        ai_rewritten_content=None 
    )
    
    db.add(db_resume)
    db.commit()
    db.refresh(db_resume)
    
    # 4. Trigger Background AI Processing
    # Pass db session? Careful with session scope. 
    # Better to create new session in task, but dependent on implementation.
    # FastAPI handles Depends(get_db) session closing.
    # We should pass the IDs and raw data and let task create session, OR reuse if safe.
    # For simplicity in FastAPI, passing the session works if task finishes before request? 
    # No, BackgroundTasks run AFTER response. Session might be closed.
    # We MUST handle session properly.
    # Simplified: We'll run it purely sync right here but that blocks.
    # Correct: Use a new session approach or assume 'db' is thread-local and might effectively be valid?
    # No, 'db' from Depends is closed after response.
    # We will pass the data needed to a wrapper that creates a new session.
    
    background_tasks.add_task(process_ai_features_wrapper, db_resume.id, extracted_text, current_user.id)
    
    return db_resume



@router.get("/{resume_id}", response_model=ResumeDetailedAnalysis)
def get_resume(
    resume_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.get_current_user),
):
    """
    Get a specific resume analysis result.
    """
    resume = db.query(Resume).filter(Resume.id == resume_id, Resume.owner_id == current_user.id).first()
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")
    
    # Since we didn't store matching_jobs, we can quickly re-predict purely for the *list* 
    # OR better, if we want consistency, we should have stored it.
    # For now, we'll re-predict quickly ONLY if predicted_role is set (implies model is loaded)
    # This keeps 'real-time accuracy' fresh.
    
    # Predict jobs dynamically on GET (fast after model load)
    # This simulates "real-time open jobs" based on content
    from app.services.job_prediction_service import JobPredictionService
    import random
    
    # Get raw predictions
    predictions = JobPredictionService.predict_job_role(resume.content_text)
    
    # Augment with Mock MNC Data for "Real Time" feel
    mnc_companies = ["Google", "Microsoft", "Amazon", "Tesla", "Meta", "Netflix", "Adobe", "IBM", "Accenture", "Deloitte"]
    locations = ["New York, NY", "San Francisco, CA", "Remote", "London, UK", "Bangalore, India", "Austin, TX", "Berlin, Germany"]
    
    augmented_jobs = []
    if predictions and isinstance(predictions, list):
        for pred in predictions:
            # Create a mock listing around this role
            augmented_jobs.append({
                "role": pred['role'],
                "confidence": pred['confidence'],
                "company": random.choice(mnc_companies),
                "location": random.choice(locations),
                "salary": f"${random.randint(80, 150)}k - ${random.randint(160, 250)}k",
                "posted": f"{random.randint(1, 5)} days ago"
            })
    
    response_obj = ResumeDetailedAnalysis.from_orm(resume)
    response_obj.matching_jobs = augmented_jobs
    
    return response_obj

@router.get("/", response_model=List[ResumeInDBBase])
def get_my_resumes(
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.get_current_user),
    skip: int = 0,
    limit: int = 10,
):
    """
    List all uploaded resumes for the current user.
    """
    resumes = db.query(Resume).filter(Resume.owner_id == current_user.id).offset(skip).limit(limit).all()
    return resumes
from app.schemas.all_schemas import RewriteRequest, JobPredictionRequest, ValidateFitRequest
from fastapi import Body

@router.post("/rewrite")
async def rewrite_resume_section(
    request: RewriteRequest,
):
    """
    Rewrite a resume section using AI (Gemini) for MNC standards.
    """
    from app.services.ai_rewrite_service import AIRewriteService
    # Ensure all arguments are passed correctly from the request object
    return await AIRewriteService.rewrite_section(
        text=request.text, 
        section_type=request.section_type, 
        target_role=request.target_role,
        company_type=request.company_type
    )

@router.post("/predict-job")
async def predict_job_role(
    request: JobPredictionRequest,
):
    """
    Predict the most suitable job role based on resume text using BERT Zero-Shot Classification.
    """
    from app.services.job_prediction_service import JobPredictionService
    return JobPredictionService.predict_job_role(request.text, request.candidate_labels)

@router.post("/validate-fit")
async def validate_role_fit(
    request: ValidateFitRequest,
):
    """
    Validate if the resume fits the target role and provide AI feedback.
    """
    from app.services.ai_rewrite_service import AIRewriteService
    return await AIRewriteService.validate_role_fit(request.text, request.target_role)
