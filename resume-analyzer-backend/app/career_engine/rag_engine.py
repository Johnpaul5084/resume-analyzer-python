from app.services.ai_rewrite_service import AIRewriteService
import numpy as np
import json
import os
import logging
import regex as re

logger = logging.getLogger(__name__)

# Global index and role tracking
_roles_data = {}
_role_names = []

def build_index():
    global _roles_data, _role_names
    
    logger.info("⚡ Initializing Optimized Lightweight RAG Engine...")
    
    # 1. Load Knowledge Base
    db_path = os.path.join(os.path.dirname(__file__), "role_database.json")
    if not os.path.exists(db_path):
        logger.error(f"❌ Role Database not found at {db_path}")
        return

    try:
        with open(db_path, encoding='utf-8') as f:
            _roles_data = json.load(f)
        _role_names = list(_roles_data.keys())
        logger.info(f"✅ AI Search Space initialized with {len(_role_names)} roles.")
    except Exception as e:
        logger.error(f"Failed to load roles: {e}")

def retrieve_relevant_roles(resume_text: str, top_k: int = 3):
    global _roles_data, _role_names
    
    if not _role_names:
        build_index()

    if not resume_text or len(resume_text.strip()) < 10:
        return ["Software Engineer"]

    try:
        # LITE SEARCH: Keyword matching for speed and 0 RAM usage
        scores = []
        text_lower = resume_text.lower()
        
        for role in _role_names:
            score = 0
            # Check for role name in text
            if role.lower() in text_lower:
                score += 10
            
            # Check for skills
            skills = _roles_data[role].get('mandatory_skills', [])
            for skill in skills:
                if skill.lower() in text_lower:
                    score += 2
            
            scores.append((role, score))
        
        # Sort by score and return top_k
        scores.sort(key=lambda x: x[1], reverse=True)
        results = [s[0] for s in scores[:top_k] if s[1] > 0]
        
        if not results:
            return ["Software Engineer"]
            
        return results
    except Exception as e:
        logger.error(f"⚠️ Optimized Retrieval Error: {e}")
        return ["Software Engineer"]
