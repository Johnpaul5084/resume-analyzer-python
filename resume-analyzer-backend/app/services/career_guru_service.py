from google import genai
from app.core.config import settings
from typing import List, Dict, Any
import logging

logger = logging.getLogger(__name__)

_client = None
if settings.GEMINI_API_KEY:
    _client = genai.Client(api_key=settings.GEMINI_API_KEY)

class CareerGuruService:
    @staticmethod
    async def get_advice(user_question: str, resume_context: str = None, chat_history: List[Dict[str, str]] = None) -> str:
        """
        Phoenix Phase 3: AI Career Guru
        """
        if not _client:
            return "Career Guru is unavailable. Please check your AI keys."

        system_prompt = """You are the 'AI Career Guru', an expert career mentor for students in 2026.
        Your goal is to provide honest, encouraging, and highly actionable career advice.
        Keep your tone: Professional, Empathetic, and Visionary. Use Markdown formatting."""
        
        full_context = f"Student's Resume:\n{resume_context[:3000]}\n\n" if resume_context else ""
        prompt = f"{system_prompt}\n\n{full_context}Student's Question: {user_question}"
        
        try:
            response = _client.models.generate_content(
                model="gemini-2.0-flash",
                contents=prompt
            )
            return response.text
        except Exception as e:
            logger.error(f"Career Guru Error: {e}")
            return "I'm having trouble connecting. Please try again in a moment."

    @staticmethod
    async def generate_skill_roadmap(target_role: str, current_skills: List[str]) -> Dict[str, Any]:
        """Phoenix Phase 4: Skill Gap Roadmap Generator"""
        if not _client:
            return {"roadmap": "Unavailable", "links": []}

        prompt = f"""Generate a 3-step Career Roadmap for reaching the role of '{target_role}'.
        Current Student Skills: {', '.join(current_skills)}
        For each step provide: Goal Name, Skills to Learn, Estimated Time, One Free Resource.
        Return in valid JSON format with keys: steps (list of objects)."""
        
        try:
            response = _client.models.generate_content(
                model="gemini-2.0-flash",
                contents=prompt
            )
            import re, json
            text = response.text
            json_match = re.search(r'\{.*\}', text, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
            return {"steps": []}
        except Exception as e:
            logger.error(f"Roadmap Generator Error: {e}")
            return {"steps": []}
