"""
Company-Specific ATS Scoring Service
=====================================
UNIQUE FEATURE: No free tool simulates how different companies score resumes.

Simulates ATS scoring patterns for:
- Google     (Impact, Innovation, Technical Depth, Culture Fit)
- Amazon     (Leadership Principles, STAR, Customer Obsession, Results)
- Microsoft  (Growth Mindset, Collaboration, Technical Excellence)
- TCS        (Certifications, Technology Breadth, Process Knowledge)
- Infosys    (Academic Excellence, Methodology, Domain Expertise)
- Meta       (Move Fast, Impact at Scale, Technical Innovation)
- Apple      (Attention to Detail, Passion, Privacy & Security)

Uses unified AIProvider (Gemini → OpenAI → keyword fallback).
"""

import json
import re
import logging
import asyncio
from typing import Dict, Any, List, Optional

logger = logging.getLogger(__name__)

# Company ATS profiles — what each company's ATS system prioritizes
COMPANY_PROFILES = {
    "google": {
        "name": "Google",
        "logo_emoji": "🔵",
        "color": "#4285F4",
        "ats_system": "Google Hire (Internal)",
        "weights": {
            "quantified_impact": 25,
            "technical_depth": 25,
            "innovation_signals": 15,
            "culture_fit": 10,
            "education": 10,
            "formatting": 15,
        },
        "critical_keywords": ["scalable", "distributed", "optimization", "algorithm", "data-driven", "impact", "research", "open-source"],
        "red_flags": ["responsible for", "helped with", "worked on", "assisted"],
        "preferred_verbs": ["Designed", "Architected", "Optimized", "Scaled", "Led", "Innovated", "Published", "Reduced"],
        "tips": "Google values measurable impact (X% improvement), technical depth, and innovation. Use XYZ bullet format: Accomplished [X] as measured by [Y] by doing [Z].",
    },
    "amazon": {
        "name": "Amazon",
        "logo_emoji": "🟠",
        "color": "#FF9900",
        "ats_system": "Amazon Jobs (Workday)",
        "weights": {
            "quantified_impact": 30,
            "leadership_principles": 20,
            "customer_focus": 15,
            "technical_depth": 15,
            "formatting": 10,
            "education": 10,
        },
        "critical_keywords": ["customer", "ownership", "deliver", "scale", "bias for action", "high standards", "results", "metrics", "data"],
        "red_flags": ["team effort", "assisted", "participated"],
        "preferred_verbs": ["Owned", "Delivered", "Drove", "Launched", "Reduced", "Improved", "Built", "Scaled"],
        "tips": "Amazon's ATS heavily weights Leadership Principles. Every bullet should demonstrate ownership, customer obsession, or measurable results. Use STAR format.",
    },
    "microsoft": {
        "name": "Microsoft",
        "logo_emoji": "🟢",
        "color": "#00A4EF",
        "ats_system": "Microsoft Careers (Greenhouse)",
        "weights": {
            "technical_depth": 25,
            "collaboration": 20,
            "growth_mindset": 15,
            "quantified_impact": 20,
            "education": 10,
            "formatting": 10,
        },
        "critical_keywords": ["collaboration", "inclusive", "growth", "cloud", "Azure", "AI", "accessibility", "cross-functional"],
        "red_flags": ["individual contributor only", "worked alone"],
        "preferred_verbs": ["Collaborated", "Mentored", "Architected", "Integrated", "Enabled", "Empowered", "Transformed"],
        "tips": "Microsoft values growth mindset and collaboration. Highlight cross-team impact, mentoring, and inclusive project work. Azure/cloud skills get bonus points.",
    },
    "meta": {
        "name": "Meta",
        "logo_emoji": "🔷",
        "color": "#0668E1",
        "ats_system": "Meta Careers (Internal)",
        "weights": {
            "technical_depth": 25,
            "scale_impact": 25,
            "speed_execution": 15,
            "quantified_impact": 20,
            "formatting": 5,
            "education": 10,
        },
        "critical_keywords": ["scale", "billions", "performance", "infrastructure", "real-time", "distributed", "mobile", "social"],
        "red_flags": ["small scale", "basic CRUD"],
        "preferred_verbs": ["Shipped", "Scaled", "Optimized", "Built", "Designed", "Reduced", "Launched", "Improved"],
        "tips": "Meta values moving fast and building at scale. Emphasize projects that handle millions/billions of interactions. Performance optimization is key.",
    },
    "tcs": {
        "name": "TCS",
        "logo_emoji": "🔴",
        "color": "#1A1A1A",
        "ats_system": "TCS iON / NextStep",
        "weights": {
            "technical_breadth": 25,
            "certifications": 20,
            "academic_score": 20,
            "process_knowledge": 15,
            "formatting": 10,
            "communication": 10,
        },
        "critical_keywords": ["agile", "SDLC", "SAP", "Oracle", "Java", "Python", "testing", "documentation", "client"],
        "red_flags": ["no certifications mentioned", "no academic details"],
        "preferred_verbs": ["Developed", "Implemented", "Tested", "Deployed", "Analyzed", "Documented", "Coordinated"],
        "tips": "TCS ATS prioritizes academic scores (60%+ required), certifications, and technology breadth. Mention Agile/SDLC knowledge and client-facing experience.",
    },
    "infosys": {
        "name": "Infosys",
        "logo_emoji": "🟣",
        "color": "#007CC3",
        "ats_system": "Infosys Careers (Taleo)",
        "weights": {
            "academic_excellence": 25,
            "certifications": 15,
            "domain_knowledge": 20,
            "technical_skills": 20,
            "formatting": 10,
            "communication": 10,
        },
        "critical_keywords": ["certification", "domain", "ERP", "cloud", "digital transformation", "analytics", "consulting"],
        "red_flags": ["no education section", "gaps without explanation"],
        "preferred_verbs": ["Spearheaded", "Facilitated", "Implemented", "Streamlined", "Analyzed", "Managed"],
        "tips": "Infosys values academic excellence, relevant certifications (AWS, Azure, Java), and domain expertise in their focus industries.",
    },
    "wipro": {
        "name": "Wipro",
        "logo_emoji": "🌸",
        "color": "#3F1D77",
        "ats_system": "Wipro Careers (SuccessFactors)",
        "weights": {
            "technical_skills": 25,
            "domain_knowledge": 20,
            "certifications": 15,
            "communication": 15,
            "academic_score": 15,
            "formatting": 10,
        },
        "critical_keywords": ["full stack", "automation", "testing", "DevOps", "cloud", "cybersecurity", "consulting"],
        "red_flags": ["no contact info", "unprofessional email"],
        "preferred_verbs": ["Engineered", "Automated", "Delivered", "Optimized", "Led", "Designed"],
        "tips": "Wipro's ATS values practical technical skills, automation experience, and certifications. Highlight projects with clear tech stacks and outcomes.",
    },
}


class CompanyATSService:
    """Scores resumes against specific company ATS patterns using AI."""

    @staticmethod
    async def score_for_company(
        resume_text: str,
        company_id: str,
        target_role: str = "Software Engineer",
    ) -> Dict[str, Any]:
        """Score a resume against a specific company's ATS system."""
        profile = COMPANY_PROFILES.get(company_id.lower())
        if not profile:
            return {"error": f"Unknown company: {company_id}"}

        from app.core.ai_provider import AIProvider

        weights_str = "\n".join(
            f"- {k.replace('_', ' ').title()}: {v}% weight"
            for k, v in profile["weights"].items()
        )

        prompt = f"""You are an expert ATS (Applicant Tracking System) simulator for {profile['name']}.

Analyze this resume as if you were {profile['name']}'s ATS system ({profile['ats_system']}).

RESUME TEXT:
{resume_text[:4000]}

TARGET ROLE: {target_role}

{profile['name']}'S ATS SCORING CRITERIA:
{weights_str}

CRITICAL KEYWORDS {profile['name']} looks for: {', '.join(profile['critical_keywords'])}
RED FLAG phrases (penalize): {', '.join(profile['red_flags'])}
PREFERRED action verbs: {', '.join(profile['preferred_verbs'])}

SCORING INSTRUCTIONS:
1. Score each category on a 0-100 scale based on how well the resume matches {profile['name']}'s specific requirements
2. Apply the weights to calculate final_score
3. Be REALISTIC — a fresh graduate should score 40-65, experienced professional 65-85, perfect match 85+
4. Identify specific issues and improvements for this company

Return ONLY valid JSON:
{{
  "company": "{profile['name']}",
  "final_score": <weighted score 0-100>,
  "category_scores": {{
    {', '.join(f'"{k}": <0-100>' for k in profile["weights"].keys())}
  }},
  "keyword_matches": ["<keywords from resume that match {profile['name']}'s criteria>"],
  "missing_keywords": ["<critical keywords missing from resume>"],
  "red_flags_found": ["<problematic phrases found in resume>"],
  "top_improvements": [
    "<specific improvement #1 for {profile['name']}>",
    "<specific improvement #2>",
    "<specific improvement #3>"
  ],
  "verdict": "<one of: 'Strong Match ✅', 'Needs Improvement ⚠️', 'Likely Rejected ❌'>"
}}"""

        result = await AIProvider.generate_json(
            prompt=prompt,
            system_prompt=f"You are {profile['name']}'s ATS system. Score resumes accurately based on {profile['name']}'s actual hiring criteria. Return only valid JSON.",
            max_tokens=800,
            temperature=0.3,
            timeout=30,
        )

        if result:
            result["company_meta"] = {
                "name": profile["name"],
                "logo_emoji": profile["logo_emoji"],
                "color": profile["color"],
                "ats_system": profile["ats_system"],
                "tip": profile["tips"],
            }
            return result

        # Keyword fallback
        return CompanyATSService._keyword_score(resume_text, profile, target_role)

    @staticmethod
    async def score_all_companies(
        resume_text: str,
        target_role: str = "Software Engineer",
        companies: List[str] = None,
    ) -> Dict[str, Any]:
        """Score resume against multiple companies simultaneously."""
        if not companies:
            companies = ["google", "amazon", "microsoft", "tcs", "infosys"]

        # Run all scoring tasks concurrently
        tasks = [
            CompanyATSService.score_for_company(resume_text, company, target_role)
            for company in companies
        ]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        scores = {}
        for company, result in zip(companies, results):
            if isinstance(result, Exception):
                logger.error(f"ATS scoring failed for {company}: {result}")
                scores[company] = {"error": str(result), "final_score": 0}
            else:
                scores[company] = result

        # Calculate summary
        valid_scores = [s.get("final_score", 0) for s in scores.values() if isinstance(s.get("final_score"), (int, float))]
        avg_score = round(sum(valid_scores) / len(valid_scores), 1) if valid_scores else 0
        best_company = max(scores.items(), key=lambda x: x[1].get("final_score", 0))[0] if scores else "N/A"

        return {
            "company_scores": scores,
            "summary": {
                "average_score": avg_score,
                "best_match": best_company,
                "companies_analyzed": len(companies),
                "target_role": target_role,
            }
        }

    @staticmethod
    def get_available_companies() -> List[Dict[str, str]]:
        """Return list of available company profiles."""
        return [
            {
                "id": cid,
                "name": profile["name"],
                "emoji": profile["logo_emoji"],
                "color": profile["color"],
                "ats_system": profile["ats_system"],
            }
            for cid, profile in COMPANY_PROFILES.items()
        ]

    @staticmethod
    def _keyword_score(resume_text: str, profile: Dict, target_role: str) -> Dict[str, Any]:
        """Keyword-based fallback scoring when AI is unavailable."""
        text_lower = resume_text.lower()

        # Score based on keyword presence
        keyword_hits = [k for k in profile["critical_keywords"] if k.lower() in text_lower]
        red_flags = [r for r in profile["red_flags"] if r.lower() in text_lower]
        verb_hits = [v for v in profile["preferred_verbs"] if v.lower() in text_lower]

        # Base score calculation
        keyword_score = min(100, (len(keyword_hits) / max(len(profile["critical_keywords"]), 1)) * 100)
        verb_score = min(100, (len(verb_hits) / max(len(profile["preferred_verbs"]), 1)) * 100)
        penalty = len(red_flags) * 5

        # Weighted calculation
        base_score = (keyword_score * 0.4 + verb_score * 0.3 + 50 * 0.3) - penalty
        final_score = max(0, min(100, round(base_score)))

        verdict = "Strong Match ✅" if final_score >= 70 else ("Needs Improvement ⚠️" if final_score >= 45 else "Likely Rejected ❌")

        return {
            "company": profile["name"],
            "final_score": final_score,
            "keyword_matches": keyword_hits,
            "missing_keywords": [k for k in profile["critical_keywords"] if k.lower() not in text_lower],
            "red_flags_found": red_flags,
            "top_improvements": [
                f"Add more {profile['name']}-specific keywords: {', '.join(profile['critical_keywords'][:3])}",
                f"Use stronger action verbs: {', '.join(profile['preferred_verbs'][:4])}",
                f"Remove weak phrases: {', '.join(profile['red_flags'][:2])}",
            ],
            "verdict": verdict,
            "company_meta": {
                "name": profile["name"],
                "logo_emoji": profile["logo_emoji"],
                "color": profile["color"],
                "ats_system": profile["ats_system"],
                "tip": profile["tips"],
            },
        }
