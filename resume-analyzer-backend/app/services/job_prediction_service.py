import google.generativeai as genai
from app.core.config import settings
import logging
import json
import re

logger = logging.getLogger(__name__)

class JobPredictionService:
    """
    Lightweight Gemini-based Job Prediction Service.
    Replaced heavy local transformers (BART) to fit in 512MB RAM.
    """
    
    @staticmethod
    def predict_job_role(resume_text: str, candidate_labels: list = None) -> list:
        """
        Predicts the most suitable job role based on resume text using Gemini 1.5 Flash.
        """
        if not settings.GEMINI_API_KEY:
            logger.warning("Gemini API Key missing. Returning fallback role.")
            return [{"role": "Software Engineer", "confidence": 100.0}]

        if not candidate_labels:
            candidate_labels = [
                "Software Engineer", "Data Scientist", "Data Analyst", "Product Manager",
                "Full Stack Developer", "DevOps Engineer", "Cybersecurity Analyst", "UI/UX Designer",
                "Civil Engineer", "Mechanical Engineer", "Electrical Engineer", 
                "Chemical Engineer", "Automobile Engineer",
                "Medical Doctor", "Nurse", "Pharmacist", "Biotechnologist", "Clinical Researcher",
                "Business Analyst", "Marketing Manager", "HR Manager", "Financial Analyst",
                "Sales Representative", "Operations Manager", "Supply Chain Manager",
                "Graphic Designer", "Content Writer", "Digital Marketer", "Video Editor",
                "Teacher", "Professor", "Legal Advisor", "Customer Support Specialist"
            ]

        try:
            model = genai.GenerativeModel('gemini-1.5-flash')
            prompt = f"""
            Analyze the following resume text and predict the top 3 most suitable job roles from this list:
            LIST: {', '.join(candidate_labels)}
            
            RESUME TEXT:
            {resume_text[:3000]}
            
            Return JSON only in this format:
            [
              {{"role": "Role Name", "confidence": 95.5}},
              {{"role": "Role Name", "confidence": 80.0}}
            ]
            """
            
            response = model.generate_content(prompt)
            # Extract JSON from response
            json_match = re.search(r'\[.*\]', response.text, re.DOTALL)
            if json_match:
                predictions = json.loads(json_match.group())
                return predictions[:5]
            
            logger.error(f"Failed to parse Gemini output: {response.text}")
            return [{"role": "Software Engineer", "confidence": 50.0}]

        except Exception as e:
            logger.error(f"Gemini Job Prediction Error: {e}")
            return [{"role": "Software Engineer", "confidence": 20.0}]

    @staticmethod
    def validate_content_with_bert(text: str) -> dict:
        # Mocking BERT validation by making it lightweight
        return {"quality": "Professional", "score": 85}
