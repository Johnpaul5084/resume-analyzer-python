"""
Application Model - Track job applications
"""

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db.session import Base


class Application(Base):
    __tablename__ = "applications"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Job details
    job_title = Column(String, nullable=False)
    company = Column(String, nullable=False)
    location = Column(String)
    job_url = Column(Text, nullable=False)
    job_description = Column(Text)
    
    # Application details
    status = Column(String, default="applied")  # applied, failed, interview, rejected, offer
    platform = Column(String, default="linkedin")  # linkedin, indeed, naukri, etc.
    cover_letter = Column(Text)
    
    # Timestamps
    applied_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Response tracking
    response_received = Column(DateTime)
    interview_date = Column(DateTime)
    
    # Notes
    notes = Column(Text)
    
    # Relationships
    user = relationship("User", back_populates="applications")
