import os
from pathlib import Path
from dotenv import load_dotenv

# Force load .env from backend root (one level up from app/)
env_path = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.api import api_router
from app.core.config import settings
from app.middleware.security import AISecurityMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from app.db.session import engine # AI Resume Analyzer - v1.0.1-stable
import logging
from app.models import all_models # Ensure models are registered

from app.career_engine.rag_engine import build_index
import threading

limiter = Limiter(key_func=get_remote_address)
app = FastAPI(
    title="AI Resume Analyzer",
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    description="AI Resume Analyzer - Intelligent Resume & Career Intelligence Platform."
)

# System Diagnostic: Ensure AI Engine has a pulse
if not os.getenv("GEMINI_API_KEY"):
    raise RuntimeError("❌ AI Neural Error: GEMINI_API_KEY not configured properly in .env")
else:
    print("✅ AI Neural Link: GEMINI_API_KEY Loaded")
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Global Security Layer
app.add_middleware(AISecurityMiddleware)

@app.on_event("startup")
def startup_event():
    # Build RAG Index & Preload Models in Background to avoid blocking Cold Start
    def preload_all():
        # 1. Database Initialization (Moved to background to avoid blocking Startup)
        try:
            print("AI System: Verifying Neural Database in background...")
            all_models.Base.metadata.create_all(bind=engine)
            
            from app.db.session import SessionLocal
            from app.db.init_db import init_db
            db = SessionLocal()
            try:
                init_db(db)
            finally:
                db.close()
            print("✅ AI Database: Synchronized.")
        except Exception as e:
            print(f"❌ AI Database: Sync Failed: {e}")

        # 2. RAG Index & NLP Parser
        print("AI System: Initializing RAG Engine & NLP Models in background...")
        try:
            # 1. RAG Index
            build_index()
            # 2. NLP Parser (loads spaCy)
            from app.services.ai_parser_service import AIParserService
            AIParserService.get_nlp()
            print("AI System: Neural Link Synchronized.")
        except Exception as e:
            print(f"AI System: Preload warning: {e}")

    threading.Thread(target=preload_all, daemon=True).start()

# Set all CORS enabled origins
# Include common Vite ports (5173) and local variants
origins = [
    "https://resume-analyzer-python.vercel.app",
    "https://resume-analyzer-frontend-blond.vercel.app",
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:3000",
    "http://127.0.0.1:3000",
] + settings.BACKEND_CORS_ORIGINS

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix=settings.API_V1_STR)

@app.get("/")
def health():
    return {"status": "running"}

@app.get("/healthz")
def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    import os
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 8080))
    )
