from app.career_engine.domain_database import ROLE_STRATEGIES
from typing import Dict, Any

class ResumeStrategy:
    """
    AI Career & Resume Strategy Guide
    Provides role-specific guidance for FAANG and MNCs.
    """

    @staticmethod
    def get_strategy(company_tier: str) -> Dict[str, Any]:
        """
        Retrieves strategy for FAANG, MNC_Service, or Core_Engineering.
        """
        return ROLE_STRATEGIES.get(company_tier, ROLE_STRATEGIES["MNC_Service"])

    @staticmethod
    def get_faang_bullet_formula() -> str:
        return "Action Verb + Technical Tool + Scale + Measurable Impact (e.g., 'Optimized query latency by 45% using Redis caching serving 50k DAU')"
