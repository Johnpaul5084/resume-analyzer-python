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

            mode_instruction = ""
            if mode == "Creative":
                mode_instruction = "11. MODE: CREATIVE. While maintaining absolute factual truth, use highly engaging narrative language, impactful vocabulary, and heavily emphasize the candidate's unique value proposition and leadership potential."
            else:
                mode_instruction = "11. MODE: ATS. Strongly prioritize exact keyword matches from the target role/JD. Keep language direct, focus purely on hard technical competencies, and maximize metric visibility."

            if job_description:
                prompt = f"""You are the world's top Executive Resume Writer and ATS Technical Recruiter for FAANG/MAANG, Fortune 500, and top-tier Tech MNCs.

Your task is to comprehensively RE-ENGINEER this resume to achieve a 100% ATS match for the specific Job Description provided, while remaining STRICTLY FACTUAL to the candidate's original history. 

JOB DESCRIPTION:
{job_description[:3000]}

ORIGINAL RESUME CONTENT:
{text[:4000]}

REWRITE RULES (CRITICAL & NON-NEGOTIABLE):
1. STRICT FACTUAL ACCURACY: You are forbidden from inventing companies, degrees, roles, or entirely fake projects. You MUST ONLY elevate, rephrase, and extract the maximum possible value from the candidate's actual provided experience.
2. HYPER-TARGETED ATS ALIGNMENT: Analyze the Job Description deeply. Identify the core skills, technologies, and phrasing used by this specific company. Mirror these EXACT keywords naturally throughout the candidate's experience. If the JD requires "Python" and the candidate used it, ensure Python is front-and-center.
3. DEEP, IMPACT-DRIVEN REWRITE: Do not just copy the old bullets. Completely rewrite every bullet point using the Google/FAANG XYZ formula: "Accomplished [X] as measured by [Y], by doing [Z]".
   - ALWAYS start with a potent action verb (Architected, Engineered, Spearheaded, Optimized, Deployed).
   - NEVER use weak verbs (Helped, Worked on, Responsible for).
4. REALISTIC QUANTIFICATION: Add realistic metrics (percentages, time saved, efficiency improved) ONLY if they logically align with the actual experience described. Do not use absurd numbers for junior roles.
5. EXECUTIVE SUMMARY: Write a commanding 3-sentence professional summary that directly positions the candidate as the perfect solution to the problems outlined in the JD.
6. SKILLS OPTIMIZATION: Rebuild the Skills section. Group them logically (Languages, Frameworks, Cloud, Tools). The skills requested in the JD MUST be listed first.
7. FORMATTING STRICTURES: Return CLEAN PLAIN TEXT ONLY.
   - NO Markdown formatting (no **, no ##). 
   - NO LaTeX.
   - NO HTML.
   - NO tables or weird characters (bullet points should use standard hyphens or plain bullets).
8. FLAWLESS EXECUTION: Zero grammar errors. Zero typos. Perfect professional corporate tone.

OUTPUT: Return the COMPLETE, aggressively optimized resume text. DO NOT include intros, commentary, or pleasantries. Jump straight into the resume content."""
            else:
                prompt = f"""You are an elite AI resume consultant who has placed 500+ candidates at FAANG, top MNCs, and Big 4 companies. 

Perform a DEEP REWRITE of this resume specifically for a **{target_role}** role at a {company_type}, maintaining absolute factual accuracy.

ORIGINAL RESUME CONTENT:
{text[:4000]}

TARGET ROLE: {target_role}
COMPANY TYPE: {company_type}

REWRITE RULES (CRITICAL — follow precisely):
1. STRICT FACTUAL ACCURACY: Do NOT invent experiences, companies, projects, or degrees. Only enhance what is provided in the ORIGINAL RESUME CONTENT.
2. Professional Summary: Write a powerful 3-sentence summary positioning the candidate as an ideal {target_role}. 
   Highlight actual relevant experience, key technical strengths, and career passion.
3. Technical Skills: Reorder to prioritize skills most critical for {target_role} first.
   - Group by: Programming Languages | Frameworks & Libraries | Databases | Tools & Platforms | Cloud & DevOps
4. Experience Bullets: Do a DEEP REWRITE of EVERY bullet using STAR format with quantified results.
   - Action Verb + Task Description + Technology Used + Measurable Result
   - Use REALISTIC metrics based on the original content.
5. Projects: Emphasize projects that demonstrate {target_role} competencies based on factual data.
6. If skills relevant to {target_role} are clearly implied by their work but not explicitly listed, add them naturally.
7. Fix ALL grammar mistakes, awkward phrasing, and typos.
8. Use ATS-friendly formatting: clear section headers, consistent bullet style, no tables or columns.
9. Plain professional English only — NO LaTeX, **, ###, or special symbols.
10. Add a "Key Achievements" or "Highlights" section if the candidate has notable accomplishments.
{mode_instruction}

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

    @staticmethod
    async def grammar_enhance(text: str) -> str:
        """
        AI Grammar & Clarity Enhancer.
        Fixes grammar, improves professional tone, and enhances readability
        while preserving technical terms and resume structure.
        """
        from app.core.ai_provider import AIProvider

        prompt = f"""Enhance this resume text for grammar, clarity, and professional tone.

RULES:
- Fix all grammar and spelling mistakes
- Improve sentence structure for clarity
- Use strong action verbs (Led, Developed, Implemented, Optimized)
- Preserve ALL technical terms exactly (e.g., React, Kubernetes, AWS)
- Keep the same overall structure and sections
- Do NOT add new information or invent anything
- Do NOT add any commentary — return ONLY the enhanced text

TEXT:
{text[:5000]}"""

        result = await AIProvider.generate(
            prompt=prompt,
            system_prompt="You are an expert resume editor. Enhance grammar and clarity. Return ONLY the enhanced text, nothing else.",
            max_tokens=2000,
            temperature=0.3,
            timeout=45,
        )

        return result if result.strip() else text
