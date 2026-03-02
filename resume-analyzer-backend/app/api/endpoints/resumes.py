from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException, status
from typing import List, Optional
from sqlalchemy.orm import Session
from app.api import dependencies as deps
from app.db.session import get_db
from app.models.all_models import Resume, User
from app.schemas.all_schemas import ResumeDetailedAnalysis, ResumeInDBBase, ResumeCreate
from app.services.ai_parser_service import AIParserService
from app.services.file_parser_service import AIRawParser
from app.services.ats_scoring_service import ATSScoringService
import os

router = APIRouter()

from fastapi import BackgroundTasks

import logging

# Configure logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

def process_ai_features_wrapper(resume_id, text, user_id, target_role=None):
    # Create new DB session for background task
    from app.db.session import SessionLocal
    db = SessionLocal()
    try:
        process_ai_features(resume_id, text, user_id, db, target_role)
    except Exception as e:
        logger.error(f"Wrapper failed: {e}")
    finally:
        db.close()

def process_ai_features(
    resume_id: int,
    extracted_text: str,
    user_id: int,
    db: Session,
    target_role: str = None,  # ← explicit role from user's input
):
    """
    Background task: rewrite the resume for the specified or predicted role.
    Role prediction is SKIPPED if the user already specified target_role.
    """
    logger.info(f"Starting AI rewrite for resume {resume_id}, target={target_role}...")
    try:
        detected_role = target_role  # use user's choice directly if provided

        # Only run prediction if user didn't specify a role
        if not detected_role:
            from app.services.job_prediction_service import JobPredictionService
            logger.info("No target role specified — predicting from resume...")
            predicted_role_data = JobPredictionService.predict_job_role(extracted_text)
            if predicted_role_data and isinstance(predicted_role_data, list):
                detected_role = predicted_role_data[0].get('role', 'Software Engineer')
            else:
                detected_role = "Software Engineer"
            logger.info(f"Predicted role: {detected_role}")

        # AI Rewrite for the chosen / predicted role
        from app.services.ai_rewrite_service import AIRewriteService
        import asyncio

        logger.info(f"Rewriting resume for role: {detected_role}...")
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        ai_rewritten_text = loop.run_until_complete(
            AIRewriteService.rewrite_section(
                text=extracted_text[:4000],
                section_type="Entire Resume",
                target_role=detected_role,
                company_type="MNC",
            )
        )
        loop.close()
        logger.info("Rewrite complete.")

        # Update DB — keep predicted_role from the main analysis (Gemini already set it)
        # Only update ai_rewritten_content here
        resume = db.query(Resume).filter(Resume.id == resume_id).first()
        if resume:
            resume.ai_rewritten_content = ai_rewritten_text
            db.commit()
            logger.info(f"Resume {resume_id} rewrite saved to DB.")
        else:
            logger.error(f"Resume {resume_id} not found in DB during background task.")

    except Exception as e:
        logger.error(f"Error in background AI processing: {str(e)}")
        import traceback
        traceback.print_exc()
        try:
            resume = db.query(Resume).filter(Resume.id == resume_id).first()
            if resume:
                resume.ai_rewritten_content = "AI rewrite failed. Please try the Optimize option manually."
                db.commit()
        except Exception as db_e:
            logger.error(f"Failed to update resume status: {db_e}")

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
    # 0. Security Validation
    ALLOWED_EXTENSIONS = {"pdf", "docx", "txt"}
    MAX_FILE_SIZE = 5 * 1024 * 1024 # 5MB
    
    file_ext = file.filename.split('.')[-1].lower()
    if file_ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=400, detail="Security: Invalid file format. Only PDF and DOCX permitted.")
        
    # Read content to check size
    content = await file.read()
    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(status_code=413, detail="Security: Document too large (Limit 5MB).")
    
    # Seek back to start for parser
    await file.seek(0)

    # 1. Parse File
    try:
        extracted_text = await AIRawParser.extract_text(file)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
        
    if not extracted_text:
         raise HTTPException(status_code=400, detail="Could not extract text from file.")

    # 2. Analyze Resume
    # Smart detection: short input = role name; long input = full job description
    user_target_role = None
    jd_text = None

    if job_description:
        if len(job_description.strip()) < 80:
            # User typed a role name (e.g. "Devops", "Data Scientist")
            user_target_role = job_description.strip()
        else:
            # User pasted a full job description
            jd_text = job_description

    analysis_result = await ATSScoringService.calculate_score(
        extracted_text,
        job_description=jd_text,
        target_role=user_target_role,
    )
    parsed_sections = AIRawParser.extract_sections(extracted_text)

    
    # 3. Save File to Disk (use the already-read content bytes)
    file_location = f"uploads/{current_user.id}_{file.filename}"
    os.makedirs("uploads", exist_ok=True)
    with open(file_location, "wb") as f:
        f.write(content)   # `content` was read at the top — no second read needed
        
    db_resume = Resume(
        title=title,
        file_path=file_location,
        file_type=file.filename.split('.')[-1],
        content_text=extracted_text,
        parsed_data=parsed_sections,
        ats_score=analysis_result["ats_score"],
        score_breakdown=analysis_result["breakdown"],
        missing_keywords=analysis_result.get("missing_skills", []),
        owner_id=current_user.id,
        # ✅ Use Gemini-predicted role immediately — no more "Analyzing..." placeholder
        predicted_role=analysis_result.get("predicted_role", "Analyzing..."),
        ai_rewritten_content=None,
        analysis=analysis_result.get("analysis"),
        suggestions=analysis_result.get("suggestions"),
        key_strengths=analysis_result.get("key_strengths"),
        market_readiness=analysis_result.get("breakdown", {}).get("market_readiness", 85)
    )
    
    db.add(db_resume)
    db.commit()
    db.refresh(db_resume)
    
    # 4. Background task: rewrite resume using the user's target role (or Gemini-predicted one)
    rewrite_role = user_target_role or analysis_result.get("predicted_role", "Software Engineer")
    background_tasks.add_task(
        process_ai_features_wrapper,
        db_resume.id,
        extracted_text,
        current_user.id,
        rewrite_role,  # ← pass the correct role explicitly
    )
    
    return db_resume



@router.get("/{resume_id}", response_model=ResumeDetailedAnalysis)
def get_resume(
    resume_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.get_current_user),
):
    """
    Get a specific resume analysis result.
    Returns cached AI analysis — no re-processing needed.
    """
    resume = db.query(Resume).filter(Resume.id == resume_id, Resume.owner_id == current_user.id).first()
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")

    import random

    # Use stored predicted_role, no re-running the slow ML model
    predicted_role = resume.predicted_role or "Software Engineer"

    # Build matching jobs from cached data — fast, no ML inference
    mnc_companies = ["Google", "Microsoft", "Amazon", "Tesla", "Meta", "Netflix", "Adobe", "IBM", "Accenture", "Infosys"]
    locations = ["Bangalore, India", "Hyderabad, India", "Remote", "Pune, India", "Chennai, India", "Mumbai, India"]
    roles_to_show = [predicted_role, "Full Stack Developer", "Backend Engineer", "Data Analyst", "Software Engineer"]

    augmented_jobs = [
        {
            "role": role,
            "confidence": round(max(0.55, (resume.ats_score or 65) / 100 - i * 0.05), 2),
            "company": random.choice(mnc_companies),
            "location": random.choice(locations),
            "salary": f"Rs.{random.randint(8, 20)}L - Rs.{random.randint(21, 40)}L",
            "posted": f"{random.randint(1, 7)} days ago"
        }
        for i, role in enumerate(roles_to_show)
    ]

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

from fastapi import Body, Request

@router.post("/rewrite")
async def rewrite_resume_section(
    request: Request,
    rewrite_req: RewriteRequest = Body(...),
):
    """
    Rewrite a resume section using AI (Gemini) for MNC standards.
    """
    from app.main import limiter
    # Throttling to protect Gemini QPS
    @limiter.limit("20/minute")
    async def _rewrite(request, rewrite_req):
        from app.services.ai_rewrite_service import AIRewriteService
        return await AIRewriteService.rewrite_section(
            text=rewrite_req.text, 
            section_type=rewrite_req.section_type, 
            target_role=rewrite_req.target_role,
            company_type=rewrite_req.company_type
        )
    return await _rewrite(request, rewrite_req)

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
