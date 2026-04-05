"""
Semantic Role Matcher v2.0
==========================

UPGRADED: Now delegates to the TF-IDF RAG Engine v2.0 for accurate matching.
Provides detailed role match results with confidence scores and skill analysis.
"""

from app.career_engine.rag_engine import (
    retrieve_relevant_roles,
    retrieve_roles_with_scores,
    get_role_data,
)
import logging

logger = logging.getLogger(__name__)


class SemanticRoleMatcher:
    """
    Semantic Role Matcher v2.0
    Uses TF-IDF + Cosine Similarity via the upgraded RAG engine.
    """

    @classmethod
    def find_best_roles(cls, resume_text: str, top_k: int = 3):
        """Find best matching roles using TF-IDF cosine similarity."""
        try:
            return retrieve_relevant_roles(resume_text, top_k=top_k)
        except Exception as e:
            logger.error(f"SemanticRoleMatcher error: {e}")
            return ["Software Engineer"]

    @classmethod
    def find_roles_with_details(cls, resume_text: str, top_k: int = 5):
        """
        Find best matching roles with detailed confidence and skill analysis.
        Returns list of dicts with role, confidence, matched/missing skills.
        """
        try:
            return retrieve_roles_with_scores(resume_text, top_k=top_k)
        except Exception as e:
            logger.error(f"SemanticRoleMatcher detailed error: {e}")
            return [{"role": "Software Engineer", "confidence": 50.0, "skills_matched": [], "skills_missing": []}]

    @classmethod
    def get_role_profile(cls, role_name: str):
        """Get complete profile data for a specific role."""
        return get_role_data(role_name)
