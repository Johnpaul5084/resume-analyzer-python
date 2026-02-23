from fastapi import APIRouter, Depends
from typing import List, Optional
from pydantic import BaseModel
from app.career_engine.career_predictor import CareerPredictor
from app.career_engine.roadmap_generator import RoadmapGenerator
from app.career_engine.resume_strategy import ResumeStrategy

router = APIRouter()

class CareerProfile(BaseModel):
    branch: str
    skills: List[str]
    interests: List[str]

class RoadmapRequest(BaseModel):
    target_role: str
    timeline_months: Optional[int] = 6

from app.career_engine.mentor_bot_service import IRISMentorBot

class MentorRequest(BaseModel):
    resume_text: str
    skills: List[str]

@router.post("/predict-career")
def predict_career(profile: CareerProfile):
    return CareerPredictor.predict_paths(profile.branch, profile.skills, profile.interests)

@router.post("/generate-roadmap")
def generate_roadmap(request: RoadmapRequest):
    return RoadmapGenerator.generate_roadmap(request.target_role, request.timeline_months)

@router.get("/resume-strategy/{tier}")
def get_resume_strategy(tier: str):
    return ResumeStrategy.get_strategy(tier)

@router.post("/mentor-insight")
def get_mentor_insight(request: MentorRequest):
    return IRISMentorBot.analyze_career_path(request.resume_text, request.skills)
