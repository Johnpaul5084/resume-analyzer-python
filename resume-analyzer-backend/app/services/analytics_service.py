"""
Advanced Analytics Service - Track resume performance and provide insights
"""
from typing import Dict, Any, List
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models.all_models import Resume, User
import json

class AnalyticsService:
    """Service for advanced resume and user analytics"""
    
    @staticmethod
    def get_resume_analytics(resume_id: int, db: Session) -> Dict[str, Any]:
        """
        Get comprehensive analytics for a specific resume
        """
        
        resume = db.query(Resume).filter(Resume.id == resume_id).first()
        if not resume:
            return {"error": "Resume not found"}
        
        # Calculate metrics
        created_date = resume.created_at
        days_since_upload = (datetime.utcnow() - created_date).days
        
        # Mock view/download data (in production, track these in separate table)
        views = 0  # Placeholder
        downloads = 0  # Placeholder
        applications = 0  # Placeholder
        
        # ATS Score trend (if multiple versions exist)
        score_trend = "stable"  # Can be: improving, declining, stable
        
        # Keyword performance
        extracted_skills = resume.score_breakdown.get("extracted_skills", []) if resume.score_breakdown else []
        
        return {
            "resume_id": resume_id,
            "title": resume.title,
            "uploaded_date": created_date.isoformat(),
            "days_active": days_since_upload,
            "performance": {
                "ats_score": resume.ats_score,
                "views": views,
                "downloads": downloads,
                "applications": applications,
                "response_rate": 0.0  # Placeholder
            },
            "score_analysis": {
                "current_score": resume.ats_score,
                "trend": score_trend,
                "breakdown": resume.score_breakdown or {},
                "improvement_potential": max(0, 90 - resume.ats_score)
            },
            "keyword_analysis": {
                "total_keywords": len(extracted_skills),
                "top_keywords": extracted_skills[:10],
                "missing_keywords": resume.missing_keywords[:10] if resume.missing_keywords else []
            },
            "recommendations": AnalyticsService._generate_recommendations(resume)
        }
    
    @staticmethod
    def get_user_analytics(user_id: int, db: Session) -> Dict[str, Any]:
        """
        Get comprehensive analytics for a user's job search journey
        """
        
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            return {"error": "User not found"}
        
        # Get all user's resumes
        resumes = db.query(Resume).filter(Resume.owner_id == user_id).all()
        
        if not resumes:
            return {
                "user_id": user_id,
                "total_resumes": 0,
                "message": "No resumes uploaded yet"
            }
        
        # Calculate aggregate metrics
        total_resumes = len(resumes)
        avg_ats_score = sum(r.ats_score for r in resumes) / total_resumes if total_resumes > 0 else 0
        highest_score = max((r.ats_score for r in resumes), default=0)
        lowest_score = min((r.ats_score for r in resumes), default=0)
        
        # Get all unique skills across resumes
        all_skills = set()
        for resume in resumes:
            if resume.score_breakdown and "extracted_skills" in resume.score_breakdown:
                all_skills.update(resume.score_breakdown["extracted_skills"])
        
        # Calculate job search progress
        account_age_days = (datetime.utcnow() - user.created_at).days
        
        return {
            "user_id": user_id,
            "account_created": user.created_at.isoformat(),
            "account_age_days": account_age_days,
            "resume_stats": {
                "total_resumes": total_resumes,
                "average_ats_score": round(avg_ats_score, 2),
                "highest_score": round(highest_score, 2),
                "lowest_score": round(lowest_score, 2),
                "score_improvement": round(highest_score - lowest_score, 2)
            },
            "skill_profile": {
                "total_unique_skills": len(all_skills),
                "top_skills": list(all_skills)[:15],
                "skill_diversity_score": min(len(all_skills) * 2, 100)
            },
            "activity": {
                "resumes_this_month": AnalyticsService._count_resumes_this_month(resumes),
                "most_active_day": AnalyticsService._get_most_active_day(resumes),
                "upload_frequency": AnalyticsService._calculate_upload_frequency(resumes)
            },
            "job_search_health": {
                "score": AnalyticsService._calculate_job_search_health(user, resumes),
                "status": AnalyticsService._get_health_status(avg_ats_score),
                "next_steps": AnalyticsService._suggest_next_steps(avg_ats_score, total_resumes)
            }
        }
    
    @staticmethod
    def get_market_insights(target_role: str = None) -> Dict[str, Any]:
        """
        Get job market insights and trends
        """
        
        # Mock data - in production, this would come from real job market APIs
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
                {"skill": "Machine Learning", "demand_change": "+25%", "avg_salary": "$140k"},
                {"skill": "Docker", "demand_change": "+10%", "avg_salary": "$125k"}
            ],
            "hot_roles": [
                {"role": "AI Engineer", "openings": 15000, "growth": "+30%"},
                {"role": "Full Stack Developer", "openings": 25000, "growth": "+20%"},
                {"role": "DevOps Engineer", "openings": 12000, "growth": "+22%"},
                {"role": "Data Scientist", "openings": 18000, "growth": "+28%"}
            ],
            "top_hiring_companies": [
                {"company": "Google", "openings": 500, "avg_salary": "$180k"},
                {"company": "Amazon", "openings": 800, "avg_salary": "$160k"},
                {"company": "Microsoft", "openings": 600, "avg_salary": "$170k"},
                {"company": "Meta", "openings": 400, "avg_salary": "$190k"}
            ],
            "geographic_insights": [
                {"location": "San Francisco, CA", "avg_salary": "$150k", "openings": 8000},
                {"location": "New York, NY", "avg_salary": "$140k", "openings": 7500},
                {"location": "Seattle, WA", "avg_salary": "$145k", "openings": 6000},
                {"location": "Austin, TX", "avg_salary": "$120k", "openings": 5000}
            ]
        }
        
        if target_role:
            insights["role_specific"] = {
                "role": target_role,
                "total_openings": 15000,
                "avg_salary": "$130k",
                "required_skills": ["Python", "SQL", "Cloud", "Agile"],
                "experience_needed": "3-5 years",
                "remote_percentage": "65%"
            }
        
        return insights
    
    @staticmethod
    def _generate_recommendations(resume: Resume) -> List[str]:
        """Generate personalized recommendations based on resume analysis"""
        
        recommendations = []
        
        if resume.ats_score < 50:
            recommendations.append("🎯 Your ATS score is below average. Focus on adding more relevant keywords.")
        elif resume.ats_score < 70:
            recommendations.append("📈 Good progress! Add more quantifiable achievements to boost your score.")
        else:
            recommendations.append("✅ Excellent ATS score! Your resume is well-optimized.")
        
        if resume.missing_keywords:
            recommendations.append(f"🔑 Add these keywords: {', '.join(resume.missing_keywords[:5])}")
        
        if resume.score_breakdown:
            grammar_score = resume.score_breakdown.get("grammar_score", 85)
            if grammar_score < 80:
                recommendations.append("✍️ Consider reviewing grammar and sentence structure.")
        
        recommendations.append("💼 Apply to 5-10 jobs per week for best results.")
        recommendations.append("🔄 Update your resume every 2-3 weeks with new achievements.")
        
        return recommendations
    
    @staticmethod
    def _count_resumes_this_month(resumes: List[Resume]) -> int:
        """Count resumes uploaded this month"""
        current_month = datetime.utcnow().month
        current_year = datetime.utcnow().year
        return sum(1 for r in resumes if r.created_at.month == current_month and r.created_at.year == current_year)
    
    @staticmethod
    def _get_most_active_day(resumes: List[Resume]) -> str:
        """Get the day of week with most uploads"""
        if not resumes:
            return "N/A"
        day_counts = {}
        for resume in resumes:
            day = resume.created_at.strftime("%A")
            day_counts[day] = day_counts.get(day, 0) + 1
        return max(day_counts, key=day_counts.get) if day_counts else "N/A"
    
    @staticmethod
    def _calculate_upload_frequency(resumes: List[Resume]) -> str:
        """Calculate how often user uploads resumes"""
        if len(resumes) < 2:
            return "Not enough data"
        
        dates = sorted([r.created_at for r in resumes])
        avg_days_between = sum((dates[i+1] - dates[i]).days for i in range(len(dates)-1)) / (len(dates)-1)
        
        if avg_days_between < 7:
            return "Very Active (multiple per week)"
        elif avg_days_between < 30:
            return "Active (weekly)"
        else:
            return "Occasional (monthly)"
    
    @staticmethod
    def _calculate_job_search_health(user: User, resumes: List[Resume]) -> int:
        """Calculate overall job search health score (0-100)"""
        score = 50  # Base score
        
        # Factor 1: Resume count
        if len(resumes) >= 3:
            score += 15
        elif len(resumes) >= 1:
            score += 10
        
        # Factor 2: Average ATS score
        if resumes:
            avg_ats = sum(r.ats_score for r in resumes) / len(resumes)
            score += int(avg_ats * 0.3)
        
        # Factor 3: Recent activity
        recent_resumes = [r for r in resumes if (datetime.utcnow() - r.created_at).days < 30]
        if recent_resumes:
            score += 10
        
        return min(score, 100)
    
    @staticmethod
    def _get_health_status(avg_ats_score: float) -> str:
        """Get health status based on ATS score"""
        if avg_ats_score >= 75:
            return "Excellent - Ready to apply!"
        elif avg_ats_score >= 60:
            return "Good - Minor improvements needed"
        elif avg_ats_score >= 45:
            return "Fair - Needs optimization"
        else:
            return "Needs Work - Focus on improvements"
    
    @staticmethod
    def _suggest_next_steps(avg_ats_score: float, total_resumes: int) -> List[str]:
        """Suggest next steps based on user's progress"""
        steps = []
        
        if total_resumes == 0:
            steps.append("📄 Upload your first resume to get started")
        elif total_resumes == 1:
            steps.append("🔄 Create role-specific versions of your resume")
        
        if avg_ats_score < 70:
            steps.append("🎯 Improve your ATS score by adding relevant keywords")
            steps.append("✍️ Use AI to rewrite weak sections")
        
        steps.append("💼 Start applying to 5-10 jobs per week")
        steps.append("🌐 Optimize your LinkedIn profile")
        steps.append("📧 Set up job alerts for your target roles")
        
        return steps[:5]  # Return top 5 suggestions
