from app.services.iris_scoring_engine import IRISScoringEngine
from app.services.iris_parser_service import IRISParserService
import re
from typing import List, Dict, Any
import logging

logger = logging.getLogger(__name__)

class ATSScoringService:
    
    @staticmethod
    async def calculate_score(resume_text: str, job_description: str = None) -> Dict[str, Any]:
        """
        IRIS (Intelligent Resume Intelligence System) Comprehensive Engine
        IIIT/IIT Level: Semantic Similarity + Structured Skill Gap + Impact Reasoning
        """
        # A. High-Fidelity Structured Parsing
        structured_data = IRISParserService.extract_structured_data(resume_text)
        
        # B. Multi-Metric Scoring Engine
        analysis = IRISScoringEngine.calculate_comprehensive_score(
            resume_text=resume_text,
            parsed_data=structured_data,
            target_role="Software Engineer" # Default, can be refined by prediction
        )
        
        return {
            "ats_score": analysis["ats_score"],
            "breakdown": analysis["breakdown"],
            "analysis": analysis["explainable_ai"],
            "suggestions": [
                "Map your skills to the specific job requirements found in the ontology.",
                "Incorporate more result-oriented metrics (e.g., 'Improved performance by 15%').",
                "Ensure your structure follows the standard global professional sections."
            ],
            "missing_skills": SkillOntology.get_missing_skills(
                SkillOntology.identify_primary_cluster(structured_data["skills"]), 
                structured_data["skills"]
            ),
            "key_strengths": structured_data["skills"][:4]
        }

