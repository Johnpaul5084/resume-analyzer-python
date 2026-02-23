import google.generativeai as genai
import os
from typing import List

class RoadmapAIGenerator:
    @staticmethod
    def generate_dynamic_roadmap(role: str, missing_skills: List[str], current_level: str = "Beginner") -> str:
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            return "Unable to generate roadmap (API Key missing)."
            
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel("gemini-1.5-flash")
        
        prompt = f"""
        Act as a Senior Career Mentor from a top IIT/IIIT. 
        Create a high-impact, 6-month career roadmap for a student aiming to become a {role}.
        
        CURRENT STATE:
        - Level: {current_level}
        - Missing Critical Skills: {', '.join(missing_skills)}
        
        REQUIREMENTS:
        1. Break it down into Month 1-2, Month 3-4, and Month 5-6.
        2. Focus strictly on closing the skill gaps identified.
        3. Suggest specific types of projects (not just 'build a project').
        4. Tone: Encouraging, professional, and data-driven.
        5. Output: Return raw text only, no markdown headers (###), use bolding sparingly.
        
        STRUCTURE:
        Month 1-2: [Focus]
        Month 3-4: [Focus]
        Month 5-6: [Final Polish & Projects]
        """
        
        try:
            response = model.generate_content(prompt)
            return response.text.replace('**', '').strip()
        except Exception as e:
            return f"Roadmap generation failed: {str(e)}"
        
