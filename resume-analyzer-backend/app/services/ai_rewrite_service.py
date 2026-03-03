import os
import google.generativeai as genai
from pathlib import Path
from dotenv import load_dotenv
from app.core.config import settings
from app.core.resilience import (
    guard_prompt_injection,
    sanitize_resume_text,
    GEMINI_TIMEOUT_SECONDS,
)
from typing import Optional, Dict, Any
import json
import re
import logging
import asyncio

logger = logging.getLogger(__name__)

# Guarantee .env is loaded regardless of import order
_env_path = Path(__file__).resolve().parent.parent.parent / ".env"
load_dotenv(dotenv_path=_env_path, override=False)


def _get_gemini_model(model_name: str = "gemini-2.0-flash"):
    """Returns a configured Gemini model. API key is configured once via singleton.
    Credit limits are checked per call."""
    from app.services.api_credit_manager import APICreditManager
    from app.core.ai_model import AIModelManager

    # Check daily credit limit first
    allowed, remaining = APICreditManager.check_and_use("gemini")
    if not allowed:
        raise ValueError(f"Gemini daily credit limit reached (0 remaining). Resets at midnight. Use fallback.")

    # Configure API key exactly once (singleton)
    key = AIModelManager.configure_gemini()
    if not key:
        raise ValueError("GEMINI_API_KEY not configured in .env")

    logger.info(f"Gemini credit used. Remaining today: {remaining}")
    return genai.GenerativeModel(
        model_name,
        generation_config={"temperature": 0.4, "max_output_tokens": 3000},
    )


class AIRewriteService:

    @staticmethod
    async def detect_best_role(text: str) -> str:
        """
        Auto-detect the most suitable job role from resume text using Gemini.
        Used when user uploads resume without specifying a target role.
        """
        import asyncio

        def _sync():
            model = _get_gemini_model()
            safe_text = guard_prompt_injection(text[:3000])
            prompt = f"""Analyze this resume and determine the SINGLE most suitable job role.

RESUME:
{safe_text}

Consider:
1. The candidate's primary skills, technologies, and experience
2. Their education background
3. Their project work and certifications
4. Industry domain they belong to

Return ONLY the job role title (e.g., "Full Stack Developer", "Data Scientist", "DevOps Engineer").
No explanation, no quotes, just the role name."""

            response = model.generate_content(prompt)
            role = response.text.strip().strip('"').strip("'")
            # Sanitize — keep only first line if multi-line
            role = role.split("\n")[0].strip()
            return role if role else "Software Engineer"

        try:
            return await asyncio.wait_for(
                asyncio.to_thread(_sync),
                timeout=GEMINI_TIMEOUT_SECONDS,
            )
        except asyncio.TimeoutError:
            logger.error("Role detection timed out after %ds", GEMINI_TIMEOUT_SECONDS)
            return "Software Engineer"
        except Exception as e:
            logger.error("Role detection error: %s", e)
            return "Software Engineer"

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
        If no target_role is provided (or is 'General'), auto-detect best fit.
        If job_description is provided, aligns to that JD.
        Otherwise rewrites specifically for target_role.
        """
        import asyncio

        # Auto-detect role if not specified
        if not target_role or target_role.lower() in ("general", ""):
            target_role = await AIRewriteService.detect_best_role(text)
            logger.info(f"Auto-detected role for rewrite: {target_role}")

        def _sync_rewrite():
            model = _get_gemini_model()

            if job_description:
                prompt = f"""You are a senior resume consultant at a top-tier career coaching firm specializing in FAANG and Fortune 500 placements.

Rewrite this resume to PERFECTLY align with the Job Description below. This is for a real student looking for jobs — make the rewrite genuine and impactful.

JOB DESCRIPTION:
{job_description[:2000]}

ORIGINAL RESUME CONTENT:
{text[:4000]}

REWRITE RULES (CRITICAL — follow precisely):
1. Mirror the EXACT keywords and phrases from the Job Description naturally throughout the resume.
2. Every experience bullet MUST use the STAR method: Action Verb + What you did + How you did it + Quantified Result.
   Example: "Engineered a microservices architecture using Spring Boot and Docker, reducing deployment time by 40% across 12 production services."
3. Add REALISTIC quantified achievements — percentages, numbers, team sizes, dollar amounts, time saved.
   - Do NOT use generic numbers. Make them believable for a student (e.g., "Improved page load speed by 28%" not "Generated $50M revenue").
4. Professional Summary: Write a compelling 3-sentence summary highlighting the top 3 reasons this candidate fits the JD.
5. Skills Section: Reorganize skills to prioritize JD-relevant ones first. Group by category (Languages, Frameworks, Tools, Cloud, etc.).
6. Format: Clean plain text. NO LaTeX, NO **, NO ###, NO markdown, NO special symbols.
7. Keep ALL sections: Professional Summary, Technical Skills, Work Experience, Projects, Education, Certifications (if any).
8. Fix ALL grammar and spelling errors.
9. Use strong action verbs: Architected, Engineered, Automated, Optimized, Spearheaded, Led, Deployed, Designed, Implemented, Streamlined.
10. For each project, clearly mention the tech stack used and the impact/outcome.

OUTPUT: Return the COMPLETE rewritten resume text only. No introduction, no commentary, no headers like "Here is your rewritten resume"."""
            else:
                prompt = f"""You are a senior resume consultant who has placed 500+ candidates at FAANG, top MNCs, and Big 4 companies. 

Rewrite this resume specifically for a **{target_role}** role at a {company_type}. This is for a real student — make every word count.

ORIGINAL RESUME CONTENT:
{text[:4000]}

TARGET ROLE: {target_role}
COMPANY TYPE: {company_type}

REWRITE RULES (CRITICAL — follow precisely):
1. Professional Summary: Write a powerful 3-sentence summary positioning the candidate as an ideal {target_role}. 
   Highlight relevant experience, key technical strengths, and career passion.
2. Technical Skills: Reorder to prioritize skills most critical for {target_role} first.
   - {target_role} top skills should appear first
   - Group by: Programming Languages | Frameworks & Libraries | Databases | Tools & Platforms | Cloud & DevOps
3. Experience Bullets: Rewrite EVERY bullet using STAR format with quantified results.
   - Action Verb + Task Description + Technology Used + Measurable Result
   - Example: "Developed a RESTful API using FastAPI and PostgreSQL, serving 15K+ daily requests with 99.9% uptime."
   - Use REALISTIC metrics a student would have (not enterprise-scale numbers).
4. Projects: Emphasize projects that demonstrate {target_role} competencies.
   - Clearly state: Problem → Approach → Tech Stack → Outcome
5. If skills relevant to {target_role} are implied but not listed, add them naturally.
6. Fix ALL grammar mistakes, awkward phrasing, and typos.
7. Use ATS-friendly formatting: clear section headers, consistent bullet style, no tables or columns.
8. Plain professional English only — NO LaTeX, **, ###, or special symbols.
9. Ensure the resume passes ATS scanners used by {company_type} companies.
10. Add a "Key Achievements" or "Highlights" section if the candidate has notable accomplishments.

OUTPUT: Return the COMPLETE rewritten resume text only. No introduction or commentary."""

            response = model.generate_content(prompt)
            cleaned = response.text
            # Strip markdown artifacts
            cleaned = re.sub(r'\*{1,2}', '', cleaned)
            cleaned = re.sub(r'#{1,3}\s', '', cleaned)
            cleaned = re.sub(r'^[-]{3,}$', '', cleaned, flags=re.MULTILINE)
            cleaned = re.sub(r'^["\']|["\']$', '', cleaned.strip())
            # Remove "Here is your..." preamble if Gemini added it
            cleaned = re.sub(r'^(Here is|Below is|I\'ve rewritten).*?\n\n', '', cleaned, flags=re.IGNORECASE)
            return cleaned

        try:
            return await asyncio.wait_for(
                asyncio.to_thread(_sync_rewrite),
                timeout=GEMINI_TIMEOUT_SECONDS,
            )
        except asyncio.TimeoutError:
            logger.error("AI Rewrite timed out after %ds", GEMINI_TIMEOUT_SECONDS)
            return "Rewrite timed out. Please try again."
        except Exception as e:
            logger.error("AI Rewrite Error: %s", e)
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
        """Polish resume text for grammar, clarity, and professionalism — ATS/FAANG standard."""
        import asyncio

        def _sync():
            model = _get_gemini_model()
            prompt = f"""You are a professional resume editor with expertise in ATS optimization and FAANG-standard writing.

Polish the following resume text. Fix EVERY issue:

1. GRAMMAR: Correct all grammatical errors, subject-verb agreement, tense consistency.
2. SPELLING: Fix all typos and misspellings.
3. CLARITY: Make sentences concise and impactful. Remove filler words.
4. ACTION VERBS: Start every bullet with a strong action verb (Developed, Architected, Implemented, Led, Optimized, etc.).
5. QUANTIFICATION: Where possible, add or preserve metrics and numbers.
6. CONSISTENCY: Ensure consistent formatting — same tense, same bullet style throughout.
7. PROFESSIONAL TONE: Make it sound polished and professional, suitable for top-tier companies.

TEXT TO POLISH:
{text[:4000]}

OUTPUT: Return ONLY the polished text. No introductions, no commentary, no "Here is the polished version"."""
            result = model.generate_content(prompt).text.strip()
            # Clean any markdown
            result = re.sub(r'\*{1,2}', '', result)
            result = re.sub(r'#{1,3}\s', '', result)
            result = re.sub(r'^(Here is|Below is).*?\n\n', '', result, flags=re.IGNORECASE)
            return result

        try:
            return await asyncio.wait_for(
                asyncio.to_thread(_sync),
                timeout=GEMINI_TIMEOUT_SECONDS,
            )
        except asyncio.TimeoutError:
            logger.error("Grammar enhancement timed out")
            return "Enhancement timed out. Please try again."
        except Exception as e:
            logger.error("Grammar Enhancement Error: %s", e)
            return f"Error: {str(e)}"

    @staticmethod
    async def generate_summary(resume_text: str, target_role: str) -> str:
        """Generate a tailored 3-sentence professional summary."""
        import asyncio

        # Auto-detect role if not specified
        if not target_role or target_role.lower() in ("general", ""):
            target_role = await AIRewriteService.detect_best_role(resume_text)

        def _sync():
            model = _get_gemini_model()
            prompt = f"""Write a compelling 3-sentence professional summary for a {target_role} role based on this resume.

RESUME:
{resume_text[:2000]}

RULES:
1. First sentence: Years of experience + core expertise area + key technology stack.
2. Second sentence: Most impressive achievement or project with quantified impact.
3. Third sentence: Career goal and what unique value the candidate brings.
4. Use plain professional English — no special symbols, no markdown.
5. Be genuine and specific to this candidate's actual experience.

OUTPUT: Return ONLY the 3-sentence summary. Nothing else."""
            return model.generate_content(prompt).text.strip()

        try:
            return await asyncio.wait_for(
                asyncio.to_thread(_sync),
                timeout=GEMINI_TIMEOUT_SECONDS,
            )
        except asyncio.TimeoutError:
            logger.error("Summary generation timed out")
            return "Summary generation timed out. Please try again."
        except Exception as e:
            logger.error("Summary Generation Error: %s", e)
            return f"Error: {str(e)}"

    @staticmethod
    async def validate_role_fit(resume_text: str, target_role: str) -> Dict[str, Any]:
        """Validates resume fit for a target role and returns JSON feedback."""
        import asyncio

        # Auto-detect role if not specified
        if not target_role or target_role.lower() in ("general", ""):
            target_role = await AIRewriteService.detect_best_role(resume_text)

        def _sync():
            model = _get_gemini_model()
            prompt = f"""Analyze how well this resume fits the role of '{target_role}'.

RESUME:
{resume_text[:3000]}

Provide a thorough, honest analysis. Be specific — reference actual content from the resume.

Return ONLY valid JSON:
{{
  "target_role": "{target_role}",
  "match_score": <0-100, be realistic: fresh grad with some relevant skills = 40-60, mid-level match = 60-80, strong match = 80+>,
  "missing_skills": ["<skill critical for {target_role} that is NOT in resume>", "<another>", "<another>", "<another>", "<another>"],
  "existing_relevant_skills": ["<skill in resume that IS relevant to {target_role}>", "<another>", "<another>"],
  "improvement_areas": [
    "<specific, actionable improvement suggestion>",
    "<another specific suggestion>",
    "<another>"
  ],
  "strengths": [
    "<actual strength found in the resume relevant to {target_role}>",
    "<another>",
    "<another>"
  ],
  "grammar_issues": <number of grammar/spelling issues detected>,
  "ats_readiness": "<Ready|Needs Improvement|Not Ready>",
  "recommendation": "<2-3 sentence honest but encouraging assessment of the candidate's fit for {target_role}>"
}}"""
            response = model.generate_content(prompt)
            raw = re.sub(r'^```(?:json)?\s*|\s*```$', '', response.text.strip())
            match = re.search(r'\{.*\}', raw, re.DOTALL)
            if match:
                return json.loads(match.group())
            return {"match_score": 0, "missing_skills": [], "improvement_areas": [], "target_role": target_role}

        try:
            return await asyncio.wait_for(
                asyncio.to_thread(_sync),
                timeout=GEMINI_TIMEOUT_SECONDS,
            )
        except asyncio.TimeoutError:
            logger.error("Validate fit timed out")
            return {"error": "Analysis timed out", "target_role": target_role}
        except Exception as e:
            logger.error("Validate fit error: %s", e)
            return {"error": str(e), "target_role": target_role}
