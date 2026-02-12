"""
LinkedIn Integration Schemas
"""

from pydantic import BaseModel, EmailStr
from typing import List, Optional
from datetime import datetime


class LinkedInLoginRequest(BaseModel):
    email: EmailStr
    password: str


class LinkedInLoginResponse(BaseModel):
    success: bool
    message: str
    connected_at: Optional[datetime] = None


class JobSearchRequest(BaseModel):
    keywords: str
    location: Optional[str] = ""
    experience_level: Optional[str] = ""
    job_type: Optional[str] = ""
    max_results: Optional[int] = 25


class JobData(BaseModel):
    title: str
    company: str
    location: str
    link: str
    posted_date: Optional[str] = None
    scraped_at: str


class JobSearchResponse(BaseModel):
    success: bool
    jobs: List[JobData]
    total_found: int


class AutoApplyRequest(BaseModel):
    resume_id: int
    keywords: str
    location: Optional[str] = ""
    experience_level: Optional[str] = ""
    job_type: Optional[str] = ""
    max_results: Optional[int] = 25
    max_applications: Optional[int] = 20
    generate_cover_letters: Optional[bool] = True


class AutoApplyResponse(BaseModel):
    success: bool
    message: str
    status: str


class CoverLetterRequest(BaseModel):
    resume_id: int
    job_title: str
    company: str


class CoverLetterResponse(BaseModel):
    success: bool
    cover_letter: str
    job_title: str
    company: str


class ApplicationResponse(BaseModel):
    id: int
    job_title: str
    company: str
    location: str
    job_url: str
    status: str
    applied_at: datetime
    platform: str
    
    class Config:
        from_attributes = True
