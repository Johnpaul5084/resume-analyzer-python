"""
Supabase Migration Script - Phoenix Upgrade
Runs all table creations in your Supabase PostgreSQL database.
Run this ONCE after setting DATABASE_URL in your .env file.
"""

import os
from dotenv import load_dotenv

# Load .env
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    print("❌ ERROR: DATABASE_URL not found in .env file!")
    print("📖 Follow SUPABASE_SETUP.md to get your connection string.")
    exit(1)

if "sqlite" in DATABASE_URL:
    print("⚠️  WARNING: You are still using SQLite, not Supabase.")
    print("📖 Update DATABASE_URL in .env with your Supabase connection string.")
    exit(1)

print("🔗 Connecting to Supabase PostgreSQL...")
print(f"   URL: {DATABASE_URL[:50]}...")

try:
    from sqlalchemy import create_engine, text
    from sqlalchemy.orm import sessionmaker

    engine = create_engine(DATABASE_URL, pool_pre_ping=True)

    # Test connection
    with engine.connect() as conn:
        result = conn.execute(text("SELECT version()"))
        version = result.fetchone()[0]
        print(f"✅ Connected! PostgreSQL version: {version[:50]}")

    # Import all models - this creates tables via SQLAlchemy
    print("\n📦 Creating tables...")

    from app.db.base import Base
    from app.models import all_models  # Register all models

    Base.metadata.create_all(bind=engine)
    print("✅ Tables created successfully!")

    # Verify tables
    with engine.connect() as conn:
        result = conn.execute(text("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
            ORDER BY table_name
        """))
        tables = [row[0] for row in result]
        print(f"\n✅ Tables in Supabase: {', '.join(tables)}")

    # Seed initial data
    print("\n🌱 Seeding initial data...")
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    try:
        from app.db.init_db import init_db
        init_db(db)
        print("✅ Initial data seeded!")
    except Exception as e:
        print(f"⚠️  Seeding skipped (may already exist): {e}")
    finally:
        db.close()

    print("\n🎉 SUPABASE MIGRATION COMPLETE!")
    print("🚀 Your database is now live on Supabase (Free, Never Expires)")
    print("\n📋 Next Steps:")
    print("   1. Run: python -m uvicorn app.main:app --reload")
    print("   2. Test at: http://127.0.0.1:8000/docs")
    print("   3. Deploy to Render with the same DATABASE_URL env variable")

except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Run: pip install -r requirements.txt")
except Exception as e:
    print(f"❌ Migration failed: {e}")
    print("\n🔧 Troubleshoot:")
    print("   1. Check your DATABASE_URL is correct in .env")
    print("   2. Make sure your Supabase project is active")
    print("   3. Check your internet connection")
