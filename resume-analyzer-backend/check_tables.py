from dotenv import load_dotenv
load_dotenv()
import os
from sqlalchemy import create_engine, text

engine = create_engine(os.getenv('DATABASE_URL'))
with engine.connect() as conn:
    result = conn.execute(text("SELECT table_name FROM information_schema.tables WHERE table_schema='public' ORDER BY table_name"))
    tables = [row[0] for row in result]
    if tables:
        print("Tables in Supabase:")
        for t in tables:
            print(f"  ✅ {t}")
    else:
        print("No tables found yet.")
