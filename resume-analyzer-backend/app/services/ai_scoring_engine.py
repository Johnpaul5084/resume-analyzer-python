"""AI Scoring Engine v2.0 — Enhanced Multi-Metric Resume Scoring (CORE).

UPGRADED from v1 with:
  - 10 section detection (was 6) — contact, education, experience, skills, projects,
    achievements, summary, certifications, publications, extracurricular
  - Action verb quality analysis (strong/weak verb ratio)
  - Quantification depth scoring (metrics, percentages, numbers)
  - ATS format quality (bullets, line length, section headers)
  - RAG-enhanced role template matching (25 roles, not 5 hardcoded)
  - Skill synonym matching via SkillOntology
  - Industry-specific scoring adjustments

This is the CORE scoring module (keyword-based, no API needed).
`ats_scoring_service.py` is the WRAPPER that tries Gemini first.
"""

from app.services.ai_skill_ontology import SkillOntology
import re
import json
import os
import time
import logging
from typing import Dict, List, Any

logger = logging.getLogger(__name__)

# ──────────────────────────────────────────────────────────────────────────────
# CONSTANTS
# ──────────────────────────────────────────────────────────────────────────────

STRONG_VERBS = frozenset({
    "architected", "designed", "engineered", "developed", "built",
    "implemented", "deployed", "optimized", "scaled", "led",
    "spearheaded", "launched", "created", "delivered", "automated",
    "reduced", "increased", "improved", "transformed", "established",
    "pioneered", "orchestrated", "mentored", "integrated", "migrated",
    "refactored", "streamlined", "accelerated", "achieved", "managed",
    "conducted", "analyzed", "resolved", "configured", "published",
    "researched", "collaborated", "coordinated", "formulated", "negotiated",
})

WEAK_VERBS = frozenset({
    "helped", "worked", "assisted", "participated", "responsible",
    "involved", "contributed", "supported", "did", "made",
    "tried", "used", "had", "got", "went", "was",
})


class AIScoringEngine:
    """
    Advanced Multi-Metric Resume Scoring Engine v2.0
    Produces genuinely different scores for different resumes with 7 scoring dimensions.
    """

    @staticmethod
    def calculate_comprehensive_score(
        resume_text: str,
        parsed_data: Dict[str, Any],
        target_role: str = "Software Engineer",
    ) -> Dict[str, Any]:
        """
        Final Score = 0.28*relevance + 0.22*skill_coverage
                    + 0.18*experience_depth + 0.12*structure_score
                    + 0.10*action_verb_quality + 0.10*quantification

        All sub-scores are in 0-100 range.
        """
        _t0 = time.perf_counter()
        words = resume_text.split()
        word_count = len(words)
        text_lower = resume_text.lower()

        # Extract skills using ontology (more accurate)
        ontology_skills = SkillOntology.extract_skills_from_text(resume_text)
        parsed_skills = parsed_data.get("skills", [])
        user_skills = list(set(ontology_skills + parsed_skills))

        # 1. Relevance Score — TF-IDF keyword overlap with role template
        template = AIScoringEngine.get_role_template(target_role)
        relevance_score = AIScoringEngine.calculate_relevance_score(resume_text, template)

        # 2. Skill Coverage — uses ontology for better matching
        cluster = SkillOntology.map_role_to_cluster(target_role)
        cluster_skills = SkillOntology.get_cluster_skills(cluster)
        matched_skills = [s for s in cluster_skills if s.lower() in text_lower]
        skill_coverage = min((len(matched_skills) / max(len(cluster_skills) * 0.4, 1)) * 100, 100)

        # 3. Experience Depth — broader achievement signals
        metric_patterns = [
            r'\d+\s*%',                            # percentages
            r'\$\s*[\d,]+',                        # dollar amounts
            r'₹\s*[\d,]+',                         # rupee amounts
            r'\d+\s*(million|billion|lakh|crore)',  # large numbers
            r'increased|decreased|improved|reduced|optimized|grew|saved|delivered|boosted|elevated',
            r'\d+\+?\s*(users|clients|projects|teams|members|customers|endpoints|requests)',
            r'\d+x\s*(faster|improvement|increase|reduction)',  # multiplier metrics
            r'(top|first|ranked)\s*\d+',           # rankings
        ]
        depth_hits = sum(
            len(re.findall(pat, resume_text, re.IGNORECASE))
            for pat in metric_patterns
        )
        experience_depth = min((depth_hits / 8) * 100, 100)

        # 4. Structure Score — checks for 10 key resume sections
        section_keywords = {
            "contact": ["email", "phone", "linkedin", "github", "@", "portfolio", "website"],
            "summary": ["summary", "objective", "profile", "about me", "professional summary"],
            "education": ["bachelor", "master", "b.tech", "m.tech", "university", "college",
                         "degree", "gpa", "cgpa", "diploma", "phd", "mba", "certification"],
            "experience": ["experience", "internship", "worked", "employed", "company",
                          "organization", "intern", "full-time", "part-time", "contract"],
            "skills": ["skills", "technologies", "tools", "languages", "frameworks",
                       "proficiency", "competencies", "technical skills"],
            "projects": ["project", "built", "developed", "created", "implemented",
                        "portfolio", "capstone", "thesis", "research project"],
            "achievements": ["award", "winner", "achievement", "rank", "gold", "silver",
                           "hackathon", "certification", "scholarship", "honor", "dean's list"],
            "certifications": ["certified", "certification", "certificate", "coursera",
                             "udemy", "aws certified", "google certified", "microsoft certified"],
            "publications": ["published", "paper", "journal", "conference", "arxiv",
                           "ieee", "acm", "research paper"],
            "extracurricular": ["volunteer", "club", "society", "leadership", "community",
                              "open source", "contributor", "organizer", "mentor"],
        }

        sections_found = sum(
            1 for kws in section_keywords.values()
            if any(kw in text_lower for kw in kws)
        )
        structure_score = min((sections_found / 7) * 100, 100)  # Expect at least 7 of 10

        # 5. Action Verb Quality (NEW in v2)
        words_lower = [w.lower().rstrip(".,;:") for w in words]
        strong_count = sum(1 for w in words_lower if w in STRONG_VERBS)
        weak_count = sum(1 for w in words_lower if w in WEAK_VERBS)
        total_verbs = strong_count + weak_count
        if total_verbs > 0:
            verb_quality = (strong_count / total_verbs) * 100
        else:
            verb_quality = 30  # No action verbs detected = low

        # 6. Quantification Score (NEW in v2)
        number_pattern = re.findall(r'\d+', resume_text)
        meaningful_numbers = [n for n in number_pattern if 2 <= len(n) <= 10]  # 2+ digit numbers
        quantification_score = min((len(meaningful_numbers) / 10) * 100, 100)

        # Final weighted score (7 dimensions)
        final_score = (
            (relevance_score      * 0.28) +
            (skill_coverage       * 0.22) +
            (experience_depth     * 0.18) +
            (structure_score      * 0.12) +
            (verb_quality         * 0.10) +
            (quantification_score * 0.10)
        )
        final_score = round(final_score, 2)

        # Market readiness — tiered assessment
        if final_score > 80:
            market_readiness = 95
        elif final_score > 70:
            market_readiness = 85
        elif final_score > 55:
            market_readiness = 70
        elif final_score > 40:
            market_readiness = 55
        else:
            market_readiness = 40

        _elapsed_ms = (time.perf_counter() - _t0) * 1000
        logger.info(
            "Keyword scoring v2 | role=%s | score=%.2f | rel=%.0f skill=%.0f exp=%.0f "
            "struct=%.0f verb=%.0f quant=%.0f | elapsed=%.1fms",
            target_role, final_score, relevance_score, skill_coverage,
            experience_depth, structure_score, verb_quality, quantification_score,
            _elapsed_ms,
        )

        # Cluster & gaps for dynamic suggestions
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
                "market_readiness":    market_readiness,
                "action_verb_quality": round(verb_quality, 2),
                "quantification":      round(quantification_score, 2),
            },
            "explainable_ai": AIScoringEngine._generate_explanation(
                score=final_score,
                cluster=primary_cluster,
                gaps=gap_analysis,
                depth_hits=depth_hits,
                sections_found=sections_found,
                total_sections=len(section_keywords),
                word_count=word_count,
                verb_quality=verb_quality,
                quantification=quantification_score,
            ),
            "_internals": {
                "cluster":         primary_cluster,
                "gaps":            gap_analysis,
                "depth_hits":      depth_hits,
                "sections_found":  sections_found,
                "total_sections":  len(section_keywords),
                "user_skills":     user_skills,
                "word_count":      word_count,
                "relevance":       relevance_score,
                "verb_quality":    verb_quality,
                "quantification":  quantification_score,
                "strong_verbs":    strong_count,
                "weak_verbs":      weak_count,
                "matched_skills":  matched_skills,
            },
        }

    # ------------------------------------------------------------------
    @staticmethod
    def generate_dynamic_suggestions(internals: Dict[str, Any]) -> List[str]:
        """
        Produce suggestions that are specific to THIS resume's weaknesses.
        v2: More granular, actionable, and role-specific.
        """
        suggestions = []
        cluster       = internals.get("cluster", "Software Engineering")
        gaps          = internals.get("gaps", [])
        depth_hits    = internals.get("depth_hits", 0)
        sections      = internals.get("sections_found", 0)
        total_sec     = internals.get("total_sections", 10)
        user_skills   = internals.get("user_skills", [])
        word_count    = internals.get("word_count", 0)
        relevance     = internals.get("relevance", 0)
        verb_quality  = internals.get("verb_quality", 50)
        quant_score   = internals.get("quantification", 50)
        strong_verbs  = internals.get("strong_verbs", 0)
        weak_verbs    = internals.get("weak_verbs", 0)

        # Priority 1: Skill gaps
        if gaps:
            suggestions.append(
                f"🔑 Add these in-demand {cluster} skills to your resume: {', '.join(gaps[:5])}."
            )

        # Priority 2: Weak action verbs
        if weak_verbs > 0 and verb_quality < 60:
            suggestions.append(
                f"💪 Replace weak verbs ('helped', 'worked on', 'assisted') with impact verbs "
                f"('Architected', 'Engineered', 'Optimized', 'Led', 'Deployed'). "
                f"Found {weak_verbs} weak verbs vs {strong_verbs} strong verbs."
            )

        # Priority 3: Quantification
        if quant_score < 40:
            suggestions.append(
                "📊 Add measurable impact to EVERY bullet point — use numbers, percentages, "
                "and timeframes (e.g., 'Reduced API latency by 40%', 'Served 10K+ daily users', "
                "'Delivered 3 features in 2 sprints')."
            )
        elif depth_hits < 4:
            suggestions.append(
                "📊 Strengthen quantifiable results — add %, $, or user counts "
                "to at least 3-4 more bullet points for stronger ATS match."
            )

        # Priority 4: Missing sections
        missing_count = total_sec - sections
        if missing_count >= 3:
            suggestions.append(
                f"📝 Your resume is missing {missing_count} key sections. "
                "Ensure you have: Professional Summary, Education, Experience, "
                "Skills, Projects, and Certifications."
            )
        elif missing_count >= 1:
            section_recs = []
            if "summary" not in str(internals).lower():
                section_recs.append("Professional Summary")
            if "certification" not in str(internals).lower():
                section_recs.append("Certifications")
            if "project" not in str(internals).lower():
                section_recs.append("Projects")
            if section_recs:
                suggestions.append(
                    f"📝 Add a '{section_recs[0]}' section to strengthen your profile."
                )

        # Priority 5: Low keyword relevance
        if relevance < 40:
            suggestions.append(
                "🎯 Your resume has LOW keyword alignment with the target role. "
                "Study job descriptions for this role and mirror their exact terminology. "
                "ATS systems rely on exact keyword matches."
            )
        elif relevance < 60:
            suggestions.append(
                "🎯 Improve keyword alignment — review 3-4 job postings for your target role "
                "and naturally incorporate their key terms into your bullets."
            )

        # Priority 6: Resume length
        if word_count < 150:
            suggestions.append(
                f"📄 Your resume is too brief ({word_count} words). "
                "Expand to 400-700 words with detailed project descriptions and experience bullets."
            )
        elif word_count < 250:
            suggestions.append(
                f"📄 Your resume is short ({word_count} words). "
                "Aim for at least 400 words — add more project details and technical depth."
            )
        elif word_count > 1000:
            suggestions.append(
                f"✂️ Your resume is long ({word_count} words). "
                "Trim to 1 page (400-700 words) — recruiters spend ~6 seconds scanning."
            )

        # Priority 7: Skill count
        if len(user_skills) < 5:
            suggestions.append(
                "🛠️ List more specific technical skills. "
                "Aim for 10-15 relevant skills grouped by category "
                "(Languages, Frameworks, Databases, Tools, Cloud)."
            )

        # Positive reinforcement
        if not suggestions:
            suggestions.append(
                "✅ Strong resume! Polish with more quantified achievements "
                "and role-specific keywords to push past 90."
            )

        return suggestions[:6]  # Cap at 6 suggestions

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
        verb_quality: float = 50,
        quantification: float = 50,
    ) -> str:
        if score >= 80:
            level = "strongly aligned with top-tier company benchmarks"
        elif score >= 65:
            level = "well-positioned with room for targeted improvements"
        elif score >= 50:
            level = "moderately aligned — above-average but needs optimization"
        elif score >= 35:
            level = "developing towards professional standards"
        else:
            level = "needs significant improvement for modern ATS systems"

        explanation = (
            f"Your profile fits the **{cluster}** domain and is {level} "
            f"(score: {score:.1f}/100). "
        )

        # Specific feedback based on metrics
        if verb_quality < 40:
            explanation += (
                "Your resume uses too many weak verbs — replace 'helped', 'worked on' "
                "with 'Architected', 'Delivered', 'Optimized'. "
            )
        if quantification < 30:
            explanation += "Lacking quantified results — add metrics to demonstrate impact. "
        if depth_hits < 2:
            explanation += "Your experience section lacks quantified achievements — add measurable results. "
        if gaps:
            explanation += f"Priority skill gaps: {', '.join(gaps[:4])}. "
        if sections_found < total_sections - 3:
            explanation += "Several key resume sections are missing. "
        if word_count < 200:
            explanation += "Resume content is too brief for ATS systems. "

        return explanation.strip()

    # ------------------------------------------------------------------
    @staticmethod
    def calculate_relevance_score(resume_text: str, target_template: str) -> float:
        """
        TF-IDF-inspired keyword relevance — no artificial floor.
        Returns genuine 0-100 reflecting actual alignment with role template.
        """
        try:
            # Build word sets (filter short words)
            resume_words = set(re.findall(r'\w+', resume_text.lower()))
            template_words = {w for w in re.findall(r'\w+', target_template.lower()) if len(w) > 2}

            if not template_words:
                return 45.0

            # Weighted matching: skill terms get 2x weight
            skill_terms = {w for w in template_words if len(w) > 3}
            basic_terms = template_words - skill_terms

            skill_matches = len(resume_words & skill_terms)
            basic_matches = len(resume_words & basic_terms)

            weighted_match = (skill_matches * 2 + basic_matches)
            weighted_total = (len(skill_terms) * 2 + len(basic_terms))

            if weighted_total == 0:
                return 45.0

            raw = (weighted_match / weighted_total) * 100
            # Mild boost (1.15x) to keep scores honest
            return round(min(raw * 1.15, 100), 2)
        except Exception as e:
            logger.error(f"Relevance scoring error: {e}")
            return 35.0

    # ------------------------------------------------------------------
    @staticmethod
    def get_role_template(role: str) -> str:
        """
        Get comprehensive role template for keyword matching.
        Uses RAG engine's role_database.json (25 roles) with fallback.
        """
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
                    parts = [
                        role,
                        role_data.get("description", ""),
                        " ".join(role_data.get("mandatory_skills", [])),
                        " ".join(role_data.get("advanced_skills", [])),
                        " ".join(role_data.get("tools", [])),
                        " ".join(role_data.get("certifications", [])),
                        " ".join(role_data.get("interview_topics", [])),
                    ]
                    return " ".join(parts)
        except Exception:
            pass

        # Expanded fallback templates
        templates = {
            "Software Engineer": "Python Java C++ algorithms data structures system design backend API REST microservices git testing CI/CD Docker Kubernetes debugging object-oriented distributed systems multithreading SQL databases agile",
            "Data Scientist": "Python R SQL machine learning statistics data analysis pandas numpy tensorflow scikit-learn visualization deep learning NLP feature engineering A/B testing regression classification modeling",
            "Full Stack Developer": "React JavaScript TypeScript Node.js HTML CSS REST API MongoDB PostgreSQL Docker frontend backend Next.js Redux state management responsive design authentication websocket",
            "DevOps Engineer": "Docker Kubernetes AWS Azure CI/CD Jenkins Linux bash terraform monitoring Prometheus Grafana Ansible automation infrastructure git GitLab GitHub Actions deployment",
            "Machine Learning Engineer": "Python TensorFlow PyTorch deep learning NLP computer vision MLOps model deployment feature engineering distributed training GPU CUDA neural networks transformers LLMs",
            "Data Engineer": "Python SQL Spark Airflow ETL data warehouse BigQuery Snowflake Kafka data pipeline dbt Hadoop data modeling batch streaming",
            "Frontend Developer": "React JavaScript TypeScript HTML CSS Tailwind responsive design accessibility performance optimization webpack Next.js Redux testing component architecture design system",
            "Backend Developer": "Python Java Node.js SQL PostgreSQL MongoDB REST API GraphQL microservices Docker Kubernetes authentication caching message queue Redis system design scalability",
            "Mobile App Developer": "React Native Flutter Kotlin Swift Android iOS Firebase REST API mobile UI state management push notifications app deployment testing accessibility",
            "Cybersecurity Analyst": "network security SIEM vulnerability assessment incident response penetration testing cryptography firewall IDS IPS threat hunting malware analysis SOC OWASP compliance",
            "Product Manager": "product strategy roadmap user research data analysis agile scrum stakeholder management A/B testing metrics KPIs OKRs prioritization user stories sprint planning",
            "UI/UX Designer": "Figma user research wireframing prototyping visual design interaction design design thinking usability testing accessibility design systems responsive design typography color theory",
            "Cloud Architect": "AWS Azure GCP cloud architecture terraform networking security serverless cost optimization CDN edge computing multi-cloud migration scalability high availability disaster recovery",
            "QA/Test Engineer": "test automation selenium cypress API testing SQL test planning agile BDD TDD performance testing security testing CI/CD bug tracking regression testing",
            "Business Analyst": "requirements analysis SQL Excel data analysis process mapping stakeholder management Agile UML BPMN Power BI Tableau documentation business intelligence",
        }
        return templates.get(role, "professional experience technical skills project management problem solving communication teamwork leadership analytical thinking")
