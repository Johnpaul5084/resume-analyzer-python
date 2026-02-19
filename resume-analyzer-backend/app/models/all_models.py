from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Float, Text, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    resumes = relationship("Resume", back_populates="owner")

class Resume(Base):
    __tablename__ = "resumes"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)  # e.g., "Software Engineer Resume - v1"
    file_path = Column(String, nullable=False) # Path to file (local or S3)
    file_type = Column(String) # pdf, docx, etc.
    content_text = Column(Text) # Extracted text
    
    # Store parsed sections as JSON
    parsed_data = Column(JSON) # { "skills": [], "experience": [], ... }
    
    # Analysis Results
    ats_score = Column(Float, default=0.0)
    score_breakdown = Column(JSON) # { "keywords": 40, "grammar": 10 ... }
    missing_keywords = Column(JSON) 
    
    # AI Features
    ai_rewritten_content = Column(Text, nullable=True) # Full AI rewrite (changed back to Text)
    predicted_role = Column(String, nullable=True) # AI detected role
    
    # Futuristic Phoenix Features
    analysis = Column(Text, nullable=True)
    suggestions = Column(JSON, nullable=True) 
    key_strengths = Column(JSON, nullable=True)
    market_readiness = Column(Float, default=85.0)

    owner_id = Column(Integer, ForeignKey("users.id"))
    owner = relationship("User", back_populates="resumes")
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

class JobDescription(Base):
    __tablename__ = "job_descriptions"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    company = Column(String)
    location = Column(String, nullable=True) # Added
    salary_range = Column(String, nullable=True) # Added
    posted_date = Column(String, nullable=True) # Added, simplified as string for now
    description_text = Column(Text)
    required_skills = Column(JSON)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
