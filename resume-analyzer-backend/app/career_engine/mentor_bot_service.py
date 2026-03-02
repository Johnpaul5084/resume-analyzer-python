"""
AI Mentor Bot Service
All intelligence features (Match Intel, Roadmap, Skill Graph) are powered by OpenAI GPT-4o-mini.
Gemini 1.5 Flash is used as a fallback if OpenAI is unavailable.
"""

import os
import json
import re
import logging
from pathlib import Path
from dotenv import load_dotenv
from typing import Dict, Any, List

load_dotenv(Path(__file__).resolve().parent.parent.parent / ".env", override=True)

logger = logging.getLogger(__name__)

_PLACEHOLDER_OPENAI = "YOUR_OPENAI_KEY_HERE"


def _oai_key() -> str:
    from dotenv import dotenv_values
    env_path = Path(__file__).resolve().parent.parent.parent / ".env"
    return dotenv_values(env_path).get("OPENAI_API_KEY", "") or os.getenv("OPENAI_API_KEY", "")


def _gem_key() -> str:
    from dotenv import dotenv_values
    env_path = Path(__file__).resolve().parent.parent.parent / ".env"
    return dotenv_values(env_path).get("GEMINI_API_KEY", "") or os.getenv("GEMINI_API_KEY", "")


def _openai_active() -> bool:
    k = _oai_key()
    return bool(k and k != _PLACEHOLDER_OPENAI and k.startswith("sk-"))


def _call_ai(prompt: str, system: str = "You are an expert AI career analyst.", max_tokens: int = 1200) -> str:
    """
    Call OpenAI GPT-4o-mini → fallback to Gemini if needed.
    Returns the text response.
    """
    if _openai_active():
        try:
            from openai import OpenAI
            client = OpenAI(api_key=_oai_key())
            resp = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": system},
                    {"role": "user",   "content": prompt},
                ],
                max_tokens=max_tokens,
                temperature=0.6,
            )
            return resp.choices[0].message.content or ""
        except Exception as e:
            logger.warning(f"OpenAI failed ({e}), trying Gemini…")

    gem = _gem_key()
    if gem:
        try:
            import google.generativeai as genai
            genai.configure(api_key=gem)
            model = genai.GenerativeModel(
                "gemini-2.0-flash",
                generation_config={"temperature": 0.6, "max_output_tokens": max_tokens},
            )
            return model.generate_content(f"{system}\n\n{prompt}").text
        except Exception as e:
            logger.error(f"Gemini also failed: {e}")

    return ""


class AIMentorBot:
    """
    AI Career Mentor Bot
    Tab 1 — Match Intel : Deep market & profile analysis via OpenAI
    Tab 2 — Roadmap     : 6-month career roadmap via OpenAI
    Tab 3 — Skill Graph : Visual skill gap chart (matplotlib)
    """

    @staticmethod
    def analyze_career_path(resume_text: str, user_skills: List[str], target_role: str = None) -> Dict[str, Any]:
        """
        Entry point called by the /insight endpoint.
        Runs all three analyses and returns one unified response object.
        """
        if not resume_text or not resume_text.strip():
            return {
                "recommended_role": "N/A",
                "market_demand": "Unknown",
                "mentor_advice": "Resume content is empty. Please upload a valid resume.",
                "domain": "Unknown",
                "missing_skills": [],
                "dynamic_roadmap": "No roadmap available — resume is empty.",
                "salary_range": "N/A",
                "growth_score": 5.0,
                "skill_graph": None,
            }

        # ── Step 1: Match Intel (OpenAI) ──────────────────────────────────
        intel = AIMentorBot._get_match_intel(resume_text, user_skills, target_role)

        # ── Step 2: Roadmap (OpenAI) ──────────────────────────────────────
        from app.career_engine.roadmap_ai_generator import RoadmapAIGenerator
        roadmap = RoadmapAIGenerator.generate_dynamic_roadmap(
            role=intel.get("recommended_role", "Software Engineer"),
            missing_skills=intel.get("missing_skills", []),
        )

        # ── Step 3: Skill Graph (matplotlib visual) ────────────────────────
        from app.career_engine.skill_graph_visualizer import SkillGraphVisualizer
        try:
            required = intel.get("required_skills", []) or intel.get("missing_skills", [])
            graph_b64 = SkillGraphVisualizer.generate_skill_graph(user_skills or [], required)
        except Exception:
            graph_b64 = None

        return {
            "recommended_role": intel.get("recommended_role", "Software Engineer"),
            "market_demand":    intel.get("market_demand",    "High 📈"),
            "salary_range":     intel.get("salary_range",     "Competitive"),
            "growth_score":     intel.get("growth_score",     7.0),
            "missing_skills":   intel.get("missing_skills",   []),
            "required_skills":  intel.get("required_skills",  []),
            "mentor_advice":    intel.get("mentor_advice",    ""),
            "domain":           intel.get("domain",           "Technology"),
            "dynamic_roadmap":  roadmap,
            "skill_graph":      graph_b64,
        }

    # ─────────────────────────────────────────────────────────────────────
    # OpenAI-powered Match Intel
    # ─────────────────────────────────────────────────────────────────────
    @staticmethod
    def _get_match_intel(resume_text: str, user_skills: List[str], target_role: str = None) -> Dict[str, Any]:
        """Use OpenAI to deeply analyze the resume profile and generate market intel."""

        skills_str = ", ".join(user_skills[:20]) if user_skills else "Not specified"

        prompt = f"""Analyze this resume and return a detailed career intelligence report.

RESUME (first 3000 chars):
{resume_text[:3000]}

DETECTED SKILLS: {skills_str}
TARGET ROLE (requested by user): {target_role or "AI Prediction"}

Return ONLY valid JSON (no markdown, no explanation):
{{
  "recommended_role": "<best matching job title, e.g. 'Java Full Stack Developer'>",
  "domain": "<broad domain, e.g. 'Full Stack Development', 'DevOps', 'Data Science'>",
  "market_demand": "<one of: 'Very High 🔥', 'High 📈', 'Stable', 'Low'>",
  "salary_range": "<realistic Indian salary range for this role, e.g. '12-22 LPA'>",
  "growth_score": <float 1-10, how fast this role is growing in the market>,
  "missing_skills": ["<skill missing from resume but needed for recommended_role>", "<another>", "<another>", "<another>", "<another>"],
  "required_skills": ["<top skill needed for this role>", "<another>", "<another>", "<another>", "<another>", "<another>"],
  "mentor_advice": "<2-3 sentence personalized career advice based on this specific resume — encouraging but honest>"
}}

RULES:
- recommended_role must match the actual resume content but PRIORITIZE the TARGET ROLE if it is provided
- missing_skills must be specific to the recommended_role domain
- required_skills are the top skills for the recommended_role (regardless of whether the candidate has them)
- salary_range must be realistic for India, 2024 market
- mentor_advice must reference actual content from this resume"""

        raw = _call_ai(
            prompt=prompt,
            system="You are an expert technical recruiter and career strategist. You provide accurate, data-driven career intelligence.",
            max_tokens=700,
        )

        if not raw:
            return AIMentorBot._default_intel()

        try:
            raw = re.sub(r"^```(?:json)?\s*", "", raw.strip())
            raw = re.sub(r"\s*```$", "", raw)
            data = json.loads(raw)
            # Ensure growth_score is float
            data["growth_score"] = float(data.get("growth_score", 7.0))
            return data
        except Exception as e:
            logger.error(f"Intel JSON parse error: {e}\nRaw: {raw[:200]}")
            return AIMentorBot._default_intel()

    @staticmethod
    def _default_intel() -> Dict[str, Any]:
        return {
            "recommended_role": "Software Engineer",
            "domain":           "Software Development",
            "market_demand":    "High 📈",
            "salary_range":     "10-20 LPA",
            "growth_score":     7.0,
            "missing_skills":   ["Docker", "Kubernetes", "System Design", "DSA", "Cloud Platforms"],
            "required_skills":  ["Python/Java", "React/Angular", "SQL", "Git", "REST APIs"],
            "mentor_advice":    "Your profile shows strong fundamentals. Focus on system design and cloud skills to unlock senior roles.",
        }
