"""
Unified AI Provider
====================
Single gateway for ALL AI features.
Priority: Gemini (free, configured) → OpenAI (paid) → Smart Fallback

This ensures every feature works regardless of which API keys are available.
"""

import os
import re
import json
import logging
import asyncio
from pathlib import Path
from typing import Optional, Dict, Any, List
from dotenv import load_dotenv

_env_path = Path(__file__).resolve().parent.parent.parent / ".env"
load_dotenv(dotenv_path=_env_path, override=False)

logger = logging.getLogger(__name__)


class AIProvider:
    """Unified AI provider — tries Gemini first, then OpenAI, then fallback."""

    @staticmethod
    def _gemini_available() -> bool:
        from app.core.ai_model import AIModelManager
        key = AIModelManager.configure_gemini()
        return bool(key)

    @staticmethod
    def _openai_available() -> bool:
        key = os.getenv("OPENAI_API_KEY", "")
        return bool(key and key.startswith("sk-") and key != "YOUR_OPENAI_KEY_HERE")

    @staticmethod
    async def generate(
        prompt: str,
        system_prompt: str = "You are a helpful AI assistant.",
        max_tokens: int = 1200,
        temperature: float = 0.7,
        provider: str = "auto",  # "auto", "gemini", "openai"
        timeout: int = 45,
    ) -> str:
        """
        Generate AI response. Tries Gemini → OpenAI → returns empty string.
        
        Args:
            prompt: The user prompt
            system_prompt: System instruction
            max_tokens: Max output tokens
            temperature: Creativity level
            provider: Force a specific provider or "auto"
            timeout: Timeout in seconds
        """
        result = ""

        # ── Try Gemini (Primary) ────────────────────────────────────
        if provider in ("auto", "gemini") and AIProvider._gemini_available():
            try:
                result = await AIProvider._call_gemini(
                    prompt, system_prompt, max_tokens, temperature, timeout
                )
                if result and result.strip():
                    logger.info("AI response generated via Gemini (%d chars)", len(result))
                    return result.strip()
            except Exception as e:
                logger.warning("Gemini failed: %s — trying OpenAI", str(e)[:100])

        # ── Try OpenAI (Secondary) ──────────────────────────────────
        if provider in ("auto", "openai") and AIProvider._openai_available():
            try:
                result = await AIProvider._call_openai(
                    prompt, system_prompt, max_tokens, temperature, timeout
                )
                if result and result.strip():
                    logger.info("AI response generated via OpenAI (%d chars)", len(result))
                    return result.strip()
            except Exception as e:
                logger.warning("OpenAI failed: %s", str(e)[:100])

        logger.warning("All AI providers failed. Returning empty string.")
        return ""

    @staticmethod
    async def generate_json(
        prompt: str,
        system_prompt: str = "You are a helpful AI that returns only valid JSON.",
        max_tokens: int = 1200,
        temperature: float = 0.4,
        timeout: int = 45,
    ) -> Optional[Dict[str, Any]]:
        """Generate AI response and parse as JSON."""
        raw = await AIProvider.generate(
            prompt=prompt,
            system_prompt=system_prompt,
            max_tokens=max_tokens,
            temperature=temperature,
            timeout=timeout,
        )
        if not raw:
            return None

        try:
            # Clean markdown code fences
            cleaned = re.sub(r'^```(?:json)?\s*', '', raw.strip())
            cleaned = re.sub(r'\s*```$', '', cleaned)
            # Try JSON object first
            match = re.search(r'\{.*\}', cleaned, re.DOTALL)
            if match:
                return json.loads(match.group())
            # Try JSON array
            match = re.search(r'\[.*\]', cleaned, re.DOTALL)
            if match:
                arr = json.loads(match.group())
                return {"items": arr} if isinstance(arr, list) else None
        except Exception as e:
            logger.error("JSON parse failed: %s\nRaw: %s", e, raw[:200])

        return None

    # ─────────────────────────────────────────────────────────────────
    # RAG-Augmented Generation (feeds role context into AI prompts)
    # ─────────────────────────────────────────────────────────────────
    @staticmethod
    async def generate_with_rag(
        prompt: str,
        resume_text: str,
        system_prompt: str = "You are an expert career advisor.",
        max_tokens: int = 1500,
        temperature: float = 0.5,
        timeout: int = 50,
    ) -> str:
        """
        RAG-Augmented Generation — retrieves relevant role context from the
        TF-IDF knowledge base and injects it into the AI prompt.
        
        This produces MORE ACCURATE, ROLE-SPECIFIC responses than generic prompts.
        """
        try:
            from app.career_engine.rag_engine import retrieve_roles_with_scores, get_role_data

            # Step 1: Retrieve top matching roles from the RAG engine
            top_roles = retrieve_roles_with_scores(resume_text, top_k=3)

            # Step 2: Build rich context from role knowledge base
            context_parts = ["RELEVANT CAREER INTELLIGENCE (from knowledge base):"]

            for i, role_match in enumerate(top_roles[:3], 1):
                role_name = role_match.get("role", "Unknown")
                confidence = role_match.get("confidence", 0)
                matched = role_match.get("skills_matched", [])
                missing = role_match.get("skills_missing", [])

                role_data = get_role_data(role_name)
                description = role_data.get("description", "N/A")
                salary = role_data.get("avg_salary_range", "N/A")
                growth = role_data.get("growth_score", "N/A")
                certs = role_data.get("certifications", [])
                interview = role_data.get("interview_topics", [])

                context_parts.append(
                    f"\n#{i} MATCH: {role_name} (Confidence: {confidence}%)\n"
                    f"  Description: {description}\n"
                    f"  Growth Score: {growth}/10 | Salary: {salary}\n"
                    f"  Skills Found: {', '.join(matched[:6])}\n"
                    f"  Skills Missing: {', '.join(missing[:5])}\n"
                    f"  Certifications: {', '.join(certs[:3])}\n"
                    f"  Interview Topics: {', '.join(interview[:4])}"
                )

            rag_context = "\n".join(context_parts)

            # Step 3: Augment the prompt with RAG context
            augmented_prompt = f"""{rag_context}

---

{prompt}

IMPORTANT: Use the career intelligence above to provide specific, accurate, data-driven advice. 
Reference actual skills, growth scores, and salary ranges from the knowledge base."""

            logger.info(
                "RAG-augmented prompt built | top_roles=%s | context_len=%d",
                [r.get("role") for r in top_roles[:3]], len(rag_context),
            )

            return await AIProvider.generate(
                prompt=augmented_prompt,
                system_prompt=system_prompt,
                max_tokens=max_tokens,
                temperature=temperature,
                timeout=timeout,
            )

        except Exception as e:
            logger.warning("RAG augmentation failed (%s), falling back to standard generation", e)
            return await AIProvider.generate(
                prompt=prompt,
                system_prompt=system_prompt,
                max_tokens=max_tokens,
                temperature=temperature,
                timeout=timeout,
            )

    # ─────────────────────────────────────────────────────────────────
    # Internal: Gemini
    # ─────────────────────────────────────────────────────────────────
    @staticmethod
    async def _call_gemini(
        prompt: str, system_prompt: str, max_tokens: int, temperature: float, timeout: int
    ) -> str:
        import google.generativeai as genai
        from app.core.ai_model import AIModelManager
        from app.services.api_credit_manager import APICreditManager

        # Check credits
        allowed, remaining = APICreditManager.check_and_use("gemini")
        if not allowed:
            raise ValueError(f"Gemini daily credit limit reached (0 remaining)")

        AIModelManager.configure_gemini()

        model = genai.GenerativeModel(
            "gemini-2.0-flash",
            generation_config={"temperature": temperature, "max_output_tokens": max_tokens},
            system_instruction=system_prompt,
        )

        def _sync():
            response = model.generate_content(prompt)
            return response.text

        logger.info("Gemini credit used. Remaining today: %d", remaining)
        return await asyncio.wait_for(asyncio.to_thread(_sync), timeout=timeout)

    # ─────────────────────────────────────────────────────────────────
    # Internal: OpenAI
    # ─────────────────────────────────────────────────────────────────
    @staticmethod
    async def _call_openai(
        prompt: str, system_prompt: str, max_tokens: int, temperature: float, timeout: int
    ) -> str:
        from openai import AsyncOpenAI
        from app.services.api_credit_manager import APICreditManager

        allowed, remaining = APICreditManager.check_and_use("openai")
        if not allowed:
            raise ValueError("OpenAI daily credit limit reached")

        key = os.getenv("OPENAI_API_KEY", "")
        client = AsyncOpenAI(api_key=key, timeout=float(timeout))

        logger.info("OpenAI credit used. Remaining today: %d", remaining)

        resp = await asyncio.wait_for(
            client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt},
                ],
                max_tokens=max_tokens,
                temperature=temperature,
            ),
            timeout=timeout,
        )
        return resp.choices[0].message.content or ""

    # ─────────────────────────────────────────────────────────────────
    # Conversational Chat (with history)
    # ─────────────────────────────────────────────────────────────────
    @staticmethod
    async def chat(
        messages: List[Dict[str, str]],
        system_prompt: str = "You are a helpful AI assistant.",
        max_tokens: int = 800,
        temperature: float = 0.7,
        timeout: int = 30,
    ) -> str:
        """
        Conversational chat with message history.
        messages format: [{"role": "user"/"assistant", "content": "..."}]
        """
        # ── Try Gemini first ──────────────────────────────────────
        if AIProvider._gemini_available():
            try:
                return await AIProvider._chat_gemini(messages, system_prompt, max_tokens, temperature, timeout)
            except Exception as e:
                logger.warning("Gemini chat failed: %s — trying OpenAI", str(e)[:100])

        # ── Try OpenAI ────────────────────────────────────────────
        if AIProvider._openai_available():
            try:
                return await AIProvider._chat_openai(messages, system_prompt, max_tokens, temperature, timeout)
            except Exception as e:
                logger.warning("OpenAI chat failed: %s", str(e)[:100])

        return ""

    @staticmethod
    async def _chat_gemini(
        messages: List[Dict[str, str]], system_prompt: str,
        max_tokens: int, temperature: float, timeout: int
    ) -> str:
        import google.generativeai as genai
        from app.core.ai_model import AIModelManager
        from app.services.api_credit_manager import APICreditManager

        allowed, remaining = APICreditManager.check_and_use("gemini")
        if not allowed:
            raise ValueError("Gemini daily limit reached")

        AIModelManager.configure_gemini()

        model = genai.GenerativeModel(
            "gemini-2.0-flash",
            generation_config={"temperature": temperature, "max_output_tokens": max_tokens},
            system_instruction=system_prompt,
        )

        # Build conversation for Gemini
        # Gemini uses a different format — we'll concatenate into a single prompt
        conversation_text = ""
        for msg in messages[-10:]:  # Last 10 messages for context
            role_label = "Student" if msg["role"] == "user" else "AI Mentor"
            conversation_text += f"\n{role_label}: {msg['content']}\n"

        final_prompt = f"""Continue this conversation as the AI Mentor. 
Respond to the student's latest message.

CONVERSATION:
{conversation_text}

AI Mentor:"""

        def _sync():
            response = model.generate_content(final_prompt)
            return response.text

        logger.info("Gemini chat credit used. Remaining: %d", remaining)
        result = await asyncio.wait_for(asyncio.to_thread(_sync), timeout=timeout)
        # Clean any "AI Mentor:" prefix that Gemini might add
        result = re.sub(r'^AI Mentor:\s*', '', result.strip())
        return result

    @staticmethod
    async def _chat_openai(
        messages: List[Dict[str, str]], system_prompt: str,
        max_tokens: int, temperature: float, timeout: int
    ) -> str:
        from openai import AsyncOpenAI
        from app.services.api_credit_manager import APICreditManager

        allowed, remaining = APICreditManager.check_and_use("openai")
        if not allowed:
            raise ValueError("OpenAI daily limit reached")

        key = os.getenv("OPENAI_API_KEY", "")
        client = AsyncOpenAI(api_key=key, timeout=float(timeout))

        oai_messages = [{"role": "system", "content": system_prompt}]
        for msg in messages[-10:]:
            oai_messages.append({"role": msg["role"], "content": msg["content"]})

        logger.info("OpenAI chat credit used. Remaining: %d", remaining)
        resp = await asyncio.wait_for(
            client.chat.completions.create(
                model="gpt-4o-mini",
                messages=oai_messages,
                max_tokens=max_tokens,
                temperature=temperature,
            ),
            timeout=timeout,
        )
        return resp.choices[0].message.content or ""
