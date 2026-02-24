from app.core.ai_model import AIModelManager
import numpy as np
import json
import os
import logging

logger = logging.getLogger(__name__)

class SemanticRoleMatcher:
    """
    Lightweight Semantic Role Matcher.
    Removed FAISS to fit in 512MB RAM.
    """
    _role_names = []
    _role_data = {}
    
    @classmethod
    def _initialize_index(cls):
        db_path = os.path.join(os.path.dirname(__file__), "role_database.json")
        if not os.path.exists(db_path):
            return
            
        with open(db_path, encoding='utf-8') as f:
            cls._role_data = json.load(f)
        cls._role_names = list(cls._role_data.keys())

    @classmethod
    def find_best_roles(cls, resume_text: str, top_k: int = 3):
        try:
            if not cls._role_names:
                cls._initialize_index()
                
            if not cls._role_names:
                return ["Software Engineer"]
                
            # Lightweight keyword Match
            text_lower = resume_text.lower()
            scores = []
            
            for role in cls._role_names:
                score = 0
                if role.lower() in text_lower:
                    score += 5
                
                # Skill matching
                skills = cls._role_data[role].get('mandatory_skills', [])
                for skill in skills:
                    if skill.lower() in text_lower:
                        score += 1
                
                scores.append((role, score))
            
            scores.sort(key=lambda x: x[1], reverse=True)
            results = [s[0] for s in scores[:top_k] if s[1] > 0]
            
            return results if results else ["Software Engineer"]
        except Exception as e:
            logger.error(f"SemanticRoleMatcher error: {e}")
            return ["Software Engineer"]
