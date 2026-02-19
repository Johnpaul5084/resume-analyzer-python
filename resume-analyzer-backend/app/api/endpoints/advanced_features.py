"""
Advanced Features API Endpoints - Simplified Version
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import Dict, Any

from app.api import dependencies as deps
from app.db.session import get_db
from app.models.all_models import User, Resume

router = APIRouter()

# ==================== QUICK FEATURES ====================

@router.get("/resume-templates")
def get_resume_templates(
    current_user: User = Depends(deps.get_current_user)
):
    """
    📄 Get available resume templates
    """
    
    templates = [
        {
            "id": "modern-tech",
            "name": "Modern Tech",
            "description": "Clean, ATS-friendly template for tech roles",
            "best_for": ["Software Engineer", "Data Scientist", "DevOps"],
            "preview_url": "/templates/modern-tech.png"
        },
        {
            "id": "executive",
            "name": "Executive",
            "description": "Professional template for senior roles",
            "best_for": ["Senior Engineer", "Engineering Manager", "Director"],
            "preview_url": "/templates/executive.png"
        },
        {
            "id": "creative",
            "name": "Creative",
            "description": "Stylish template for creative roles",
            "best_for": ["Designer", "Product Manager", "Marketing"],
            "preview_url": "/templates/creative.png"
        },
        {
            "id": "minimal",
            "name": "Minimal",
            "description": "Simple, clean template that works everywhere",
            "best_for": ["All roles"],
            "preview_url": "/templates/minimal.png"
        }
    ]
    
    return {
        "templates": templates,
        "total_count": len(templates)
    }

@router.get("/export-formats")
def get_export_formats(
    current_user: User = Depends(deps.get_current_user)
):
    """
    💾 Get available export formats for resumes
    """
    
    formats = [
        {
            "format": "PDF",
            "description": "Standard PDF format (recommended)",
            "file_extension": ".pdf",
            "ats_compatible": True
        },
        {
            "format": "DOCX",
            "description": "Microsoft Word format",
            "file_extension": ".docx",
            "ats_compatible": True
        },
        {
            "format": "TXT",
            "description": "Plain text format",
            "file_extension": ".txt",
            "ats_compatible": True
        }
    ]
    
    return {
        "formats": formats,
        "recommended": "PDF"
    }

@router.get("/market-insights")
def get_market_insights(
    target_role: str = "Software Engineer",
    current_user: User = Depends(deps.get_current_user)
):
    """
    🌐 Get job market insights and trends
    """
    
    insights = {
        "market_overview": {
            "total_jobs_available": 125000,
            "avg_salary_range": "$80k - $150k",
            "demand_trend": "increasing",
            "competition_level": "moderate"
        },
        "trending_skills": [
            {"skill": "Python", "demand_change": "+15%", "avg_salary": "$120k"},
            {"skill": "React", "demand_change": "+12%", "avg_salary": "$115k"},
            {"skill": "AWS", "demand_change": "+18%", "avg_salary": "$130k"},
            {"skill": "Machine Learning", "demand_change": "+25%", "avg_salary": "$140k"}
        ],
        "hot_roles": [
            {"role": "AI Engineer", "openings": 15000, "growth": "+30%"},
            {"role": "Full Stack Developer", "openings": 25000, "growth": "+20%"},
            {"role": "DevOps Engineer", "openings": 12000, "growth": "+22%"}
        ]
    }
    
    return insights

@router.get("/user-stats")
def get_user_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.get_current_user)
):
    """
    📊 Get user statistics and achievements
    """
    
    resumes = db.query(Resume).filter(Resume.owner_id == current_user.id).all()
    
    total_resumes = len(resumes)
    avg_score = sum(r.ats_score for r in resumes) / total_resumes if total_resumes > 0 else 0
    
    achievements = []
    
    if total_resumes >= 1:
        achievements.append({
            "name": "First Steps",
            "description": "Uploaded your first resume",
            "icon": "🎯",
            "unlocked": True
        })
    
    if any(r.ats_score >= 80 for r in resumes):
        achievements.append({
            "name": "ATS Master",
            "description": "Achieved 80+ ATS score",
            "icon": "⭐",
            "unlocked": True
        })
    
    if total_resumes >= 3:
        achievements.append({
            "name": "Resume Collector",
            "description": "Created 3+ resume versions",
            "icon": "📚",
            "unlocked": True
        })
    
    return {
        "user_id": current_user.id,
        "stats": {
            "total_resumes": total_resumes,
            "average_ats_score": round(avg_score, 2),
            "highest_score": round(max((r.ats_score for r in resumes), default=0), 2)
        },
        "achievements": achievements,
        "job_search_health": {
            "score": min(50 + int(avg_score * 0.5), 100),
            "status": "Good" if avg_score >= 70 else "Needs Improvement"
        }
    }

@router.get("/salary-insights")
def get_salary_insights(
    role: str = "Software Engineer",
    experience_years: int = 3,
    current_user: User = Depends(deps.get_current_user)
):
    """
    💰 Get salary insights for a role
    """
    
    base_salary = 80000 + (experience_years * 10000)
    
    return {
        "role": role,
        "experience_years": experience_years,
        "salary_range": {
            "min": base_salary,
            "median": base_salary + 40000,
            "max": base_salary + 100000,
            "currency": "USD"
        },
        "negotiation_tips": [
            "Research market rates thoroughly",
            "Highlight your unique value proposition",
            "Consider total compensation (equity, benefits)",
            "Be prepared to walk away"
        ]
    }
