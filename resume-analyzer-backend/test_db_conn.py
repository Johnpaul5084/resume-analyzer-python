import os
import sys
from dotenv import load_dotenv

load_dotenv()
url = os.getenv("DATABASE_URL", "NOT_SET")
print(f"URL (first 70 chars): {url[:70]}...")

try:
    from sqlalchemy import create_engine, text
    engine = create_engine(url, pool_pre_ping=True, pool_timeout=10)
    with engine.connect() as conn:
        result = conn.execute(text("SELECT version()"))
        print("SUCCESS:", result.fetchone()[0][:60])
except Exception as e:
    err = str(e)
    # Write full error to file
    with open("db_error.txt", "w") as f:
        f.write(err)
    print("FAILED - check db_error.txt for full error")
    # Print first 500 chars
    print("Error preview:", err[:500])
