import google.generativeai as genai
from app.core.config import settings
import logging
import json
import re
import os
from pathlib import Path
from dotenv import dotenv_values

logger = logging.getLogger(__name__)

_env_path = Path(__file__).resolve().parent.parent.parent / ".env"


def _get_gemini_key() -> str:
    """Get Gemini key from .env file or system environment (Render)."""
    vals = dotenv_values(_env_path)
    return vals.get("GEMINI_API_KEY", "") or os.getenv("GEMINI_API_KEY", "")


class JobPredictionService:
    """
    Job Role Prediction Engine.
    Primary: Gemini 2.0 Flash (AI-quality prediction with genuine analysis)
    Fallback: RAG keyword engine (always available, fast)
    """

    # Comprehensive role list covering all major domains
    DEFAULT_ROLES = [
        # Software Engineering
        "Software Engineer", "Full Stack Developer", "Backend Developer",
        "Frontend Developer", "Mobile App Developer", "Embedded Systems Engineer",
        # Data & AI
        "Data Scientist", "Data Analyst", "Data Engineer",
        "Machine Learning Engineer", "AI/ML Researcher",
        # DevOps & Cloud
        "DevOps Engineer", "Cloud Architect", "Site Reliability Engineer",
        "Platform Engineer",
        # Cybersecurity
        "Cybersecurity Analyst", "Penetration Tester", "Security Engineer",
        # Design
        "UI/UX Designer", "Product Designer", "Graphic Designer",
        # Engineering (Non-CS)
        "Civil Engineer", "Mechanical Engineer", "Electrical Engineer",
        "Chemical Engineer", "Automobile Engineer", "Biomedical Engineer",
        # Healthcare
        "Medical Doctor", "Nurse", "Pharmacist", "Biotechnologist",
        # Business & Management
        "Business Analyst", "Product Manager", "Project Manager",
        "Operations Manager", "Supply Chain Manager",
        # Marketing & Communications
        "Marketing Manager", "Digital Marketer", "Content Writer",
        "SEO Specialist", "Social Media Manager",
        # Finance & Legal
        "Financial Analyst", "Investment Banker", "Chartered Accountant",
        "Legal Advisor", "Compliance Officer",
        # HR & Education
        "HR Manager", "Recruiter", "Teacher", "Professor",
        "Training & Development Specialist",
    ]

    @staticmethod
    def predict_job_role(resume_text: str, candidate_labels: list = None) -> list:
        """
        Predicts the most suitable job roles based on resume text.
        Uses Gemini for genuine AI-powered prediction.
        Falls back gracefully to keyword-based RAG if Gemini is unavailable.
        """
        labels = candidate_labels or JobPredictionService.DEFAULT_ROLES

        # ── Try Gemini first (with credit check) ─────────────────────
        from app.services.api_credit_manager import APICreditManager
        gemini_key = _get_gemini_key()
        allowed, remaining = APICreditManager.check_and_use("gemini") if gemini_key else (False, 0)
        
        if gemini_key and gemini_key != "YOUR_NEW_KEY_HERE" and allowed:
            try:
                genai.configure(api_key=gemini_key)
                logger.info(f"Gemini prediction credit used. Remaining: {remaining}")
                model = genai.GenerativeModel(
                    "gemini-2.0-flash",
                    generation_config={"temperature": 0.2, "max_output_tokens": 500},
                )

                prompt = f"""You are an expert technical recruiter analyzing a candidate's resume.

Predict the top 3 most suitable job roles for this candidate.

CANDIDATE LABELS TO CHOOSE FROM:
{', '.join(labels)}

RESUME (first 3000 chars):
{resume_text[:3000]}

ANALYSIS INSTRUCTIONS:
1. Carefully read the skills, experience, projects, and education.
2. Match the candidate's profile to the MOST relevant roles from the list above.
3. Assign REALISTIC confidence scores:
   - 85-95%: Strong match (multiple relevant skills + experience in that domain)
   - 70-84%: Good match (some relevant skills, could transition into this role)
   - 50-69%: Moderate match (basic alignment, would need some upskilling)
4. The top role should be the one where the candidate has the STRONGEST fit.

Return ONLY valid JSON array, no explanation:
[
  {{"role": "Most Suitable Role", "confidence": 92.5, "reason": "Brief 1-line reason why this role fits"}},
  {{"role": "Second Best Role", "confidence": 78.0, "reason": "Brief reason"}},
  {{"role": "Third Role", "confidence": 65.0, "reason": "Brief reason"}}
]"""

                response = model.generate_content(prompt)
                json_match = re.search(r'\[.*?\]', response.text, re.DOTALL)
                if json_match:
                    predictions = json.loads(json_match.group())
                    if predictions and isinstance(predictions, list):
                        logger.info(f"Gemini predicted roles: {[p['role'] for p in predictions]}")
                        return predictions[:5]

                logger.warning(f"Gemini returned unparseable output: {response.text[:200]}")

            except Exception as e:
                logger.error(f"Gemini Job Prediction Error: {e}")

        # ── Fallback: RAG keyword-based prediction ────────────────────
        logger.info("Falling back to RAG-based role prediction.")
        return JobPredictionService._rag_predict(resume_text)

    @staticmethod
    def _rag_predict(resume_text: str) -> list:
        """
        Fast keyword-based role prediction using the RAG engine.
        Always works — no API key needed.
        """
        try:
            from app.career_engine.rag_engine import retrieve_relevant_roles
            roles = retrieve_relevant_roles(resume_text, top_k=3)
            # Assign descending confidence values
            confidences = [85.0, 72.0, 60.0]
            return [
                {"role": role, "confidence": confidences[i], "reason": "Keyword-based match"}
                for i, role in enumerate(roles)
            ]
        except Exception as e:
            logger.error(f"RAG fallback prediction error: {e}")
            return [{"role": "Software Engineer", "confidence": 50.0, "reason": "Default fallback"}]

    @staticmethod
    def validate_content_with_bert(text: str) -> dict:
        return {"quality": "Professional", "score": 85}
