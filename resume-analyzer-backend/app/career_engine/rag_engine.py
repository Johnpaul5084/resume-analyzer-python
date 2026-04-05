"""
Advanced RAG Engine v2.0 — TF-IDF + Cosine Similarity
=====================================================

UPGRADED from basic keyword matching to a REAL vector search engine:
  1. TF-IDF vectorization of role profiles (skills + description + tools)
  2. Cosine similarity for accurate role-resume matching
  3. Multi-signal scoring: TF-IDF + skill overlap + section detection
  4. Weighted ranking with configurable boosting
  5. Cold-start cache protection with hash-based invalidation

This engine feeds:
  - Job prediction (top-3 roles with confidence)
  - ATS scoring (role-specific analysis prompt)
  - Resume rewrite (role-aware optimizations)
  - Company ATS (role-specific keyword matching)
  - Interview prep (role-specific question generation)
"""

import numpy as np
import json
import os
import time
import logging
import hashlib
import math
import re
from typing import List, Dict, Any, Tuple
from collections import Counter

logger = logging.getLogger(__name__)

# Global state
_roles_data: Dict[str, Any] = {}
_role_names: List[str] = []
_tfidf_matrix: Dict[str, Dict[str, float]] = {}  # role_name -> {word: tfidf_score}
_idf_scores: Dict[str, float] = {}
_vocabulary: set = set()

# Cache paths
_CACHE_DIR = os.path.join(os.path.dirname(__file__), ".cache")
_CACHE_FILE = os.path.join(_CACHE_DIR, "rag_index_v2_cache.json")
_DB_PATH = os.path.join(os.path.dirname(__file__), "role_database.json")


# ──────────────────────────────────────────────────────────────────────────────
# TF-IDF ENGINE (local, zero dependencies beyond stdlib + numpy)
# ──────────────────────────────────────────────────────────────────────────────

_STOP_WORDS = frozenset({
    "the", "a", "an", "and", "or", "but", "is", "are", "was", "were", "be",
    "been", "being", "have", "has", "had", "do", "does", "did", "will",
    "would", "shall", "should", "may", "might", "can", "could", "to", "of",
    "in", "for", "on", "with", "at", "by", "from", "as", "into", "through",
    "during", "before", "after", "above", "below", "between", "under", "over",
    "that", "this", "these", "those", "it", "its", "not", "no", "nor",
    "so", "up", "out", "if", "about", "than", "then", "also", "very",
    "just", "how", "all", "each", "every", "both", "such", "when", "where",
    "which", "who", "whom", "what", "while", "other", "some", "any", "most",
    "more", "using", "etc", "via", "including", "based",
})


def _tokenize(text: str) -> List[str]:
    """Tokenize text into lowercase words, removing stop words and short tokens."""
    words = re.findall(r'[a-zA-Z][a-zA-Z0-9+#./-]{1,}', text.lower())
    return [w for w in words if w not in _STOP_WORDS and len(w) > 1]


def _compute_tf(tokens: List[str]) -> Dict[str, float]:
    """Compute term frequency (normalized by max frequency)."""
    counts = Counter(tokens)
    if not counts:
        return {}
    max_freq = max(counts.values())
    return {word: 0.5 + 0.5 * (count / max_freq) for word, count in counts.items()}


def _compute_idf(documents: List[List[str]]) -> Dict[str, float]:
    """Compute inverse document frequency across all role documents."""
    n_docs = len(documents)
    df = Counter()
    for doc in documents:
        unique_tokens = set(doc)
        for token in unique_tokens:
            df[token] += 1

    return {
        word: math.log((1 + n_docs) / (1 + doc_freq)) + 1
        for word, doc_freq in df.items()
    }


def _cosine_similarity(vec_a: Dict[str, float], vec_b: Dict[str, float]) -> float:
    """Compute cosine similarity between two sparse TF-IDF vectors."""
    common = set(vec_a.keys()) & set(vec_b.keys())
    if not common:
        return 0.0

    dot_product = sum(vec_a[w] * vec_b[w] for w in common)
    norm_a = math.sqrt(sum(v ** 2 for v in vec_a.values()))
    norm_b = math.sqrt(sum(v ** 2 for v in vec_b.values()))

    if norm_a == 0 or norm_b == 0:
        return 0.0
    return dot_product / (norm_a * norm_b)


# ──────────────────────────────────────────────────────────────────────────────
# CACHE MANAGEMENT (cold start protection)
# ──────────────────────────────────────────────────────────────────────────────

def _compute_db_hash() -> str:
    try:
        with open(_DB_PATH, "rb") as f:
            return hashlib.md5(f.read()).hexdigest()
    except Exception:
        return ""


def _save_cache():
    try:
        os.makedirs(_CACHE_DIR, exist_ok=True)
        cache_data = {
            "db_hash": _compute_db_hash(),
            "roles_data": _roles_data,
            "role_names": _role_names,
            "tfidf_matrix": _tfidf_matrix,
            "idf_scores": _idf_scores,
        }
        with open(_CACHE_FILE, "w", encoding="utf-8") as f:
            json.dump(cache_data, f)
        logger.info("✅ RAG v2 index cached to disk (TF-IDF precomputed)")
    except Exception as e:
        logger.warning("Failed to save RAG v2 cache: %s", e)


def _load_cache() -> bool:
    global _roles_data, _role_names, _tfidf_matrix, _idf_scores, _vocabulary
    try:
        if not os.path.exists(_CACHE_FILE):
            return False
        with open(_CACHE_FILE, "r", encoding="utf-8") as f:
            cache = json.load(f)
        if cache.get("db_hash") != _compute_db_hash():
            logger.info("RAG v2 cache stale — rebuilding TF-IDF index")
            return False
        _roles_data = cache["roles_data"]
        _role_names = cache["role_names"]
        _tfidf_matrix = cache["tfidf_matrix"]
        _idf_scores = cache.get("idf_scores", {})
        _vocabulary = set(_idf_scores.keys())
        logger.info("⚡ RAG v2 index loaded from cache | roles=%d | vocab=%d", len(_role_names), len(_vocabulary))
        return True
    except Exception as e:
        logger.warning("Failed to load RAG v2 cache: %s", e)
        return False


# ──────────────────────────────────────────────────────────────────────────────
# INDEX BUILDING
# ──────────────────────────────────────────────────────────────────────────────

def _build_role_document(role_name: str, role_data: Dict) -> str:
    """Build a rich text document for a role by combining all fields."""
    parts = [
        role_name,
        role_name,  # double-weight the role name
        role_data.get("description", ""),
        role_data.get("category", ""),
        " ".join(role_data.get("mandatory_skills", [])),
        " ".join(role_data.get("mandatory_skills", [])),  # double-weight mandatory skills
        " ".join(role_data.get("advanced_skills", [])),
        " ".join(role_data.get("tools", [])),
        " ".join(role_data.get("industry", [])),
        " ".join(role_data.get("certifications", [])),
        " ".join(role_data.get("interview_topics", [])),
    ]
    return " ".join(parts)


def build_index():
    """Build the TF-IDF vector index from role_database.json."""
    global _roles_data, _role_names, _tfidf_matrix, _idf_scores, _vocabulary
    _t0 = time.perf_counter()

    logger.info("⚡ Initializing RAG v2.0 Engine (TF-IDF + Cosine Similarity)...")

    # Try cache first
    if _load_cache():
        return

    # Load knowledge base
    if not os.path.exists(_DB_PATH):
        logger.error("❌ Role Database not found at %s", _DB_PATH)
        return

    try:
        with open(_DB_PATH, encoding='utf-8') as f:
            _roles_data = json.load(f)
        _role_names = list(_roles_data.keys())

        # Build documents for each role
        documents = []
        for role_name in _role_names:
            doc_text = _build_role_document(role_name, _roles_data[role_name])
            tokens = _tokenize(doc_text)
            documents.append(tokens)

        # Compute IDF across all documents
        _idf_scores = _compute_idf(documents)
        _vocabulary = set(_idf_scores.keys())

        # Compute TF-IDF vectors for each role
        _tfidf_matrix = {}
        for i, role_name in enumerate(_role_names):
            tf = _compute_tf(documents[i])
            tfidf_vec = {
                word: tf_val * _idf_scores.get(word, 1.0)
                for word, tf_val in tf.items()
            }
            _tfidf_matrix[role_name] = tfidf_vec

        _elapsed_ms = (time.perf_counter() - _t0) * 1000
        logger.info(
            "✅ RAG v2 index built | roles=%d | vocab=%d | elapsed=%.1fms",
            len(_role_names), len(_vocabulary), _elapsed_ms,
        )

        # Cache for cold starts
        _save_cache()

    except Exception as e:
        logger.error("Failed to build RAG v2 index: %s", e)


# ──────────────────────────────────────────────────────────────────────────────
# RETRIEVAL (core function used across all endpoints)
# ──────────────────────────────────────────────────────────────────────────────

def retrieve_relevant_roles(resume_text: str, top_k: int = 3) -> List[str]:
    """Retrieve top-K most relevant roles using TF-IDF cosine similarity."""
    global _roles_data, _role_names, _tfidf_matrix
    _t0 = time.perf_counter()

    if not _role_names:
        build_index()
    if not resume_text or len(resume_text.strip()) < 10:
        return ["Software Engineer"]

    try:
        # Tokenize resume
        resume_tokens = _tokenize(resume_text)
        resume_tf = _compute_tf(resume_tokens)
        resume_tfidf = {
            word: tf_val * _idf_scores.get(word, 1.0)
            for word, tf_val in resume_tf.items()
            if word in _vocabulary  # only consider known vocabulary
        }

        # Score each role using multi-signal approach
        scored_roles: List[Tuple[str, float]] = []

        for role_name in _role_names:
            role_vec = _tfidf_matrix.get(role_name, {})

            # Signal 1: TF-IDF Cosine Similarity (0-1 range, weight=50%)
            cos_sim = _cosine_similarity(resume_tfidf, role_vec)

            # Signal 2: Direct Skill Match (weight=30%)
            role_data = _roles_data[role_name]
            mandatory_skills = role_data.get("mandatory_skills", [])
            advanced_skills = role_data.get("advanced_skills", [])
            tools = role_data.get("tools", [])
            all_skills = mandatory_skills + advanced_skills + tools

            text_lower = resume_text.lower()
            mandatory_hits = sum(1 for s in mandatory_skills if s.lower() in text_lower)
            advanced_hits = sum(1 for s in advanced_skills if s.lower() in text_lower)
            tool_hits = sum(1 for t in tools if t.lower() in text_lower)

            if mandatory_skills:
                skill_score = (
                    (mandatory_hits / len(mandatory_skills)) * 0.6 +
                    (advanced_hits / max(len(advanced_skills), 1)) * 0.25 +
                    (tool_hits / max(len(tools), 1)) * 0.15
                )
            else:
                skill_score = 0

            # Signal 3: Role Name in Resume (weight=20%)
            name_score = 0.0
            role_words = role_name.lower().split()
            for rw in role_words:
                if rw in text_lower and len(rw) > 2:
                    name_score += 0.3
            name_score = min(name_score, 1.0)

            # Combined score (weighted)
            final_score = (cos_sim * 0.50) + (skill_score * 0.30) + (name_score * 0.20)
            scored_roles.append((role_name, final_score))

        # Sort and return top-k
        scored_roles.sort(key=lambda x: x[1], reverse=True)
        results = [name for name, score in scored_roles[:top_k] if score > 0.01]

        if not results:
            results = ["Software Engineer"]

        _elapsed_ms = (time.perf_counter() - _t0) * 1000
        logger.info(
            "RAG v2 retrieval | top_roles=%s | scores=%s | elapsed=%.1fms",
            results,
            [f"{s:.3f}" for _, s in scored_roles[:top_k]],
            _elapsed_ms,
        )
        return results

    except Exception as e:
        logger.error("⚠️ RAG v2 retrieval error: %s", e)
        return ["Software Engineer"]


def retrieve_roles_with_scores(resume_text: str, top_k: int = 5) -> List[Dict[str, Any]]:
    """
    Enhanced retrieval returning detailed role matches with confidence scores.
    Used by the Smart Pipeline and Career Predictor for detailed feedback.
    """
    global _roles_data, _role_names, _tfidf_matrix
    _t0 = time.perf_counter()

    if not _role_names:
        build_index()
    if not resume_text or len(resume_text.strip()) < 10:
        return [{"role": "Software Engineer", "confidence": 50.0, "skills_matched": [], "skills_missing": []}]

    try:
        resume_tokens = _tokenize(resume_text)
        resume_tf = _compute_tf(resume_tokens)
        resume_tfidf = {
            word: tf_val * _idf_scores.get(word, 1.0)
            for word, tf_val in resume_tf.items()
            if word in _vocabulary
        }
        text_lower = resume_text.lower()

        scored_roles = []
        for role_name in _role_names:
            role_vec = _tfidf_matrix.get(role_name, {})
            role_data = _roles_data[role_name]

            # Cosine similarity
            cos_sim = _cosine_similarity(resume_tfidf, role_vec)

            # Skill analysis
            mandatory = role_data.get("mandatory_skills", [])
            advanced = role_data.get("advanced_skills", [])
            tools = role_data.get("tools", [])

            matched_mandatory = [s for s in mandatory if s.lower() in text_lower]
            matched_advanced = [s for s in advanced if s.lower() in text_lower]
            matched_tools = [t for t in tools if t.lower() in text_lower]
            missing_mandatory = [s for s in mandatory if s.lower() not in text_lower]

            all_matched = matched_mandatory + matched_advanced + matched_tools
            total_skills = len(mandatory) + len(advanced) + len(tools)
            skill_coverage = len(all_matched) / max(total_skills, 1)

            # Combined confidence (0-100)
            confidence = min(100, round(
                (cos_sim * 40) +
                (skill_coverage * 35) +
                (len(matched_mandatory) / max(len(mandatory), 1)) * 25
            , 1))

            scored_roles.append({
                "role": role_name,
                "confidence": confidence,
                "cosine_score": round(cos_sim * 100, 1),
                "skill_coverage": round(skill_coverage * 100, 1),
                "skills_matched": all_matched[:8],
                "skills_missing": missing_mandatory[:5],
                "category": role_data.get("category", "General"),
                "growth_score": role_data.get("growth_score", 7.0),
                "salary_range": role_data.get("avg_salary_range", "N/A"),
            })

        # Sort by confidence
        scored_roles.sort(key=lambda x: x["confidence"], reverse=True)

        _elapsed_ms = (time.perf_counter() - _t0) * 1000
        logger.info(
            "RAG v2 detailed retrieval | top=%s | elapsed=%.1fms",
            [r["role"] for r in scored_roles[:top_k]], _elapsed_ms,
        )
        return scored_roles[:top_k]

    except Exception as e:
        logger.error("RAG v2 detailed retrieval error: %s", e)
        return [{"role": "Software Engineer", "confidence": 50.0, "skills_matched": [], "skills_missing": []}]


def get_role_data(role_name: str) -> Dict[str, Any]:
    """Get full role profile data for a specific role."""
    if not _roles_data:
        build_index()
    return _roles_data.get(role_name, {})


def get_all_role_names() -> List[str]:
    """Get all available role names."""
    if not _role_names:
        build_index()
    return _role_names.copy()
