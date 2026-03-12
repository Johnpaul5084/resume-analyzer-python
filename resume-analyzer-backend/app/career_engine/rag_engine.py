import numpy as np
import json
import os
import time
import logging
import regex as re
import hashlib

logger = logging.getLogger(__name__)

# Global index and role tracking
_roles_data = {}
_role_names = []

# Cache file path (next to role_database.json)
_CACHE_DIR = os.path.join(os.path.dirname(__file__), ".cache")
_CACHE_FILE = os.path.join(_CACHE_DIR, "rag_index_cache.json")
_DB_PATH = os.path.join(os.path.dirname(__file__), "role_database.json")


def _compute_db_hash() -> str:
    """Compute MD5 hash of role_database.json for cache invalidation."""
    try:
        with open(_DB_PATH, "rb") as f:
            return hashlib.md5(f.read()).hexdigest()
    except Exception:
        return ""


def _save_cache():
    """Serialize RAG index to disk for cold start protection."""
    try:
        os.makedirs(_CACHE_DIR, exist_ok=True)
        cache_data = {
            "db_hash": _compute_db_hash(),
            "roles_data": _roles_data,
            "role_names": _role_names,
        }
        with open(_CACHE_FILE, "w", encoding="utf-8") as f:
            json.dump(cache_data, f)
        logger.info("✅ RAG index cached to disk for cold start protection")
    except Exception as e:
        logger.warning("Failed to save RAG cache: %s", e)


def _load_cache() -> bool:
    """Load RAG index from disk cache. Returns True if valid cache loaded."""
    global _roles_data, _role_names
    try:
        if not os.path.exists(_CACHE_FILE):
            return False

        with open(_CACHE_FILE, "r", encoding="utf-8") as f:
            cache = json.load(f)

        # Validate cache freshness
        if cache.get("db_hash") != _compute_db_hash():
            logger.info("RAG cache stale (role_database.json changed) — rebuilding")
            return False

        _roles_data = cache["roles_data"]
        _role_names = cache["role_names"]
        logger.info("⚡ RAG index loaded from cache | roles=%d", len(_role_names))
        return True
    except Exception as e:
        logger.warning("Failed to load RAG cache: %s", e)
        return False


def build_index():
    global _roles_data, _role_names
    _t0 = time.perf_counter()
    
    logger.info("⚡ Initializing Optimized Lightweight RAG Engine...")

    # Try loading from cache first (cold start protection)
    if _load_cache():
        return
    
    # 1. Load Knowledge Base from file
    if not os.path.exists(_DB_PATH):
        logger.error("❌ Role Database not found at %s", _DB_PATH)
        return

    try:
        with open(_DB_PATH, encoding='utf-8') as f:
            _roles_data = json.load(f)
        _role_names = list(_roles_data.keys())
        _elapsed_ms = (time.perf_counter() - _t0) * 1000
        logger.info(
            "✅ RAG index built | roles=%d | elapsed=%.1fms",
            len(_role_names), _elapsed_ms,
        )
        # Cache for next cold start
        _save_cache()
    except Exception as e:
        logger.error("Failed to load roles: %s", e)

def retrieve_relevant_roles(resume_text: str, top_k: int = 3):
    global _roles_data, _role_names
    _t0 = time.perf_counter()
    
    if not _role_names:
        build_index()

    if not resume_text or len(resume_text.strip()) < 10:
        return ["Software Engineer"]

    try:
        # LITE SEARCH: Keyword matching for speed and 0 RAM usage
        scores = []
        text_lower = resume_text.lower()
        
        for role in _role_names:
            score = 0
            # Check for role name in text
            if role.lower() in text_lower:
                score += 10
            
            # Check for skills
            skills = _roles_data[role].get('mandatory_skills', [])
            for skill in skills:
                if skill.lower() in text_lower:
                    score += 2
            
            scores.append((role, score))
        
        # Sort by score and return top_k
        scores.sort(key=lambda x: x[1], reverse=True)
        results = [s[0] for s in scores[:top_k] if s[1] > 0]
        
        if not results:
            results = ["Software Engineer"]

        _elapsed_ms = (time.perf_counter() - _t0) * 1000
        logger.info(
            "RAG retrieval completed | top_roles=%s | elapsed=%.1fms",
            results, _elapsed_ms,
        )
        return results
    except Exception as e:
        logger.error("⚠️ Optimized Retrieval Error: %s", e)
        return ["Software Engineer"]

