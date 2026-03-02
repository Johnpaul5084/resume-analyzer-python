"""
API Credit Manager
==================
Tracks and limits API usage per day to protect free tier credits.

FREE TIER LIMITS (per day):
  - Gemini API   : 50 requests/day  (Free: 15 RPM, ~1500/day)
  - OpenAI API   : 20 requests/day  (Free tier: limited credits)
  - SerpAPI      : 10 requests/day  (Free: 100/month ≈ 3.3/day)

These are CONSERVATIVE limits to ensure credits last the full month.
Adjust in .env if you have paid plans with higher limits.
"""

import os
import time
import logging
from pathlib import Path
from threading import Lock
from dotenv import dotenv_values

logger = logging.getLogger(__name__)

_env_path = Path(__file__).resolve().parent.parent / ".env"


def _get_limit(env_key: str, default: int) -> int:
    """Read a limit from .env or use default."""
    try:
        vals = dotenv_values(_env_path)
        val = vals.get(env_key, "") or os.getenv(env_key, "")
        return int(val) if val else default
    except Exception:
        return default


class APICreditManager:
    """
    Per-day credit tracker for all 3 APIs.
    Thread-safe. Resets daily at midnight.
    """

    _lock = Lock()
    _usage = {
        "gemini":  {"count": 0, "date": ""},
        "openai":  {"count": 0, "date": ""},
        "serpapi": {"count": 0, "date": ""},
    }

    # Default conservative daily limits (can override via .env)
    _limits = {
        "gemini":  50,   # Gemini free tier: ~1500/day — we use 50 to be safe
        "openai":  20,   # OpenAI free tier: very limited — conserve
        "serpapi": 10,   # SerpAPI free: 100/month ≈ 3.3/day — we use 10
    }

    @classmethod
    def _today(cls) -> str:
        return time.strftime("%Y-%m-%d")

    @classmethod
    def _load_limits(cls):
        """Load custom limits from .env if set."""
        cls._limits["gemini"]  = _get_limit("GEMINI_DAILY_LIMIT",  50)
        cls._limits["openai"]  = _get_limit("OPENAI_DAILY_LIMIT",  20)
        cls._limits["serpapi"] = _get_limit("SERPAPI_DAILY_LIMIT",  10)

    @classmethod
    def can_use(cls, api_name: str) -> bool:
        """
        Check if we can make another call to this API today.
        Returns True if under limit, False if quota exhausted.
        """
        api = api_name.lower()
        if api not in cls._usage:
            return True

        cls._load_limits()
        today = cls._today()

        with cls._lock:
            usage = cls._usage[api]
            # Reset counter if new day
            if usage["date"] != today:
                usage["count"] = 0
                usage["date"] = today

            return usage["count"] < cls._limits.get(api, 100)

    @classmethod
    def record_use(cls, api_name: str):
        """Record one API call."""
        api = api_name.lower()
        if api not in cls._usage:
            return

        today = cls._today()

        with cls._lock:
            usage = cls._usage[api]
            if usage["date"] != today:
                usage["count"] = 0
                usage["date"] = today
            usage["count"] += 1

            remaining = cls._limits.get(api, 100) - usage["count"]
            if remaining <= 5:
                logger.warning(f"⚠️ {api.upper()} API: Only {remaining} credits left today!")

    @classmethod
    def get_remaining(cls, api_name: str) -> int:
        """Get remaining credits for today."""
        api = api_name.lower()
        if api not in cls._usage:
            return 999

        cls._load_limits()
        today = cls._today()

        with cls._lock:
            usage = cls._usage[api]
            if usage["date"] != today:
                return cls._limits.get(api, 100)
            return max(0, cls._limits.get(api, 100) - usage["count"])

    @classmethod
    def get_status(cls) -> dict:
        """Get all API usage status for dashboard."""
        cls._load_limits()
        today = cls._today()
        status = {}
        for api in cls._usage:
            with cls._lock:
                usage = cls._usage[api]
                if usage["date"] != today:
                    used = 0
                else:
                    used = usage["count"]
                limit = cls._limits.get(api, 100)
                status[api] = {
                    "used_today": used,
                    "daily_limit": limit,
                    "remaining": max(0, limit - used),
                    "percentage_used": round(used / limit * 100, 1) if limit > 0 else 0,
                }
        return status

    @classmethod
    def check_and_use(cls, api_name: str) -> tuple:
        """
        Combined check + record. Returns (allowed: bool, remaining: int).
        Use this before making an API call.
        """
        if cls.can_use(api_name):
            cls.record_use(api_name)
            remaining = cls.get_remaining(api_name)
            return True, remaining
        else:
            remaining = cls.get_remaining(api_name)
            logger.warning(f"🚫 {api_name.upper()} daily limit reached (0/{cls._limits.get(api_name.lower(), 0)} remaining)")
            return False, remaining
