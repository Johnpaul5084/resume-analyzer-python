from app.services.ai_scoring_engine import AIScoringEngine
from app.services.ai_parser_service import AIParserService
from app.services.ai_skill_ontology import SkillOntology
from app.career_engine.rag_engine import retrieve_relevant_roles
import re
from typing import List, Dict, Any
import logging

logger = logging.getLogger(__name__)

class ATSScoringService:
    
    @staticmethod
    async def calculate_score(resume_text: str, job_description: str = None) -> Dict[str, Any]:
        """
        AI Resume Analyzer Comprehensive Engine
        Semantic Similarity + Structured Skill Gap + Impact Reasoning
        """
        # A. High-Fidelity Structured Parsing
        structured_data = AIParserService.extract_structured_data(resume_text)

        # B. RAG-Driven Role Identification
        if job_description:
            target_role_detected = "Software Engineer" # Placeholder for JD role extraction
        else:
            detected_roles = retrieve_relevant_roles(resume_text, top_k=1)
            target_role_detected = detected_roles[0]

        # C. Multi-Metric Scoring Engine
        analysis = AIScoringEngine.calculate_comprehensive_score(
            resume_text=resume_text,
            parsed_data=structured_data,
            target_role=target_role_detected
        )
        
        return {
            "ats_score": analysis["ats_score"],
            "breakdown": analysis["breakdown"],
            "analysis": analysis["explainable_ai"],
            "suggestions": [
                "Map your skills to the specific job requirements found in the ontology.",
                "Incorporate more result-oriented metrics (e.g., 'Improved performance by 15%').",
                "Ensure your structure follows the standard professional sections."
            ],
            "missing_skills": SkillOntology.get_missing_skills(
                SkillOntology.identify_primary_cluster(structured_data["skills"]), 
                structured_data["skills"]
            ),
            "key_strengths": structured_data["skills"][:4]
        }

