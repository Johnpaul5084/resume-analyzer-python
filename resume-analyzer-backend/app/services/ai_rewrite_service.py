import google.generativeai as genai
from app.core.config import settings
from typing import Optional, Dict, Any
import json
import re

# Configure Gemini if API key is present
if settings.GEMINI_API_KEY:
    genai.configure(api_key=settings.GEMINI_API_KEY)

class AIRewriteService:
    
    @staticmethod
    async def rewrite_section(text: str, section_type: str, target_role: str = "General", company_type: str = "MNC", job_description: str = None) -> str:
        """
        Rewrites resume content using LLM. 
        If job_description is provided, tailors the resume to that specific JD.
        Otherwise, targets the predicted role and MNC standards.
        """
        if not settings.GEMINI_API_KEY:
             return "AI Rewrite Service not configured (Missing API Key). Please set GEMINI_API_KEY in .env."

        # Dynamic Prompt Construction
        if job_description:
            # 1. JD-Based Tailoring (Highest Priority)
            prompt = f"""
            Act as a hiring manager. Rewrite the following resume {section_type} section to perfectly match the provided Job Description.

            Target Job Description:
            "{job_description[:1000]}"... (truncated)

            Key Requirements:
            1. **Keyword Alignment**: Integrate keywords from the JD naturally.
            2. **Relevance**: Highlight experience most relevant to this specific job.
            3. **Quantifiable Impact**: Use metrics to prove capability.
            4. **MNC Standard**: Maintain professional, active voice.

            Original Resume Text:
            "{text}"

            Rewritten Tailored Version:
            """
        else:
            # 2. Role-Based Tailoring (MNC Standard)
            prompt = f"""
            Act as a senior global recruiter for top MNC companies across industries. 
            Rewrite the following resume {section_type} section specifically for a {target_role} position.

            Key Requirements:
            1. **MNC Standard Language**: Use professional, industry-specific terminology.
            2. **Quantifiable Impact**: Emphasize scale and impact (e.g., "Improved X by Y%").
            3. **Role Alignment**: Integrate skills relevant to {target_role}.
            4. **Tone**: Professional, confident, and action-oriented.

            Original Text:
            "{text}"

            Rewritten Professional Version:
            """
        
        try:
            model = genai.GenerativeModel('gemini-1.5-flash')
            response = model.generate_content(prompt)
            cleaned_text = response.text.replace('**', '').strip() 
            if cleaned_text.startswith('"') and cleaned_text.endswith('"'):
                cleaned_text = cleaned_text[1:-1]
            return cleaned_text
        except Exception as e:
            return f"Error during AI rewrite: {str(e)}"

    @staticmethod
    async def generate_summary(resume_text: str, target_role: str) -> str:
        """
        Generates a professional summary based on the entire resume content.
        """
        if not settings.GEMINI_API_KEY:
             return "AI Rewrite Service not configured."

        prompt = f"""
        Read the following resume content and write a compelling professional summary (3-4 sentences) tailored for a {target_role} position.
        
        Resume Content:
        {resume_text[:2000]} 
        
        Professional Summary:
        """
        
        try:
            model = genai.GenerativeModel('gemini-1.5-flash')
            response = model.generate_content(prompt)
            return response.text.strip()
        except Exception as e:
            return f"Error generation summary: {str(e)}"

    @staticmethod
    async def validate_role_fit(resume_text: str, target_role: str) -> Dict[str, Any]:
        """
        Validates if the resume fits the target role and provides actionable feedback.
        Returns a dictionary with match score and suggestions.
        """
        if not settings.GEMINI_API_KEY:
             return {"error": "AI Service not configured"}

        prompt = f"""
        Analyze the following resume content specifically for a {target_role} role at an MNC.
        Provide a JSON response with the following keys:
        1. "match_score": A number from 0-100 indicating fit.
        2. "missing_skills": List of critical skills missing for {target_role}.
        3. "improvement_areas": List of specific improvements needed for MNC application.
        4. "rewrite_suggestions": A brief example of how a bullet point could be rewritten.

        Resume Content:
        {resume_text[:3000]}
        
        JSON Response:
        """
        try:
            model = genai.GenerativeModel('gemini-1.5-flash')
            response = model.generate_content(prompt)
            text = response.text.strip()
            # Extract JSON block
            if "```json" in text:
                text = text.split("```json")[1].split("```")[0].strip()
            elif "```" in text:
                text = text.split("```")[1].split("```")[0].strip()
            
            return json.loads(text)
        except Exception as e:
            return {"error": f"Validation failed: {str(e)}", "raw_response": text if 'text' in locals() else ""}
