from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.api import dependencies as deps
from app.db.session import get_db
from app.models.all_models import User, Resume
from app.services.career_guru_service import CareerGuruService
from pydantic import BaseModel
from typing import Optional, List

router = APIRouter()

class ChatRequest(BaseModel):
    question: str
    resume_id: Optional[int] = None

class RoadmapRequest(BaseModel):
    target_role: str
    resume_id: int

@router.post("/chat")
async def chat_with_guru(
    request: ChatRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.get_current_user),
):
    """
    Chat with the AI Career Guru about career goals or resume feedback.
    """
    resume_content = None
    if request.resume_id:
        resume = db.query(Resume).filter(Resume.id == request.resume_id, Resume.owner_id == current_user.id).first()
        if resume:
            resume_content = resume.content_text

    response = await CareerGuruService.get_advice(
        user_question=request.question,
        resume_context=resume_content
    )
    
    return {"reply": response}

@router.post("/roadmap")
async def get_career_roadmap(
    request: RoadmapRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.get_current_user),
):
    """
    Generate a personalized learning roadmap to reach a target role.
    """
    resume = db.query(Resume).filter(Resume.id == request.resume_id, Resume.owner_id == current_user.id).first()
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")

    current_skills = resume.parsed_data.get("skills", []) if resume.parsed_data else []
    
    roadmap = await CareerGuruService.generate_skill_roadmap(
        target_role=request.target_role,
        current_skills=current_skills
    )
    
    return roadmap
