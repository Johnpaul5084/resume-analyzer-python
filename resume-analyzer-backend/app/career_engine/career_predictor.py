from typing import List, Dict, Any
from app.career_engine.domain_database import CAREER_DOMAINS

class CareerPredictor:
    """
    AI Career Prediction Engine
    Analyzes branch, skills, and interests to suggest career domains.
    """

    @staticmethod
    def predict_paths(branch: str, skills: List[str], interests: List[str]) -> Dict[str, Any]:
        """
        Predicts best-fit domains and emerging roles.
        """
        # Simple heuristic-based matching
        recommended_domains = CAREER_DOMAINS.get(branch, ["General Engineering"])
        
        # Refine recommendations based on skills
        skills_lower = [s.lower() for s in skills]
        refined_roles = []
        
        if "python" in skills_lower or "ml" in skills_lower:
            refined_roles.append("AI/ML Engineer")
        if "react" in skills_lower or "node" in skills_lower:
            refined_roles.append("Full Stack Developer")
            
        return {
            "recommended_domains": recommended_domains[:3],
            "emerging_roles": refined_roles if refined_roles else ["SDE - Product"],
            "future_growth_score": 8.8 if branch == "Computer Science" else 7.5,
            "risk_level": "Low"
        }
