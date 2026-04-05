"""
Roadmap AI Generator
====================
Uses the Unified AI Provider (Gemini → OpenAI → Static Fallback)

Generates personalized 6-month career roadmaps using real AI.
Falls back to structured static roadmap only when all AI providers fail.
"""

import logging
import asyncio
from typing import List

logger = logging.getLogger(__name__)


class RoadmapAIGenerator:

    @staticmethod
    def generate_dynamic_roadmap(
        role: str,
        missing_skills: List[str],
        current_level: str = "Beginner",
    ) -> str:
        """
        Generate a 6-month career roadmap.
        Uses unified AIProvider (Gemini → OpenAI → static fallback).
        """
        # Run async in sync context
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                # Already in async context — use thread
                import concurrent.futures
                with concurrent.futures.ThreadPoolExecutor() as pool:
                    future = pool.submit(
                        asyncio.run,
                        RoadmapAIGenerator._async_generate(role, missing_skills, current_level)
                    )
                    return future.result(timeout=60)
            else:
                return loop.run_until_complete(
                    RoadmapAIGenerator._async_generate(role, missing_skills, current_level)
                )
        except RuntimeError:
            return asyncio.run(
                RoadmapAIGenerator._async_generate(role, missing_skills, current_level)
            )
        except Exception as e:
            logger.error(f"Roadmap generation error: {e}")
            return RoadmapAIGenerator._static_fallback(role, missing_skills)

    @staticmethod
    async def _async_generate(
        role: str,
        missing_skills: List[str],
        current_level: str = "Beginner",
        resume_text: str = "",
    ) -> str:
        """Async roadmap generation via RAG-augmented AIProvider."""
        from app.core.ai_provider import AIProvider

        prompt = f"""You are an expert AI Career Mentor advising a tech professional.

Create a detailed, actionable 6-month roadmap for someone aiming to become a {role}.

Current Level  : {current_level}
Key Skill Gaps : {', '.join(missing_skills) if missing_skills else 'General improvement needed'}

ROADMAP STRUCTURE (use plain text, no markdown symbols like ** or ###):

MONTH 1-2: Foundation & Core Skills
- Specific skills to learn with exact resource names (free courses, docs)
- Mini project to build (be specific about what to build)
- Daily practice routine

MONTH 3-4: Intermediate Mastery
- Advanced skills to develop
- Real-world project idea with tech stack
- Portfolio milestone to achieve

MONTH 5-6: Job-Ready Polish
- Industry-level capstone project
- Interview preparation focus areas
- How to showcase expertise on resume & LinkedIn

WEEK-BY-WEEK TIPS:
- Include 2-3 specific weekly goals for extra clarity

Keep the tone encouraging, professional, and specific to {role}. 
Do NOT use ** or ### formatting. Use CAPS for section headers."""

        # Use RAG-augmented generation if resume text is available
        if resume_text and len(resume_text.strip()) > 50:
            result = await AIProvider.generate_with_rag(
                prompt=prompt,
                resume_text=resume_text,
                system_prompt="You are an expert AI Career Mentor who creates highly specific, actionable career roadmaps. Use the career intelligence data to provide precise skill recommendations, realistic salary expectations, and relevant certifications.",
                max_tokens=1500,
                temperature=0.7,
                timeout=50,
            )
        else:
            result = await AIProvider.generate(
                prompt=prompt,
                system_prompt="You are an expert AI Career Mentor who creates highly specific, actionable career roadmaps. Always use real resource names and specific project ideas.",
                max_tokens=1200,
                temperature=0.7,
                timeout=45,
            )

        if result and result.strip() and len(result.strip()) > 100:
            # Clean any leftover markdown
            cleaned = result.replace("**", "").replace("###", "").replace("##", "").strip()
            logger.info("AI roadmap generated (%d chars)", len(cleaned))
            return cleaned

        # ── Static Fallback ────────────────────────────────────
        logger.info("Using static roadmap fallback for %s", role)
        return RoadmapAIGenerator._static_fallback(role, missing_skills)

    @staticmethod
    def _static_fallback(role: str, missing_skills: List[str]) -> str:
        """Structured static roadmap when all AI providers fail."""
        from app.career_engine.roadmap_generator import RoadmapGenerator
        offline_roadmap = RoadmapGenerator.generate_roadmap(role)
        
        text = f"CAREER ROADMAP: {role.upper()}\n\n"
        for item in offline_roadmap:
            text += f"{item['period'].upper()}: {item['focus']}\n"
            matching_skills = [s for s in missing_skills if s.lower() in item['focus'].lower()]
            if matching_skills:
                text += f"- Priority Gap Fix: {', '.join(matching_skills)}\n"
            else:
                text += f"- Key Focus: Deep dive into core competencies for {role}\n"
            text += "\n"
            
        text += "DAILY SCHEDULE (Recommended):\n"
        text += "- 2 hours: Coding practice / Project building\n"
        text += "- 1 hour: DSA / Interview prep\n"
        text += "- 30 minutes: Learning new concepts / Reading tech blogs\n\n"
        text += "Remember: Consistency beats intensity. Stay focused on the goal!"
        
        return text.strip()
