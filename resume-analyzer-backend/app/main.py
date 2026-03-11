import os
import sys
import time
from pathlib import Path
import urllib.request
from dotenv import load_dotenv

# Force load .env from backend root (one level up from app/)
env_path = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

# ── Structured Logging ──────────────────────────────────────────────────────
import logging

logging.basicConfig(
    level=getattr(logging, os.environ.get("LOG_LEVEL", "INFO").upper(), logging.INFO),
    format="%(asctime)s | %(levelname)-7s | %(name)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    stream=sys.stdout,
)
logger = logging.getLogger("ai_resume_analyzer")

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException
from app.api.api import api_router
from app.core.config import settings
from app.middleware.security import AISecurityMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from app.db.session import engine  # AI Resume Analyzer - v1.0.1-stable
from app.models import all_models  # Ensure models are registered

from app.career_engine.rag_engine import build_index
import threading

limiter = Limiter(key_func=get_remote_address)
app = FastAPI(
    title="AI Resume Analyzer",
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    description="AI Resume Analyzer - Intelligent Resume & Career Intelligence Platform.",
)

# 🔥 UNIVERSAL CORS UNBLOCKER (Priority 1)
# Allows Vercel Preview URLs, Local Dev, and Production domains
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# System Diagnostic: Ensure AI Engine has a pulse
_gemini_key = os.getenv("GEMINI_API_KEY", "")
if not _gemini_key or _gemini_key == "YOUR_NEW_KEY_HERE":
    logger.warning("GEMINI_API_KEY not configured. AI features will be unavailable.")
else:
    logger.info("✅ AI Neural Link: GEMINI_API_KEY Loaded")
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Global Security Layer
app.add_middleware(AISecurityMiddleware)


# ── 🔹4a Specific Exception Handler: HTTPException ──────────────────────
@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    """
    Handle FastAPI/Starlette HTTPExceptions.
    Returns structured JSON instead of raw errors.
    """
    logger.warning(
        "HTTP %d | method=%s | path=%s | detail=%s",
        exc.status_code, request.method, request.url.path, exc.detail,
    )
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "error": str(exc.detail),
        },
    )


# ── 🔹4b Specific Exception Handler: ValidationError ───────────────────
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """
    Handle Pydantic validation errors.
    Returns structured JSON with field-level error details.
    """
    errors = []
    for err in exc.errors():
        field = " -> ".join(str(loc) for loc in err.get("loc", []))
        errors.append({"field": field, "message": err.get("msg", "")})

    logger.warning(
        "Validation error | method=%s | path=%s | errors=%s",
        request.method, request.url.path, errors,
    )
    return JSONResponse(
        status_code=422,
        content={
            "success": False,
            "error": "Request validation failed",
            "details": errors,
        },
    )


# ── 🔹4c Global Exception Handler (Catch-All) ───────────────────────────
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """
    Catch-all exception handler. Prevents unhandled exceptions from crashing
    the server. Logs full details server-side, returns sanitized error to client.
    """
    logger.error(
        "Unhandled exception | method=%s | path=%s | error=%s",
        request.method,
        request.url.path,
        str(exc),
        exc_info=True,
    )
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "error": "An internal error occurred. Our AI systems are self-recovering. Please retry.",
        },
    )


# ── 🔹5 In-Memory Caching Layer ──────────────────────────────────────────
from functools import lru_cache

@lru_cache(maxsize=64)
def _cached_role_template(role: str) -> str:
    """Cache role templates so repeated scoring for the same role avoids disk I/O."""
    from app.services.ai_scoring_engine import AIScoringEngine
    return AIScoringEngine.get_role_template(role)

@lru_cache(maxsize=128)
def _cached_rag_retrieval(resume_hash: str, top_k: int = 3):
    """Cache RAG retrieval results for identical resume text (keyed by hash)."""
    # This is populated by callers who hash the resume_text first.
    # Actual retrieval is done inline; this wrapper enables caching.
    from app.career_engine.rag_engine import retrieve_relevant_roles
    return tuple(retrieve_relevant_roles(resume_hash, top_k))

# Expose cache utilities for services to use
app.state.cache = {
    "role_template": _cached_role_template,
    "rag_retrieval": _cached_rag_retrieval,
}


@app.on_event("startup")
def startup_event():
    # Build RAG Index & Preload Models in Background to avoid blocking Cold Start
    def preload_all():
        # 1. Database Initialization (Moved to background to avoid blocking Startup)
        try:
            logger.info("Verifying Neural Database in background...")
            all_models.Base.metadata.create_all(bind=engine)

            from app.db.session import SessionLocal
            from app.db.init_db import init_db
            db = SessionLocal()
            try:
                init_db(db)
            finally:
                db.close()
            logger.info("✅ AI Database: Synchronized.")
        except Exception as e:
            logger.error(f"❌ AI Database: Sync Failed: {e}")

        # 2. RAG Index & NLP Parser & Gemini Config (all singletons)
        logger.info("Initializing RAG Engine, NLP Models & Gemini in background...")
        try:
            # 1. RAG Index
            build_index()
            # 2. All singletons via AIModelManager (spaCy, Gemini config, embedding)
            from app.core.ai_model import AIModelManager
            AIModelManager.preload()
            logger.info("✅ All AI models pre-loaded (singleton).")
        except Exception as e:
            logger.warning(f"AI System: Preload warning: {e}")

    threading.Thread(target=preload_all, daemon=True).start()

    # ── Self-Ping Keep-Alive (prevents Render Free Tier from sleeping) ────────
    KEEP_ALIVE_URL = os.getenv("KEEP_ALIVE_URL", "")  # e.g. https://resume-analyzer-python-1.onrender.com
    KEEP_ALIVE_INTERVAL = int(os.getenv("KEEP_ALIVE_INTERVAL", "840"))  # 14 minutes

    if KEEP_ALIVE_URL:
        def self_ping():
            ping_url = KEEP_ALIVE_URL.rstrip("/") + "/ping"
            logger.info(f"🏓 Keep-alive enabled: pinging {ping_url} every {KEEP_ALIVE_INTERVAL}s")
            while True:
                time.sleep(KEEP_ALIVE_INTERVAL)
                try:
                    req = urllib.request.Request(ping_url, method="GET")
                    with urllib.request.urlopen(req, timeout=10) as resp:
                        logger.info(f"🏓 Keep-alive ping OK: {resp.status}")
                except Exception as e:
                    logger.warning(f"🏓 Keep-alive ping failed: {e}")

        threading.Thread(target=self_ping, daemon=True).start()
    else:
        logger.info("ℹ️ KEEP_ALIVE_URL not set. Self-ping disabled. "
                    "Set KEEP_ALIVE_URL env var to prevent Render sleep.")


app.include_router(api_router, prefix=settings.API_V1_STR)


# ── Lightweight ping (responds instantly, even during cold start) ─────────
@app.get("/ping")
def ping():
    """Ultra-lightweight liveness probe. No DB, no model checks."""
    return {"pong": True}


@app.get("/")
def health():
    return {"status": "running"}


@app.get("/healthz")
def health_check():
    """Enhanced health check with component readiness status."""
    import datetime
    from app.core.ai_model import AIModelManager

    # DB connectivity check
    db_healthy = False
    try:
        from app.db.session import SessionLocal
        from sqlalchemy import text
        db = SessionLocal()
        db.execute(text("SELECT 1"))
        db.close()
        db_healthy = True
    except Exception:
        pass

    components = {
        "api": "healthy",
        "database": db_healthy,
        "gemini_configured": AIModelManager._gemini_configured,
        "spacy_loaded": AIModelManager._spacy_nlp is not None,
        "rag_index": len(_role_names_check()) > 0,
    }
    all_healthy = all(v for v in components.values() if isinstance(v, bool))

    return {
        "status": "healthy" if all_healthy else "degraded",
        "timestamp": datetime.datetime.utcnow().isoformat(),
        "components": components,
    }


def _role_names_check():
    """Check if RAG index is built."""
    try:
        from app.career_engine.rag_engine import _role_names
        return _role_names
    except Exception:
        return []


if __name__ == "__main__":
    import uvicorn
    import os
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 8080)),
    )
