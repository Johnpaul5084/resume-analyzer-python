from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.api import api_router
from app.core.config import settings
from app.db.session import engine
from app.models import all_models # Ensure models are registered

# Create Tables (Simple approach for MVP, use Alembic for Prod)
all_models.Base.metadata.create_all(bind=engine)

# Seed Database
from app.db.session import SessionLocal
from app.db.init_db import init_db
db = SessionLocal()
try:
    init_db(db)
except Exception as e:
    print(f"Error seeding database: {e}")
finally:
    db.close()

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    description="Backend for Resume Analyzer with ATS Scoring, Job Matching, and AI Rewriting."
)

# Set all CORS enabled origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix=settings.API_V1_STR)

@app.get("/")
def root():
    return {"message": "Welcome to Resume Analyzer AI API. Visit /docs for Swagger UI."}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
