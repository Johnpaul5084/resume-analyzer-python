from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from pydantic import BaseModel
from app.api import dependencies as deps
from app.db.session import get_db
from app.models.all_models import User, Resume
from app.services.mentor_service import MentorService
from app.career_engine.mentor_bot_service import AIMentorBot
from app.career_engine.career_predictor import CareerPredictor
from app.career_engine.resume_strategy import ResumeStrategy

router = APIRouter()

class ChatMessage(BaseModel):
    role: str  # "user" or "assistant"
    content: str

class ChatRequest(BaseModel):
    question: str
    resume_id: Optional[int] = None
    chat_history: Optional[List[ChatMessage]] = None

class MentorInsightRequest(BaseModel):
    resume_text: str
    skills: List[str]
    target_role: Optional[str] = None

class CareerProfile(BaseModel):
    branch: str
    skills: List[str]
    interests: List[str]

@router.post("/chat")
async def chat_with_mentor(
    request: Request,
    chat_req: ChatRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.get_current_user),
):
    """
    Direct Chat with AI Career Mentor.
    Supports chat history for contextual conversations.
    Rate limit: 30 messages/minute per user — enough for a natural conversation.
    """
    from app.main import limiter

    @limiter.limit("30/minute")
    async def _chat(request, chat_req, db, current_user):
        resume_content = None
        if chat_req.resume_id:
            resume = db.query(Resume).filter(
                Resume.id == chat_req.resume_id,
                Resume.owner_id == current_user.id
            ).first()
            if resume:
                resume_content = resume.content_text

        # Convert chat_history from Pydantic models to dicts
        history = None
        if chat_req.chat_history:
            history = [{"role": m.role, "content": m.content} for m in chat_req.chat_history]

        response = await MentorService.get_advice(
            user_question=chat_req.question,
            resume_context=resume_content,
            chat_history=history,
        )
        return {"reply": response}

    return await _chat(request, chat_req, db, current_user)

@router.post("/insight")
async def get_mentor_insight(
    request: MentorInsightRequest,
    current_user: User = Depends(deps.get_current_user),
):
    """
    Get deep AI insights (Roadmap, Fit Analysis, Skill Graph).
    Uses unified AIProvider (Gemini → OpenAI → Keyword Fallback).
    """
    return AIMentorBot.analyze_career_path(
        request.resume_text, 
        request.skills, 
        request.target_role
    )

@router.post("/predict")
def predict_career(
    profile: CareerProfile,
    current_user: User = Depends(deps.get_current_user),
):
    """
    Predict career paths based on profile branch and skills.
    """
    return CareerPredictor.predict_paths(profile.branch, profile.skills, profile.interests)

@router.get("/strategy/{tier}")
def get_resume_strategy(
    tier: str,
    current_user: User = Depends(deps.get_current_user),
):
    """
    Get industry-specific resume strategies (FAANG, MNC, startup).
    """
    return ResumeStrategy.get_strategy(tier)
