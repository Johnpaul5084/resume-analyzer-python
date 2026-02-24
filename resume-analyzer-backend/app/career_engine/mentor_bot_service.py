import json
import os
import logging
from typing import Dict, Any, List
from app.career_engine.rag_engine import retrieve_relevant_roles
from app.career_engine.roadmap_ai_generator import RoadmapAIGenerator
from app.career_engine.skill_graph_visualizer import SkillGraphVisualizer
from app.career_engine.domain_classifier import DomainClassifier

logger = logging.getLogger(__name__)

class AIMentorBot:
    """
    AI Career Mentor Bot v4.2
    The brain of the career intelligence platform.
    """
    
    @staticmethod
    def get_market_demand(role: str) -> str:
        demand_path = os.path.join(os.path.dirname(__file__), "demand_scores.json")
        try:
            with open(demand_path, encoding='utf-8') as f:
                scores = json.load(f)
            score = scores.get(role, 5.0)
            if score >= 9.0: return "Very High 🔥"
            if score >= 8.0: return "High 📈"
            return "Stable"
        except:
            return "Stable"

    @staticmethod
    def analyze_career_path(resume_text: str, user_skills: List[str]) -> Dict[str, Any]:
        # 0. Crash-proof Validation
        if not resume_text or not resume_text.strip():
            return {
                "recommended_role": "N/A",
                "mentor_advice": "Neural link failed: Resume content is empty. Please upload a valid resume to begin analysis.",
                "domain": "Unknown",
                "missing_skills": []
            }

        # 1. Domain Discovery
        domain = DomainClassifier.classify_profile(user_skills)
        
        # 2. RAG Retrieval (Grounded search)
        best_roles = retrieve_relevant_roles(resume_text)
        target_role = best_roles[0]
        
        # 3. Get Role Meta
        role_db_path = os.path.join(os.path.dirname(__file__), "role_database.json")
        try:
            with open(role_db_path, encoding='utf-8') as f:
                role_db = json.load(f)
            role_info = role_db.get(target_role, {})
        except:
            role_info = {}
            
        required_skills = role_info.get("mandatory_skills", [])
        
        # 4. Gap Analysis
        user_skills_lower = [s.lower() for s in user_skills]
        missing_skills = [s for s in required_skills if s.lower() not in user_skills_lower]
        
        # 5. Market Demand
        demand = AIMentorBot.get_market_demand(target_role)
        
        # 6. AI Roadmap
        roadmap = RoadmapAIGenerator.generate_dynamic_roadmap(target_role, missing_skills)
        
        # 7. Skill Graph
        graph_b64 = SkillGraphVisualizer.generate_skill_graph(user_skills, required_skills)
        
        return {
            "recommended_role": target_role,
            "market_demand": demand,
            "salary_range": role_info.get("avg_salary_range", "N/A"),
            "growth_score": role_info.get("growth_score", 7.0),
            "missing_skills": missing_skills,
            "dynamic_roadmap": roadmap,
            "skill_graph": graph_b64,
            "domain": domain,
            "mentor_advice": f"The AI has identified your profile in the {domain} domain. You are a strong candidate for a {target_role} role. Focusing on {len(missing_skills)} key areas will significantly increase your MNC visibility."
        }
