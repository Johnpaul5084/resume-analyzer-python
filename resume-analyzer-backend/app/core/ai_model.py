"""Singleton Model Manager — loads all AI models ONCE.

All heavy model initialization (Gemini API config, spaCy NLP, embedding mock)
is centralized here.  Call `get_*` methods from any service — the first call
initializes, all subsequent calls return the cached instance.
"""

import os
import logging
import threading
from pathlib import Path

import google.generativeai as genai
from app.core.config import settings

logger = logging.getLogger(__name__)

_init_lock = threading.Lock()


class AIModelManager:
    """
    Lightweight Singleton Model Manager.
    - Gemini API key is configured exactly once.
    - spaCy NLP model is loaded exactly once.
    - Embedding mock is created exactly once.
    """

    _gemini_configured: bool = False
    _gemini_api_key: str = ""
    _spacy_nlp = None
    _embedding_model = None

    # ── Gemini Singleton ─────────────────────────────────────────
    @classmethod
    def configure_gemini(cls) -> str:
        """Configure Gemini API key exactly once. Returns the key."""
        if cls._gemini_configured:
            return cls._gemini_api_key

        with _init_lock:
            if cls._gemini_configured:          # double-check after lock
                return cls._gemini_api_key

            # Read from .env (fresh) → env var → settings, in priority order
            from dotenv import dotenv_values
            env_path = Path(__file__).resolve().parent.parent / ".env"
            vals = dotenv_values(env_path)
            key = (
                vals.get("GEMINI_API_KEY")
                or os.getenv("GEMINI_API_KEY")
                or settings.GEMINI_API_KEY
                or ""
            )
            if key and key != "YOUR_NEW_KEY_HERE":
                genai.configure(api_key=key)
                cls._gemini_api_key = key
                cls._gemini_configured = True
                logger.info("✅ Gemini API configured (singleton).")
            else:
                logger.warning("⚠️ GEMINI_API_KEY not set — Gemini features unavailable.")

            return cls._gemini_api_key

    @classmethod
    def get_gemini_model(
        cls,
        model_name: str = "gemini-2.0-flash",
        temperature: float = 0.4,
        max_output_tokens: int = 3000,
    ):
        """Return a GenerativeModel after ensuring the API key is configured once."""
        key = cls.configure_gemini()
        if not key:
            raise ValueError("GEMINI_API_KEY not configured in .env")
        return genai.GenerativeModel(
            model_name,
            generation_config={
                "temperature": temperature,
                "max_output_tokens": max_output_tokens,
            },
        )

    # ── spaCy Singleton ──────────────────────────────────────────
    @classmethod
    def get_spacy_nlp(cls):
        """Load spaCy model exactly once."""
        if cls._spacy_nlp is not None:
            return cls._spacy_nlp

        with _init_lock:
            if cls._spacy_nlp is not None:
                return cls._spacy_nlp
            try:
                import spacy
                cls._spacy_nlp = spacy.load("en_core_web_sm")
                logger.info("✅ spaCy NLP model loaded (singleton).")
            except Exception as e:
                logger.error(f"Failed to load spaCy model: {e}")
                return None
        return cls._spacy_nlp

    # ── Embedding Mock Singleton ─────────────────────────────────
    @classmethod
    def get_embedding_model(cls):
        """Return lightweight embedding mock (created once)."""
        if cls._embedding_model is None:
            with _init_lock:
                if cls._embedding_model is None:
                    cls._embedding_model = GeminiEmbeddingMock()
                    logger.info("⚡ Embedding mock initialized (singleton).")
        return cls._embedding_model

    @classmethod
    def preload(cls):
        """Pre-warm all singletons at startup."""
        cls.configure_gemini()
        cls.get_spacy_nlp()
        cls.get_embedding_model()


class GeminiEmbeddingMock:
    """
    A mock class that provides the 'encode' method required by the RAG engine,
    but uses zero vectors to save RAM (real analysis happens via Gemini API).
    """

    def encode(self, sentences):
        import numpy as np
        return np.zeros((len(sentences), 384))

