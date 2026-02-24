from app.services.ai_skill_ontology import SkillOntology
from app.core.ai_model import AIModelManager
from sentence_transformers import util
import re
import json
import os
import logging
from typing import Dict, List, Any

logger = logging.getLogger(__name__)

class AIScoringEngine:
    """
    AI Resume Analyzer Multi-Metric Intelligence Engine
    IIIT/IIT Level Implementation: Weighted multi-stage evaluation.
    """
    
    @staticmethod
    def calculate_comprehensive_score(resume_text: str, parsed_data: Dict[str, Any], target_role: str = "Software Engineer") -> Dict[str, Any]:
        """
        IIIT-Level Engine:
        Final Score = 0.35*semantic_similarity + 0.25*skill_coverage + 0.20*experience_depth + 0.20*ats_format_score
        """
        # 1. Semantic Similarity (Sentence Transformers)
        template = AIScoringEngine.get_role_template(target_role)
        semantic_similarity = AIScoringEngine.calculate_semantic_score(resume_text, template)
        
        # 2. Skill Coverage (Ontology Match)
        user_skills = parsed_data.get("skills", [])
        primary_cluster = SkillOntology.identify_primary_cluster(user_skills)
        skill_coverage = min((len(user_skills) / 12) * 100, 100)
        gap_analysis = SkillOntology.get_missing_skills(primary_cluster, user_skills)
        
        # 3. Experience Depth (Impact & Context)
        metrics_found = len(re.findall(r'\d+%', resume_text)) + len(re.findall(r'\$\d+', resume_text))
        experience_depth = min((metrics_found / 5) * 100, 100)
        
        # 4. ATS Format Score (Structural Quality)
        ats_format_score = 0
        if parsed_data.get("personal_info", {}).get("email"): ats_format_score += 25
        if user_skills: ats_format_score += 25
        if len(resume_text.split()) > 200: ats_format_score += 50
        
        # Final Weighted Aggregation
        final_score = (
            (semantic_similarity * 0.35) +
            (skill_coverage * 0.25) +
            (experience_depth * 0.20) +
            (ats_format_score * 0.20)
        )
        
        return {
            "ats_score": round(final_score, 2),
            "breakdown": {
                "semantic_similarity": round(semantic_similarity, 2),
                "skill_coverage": round(skill_coverage, 2),
                "experience_depth": round(experience_depth, 2),
                "ats_format_score": round(ats_format_score, 2),
                "market_readiness": 90 if final_score > 80 else 75
            },
            "explainable_ai": AIScoringEngine._generate_explanation(final_score, primary_cluster, gap_analysis, metrics_found)
        }

    @staticmethod
    def _generate_explanation(score: float, cluster: str, gaps: List[str], metrics: int) -> str:
        explanation = f"Projected Fit: {cluster} Profile. "
        if score > 80:
            explanation += "Your profile aligns with top-tier MNC benchmarks. "
        else:
            explanation += "Profile is developing towards professional standards. "
            
        if metrics < 3:
            explanation += "Enhance impact quantification by adding more percentages and data-driven results. "
            
        if gaps:
            explanation += f"Critical skill gaps identified in: {', '.join(gaps)}."
            
        return explanation

    @staticmethod
    def calculate_semantic_score(resume_text: str, target_template: str) -> float:
        try:
            model = AIModelManager.get_model()
            resume_emb = model.encode(resume_text, convert_to_tensor=True)
            template_emb = model.encode(target_template, convert_to_tensor=True)
            cos_sim = util.pytorch_cos_sim(resume_emb, template_emb)
            return round(min(max(cos_sim.item() * 140, 0), 100), 2)
        except Exception as e:
            logger.error(f"Semantic scoring error: {e}")
            return 70.0

    @staticmethod
    def get_role_template(role: str) -> str:
        db_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "career_engine", "role_database.json")
        try:
            with open(db_path, encoding='utf-8') as f:
                role_db = json.load(f)
            role_data = role_db.get(role)
            if role_data:
                return f"{role}. {role_data.get('description', '')} Mandatory Skills: {', '.join(role_data.get('mandatory_skills', []))}."
        except Exception as e:
            logger.warning(f"Failed to load role template for {role}: {e}")
            
        templates = {
            "Software Engineer": "Backend development, algorithms, data structures, system design, microservices, cloud computing, unit testing.",
            "Data Scientist": "Machine learning, statistical modeling, data visualization, Python, SQL, deep learning, feature engineering.",
            "Full Stack Developer": "Frontend UI/UX, Backend APIs, database management, React, Node.js, deployment, responsive design."
        }
        return templates.get(role, "Professional industrial experience with leadership and technical excellence.")
