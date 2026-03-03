"""AI Scoring Engine — CORE scoring logic (keyword-based fallback).

This is the CORE scoring module. It implements the keyword-based,
multi-metric scoring algorithm that runs without any external API.

`ats_scoring_service.py` is the WRAPPER that:
  - Tries Gemini first (deep semantic analysis)
  - Falls back to THIS engine when Gemini is unavailable

Do NOT duplicate scoring logic — all local scoring must live here.
"""

from app.services.ai_skill_ontology import SkillOntology
import re
import json
import os
import time
import logging
from typing import Dict, List, Any

logger = logging.getLogger(__name__)


class AIScoringEngine:
    """
    Realistic Multi-Metric Resume Scoring Engine.
    Produces genuinely different scores for different resumes.
    """

    @staticmethod
    def calculate_comprehensive_score(
        resume_text: str,
        parsed_data: Dict[str, Any],
        target_role: str = "Software Engineer",
    ) -> Dict[str, Any]:
        """
        Final Score = 0.35*relevance + 0.25*skill_coverage
                    + 0.20*experience_depth + 0.20*structure_score
        All sub-scores are in 0-100 range.
        """
        _t0 = time.perf_counter()
        words = resume_text.split()
        word_count = len(words)
        user_skills = parsed_data.get("skills", [])

        # 1. Relevance Score — keyword overlap, NO artificial +40 floor
        template = AIScoringEngine.get_role_template(target_role)
        relevance_score = AIScoringEngine.calculate_relevance_score(resume_text, template)

        # 2. Skill Coverage — scaled to 15 skills for more differentiation
        skill_coverage = min((len(user_skills) / 15) * 100, 100)

        # 3. Experience Depth — broader set of achievement signals
        metric_patterns = [
            r'\d+\s*%',                          # percentages
            r'\$\s*\d+',                         # dollar amounts
            r'₹\s*\d+',                          # rupee amounts
            r'\d+\s*(million|billion|lakh|crore)',# large numbers
            r'increased|decreased|improved|reduced|optimised|optimized|grew|saved|delivered',
            r'\d+\+?\s*(users|clients|projects|teams|members)',
        ]
        depth_hits = sum(
            len(re.findall(pat, resume_text, re.IGNORECASE))
            for pat in metric_patterns
        )
        experience_depth = min((depth_hits / 6) * 100, 100)

        # 4. Structure Score — checks for key resume sections
        section_keywords = {
            "contact":     ["email", "phone", "linkedin", "github", "@"],
            "education":   ["bachelor", "master", "b.tech", "m.tech", "university", "college", "degree", "gpa", "cgpa"],
            "experience":  ["experience", "internship", "worked", "employed", "company", "organization"],
            "skills":      ["skills", "technologies", "tools", "languages", "frameworks"],
            "projects":    ["project", "built", "developed", "created", "implemented"],
            "achievements":["award", "winner", "achievement", "rank", "gold", "silver", "hackathon", "certification"],
        }
        text_lower = resume_text.lower()
        sections_found = sum(
            1 for kws in section_keywords.values()
            if any(kw in text_lower for kw in kws)
        )
        structure_score = (sections_found / len(section_keywords)) * 100

        # Final weighted score
        final_score = (
            (relevance_score  * 0.35) +
            (skill_coverage   * 0.25) +
            (experience_depth * 0.20) +
            (structure_score  * 0.20)
        )
        final_score = round(final_score, 2)

        _elapsed_ms = (time.perf_counter() - _t0) * 1000
        logger.info(
            "Keyword scoring completed | role=%s | score=%.2f | elapsed=%.1fms",
            target_role, final_score, _elapsed_ms,
        )

        # Cluster & gaps for dynamic suggestions — priority to target_role
        if target_role and target_role != "Software Engineer":
            primary_cluster = SkillOntology.map_role_to_cluster(target_role)
        else:
            primary_cluster = SkillOntology.identify_primary_cluster(user_skills)
            
        gap_analysis = SkillOntology.get_missing_skills(primary_cluster, user_skills)

        return {
            "ats_score": final_score,
            "breakdown": {
                "semantic_similarity": round(relevance_score, 2),
                "skill_coverage":      round(skill_coverage, 2),
                "experience_depth":    round(experience_depth, 2),
                "ats_format_score":    round(structure_score, 2),
                "market_readiness":    90 if final_score > 75 else (70 if final_score > 55 else 50),
            },
            "explainable_ai": AIScoringEngine._generate_explanation(
                score=final_score,
                cluster=primary_cluster,
                gaps=gap_analysis,
                depth_hits=depth_hits,
                sections_found=sections_found,
                total_sections=len(section_keywords),
                word_count=word_count,
            ),
            # pass internals so _run_scoring can build dynamic suggestions
            "_internals": {
                "cluster":        primary_cluster,
                "gaps":           gap_analysis,
                "depth_hits":     depth_hits,
                "sections_found": sections_found,
                "total_sections": len(section_keywords),
                "user_skills":    user_skills,
                "word_count":     word_count,
                "relevance":      relevance_score,
            },
        }

    # ------------------------------------------------------------------
    @staticmethod
    def generate_dynamic_suggestions(internals: Dict[str, Any]) -> List[str]:
        """
        Produce suggestions that are specific to THIS resume's weaknesses.
        """
        suggestions = []
        cluster      = internals.get("cluster", "General Engineering")
        gaps         = internals.get("gaps", [])
        depth_hits   = internals.get("depth_hits", 0)
        sections     = internals.get("sections_found", 0)
        total_sec    = internals.get("total_sections", 6)
        user_skills  = internals.get("user_skills", [])
        word_count   = internals.get("word_count", 0)
        relevance    = internals.get("relevance", 0)

        # Missing skills
        if gaps:
            suggestions.append(
                f"🔑 Add these in-demand {cluster} skills: {', '.join(gaps[:4])}."
            )

        # Quantification
        if depth_hits < 3:
            suggestions.append(
                "📊 Quantify your impact — add numbers, %, or results "
                "(e.g., 'Reduced load time by 40%', 'Led a team of 5')."
            )

        # Missing sections
        missing_count = total_sec - sections
        if missing_count >= 2:
            suggestions.append(
                f"📝 Your resume is missing {missing_count} key sections. "
                "Ensure you have: Education, Experience, Skills, Projects, and Contact info."
            )
        elif missing_count == 1:
            suggestions.append(
                "📝 Add a Projects or Achievements section to strengthen your profile."
            )

        # Low keyword relevance
        if relevance < 50:
            suggestions.append(
                "🎯 Your resume has low keyword alignment. "
                "Mirror language from job descriptions for better ATS matching."
            )

        # Short resume
        if word_count < 200:
            suggestions.append(
                f"📄 Your resume is quite short ({word_count} words). "
                "Aim for 400–700 words with detailed experience and project descriptions."
            )
        elif word_count > 900:
            suggestions.append(
                f"✂️ Your resume is long ({word_count} words). "
                "Trim to 1 page — recruiters spend ~6 seconds scanning."
            )

        # Skill count
        if len(user_skills) < 5:
            suggestions.append(
                "🛠️ List more specific technical skills — aim for at least 8–12 relevant skills."
            )

        # Fallback
        if not suggestions:
            suggestions.append(
                "✅ Strong resume! Polish with more quantified achievements and role-specific keywords to reach 90+."
            )

        return suggestions[:5]  # Cap at 5 suggestions

    # ------------------------------------------------------------------
    @staticmethod
    def _generate_explanation(
        score: float,
        cluster: str,
        gaps: List[str],
        depth_hits: int,
        sections_found: int,
        total_sections: int,
        word_count: int,
    ) -> str:
        if score >= 80:
            level = "strongly aligned with MNC benchmarks"
        elif score >= 60:
            level = "moderately aligned — above-average but improvable"
        elif score >= 40:
            level = "developing towards professional standards"
        else:
            level = "needs significant improvement for ATS systems"

        explanation = (
            f"Your profile fits the **{cluster}** domain and is {level} "
            f"(score: {score:.1f}/100). "
        )

        if depth_hits < 2:
            explanation += "Your experience section lacks quantified achievements — add measurable results. "
        if gaps:
            explanation += f"Priority skill gaps: {', '.join(gaps[:3])}. "
        if sections_found < total_sections - 1:
            explanation += "Several key resume sections are missing. "
        if word_count < 200:
            explanation += "Resume content is too brief for ATS systems. "

        return explanation.strip()

    # ------------------------------------------------------------------
    @staticmethod
    def calculate_relevance_score(resume_text: str, target_template: str) -> float:
        """
        Keyword overlap score — NO artificial floor.
        Returns a genuine 0-100 reflecting actual alignment.
        """
        try:
            resume_words   = set(re.findall(r'\w+', resume_text.lower()))
            template_words = {w for w in re.findall(r'\w+', target_template.lower()) if len(w) > 3}

            if not template_words:
                return 50.0

            match_count = len(resume_words & template_words)
            raw = (match_count / len(template_words)) * 100
            # Mild boost (1.2x) but capped — keeps scores honest
            return round(min(raw * 1.2, 100), 2)
        except Exception as e:
            logger.error(f"Relevance scoring error: {e}")
            return 40.0

    # ------------------------------------------------------------------
    @staticmethod
    def get_role_template(role: str) -> str:
        db_path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            "career_engine", "role_database.json"
        )
        try:
            if os.path.exists(db_path):
                with open(db_path, encoding='utf-8') as f:
                    role_db = json.load(f)
                role_data = role_db.get(role)
                if role_data:
                    return (
                        f"{role}. {role_data.get('description', '')} "
                        f"{', '.join(role_data.get('mandatory_skills', []))}."
                    )
        except Exception:
            pass

        templates = {
            "Software Engineer":    "Python Java algorithms data structures system design backend API REST microservices git testing CI/CD",
            "Data Scientist":       "Python R SQL machine learning statistics data analysis pandas numpy tensorflow scikit-learn visualization",
            "Full Stack Developer": "React JavaScript Node.js HTML CSS REST API MongoDB PostgreSQL Docker frontend backend",
            "DevOps Engineer":      "Docker Kubernetes AWS Azure CI/CD Jenkins Linux bash scripting terraform monitoring",
            "Android Developer":    "Java Kotlin Android Studio XML REST API Firebase SQLite MVP MVVM",
        }
        return templates.get(role, "professional experience technical skills project management problem solving")
