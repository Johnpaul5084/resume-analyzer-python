from pydantic import BaseModel, EmailStr, Field, HttpUrl
from typing import Optional, List, Dict, Any
from datetime import datetime

# --- Token Schemas ---
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    sub: Optional[str] = None  # Subject (user ID)

# --- User Schemas ---
class UserBase(BaseModel):
    email: EmailStr
    full_name: Optional[str] = None

class UserCreate(UserBase):
    password: str

class UserUpdate(UserBase):
    password: Optional[str] = None

class User(UserBase):
    id: int
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True

# --- Resume Schemas ---

class ResumeBase(BaseModel):
    title: str

class ResumeCreate(ResumeBase):
    pass # File is handled via Form data

class ResumeUpdate(ResumeBase):
    pass

class ResumeInDBBase(ResumeBase):
    id: int
    file_path: Optional[str] = None
    file_type: Optional[str] = None
    ats_score: Optional[float] = 0.0
    parsed_data: Optional[Dict[str, Any]] = None
    score_breakdown: Optional[Dict[str, float]] = None
    missing_keywords: Optional[List[str]] = None
    ai_rewritten_content: Optional[str] = None
    predicted_role: Optional[str] = None
    created_at: datetime
    owner_id: int

    class Config:
        from_attributes = True

class Resume(ResumeInDBBase):
    pass

class ResumeDetailedAnalysis(Resume):
    grammar_errors: Optional[List[Any]] = None
    ai_feedback: Optional[str] = None
    matching_jobs: Optional[List[Dict[str, Any]]] = None # Jobs predicted for this resume

# --- Job/Matching Schemas ---
class JobDescriptionCreate(BaseModel):
    title: str
    company: Optional[str] = None
    description_text: str

class JobMatchResult(BaseModel):
    job_id: Optional[int] = None
    match_percentage: float
    missing_skills: List[str]
    improvement_suggestions: List[str]
    title: Optional[str] = None
    company: Optional[str] = None
    location: Optional[str] = None
    salary_range: Optional[str] = None
    posted_date: Optional[str] = None
    apply_link: Optional[str] = None
    logo: Optional[str] = None

# --- AI Feature Request Schemas ---

class RewriteRequest(BaseModel):
    text: str
    section_type: str = "Experience"
    target_role: str = "General"
    company_type: str = "MNC"
    tone: str = "Professional"

class JobPredictionRequest(BaseModel):
    text: str
    candidate_labels: Optional[List[str]] = None

class ValidateFitRequest(BaseModel):
    text: str
    target_role: str
