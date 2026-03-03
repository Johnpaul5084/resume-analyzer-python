"""
Advanced Features API Endpoints
================================
Includes:
  - API Credit Status
  - Career Risk Indicator (demand-based)
  - Skill Gap Heatmap (color-coded)
  - Resume Benchmark Mode (FAANG comparison)
  - Resume Version Tracking (improvement over time)
  - System Status & Health
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Dict, Any, List, Optional

from app.api import dependencies as deps
from app.db.session import get_db
from app.models.all_models import User, Resume, ResumeVersion

router = APIRouter()

# ==================== API CREDIT STATUS ====================

@router.get("/api-credits")
def get_api_credit_status(
    current_user: User = Depends(deps.get_current_user)
):
    """
    📊 Get daily API credit usage for all 3 AI services.
    Shows used/remaining/limit/exhausted for Gemini, OpenAI, and SerpAPI.
    Includes reset time info so the frontend knows when credits renew.
    """
    from app.services.api_credit_manager import APICreditManager
    return APICreditManager.get_status()

@router.get("/credits-check")
def check_credits_quick():
    """
    ⚡ Quick credit check (no auth required) — for global banner display.
    Returns only exhaustion flags and reset info (lightweight).
    """
    from app.services.api_credit_manager import APICreditManager
    status = APICreditManager.get_status()
    return {
        "any_exhausted": status["any_exhausted"],
        "exhausted_apis": status["exhausted_apis"],
        "reset_info": status["reset_info"],
        "credits": status["credits"],
    }

# ==================== CAREER RISK INDICATOR ====================

@router.get("/career-risk")
def get_career_risk(
    target_role: str = "Software Engineer",
    current_user: User = Depends(deps.get_current_user),
):
    """
    🚨 Career Risk Indicator
    ========================
    Shows whether a target role is:
      - 🟢 Growing & high demand
      - 🟡 Stable but competitive
      - 🔴 Declining or saturated

    Based on demand_scores.json data + market intelligence.
    """
    import json, os

    # Load demand scores
    demand_path = os.path.join(
        os.path.dirname(os.path.dirname(__file__)),
        "career_engine", "demand_scores.json",
    )
    demand_scores = {}
    try:
        with open(demand_path, encoding="utf-8") as f:
            demand_scores = json.load(f)
    except Exception:
        pass

    # Find best match for the target role
    role_lower = target_role.lower()
    score = None
    matched_role = target_role
    for ds_role, ds_score in demand_scores.items():
        if role_lower in ds_role.lower() or ds_role.lower() in role_lower:
            score = ds_score
            matched_role = ds_role
            break

    if score is None:
        # Default score for unknown roles
        score = 7.5

    # Classify risk level
    if score >= 9.0:
        risk_level = "LOW"
        risk_color = "green"
        risk_emoji = "🟢"
        demand_trend = "High demand, strong growth"
        advice = f"Great choice! {matched_role} is one of the most in-demand roles. Focus on building strong portfolio projects."
    elif score >= 8.0:
        risk_level = "MODERATE"
        risk_color = "yellow"
        risk_emoji = "🟡"
        demand_trend = "Stable demand, competitive"
        advice = f"{matched_role} has stable demand. Differentiate yourself with niche skills and certifications."
    else:
        risk_level = "HIGH"
        risk_color = "red"
        risk_emoji = "🔴"
        demand_trend = "Declining demand or market saturation"
        advice = f"Consider pivoting or adding complementary skills. {matched_role} market may be narrowing."

    # Alternative roles with higher demand
    alternatives = sorted(
        demand_scores.items(), key=lambda x: x[1], reverse=True
    )[:3]

    return {
        "target_role": matched_role,
        "demand_score": score,
        "risk_level": risk_level,
        "risk_color": risk_color,
        "risk_emoji": risk_emoji,
        "demand_trend": demand_trend,
        "advice": advice,
        "market_alternatives": [
            {"role": r, "demand_score": s, "label": "High Demand"}
            for r, s in alternatives
        ],
    }


# ==================== SKILL GAP HEATMAP ====================

@router.get("/skill-heatmap")
def get_skill_heatmap(
    resume_id: int,
    target_role: str = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.get_current_user),
):
    """
    🔥 Skill Gap Heatmap
    ====================
    Color-coded skill analysis:
      - 🟢 Green: Strong match (skill present + highly relevant)
      - 🟡 Yellow: Partial match (related skill present)
      - 🔴 Red: Missing (critical skill not found)

    Returns per-skill status for visual heatmap rendering.
    """
    from app.services.ai_skill_ontology import SkillOntology
    from app.services.ai_parser_service import AIParserService

    resume = db.query(Resume).filter(
        Resume.id == resume_id,
        Resume.owner_id == current_user.id,
    ).first()
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")

    text = resume.content_text or ""
    role = target_role or resume.predicted_role or "Software Engineer"

    # Extract user skills
    structured = AIParserService.extract_structured_data(text)
    user_skills = [s.lower() for s in structured.get("skills", [])]

    # Get required skills for role
    cluster = SkillOntology.map_role_to_cluster(role)
    all_role_skills = SkillOntology.get_cluster_skills(cluster)

    heatmap = []
    strong_count = 0
    partial_count = 0
    missing_count = 0

    for skill in all_role_skills:
        skill_lower = skill.lower()
        if skill_lower in user_skills:
            heatmap.append({
                "skill": skill,
                "status": "strong",
                "color": "green",
                "level": 3,
            })
            strong_count += 1
        elif any(
            s in skill_lower or skill_lower in s
            for s in user_skills
        ):
            heatmap.append({
                "skill": skill,
                "status": "partial",
                "color": "yellow",
                "level": 2,
            })
            partial_count += 1
        else:
            heatmap.append({
                "skill": skill,
                "status": "missing",
                "color": "red",
                "level": 1,
            })
            missing_count += 1

    total = len(all_role_skills) or 1
    coverage_pct = round((strong_count + partial_count * 0.5) / total * 100, 1)

    return {
        "role": role,
        "cluster": cluster,
        "skills": heatmap,
        "summary": {
            "strong": strong_count,
            "partial": partial_count,
            "missing": missing_count,
            "total": total,
            "coverage_percentage": coverage_pct,
        },
    }


# ==================== RESUME BENCHMARK MODE ====================

@router.get("/benchmark")
def benchmark_resume(
    resume_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.get_current_user),
):
    """
    📊 Resume Benchmark Mode
    ========================
    Compare user's resume against:
      - FAANG average template score
      - IIT/IIIT graduate profile average
      - Industry average

    Returns percentile ranking and improvement areas.
    """
    resume = db.query(Resume).filter(
        Resume.id == resume_id,
        Resume.owner_id == current_user.id,
    ).first()
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")

    user_score = resume.ats_score or 50.0
    breakdown = resume.score_breakdown or {}

    # Benchmark reference scores
    benchmarks = {
        "faang_average": {
            "label": "FAANG Candidate Average",
            "ats_score": 82.5,
            "breakdown": {
                "semantic_similarity": 85.0,
                "skill_coverage": 80.0,
                "experience_depth": 82.0,
                "ats_format_score": 88.0,
                "market_readiness": 85.0,
            },
        },
        "iit_graduate": {
            "label": "Top IIT/IIIT Graduate",
            "ats_score": 72.0,
            "breakdown": {
                "semantic_similarity": 72.0,
                "skill_coverage": 75.0,
                "experience_depth": 60.0,
                "ats_format_score": 80.0,
                "market_readiness": 72.0,
            },
        },
        "industry_average": {
            "label": "Industry Average",
            "ats_score": 55.0,
            "breakdown": {
                "semantic_similarity": 55.0,
                "skill_coverage": 50.0,
                "experience_depth": 45.0,
                "ats_format_score": 65.0,
                "market_readiness": 55.0,
            },
        },
    }

    # Calculate percentile vs each benchmark
    comparisons = {}
    for key, bench in benchmarks.items():
        diff = round(user_score - bench["ats_score"], 1)
        comparisons[key] = {
            "label": bench["label"],
            "benchmark_score": bench["ats_score"],
            "user_score": user_score,
            "difference": diff,
            "status": "above" if diff > 0 else "below" if diff < 0 else "at",
            "breakdown_comparison": {
                metric: {
                    "user": breakdown.get(metric, 50.0),
                    "benchmark": bench["breakdown"].get(metric, 50.0),
                    "difference": round(
                        breakdown.get(metric, 50.0) - bench["breakdown"].get(metric, 50.0), 1
                    ),
                }
                for metric in bench["breakdown"]
            },
        }

    # Overall percentile estimate
    if user_score >= 85:
        percentile = 95
    elif user_score >= 75:
        percentile = 80
    elif user_score >= 65:
        percentile = 65
    elif user_score >= 55:
        percentile = 45
    else:
        percentile = 25

    return {
        "resume_id": resume_id,
        "user_score": user_score,
        "percentile": percentile,
        "percentile_label": f"Top {100 - percentile}% of candidates",
        "comparisons": comparisons,
    }


# ==================== RESUME VERSION TRACKING ====================

@router.get("/versions/{resume_id}")
def get_resume_versions(
    resume_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.get_current_user),
):
    """
    📋 Resume Version History
    =========================
    Get all analysis snapshots for a resume to track improvement over time.
    """
    resume = db.query(Resume).filter(
        Resume.id == resume_id,
        Resume.owner_id == current_user.id,
    ).first()
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")

    versions = db.query(ResumeVersion).filter(
        ResumeVersion.resume_id == resume_id,
        ResumeVersion.owner_id == current_user.id,
    ).order_by(ResumeVersion.version_number.asc()).all()

    result = []
    for v in versions:
        result.append({
            "version": v.version_number,
            "title": v.title,
            "ats_score": v.ats_score,
            "predicted_role": v.predicted_role,
            "score_breakdown": v.score_breakdown,
            "missing_skills": v.missing_skills,
            "key_strengths": v.key_strengths,
            "created_at": str(v.created_at) if v.created_at else None,
        })

    # Calculate improvement trends
    if len(result) >= 2:
        first = result[0]["ats_score"] or 0
        latest = result[-1]["ats_score"] or 0
        improvement = round(latest - first, 1)
    else:
        improvement = 0

    return {
        "resume_id": resume_id,
        "current_score": resume.ats_score,
        "total_versions": len(result),
        "improvement": improvement,
        "versions": result,
    }


@router.post("/versions/{resume_id}/snapshot")
def create_version_snapshot(
    resume_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.get_current_user),
):
    """
    📸 Create a snapshot of the current resume analysis.
    Call this before and after rewrites to track improvement.
    """
    resume = db.query(Resume).filter(
        Resume.id == resume_id,
        Resume.owner_id == current_user.id,
    ).first()
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")

    # Get next version number
    last_version = db.query(ResumeVersion).filter(
        ResumeVersion.resume_id == resume_id,
    ).order_by(ResumeVersion.version_number.desc()).first()

    next_version = (last_version.version_number + 1) if last_version else 1

    # Retention limit: max 20 versions per resume
    MAX_VERSIONS = 20
    version_count = db.query(ResumeVersion).filter(
        ResumeVersion.resume_id == resume_id,
    ).count()
    if version_count >= MAX_VERSIONS:
        # Delete oldest versions beyond limit
        oldest = db.query(ResumeVersion).filter(
            ResumeVersion.resume_id == resume_id,
        ).order_by(ResumeVersion.version_number.asc()).first()
        if oldest:
            db.delete(oldest)
            db.flush()

    snapshot = ResumeVersion(
        resume_id=resume_id,
        owner_id=current_user.id,
        version_number=next_version,
        title=f"v{next_version} - {resume.title or 'Resume'}",
        ats_score=resume.ats_score,
        predicted_role=resume.predicted_role,
        score_breakdown=resume.score_breakdown,
        missing_skills=resume.missing_keywords,
        key_strengths=resume.key_strengths,
    )
    db.add(snapshot)
    db.commit()
    db.refresh(snapshot)

    return {
        "message": f"Version {next_version} snapshot created",
        "version": next_version,
        "ats_score": snapshot.ats_score,
    }


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


# ==================== SYSTEM STATUS ====================

@router.get("/system-status")
def get_system_status(
    current_user: User = Depends(deps.get_current_user)
):
    """
    🏥 System health & component status.
    Shows which AI services are available.
    """
    import datetime
    from app.core.ai_model import AIModelManager

    return {
        "timestamp": datetime.datetime.utcnow().isoformat(),
        "components": {
            "gemini": {
                "configured": AIModelManager._gemini_configured,
                "status": "online" if AIModelManager._gemini_configured else "offline",
            },
            "spacy": {
                "loaded": AIModelManager._spacy_nlp is not None,
                "status": "online" if AIModelManager._spacy_nlp is not None else "loading",
            },
            "rag_engine": {
                "status": "online",
            },
            "offline_mode": {
                "available": True,
                "description": "ATS scoring, role matching, skill graph work without Gemini",
            },
        },
    }

