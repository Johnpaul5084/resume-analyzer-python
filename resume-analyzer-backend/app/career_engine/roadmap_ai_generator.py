"""
Roadmap AI Generator
====================
STRICT API SEPARATION:
  - Career Roadmap Generation: OpenAI GPT-4o-mini ONLY
  - NO Gemini here (Gemini is reserved for resume analysis only)

If OpenAI is unavailable, provides a structured static roadmap.
"""

import os
import logging
from pathlib import Path
from dotenv import load_dotenv
from typing import List

load_dotenv(Path(__file__).resolve().parent.parent.parent / ".env", override=True)

logger = logging.getLogger(__name__)

_PLACEHOLDER_OPENAI = "YOUR_OPENAI_KEY_HERE"


def _openai_key() -> str:
    from dotenv import dotenv_values
    env_path = Path(__file__).resolve().parent.parent.parent / ".env"
    return dotenv_values(env_path).get("OPENAI_API_KEY", "") or os.getenv("OPENAI_API_KEY", "")


class RoadmapAIGenerator:

    @staticmethod
    def generate_dynamic_roadmap(
        role: str,
        missing_skills: List[str],
        current_level: str = "Beginner",
    ) -> str:
        """
        Generate a 6-month career roadmap.
        Uses OpenAI GPT-4o-mini ONLY.
        Falls back to structured static roadmap if unavailable.
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

        # ── OpenAI ONLY ────────────────────────────────────────
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
                logger.error(f"OpenAI roadmap failed: {e}")

        # ── Static Fallback ────────────────────────────────────
        skills_str = ', '.join(missing_skills[:3]) if missing_skills else 'core fundamentals'
        return f"""CAREER ROADMAP: {role}

MONTH 1-2: Foundation & Core Skills
- Focus on learning: {skills_str}
- Free Resources: freeCodeCamp, Coursera (audit mode), YouTube tutorials
- Mini Project: Build a small {role.lower()}-related project to apply basics
- Practice DSA: Solve 30+ easy problems on LeetCode

MONTH 3-4: Intermediate Mastery
- Deep dive into: {', '.join(missing_skills[1:4]) if len(missing_skills) > 1 else 'advanced concepts'}
- Build a real-world project that solves an actual problem
- Deploy it on cloud (AWS/Render/Vercel)
- Start contributing to open source projects on GitHub

MONTH 5-6: Job-Ready Polish
- Build one impressive portfolio project showcasing {role} skills
- Prepare for technical interviews:
  * Data Structures & Algorithms (LeetCode medium/hard)
  * System Design fundamentals
  * Behavioral questions using STAR method
- Optimize your resume with quantified achievements
- Update LinkedIn profile with projects and certifications
- Apply to 10-15 jobs per week on LinkedIn, Naukri, and Indeed

DAILY SCHEDULE (Recommended):
- 2 hours: Coding practice / Project building
- 1 hour: DSA / Interview prep
- 30 minutes: Learning new concepts / Reading tech blogs

Remember: Consistency beats intensity. Show up every day!"""
