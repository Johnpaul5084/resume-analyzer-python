from app.services.ai_skill_ontology import SkillOntology
import re
import json
import os
import logging
from typing import Dict, List, Any

logger = logging.getLogger(__name__)

class AIScoringEngine:
    """
    Lightweight Multi-Metric Intelligence Engine.
    Removed SentenceTransformers and PyTorch to fit in 512MB RAM.
    Uses Keyword Relevance and Structure Analysis.
    """
    
    @staticmethod
    def calculate_comprehensive_score(resume_text: str, parsed_data: Dict[str, Any], target_role: str = "Software Engineer") -> Dict[str, Any]:
        """
        IIIT-Level Engine (Optimized for Cloud RAM):
        Final Score = 0.35*relevance_score + 0.25*skill_coverage + 0.20*experience_depth + 0.20*ats_format_score
        """
        # 1. Relevance Score (Keyword Similarity)
        template = AIScoringEngine.get_role_template(target_role)
        relevance_score = AIScoringEngine.calculate_relevance_score(resume_text, template)
        
        # 2. Skill Coverage (Ontology Match)
        user_skills = parsed_data.get("skills", [])
        primary_cluster = SkillOntology.identify_primary_cluster(user_skills)
        skill_coverage = min((len(user_skills) / 10) * 100, 100) # Balanced for 10 core skills
        gap_analysis = SkillOntology.get_missing_skills(primary_cluster, user_skills)
        
        # 3. Experience Depth (Impact & Metrics)
        metrics_found = len(re.findall(r'\d+%', resume_text)) + len(re.findall(r'\$\d+', resume_text))
        experience_depth = min((metrics_found / 4) * 100, 100)
        
        # 4. ATS Format Score (Structural Quality)
        ats_format_score = 0
        if parsed_data.get("personal_info", {}).get("email"): ats_format_score += 25
        if user_skills: ats_format_score += 25
        if len(resume_text.split()) > 150: ats_format_score += 50
        
        # Final Weighted Aggregation
        final_score = (
            (relevance_score * 0.35) +
            (skill_coverage * 0.25) +
            (experience_depth * 0.20) +
            (ats_format_score * 0.20)
        )
        
        return {
            "ats_score": round(final_score, 2),
            "breakdown": {
                "semantic_similarity": round(relevance_score, 2), # Key preserved for UI
                "skill_coverage": round(skill_coverage, 2),
                "experience_depth": round(experience_depth, 2),
                "ats_format_score": round(ats_format_score, 2),
                "market_readiness": 90 if final_score > 75 else 70
            },
            "explainable_ai": AIScoringEngine._generate_explanation(final_score, primary_cluster, gap_analysis, metrics_found)
        }

    @staticmethod
    def _generate_explanation(score: float, cluster: str, gaps: List[str], metrics: int) -> str:
        explanation = f"Projected Fit: {cluster} Profile. "
        if score > 75:
            explanation += "Your profile aligns with top-tier MNC benchmarks. "
        else:
            explanation += "Profile is developing towards professional standards. "
            
        if metrics < 2:
            explanation += "Pro Tip: Quantify your impact with data (%, $, values) to impress recruiters. "
            
        if gaps:
            explanation += f"Priority Skill Gaps: {', '.join(gaps[:3])}."
            
        return explanation

    @staticmethod
    def calculate_relevance_score(resume_text: str, target_template: str) -> float:
        """
        Lightweight Semantic Proxy using Keyword Overlap.
        Saves 500MB RAM compared to local Transformers.
        """
        try:
            resume_words = set(re.findall(r'\w+', resume_text.lower()))
            template_words = set(re.findall(r'\w+', target_template.lower()))
            
            # Remove small words
            template_words = {w for w in template_words if len(w) > 3}
            
            if not template_words:
                return 70.0
                
            match_count = len(resume_words.intersection(template_words))
            score = (match_count / len(template_words)) * 100
            
            # Boost score as exact keyword match is strict
            return round(min(score * 1.5 + 40, 100), 2)
        except Exception as e:
            logger.error(f"Relevance scoring error: {e}")
            return 65.0

    @staticmethod
    def get_role_template(role: str) -> str:
        db_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "career_engine", "role_database.json")
        try:
            if os.path.exists(db_path):
                with open(db_path, encoding='utf-8') as f:
                    role_db = json.load(f)
                role_data = role_db.get(role)
                if role_data:
                    return f"{role}. {role_data.get('description', '')} {', '.join(role_data.get('mandatory_skills', []))}."
        except Exception:
            pass
            
        templates = {
            "Software Engineer": "Backend Java Python FastAPI Software Developer Algorithms Coding Engineer",
            "Data Scientist": "Machine Learning ML Data Science Python Statistics Analysis Data Analyst",
            "Full Stack Developer": "Frontend React Javascript Node Web Developer Fullstack API"
        }
        return templates.get(role, "Professional industrial experience with leadership and technical excellence.")
