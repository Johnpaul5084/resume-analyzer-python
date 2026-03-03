from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from app.core.config import settings

SQLALCHEMY_DATABASE_URL = settings.database_url

# SQLite requires check_same_thread=False for FastAPI
if SQLALCHEMY_DATABASE_URL.startswith("sqlite"):
    connect_args = {"check_same_thread": False}
    engine = create_engine(
        SQLALCHEMY_DATABASE_URL,
        pool_pre_ping=True,
        connect_args=connect_args,
    )
else:
    # Production: PostgreSQL / MySQL — configure connection pooling
    engine = create_engine(
        SQLALCHEMY_DATABASE_URL,
        pool_pre_ping=True,      # Verify connections before reuse
        pool_size=5,             # Maintain 5 connections in pool
        max_overflow=10,         # Allow up to 10 extra under burst
        pool_recycle=1800,       # Recycle connections every 30 min
        pool_timeout=30,         # Wait 30s for available connection
    )

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
