import os
import google.generativeai as genai
from pathlib import Path
from dotenv import load_dotenv
from app.core.config import settings
from typing import Optional, Dict, Any
import json
import re
import logging

logger = logging.getLogger(__name__)

# Guarantee .env is loaded regardless of import order
_env_path = Path(__file__).resolve().parent.parent.parent / ".env"
load_dotenv(dotenv_path=_env_path, override=False)


def _get_gemini_model(model_name: str = "gemini-2.0-flash"):
    """Always fetches the API key fresh and returns a configured model."""
    from dotenv import dotenv_values
    env_path = Path(__file__).resolve().parent.parent.parent / ".env"
    vals = dotenv_values(env_path)
    key = vals.get("GEMINI_API_KEY") or settings.GEMINI_API_KEY or ""
    
    if not key or key == "YOUR_NEW_KEY_HERE":
        raise ValueError("GEMINI_API_KEY not configured in .env")
    genai.configure(api_key=key)
    return genai.GenerativeModel(
        model_name,
        generation_config={"temperature": 0.4, "max_output_tokens": 2048},
    )


class AIRewriteService:

    @staticmethod
    async def rewrite_section(
        text: str,
        section_type: str,
        target_role: str = "General",
        company_type: str = "MNC",
        job_description: str = None,
        mode: str = "ATS",
    ) -> str:
        """
        Rewrite resume content using Gemini for a specific target role.
        If job_description is provided, aligns to that JD.
        Otherwise rewrites specifically for target_role.
        """
        import asyncio

        def _sync_rewrite():
            model = _get_gemini_model()

            if job_description:
                prompt = f"""You are an expert MNC resume writer. Rewrite the resume below to perfectly match this Job Description.

JOB DESCRIPTION:
{job_description[:1500]}

RESUME CONTENT:
{text[:4000]}

REWRITE RULES:
1. Mirror the exact keywords and phrases from the Job Description.
2. Use STAR method for every experience bullet (Situation→Task→Action→Result).
3. Add realistic quantified achievements (e.g., "Reduced latency by 35%", "Led a team of 6").
4. Plain professional English only — no LaTeX, **, ###, or special symbols.
5. Keep all sections: Summary, Skills, Experience, Education, Projects.

OUTPUT: Return the complete rewritten resume text only. No introduction or commentary."""
            else:
                prompt = f"""You are a senior technical recruiter for top MNCs. Rewrite this resume specifically for a **{target_role}** role at a {company_type}.

RESUME CONTENT:
{text[:4000]}

TARGET ROLE: {target_role}

REWRITE RULES:
1. Tailor the professional summary to highlight fit for {target_role}.
2. Reorder and emphasize skills most relevant to {target_role}.
3. Rewrite each experience bullet with: strong action verb + specific task + quantified result.
4. Add or adapt projects that demonstrate {target_role} competency.
5. Plain professional English only — no LaTeX, **, ###, or special symbols.
6. If skills relevant to {target_role} are implied but not stated, surface them naturally.

OUTPUT: Return the complete rewritten resume text only. No introduction or commentary."""

            response = model.generate_content(prompt)
            cleaned = response.text
            # Strip markdown artifacts
            cleaned = re.sub(r'\*{1,2}', '', cleaned)
            cleaned = re.sub(r'#{1,3}\s', '', cleaned)
            cleaned = re.sub(r'^[-]{3,}$', '', cleaned, flags=re.MULTILINE)
            cleaned = re.sub(r'^["\']|["\']$', '', cleaned.strip())
            return cleaned

        try:
            return await asyncio.to_thread(_sync_rewrite)
        except Exception as e:
            logger.error(f"AI Rewrite Error: {e}")
            return f"Rewrite failed: {str(e)}"

    @staticmethod
    async def rewrite_resume(resume_text: str, job_description: str, mode: str = "ATS") -> str:
        """Alias — rewrites a full resume aligned to a Job Description."""
        return await AIRewriteService.rewrite_section(
            text=resume_text,
            section_type="Entire Resume",
            job_description=job_description,
            mode=mode,
        )

    @staticmethod
    async def grammar_enhance(text: str) -> str:
        """Polish resume text for grammar, clarity, and professionalism."""
        import asyncio

        def _sync():
            model = _get_gemini_model()
            prompt = f"""Polish the following resume text for grammar, clarity, and professional impact.
Keep the original meaning but make it concise and powerful.

TEXT:
{text[:3000]}

OUTPUT: Return only the polished text. No introductions or commentary."""
            return model.generate_content(prompt).text.strip()

        try:
            return await asyncio.to_thread(_sync)
        except Exception as e:
            logger.error(f"Grammar Enhancement Error: {e}")
            return f"Error: {str(e)}"

    @staticmethod
    async def generate_summary(resume_text: str, target_role: str) -> str:
        """Generate a tailored 3-sentence professional summary."""
        import asyncio

        def _sync():
            model = _get_gemini_model()
            prompt = (
                f"Write a compelling 3-sentence professional summary for a {target_role} role "
                f"based on this resume: {resume_text[:2000]}. "
                "Plain text only, no formatting symbols."
            )
            return model.generate_content(prompt).text.strip()

        try:
            return await asyncio.to_thread(_sync)
        except Exception as e:
            logger.error(f"Summary Generation Error: {e}")
            return f"Error: {str(e)}"

    @staticmethod
    async def validate_role_fit(resume_text: str, target_role: str) -> Dict[str, Any]:
        """Validates resume fit for a target role and returns JSON feedback."""
        import asyncio

        def _sync():
            model = _get_gemini_model()
            prompt = f"""Analyze how well this resume fits the role of '{target_role}'.
Return ONLY valid JSON:
{{
  "match_score": <0-100>,
  "missing_skills": ["skill1", "skill2"],
  "improvement_areas": ["area1", "area2"],
  "strengths": ["strength1", "strength2"]
}}

Resume:
{resume_text[:3000]}"""
            response = model.generate_content(prompt)
            raw = re.sub(r'^```(?:json)?\s*|\s*```$', '', response.text.strip())
            match = re.search(r'\{.*\}', raw, re.DOTALL)
            if match:
                return json.loads(match.group())
            return {"match_score": 0, "missing_skills": [], "improvement_areas": []}

        try:
            return await asyncio.to_thread(_sync)
        except Exception as e:
            logger.error(f"Validate fit error: {e}")
            return {"error": str(e)}
