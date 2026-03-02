"""
AI Resume Analyzer — ATS Scoring Service
Primary Engine  : Google Gemini 1.5 Flash  (deep semantic analysis)
Fallback Engine : Keyword-overlap scorer   (always works, no API key needed)
"""

import asyncio
import re
import json
import logging
from typing import Dict, Any, List

import google.generativeai as genai

from app.core.config import settings
from app.services.ai_scoring_engine import AIScoringEngine
from app.services.ai_parser_service import AIParserService
from app.services.ai_skill_ontology import SkillOntology
from app.career_engine.rag_engine import retrieve_relevant_roles

logger = logging.getLogger(__name__)

# ──────────────────────────────────────────────────────────────────────────────
# GEMINI DEEP ANALYZER  (primary)
# ──────────────────────────────────────────────────────────────────────────────

_ANALYSIS_PROMPT = """You are a senior technical recruiter and ATS expert with 15+ years experience.
Analyze the resume below and return a JSON evaluation.

{role_context}

RESUME TEXT:
{resume_text}

Return ONLY valid JSON, no markdown, no explanation:
{{
  "ats_score": <realistic float 0-100>,
  "predicted_role": "<the target role exactly as specified, or best match from resume>",
  "breakdown": {{
    "semantic_similarity": <float 0-100, how well resume keywords match {target_role_label} requirements>,
    "skill_coverage":      <float 0-100, % of core {target_role_label} skills present in resume>,
    "experience_depth":    <float 0-100, quality + quantity of experience relevant to {target_role_label}>,
    "ats_format_score":    <float 0-100, structure, sections, ATS readability>,
    "market_readiness":    <float 0-100, overall readiness for {target_role_label} job market>
  }},
  "analysis": "<2-3 sentence honest assessment of fit for {target_role_label}>",
  "missing_skills": [
    "<skill that a {target_role_label} MUST have but is NOT in this resume>",
    "<another missing {target_role_label} skill>",
    "<another>",
    "<another>",
    "<another>"
  ],
  "key_strengths": [
    "<actual skill or achievement found in resume relevant to {target_role_label}>",
    "<another>",
    "<another>",
    "<another>"
  ],
  "suggestions": [
    "<specific actionable advice to improve resume for {target_role_label}>",
    "<another specific suggestion>",
    "<another>",
    "<another>",
    "<another>"
  ]
}}

STRICT RULES — violating these makes the response useless:
1. missing_skills MUST be skills required for {target_role_label} that are ABSENT from the resume.
   - If role is Java Full Stack → missing could be: Spring Boot, Hibernate, React, Angular, Microservices, Docker
   - If role is DevOps → missing could be: Kubernetes, Terraform, Jenkins, AWS, CI/CD pipelines
   - If role is Data Scientist → missing could be: PyTorch, TensorFlow, Statistics, A/B Testing, SQL
   - NEVER list skills from a completely different domain (e.g., ML skills for a Java role)
2. ats_score: Fresh grad → 30-55. Mid-level → 55-75. Senior with impact → 75-85. Exceptional → 85+.
3. All analysis MUST be specific to {target_role_label}, not generic.
4. key_strengths must be ACTUAL skills found in the resume text, not invented.
"""


def _call_gemini_sync(resume_text: str, job_description: str = None, target_role: str = None) -> Dict[str, Any]:
    """Synchronous Gemini call — runs in thread pool via asyncio.to_thread."""
    from dotenv import dotenv_values
    from pathlib import Path
    env_path = Path(__file__).resolve().parent.parent.parent / ".env"
    vals = dotenv_values(env_path)
    key = vals.get("GEMINI_API_KEY") or settings.GEMINI_API_KEY
    
    if not key or key == "YOUR_NEW_KEY_HERE":
        raise ValueError("GEMINI_API_KEY not configured")

    genai.configure(api_key=key)
    model = genai.GenerativeModel(
        "gemini-2.0-flash",
        generation_config={"temperature": 0.1, "max_output_tokens": 1200},
    )

    # Build role context block — this drives ALL role-specific outputs
    if target_role:
        role_context = (
            f"TARGET ROLE (specified by user): {target_role}\n"
            f"CRITICAL: All missing_skills, suggestions, and analysis MUST be specific to '{target_role}'.\n"
            f"Do NOT suggest skills from unrelated domains."
        )
        target_role_label = target_role
    elif job_description:
        role_context = f"JOB DESCRIPTION TO ALIGN WITH:\n{job_description[:1500]}"
        target_role_label = "the role described in the JD"
    else:
        role_context = "Determine the most suitable role from the resume content."
        target_role_label = "the most suitable role"

    prompt = _ANALYSIS_PROMPT.format(
        resume_text=resume_text[:4000],
        role_context=role_context,
        target_role_label=target_role_label,
    )

    response = model.generate_content(prompt)
    raw = response.text.strip()
    raw = re.sub(r"^```(?:json)?\s*", "", raw)
    raw = re.sub(r"\s*```$", "", raw)

    result = json.loads(raw)

    score = float(result.get("ats_score", 50))
    score = max(0.0, min(100.0, score))

    breakdown = result.get("breakdown", {})
    for k in ["semantic_similarity", "skill_coverage", "experience_depth",
              "ats_format_score", "market_readiness"]:
        breakdown[k] = max(0.0, min(100.0, float(breakdown.get(k, 50))))

    # Always honour explicit user role
    predicted = target_role if target_role else str(result.get("predicted_role", "Software Engineer"))

    return {
        "ats_score":      round(score, 2),
        "predicted_role": predicted,
        "breakdown":      {k: round(v, 2) for k, v in breakdown.items()},
        "analysis":       str(result.get("analysis", "")),
        "missing_skills": list(result.get("missing_skills", []))[:5],
        "key_strengths":  list(result.get("key_strengths",  []))[:4],
        "suggestions":    list(result.get("suggestions",    []))[:5],
    }


# ──────────────────────────────────────────────────────────────────────────────
# KEYWORD FALLBACK  (no API key needed)
# ──────────────────────────────────────────────────────────────────────────────

def _keyword_score_sync(resume_text: str, job_description: str = None, target_role: str = None) -> Dict[str, Any]:
    """Fast keyword-based fallback — always works."""
    structured = AIParserService.extract_structured_data(resume_text)

    # Use explicit role if provided, otherwise predict
    if not target_role:
        roles = retrieve_relevant_roles(resume_text, top_k=1)
        target_role = roles[0] if roles else "Software Engineer"

    analysis = AIScoringEngine.calculate_comprehensive_score(
        resume_text=resume_text,
        parsed_data=structured,
        target_role=target_role,
    )
    internals    = analysis.pop("_internals", {})
    suggestions  = AIScoringEngine.generate_dynamic_suggestions(internals)
    cluster      = internals.get("cluster", "General Engineering")
    user_skills  = internals.get("user_skills", [])
    missing      = SkillOntology.get_missing_skills(cluster, user_skills)

    return {
        "ats_score":      analysis["ats_score"],
        "predicted_role": target_role,
        "breakdown":      analysis["breakdown"],
        "analysis":       analysis["explainable_ai"],
        "missing_skills": missing,
        "key_strengths":  user_skills[:4],
        "suggestions":    suggestions,
    }


# ──────────────────────────────────────────────────────────────────────────────
# PUBLIC SERVICE
# ──────────────────────────────────────────────────────────────────────────────

class ATSScoringService:

    # --- Fast sync matcher for job recommendations (no ML needed) --------
    @staticmethod
    def calculate_match_score(resume_text: str, job_description: str) -> Dict[str, Any]:
        if not resume_text or not job_description:
            return {"ats_score": 60, "missing_keywords": []}

        stop = {"the","and","for","with","you","are","our","this","that",
                "have","from","will","your","not","but","can","all","any"}
        r = set(re.findall(r'\b[a-zA-Z]{3,}\b', resume_text.lower())) - stop
        j = set(re.findall(r'\b[a-zA-Z]{3,}\b', job_description.lower())) - stop

        if not j:
            return {"ats_score": 65, "missing_keywords": []}

        matched = r & j
        missing = list(j - r)[:10]
        raw     = round(min(100, (len(matched) / len(j)) * 100), 1)
        score   = round(50 + (raw / 100) * 45, 1)
        return {"ats_score": score, "missing_keywords": missing}

    # --- Main async entry point called by the upload endpoint ------------
    @staticmethod
    async def calculate_score(
        resume_text: str,
        job_description: str = None,
        target_role: str = None,
    ) -> Dict[str, Any]:
        """
        Full resume analysis.
        - target_role: user-specified role (e.g. "DevOps") — always honoured
        - job_description: full JD text for alignment matching
        Tries Gemini first (90%+ accuracy), falls back to keyword engine.
        """
        from dotenv import dotenv_values
        from pathlib import Path
        env_path = Path(__file__).resolve().parent.parent.parent / ".env"
        key = dotenv_values(env_path).get("GEMINI_API_KEY") or os.getenv("GEMINI_API_KEY")

        if key and key != "YOUR_NEW_KEY_HERE":
            try:
                result = await asyncio.to_thread(
                    _call_gemini_sync, resume_text, job_description, target_role
                )
                logger.info(
                    f"Gemini analysis done: score={result['ats_score']}, "
                    f"role={result['predicted_role']}"
                )
                return result
            except Exception as e:
                logger.warning(f"Gemini analysis failed ({e}), using keyword fallback")

        # Keyword fallback
        result = await asyncio.to_thread(
            _keyword_score_sync, resume_text, job_description, target_role
        )
        # Still honour the user's target role in fallback
        if target_role:
            result["predicted_role"] = target_role
        return result
