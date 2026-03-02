import os
import logging
from pathlib import Path
from dotenv import load_dotenv
from typing import List

# Ensure .env is loaded regardless of import order
load_dotenv(Path(__file__).resolve().parent.parent.parent / ".env", override=True)

logger = logging.getLogger(__name__)

_PLACEHOLDER_OPENAI = "YOUR_OPENAI_KEY_HERE"


def _openai_key() -> str:
    from dotenv import dotenv_values
    env_path = Path(__file__).resolve().parent.parent.parent / ".env"
    return dotenv_values(env_path).get("OPENAI_API_KEY", "") or os.getenv("OPENAI_API_KEY", "")


def _gemini_key() -> str:
    from dotenv import dotenv_values
    env_path = Path(__file__).resolve().parent.parent.parent / ".env"
    return dotenv_values(env_path).get("GEMINI_API_KEY", "") or os.getenv("GEMINI_API_KEY", "")


class RoadmapAIGenerator:

    @staticmethod
    def generate_dynamic_roadmap(
        role: str,
        missing_skills: List[str],
        current_level: str = "Beginner",
    ) -> str:
        """
        Generate a 6-month career roadmap.
        Primary  : OpenAI GPT-4o-mini
        Fallback : Gemini 1.5 Flash
        """
        prompt = f"""You are an expert AI Career Mentor advising a tech professional.

Create a detailed, actionable 6-month roadmap for someone aiming to become a {role}.

Current Level  : {current_level}
Key Skill Gaps : {', '.join(missing_skills) if missing_skills else 'General improvement needed'}

ROADMAP STRUCTURE (use plain text, no markdown symbols like ** or ###):

MONTH 1-2: Foundation & Core Skills
- Specific skills to learn
- Resources (free courses, docs)
- Mini project to build

MONTH 3-4: Intermediate Mastery
- Advanced skills to develop
- Real-world project idea
- Portfolio milestone

MONTH 5-6: Job-Ready Polish
- Industry-level project
- Interview preparation focus
- How to showcase on resume & LinkedIn

Keep the tone encouraging, professional, and specific. Do NOT use ** or ### formatting."""

        # ── Try OpenAI first ────────────────────────────────────
        oai_key = _openai_key()
        if oai_key and oai_key != _PLACEHOLDER_OPENAI and oai_key.startswith("sk-"):
            try:
                from openai import OpenAI
                client = OpenAI(api_key=oai_key)
                resp = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {"role": "system", "content": "You are an expert AI Career Mentor."},
                        {"role": "user",   "content": prompt},
                    ],
                    max_tokens=900,
                    temperature=0.7,
                )
                text = resp.choices[0].message.content or ""
                return text.replace("**", "").replace("###", "").strip()
            except Exception as e:
                logger.warning(f"OpenAI roadmap failed ({e}), trying Gemini…")

        # ── Fallback: Gemini ────────────────────────────────────
        gem_key = _gemini_key()
        if gem_key:
            try:
                import google.generativeai as genai
                genai.configure(api_key=gem_key)
                model = genai.GenerativeModel(
                    "gemini-2.0-flash",
                    generation_config={"temperature": 0.7, "max_output_tokens": 900},
                )
                resp = model.generate_content(prompt)
                return resp.text.replace("**", "").replace("###", "").strip()
            except Exception as e:
                logger.error(f"Gemini roadmap also failed: {e}")

        return (
            f"Could not generate roadmap for {role}. "
            "Please check your OPENAI_API_KEY or GEMINI_API_KEY in .env."
        )
