"""
AI Mentor Bot Service
=====================
STRICT API SEPARATION:
  - Match Intel, Roadmap, Skill Graph: OpenAI GPT-4o-mini ONLY
  - NO Gemini here (Gemini is reserved for resume analysis only)

If OpenAI is unavailable, uses intelligent keyword-based fallback.
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


def _openai_active() -> bool:
    k = _oai_key()
    return bool(k and k != _PLACEHOLDER_OPENAI and k.startswith("sk-"))


def _call_openai(prompt: str, system: str = "You are an expert AI career analyst.", max_tokens: int = 1200) -> str:
    """
    Call OpenAI GPT-4o-mini ONLY — no Gemini fallback.
    Returns the text response, or empty string on failure.
    """
    if not _openai_active():
        logger.info("OpenAI key not available — using fallback intelligence.")
        return ""

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
        logger.error(f"OpenAI failed: {e}")
        return ""


class AIMentorBot:
    """
    AI Career Mentor Bot — OpenAI ONLY
    Tab 1 — Match Intel : Deep market & profile analysis
    Tab 2 — Roadmap     : 6-month career roadmap
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
    # OpenAI-powered Match Intel (ONLY OpenAI)
    # ─────────────────────────────────────────────────────────────────────
    @staticmethod
    def _get_match_intel(resume_text: str, user_skills: List[str], target_role: str = None) -> Dict[str, Any]:
        """Use OpenAI ONLY to deeply analyze the resume profile and generate market intel."""

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
- salary_range must be realistic for India, 2025 market
- mentor_advice must reference actual content from this resume"""

        raw = _call_openai(
            prompt=prompt,
            system="You are an expert technical recruiter and career strategist. You provide accurate, data-driven career intelligence.",
            max_tokens=700,
        )

        if not raw:
            return AIMentorBot._keyword_intel(resume_text, user_skills, target_role)

        try:
            raw = re.sub(r"^```(?:json)?\s*", "", raw.strip())
            raw = re.sub(r"\s*```$", "", raw)
            data = json.loads(raw)
            data["growth_score"] = float(data.get("growth_score", 7.0))
            return data
        except Exception as e:
            logger.error(f"Intel JSON parse error: {e}\nRaw: {raw[:200]}")
            return AIMentorBot._keyword_intel(resume_text, user_skills, target_role)

    @staticmethod
    def _keyword_intel(resume_text: str, user_skills: List[str], target_role: str = None) -> Dict[str, Any]:
        """Smart keyword-based fallback when OpenAI is unavailable."""
        text_lower = resume_text.lower()
        skills_lower = {s.lower() for s in (user_skills or [])}

        # Detect domain from resume content
        domain = "Software Development"
        role = target_role or "Software Engineer"
        salary = "8-18 LPA"
        growth = 7.5

        if any(k in text_lower for k in ["machine learning", "tensorflow", "pytorch", "deep learning", "nlp", "ai/ml"]):
            domain = "AI & Machine Learning"
            role = target_role or "ML Engineer"
            salary = "12-25 LPA"
            growth = 9.2
        elif any(k in text_lower for k in ["react", "angular", "vue", "frontend", "full stack", "node.js", "fastapi"]):
            domain = "Full Stack Development"
            role = target_role or "Full Stack Developer"
            salary = "8-22 LPA"
            growth = 8.5
        elif any(k in text_lower for k in ["docker", "kubernetes", "devops", "ci/cd", "terraform", "jenkins"]):
            domain = "DevOps & Cloud"
            role = target_role or "DevOps Engineer"
            salary = "10-25 LPA"
            growth = 8.8
        elif any(k in text_lower for k in ["data analyst", "sql", "tableau", "power bi", "pandas", "data science"]):
            domain = "Data Science & Analytics"
            role = target_role or "Data Analyst"
            salary = "8-20 LPA"
            growth = 8.0
        elif any(k in text_lower for k in ["java", "spring boot", "microservices", "hibernate"]):
            domain = "Java Backend Development"
            role = target_role or "Java Full Stack Developer"
            salary = "10-22 LPA"
            growth = 8.2

        # Determine missing skills based on detected domain
        missing_by_domain = {
            "AI & Machine Learning": ["PyTorch", "Deep Learning", "MLOps", "A/B Testing", "Feature Engineering"],
            "Full Stack Development": ["TypeScript", "Next.js", "Docker", "System Design", "GraphQL"],
            "DevOps & Cloud": ["Kubernetes", "Terraform", "AWS Certification", "Monitoring (Prometheus)", "Service Mesh"],
            "Data Science & Analytics": ["Statistical Modeling", "A/B Testing", "SQL Advanced", "Tableau", "ML Fundamentals"],
            "Java Backend Development": ["Spring Boot", "Microservices", "Kafka", "System Design", "Docker"],
            "Software Development": ["Docker", "Kubernetes", "System Design", "DSA", "Cloud Platforms"],
        }

        missing = missing_by_domain.get(domain, missing_by_domain["Software Development"])
        # Remove skills the user already has
        missing = [s for s in missing if s.lower() not in skills_lower][:5]

        return {
            "recommended_role": role,
            "domain": domain,
            "market_demand": "High 📈" if growth >= 8 else "Stable",
            "salary_range": salary,
            "growth_score": growth,
            "missing_skills": missing,
            "required_skills": list(skills_lower)[:6] if skills_lower else ["Python", "SQL", "Git", "REST APIs"],
            "mentor_advice": f"Your profile shows good alignment with {domain}. Focus on building practical projects and strengthening your {', '.join(missing[:2])} skills to unlock better opportunities.",
        }
