import json
import os
import logging
from typing import Dict, Any, List
from app.career_engine.semantic_role_matcher import SemanticRoleMatcher
from app.career_engine.roadmap_ai_generator import RoadmapAIGenerator
from app.career_engine.skill_graph_visualizer import SkillGraphVisualizer

logger = logging.getLogger(__name__)

class IRISMentorBot:
    """
    IRIS Career Mentor Bot 2.0
    The brain of the career intelligence platform.
    """
    
    @staticmethod
    def get_market_demand(role: str) -> str:
        demand_path = os.path.join(os.path.dirname(__file__), "demand_scores.json")
        try:
            with open(demand_path) as f:
                scores = json.load(f)
            score = scores.get(role, 5.0)
            if score >= 9.0: return "Very High 🔥"
            if score >= 8.0: return "High 📈"
            return "Stable"
        except:
            return "Stable"

    @staticmethod
    def analyze_career_path(resume_text: str, user_skills: List[str]) -> Dict[str, Any]:
        # 1. Semantic Match
        best_roles = SemanticRoleMatcher.find_best_roles(resume_text)
        target_role = best_roles[0]
        
        # 2. Get Role Meta
        role_db_path = os.path.join(os.path.dirname(__file__), "role_database.json")
        try:
            with open(role_db_path) as f:
                role_db = json.load(f)
            role_info = role_db.get(target_role, {})
        except:
            role_info = {}
            
        required_skills = role_info.get("mandatory_skills", [])
        
        # 3. Gap Analysis
        user_skills_lower = [s.lower() for s in user_skills]
        missing_skills = [s for s in required_skills if s.lower() not in user_skills_lower]
        
        # 4. Market Demand
        demand = IRISMentorBot.get_market_demand(target_role)
        
        # 5. AI Roadmap
        roadmap = RoadmapAIGenerator.generate_dynamic_roadmap(target_role, missing_skills)
        
        # 6. Skill Graph
        graph_b64 = SkillGraphVisualizer.generate_skill_graph(user_skills, required_skills)
        
        return {
            "recommended_role": target_role,
            "market_demand": demand,
            "salary_range": role_info.get("avg_salary_range", "N/A"),
            "growth_score": role_info.get("growth_score", 7.0),
            "missing_skills": missing_skills,
            "dynamic_roadmap": roadmap,
            "skill_graph": graph_b64,
            "mentor_advice": f"As your IRIS Career Mentor, I've analyzed your {len(user_skills)} skills. You are a strong candidate for a {target_role} role. Focusing on {len(missing_skills)} key areas will significantly increase your MNC visibility."
        }
