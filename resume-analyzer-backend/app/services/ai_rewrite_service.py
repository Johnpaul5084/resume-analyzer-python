import google.generativeai as genai
from app.core.config import settings
from typing import Optional, Dict, Any
import json
import re
import logging

logger = logging.getLogger(__name__)

# Configure once at module level
if settings.GEMINI_API_KEY:
    genai.configure(api_key=settings.GEMINI_API_KEY)

class AIRewriteService:
    
    @staticmethod
    async def rewrite_section(text: str, section_type: str, target_role: str = "General", company_type: str = "MNC", job_description: str = None) -> str:
        """
        Rewrites resume content using Gemini 1.5 Flash.
        Produces professional, standard-formatted text ready for direct use.
        """
        if not settings.GEMINI_API_KEY:
             return "AI Rewrite Service not configured."

        try:
            model = genai.GenerativeModel('gemini-1.5-flash')
            
            # Refined prompt for direct professional text
            if job_description:
                prompt = f"""
                Act as a specialized MNC recruiter. Rewrite the following resume content to perfectly match this Job Description.
                
                JOB DESCRIPTION:
                {job_description[:1500]}
                
                RESUME CONTENT:
                {text[:4000]}
                
                REQUIREMENTS:
                1. Use standard professional English. No LaTeX, no Markdown, no symbols.
                2. Use the STAR method (Situation, Task, Action, Result) for experience.
                3. Include specific metrics and achievements (e.g., 'Increased revenue by 20%').
                4. Focus on keywords from the Job Description.
                
                OUTPUT: Return ONLY the raw, professional text for the resume. No conversational filler or formatting code.
                """
            else:
                prompt = f"""
                Act as a high-end recruiter for top global MNCs. Rewrite the following resume for a {target_role} role.
                
                RESUME CONTENT:
                {text[:4000]}
                
                REQUIREMENTS:
                1. FORMAT: Standard text only. No LaTeX, markdown (**), or special symbols.
                2. CONTENT: Professional summary, bullet-pointed skills, and result-oriented experience.
                3. STANDARDS: Use global MNC terminology. Improve grammar and impact.
                4. IMPACT: Ensure every bullet point starts with a strong action verb and includes a quantifiable result.
                
                OUTPUT: Return the complete, polished resume text. No labels like 'Here is your resume'.
                """

            response = model.generate_content(prompt)
            cleaned = response.text.replace('**', '').replace('###', '').replace('---', '').strip()
            # Remove any leading/trailing quotes often added by AI
            cleaned = re.sub(r'^["\']|["\']$', '', cleaned)
            return cleaned

        except Exception as e:
            logger.error(f"AI Rewrite Error: {e}")
            return f"Error during AI rewrite: {str(e)}"

    @staticmethod
    async def generate_summary(resume_text: str, target_role: str) -> str:
        """
        Generates a professional summary.
        """
        if not settings.GEMINI_API_KEY:
             return "AI Rewrite Service not configured."

        try:
            model = genai.GenerativeModel('gemini-1.5-flash')
            prompt = f"Write a 3-sentence professional summary for a {target_role} role based on: {resume_text[:2000]}. Text only, no formatting."
            response = model.generate_content(prompt)
            return response.text.strip()
        except Exception as e:
            logger.error(f"Summary Generation Error: {e}")
            return f"Error: {str(e)}"

    @staticmethod
    async def validate_role_fit(resume_text: str, target_role: str) -> Dict[str, Any]:
        """
        Validates fit and provides JSON feedback.
        """
        if not settings.GEMINI_API_KEY:
             return {"error": "AI Service not configured"}

        try:
            model = genai.GenerativeModel('gemini-1.5-flash')
            prompt = f"""
            Analyze resume fit for {target_role}. Return JSON only:
            {{ "match_score": 0-100, "missing_skills": [], "improvement_areas": [] }}
            Resume: {resume_text[:3000]}
            """
            response = model.generate_content(prompt)
            json_match = re.search(r'\{.*\}', response.text, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
            return {"match_score": 0}
        except Exception as e:
            logger.error(f"Validation fit error: {e}")
            return {"error": str(e)}
