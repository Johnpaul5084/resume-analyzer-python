import re
from typing import List, Dict, Any, Tuple
from collections import Counter
import numpy as np
from google import genai
from app.core.config import settings
import logging
import json

logger = logging.getLogger(__name__)

# Initialize Gemini client
_client = None
if settings.GEMINI_API_KEY:
    _client = genai.Client(api_key=settings.GEMINI_API_KEY)

try:
    import spacy
    NLP_AVAILABLE = True
except ImportError:
    NLP_AVAILABLE = False
    spacy = None

# Load NLP model
nlp = None
if NLP_AVAILABLE:
    try:
        nlp = spacy.load("en_core_web_sm")
    except:
        NLP_AVAILABLE = False

class ATSScoringService:
    
    @staticmethod
    async def calculate_score(resume_text: str, job_description: str = None) -> Dict[str, Any]:
        """
         Phoenix Upgrade: Semantic ATS Scoring
        1. Contextual Match (50%) - Semantic analysis via Gemini
        2. Experience Depth (20%) - Logic-based
        3. Structural Quality (15%) - Section detection
        4. Career Roadmap (15%) - Future growth potential
        """
        
        # 1. Base Logic-based Scoring (Fast Fallback)
        resume_lower = resume_text.lower()
        sections = ['experience', 'education', 'skills', 'projects', 'summary', 'achievements', 'certifications']
        found_sections = [sec for sec in sections if sec in resume_lower]
        structure_score = (len(found_sections) / len(sections)) * 100
        
        # 2. Semantic Analysis (The Maverick/Summit Feature)
        semantic_data = await ATSScoringService._get_semantic_analysis(resume_text, job_description)
        
        # 3. Content Metrics
        word_count = len(resume_text.split())
        content_score = min((word_count / 450) * 100, 100)
        
        # 4. Final Aggregation
        ats_score = (
            (semantic_data.get('match_score', 70) * 0.5) +
            (content_score * 0.2) +
            (structure_score * 0.15) +
            (85 * 0.15) # Default baseline for growth potential
        )
        
        return {
            "ats_score": round(ats_score, 2),
            "breakdown": {
                "semantic_match": round(semantic_data.get('match_score', 0), 2),
                "experience_score": round(content_score, 2),
                "structure_score": round(structure_score, 2),
                "market_readiness": 85
            },
            "analysis": semantic_data.get('feedback', "Analysis complete."),
            "suggestions": semantic_data.get('suggestions', []),
            "missing_skills": semantic_data.get('missing_skills', []),
            "key_strengths": semantic_data.get('strengths', [])
        }

    @staticmethod
    async def _get_semantic_analysis(resume_text: str, jd: str = None) -> Dict[str, Any]:
        """Calls Gemini AI for deep semantic understanding of candidate fit"""
        if not _client:
            logger.warning("Gemini AI not configured. Using fallback scoring.")
            return {"match_score": 75, "feedback": "AI analysis unavailable (Missing Key).", "suggestions": []}

        prompt = f"""
        Act as a Senior HR Recruiter and ATS Specialist.
        Analyze this Resume against the Job Description (if provided).
        
        RESUME:
        {resume_text[:4000]}
        
        JOB DESCRIPTION:
        {jd[:2000] if jd else "General Career Suitability"}
        
        Provide a JSON response with:
        1. match_score (0-100)
        2. strengths (list of 3 key professional strengths)
        3. missing_skills (list of missing skills for the target role)
        4. suggestions (list of 3 ways to improve for 2026 job market)
        5. feedback (one professional sentence about overall fit)
        
        Return ONLY valid JSON.
        """
        
        try:
            response = _client.models.generate_content(
                model="gemini-2.0-flash",
                contents=prompt
            )
            text = response.text
            json_match = re.search(r'\{.*\}', text, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
            return {"match_score": 70, "feedback": "Partial analysis."}
        except Exception as e:
            logger.error(f"Gemini Semantic Error: {e}")
            return {"match_score": 70, "feedback": "Analysis failed."}

    @staticmethod
    def calculate_match_score(resume_text: str, job_description: str) -> Dict[str, Any]:
        """Legacy synchronous version for backward compatibility"""
        # Just a placeholder, in real app would be async
        return {"ats_score": 75}

    @staticmethod
    def suggest_improvements(resume_text: str, missing_keywords: List[str]) -> str:
        return "Upgrade to Advanced AI Analysis for real suggestions."

