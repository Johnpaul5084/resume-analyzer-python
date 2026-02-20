import google.generativeai as genai
from app.core.config import settings
from typing import List, Dict, Any
import logging
import json
import re

logger = logging.getLogger(__name__)

# Configure once at module level
if settings.GEMINI_API_KEY:
    genai.configure(api_key=settings.GEMINI_API_KEY)

class CareerGuruService:
    @staticmethod
    async def get_advice(user_question: str, resume_context: str = None, chat_history: List[Dict[str, str]] = None) -> str:
        """
        AI Career Guru - Get personalized career advice
        """
        if not settings.GEMINI_API_KEY:
            return "Career Guru is unavailable. Please check your AI keys."

        try:
            model = genai.GenerativeModel('gemini-1.5-flash')
            
            system_prompt = """You are the 'AI Career Guru', an expert career mentor.
            Your goal is to provide honest, encouraging, and highly actionable career advice.
            Keep your tone: Professional, Empathetic, and Visionary. Use Markdown formatting."""
            
            full_context = f"Student's Resume Content:\n{resume_context[:4000]}\n\n" if resume_context else ""
            prompt = f"{system_prompt}\n\n{full_context}Student's Question: {user_question}"
            
            response = model.generate_content(prompt)
            return response.text
        except Exception as e:
            logger.error(f"Career Guru Error: {e}")
            return "I'm having trouble connecting. Please try again in a moment."

    @staticmethod
    async def generate_skill_roadmap(target_role: str, current_skills: List[str]) -> Dict[str, Any]:
        """Skill Gap Roadmap Generator"""
        if not settings.GEMINI_API_KEY:
            return {"steps": []}

        try:
            model = genai.GenerativeModel('gemini-1.5-flash')
            
            prompt = f"""Generate a 3-step Career Roadmap for reaching the role of '{target_role}'.
            Current Student Skills: {', '.join(current_skills)}
            
            For each step provide: Goal Name, Skills to Learn, Estimated Time, One Free Resource.
            
            Return ONLY a valid JSON object with the key "steps" containing a list of objects.
            Example format:
            {{
              "steps": [
                {{
                  "Goal": "Step title",
                  "Skills": "comma separated skills",
                  "Time": "duration",
                  "Resource": "resource name"
                }}
              ]
            }}
            """
            
            response = model.generate_content(prompt)
            text = response.text
            
            # Extract JSON from potential markdown blocks
            json_match = re.search(r'\{.*\}', text, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
            return {"steps": []}
        except Exception as e:
            logger.error(f"Roadmap Generator Error: {e}")
            return {"steps": []}
