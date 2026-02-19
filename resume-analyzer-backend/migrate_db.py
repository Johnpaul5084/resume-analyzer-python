import sqlite3
import os

db_path = "resume_analyzer.db"
if os.path.exists(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        cursor.execute("ALTER TABLE resumes ADD COLUMN analysis TEXT;")
    except Exception as e:
        print(f"analysis column: {e}")
        
    try:
        cursor.execute("ALTER TABLE resumes ADD COLUMN suggestions JSON;")
    except Exception as e:
        print(f"suggestions column: {e}")
        
    try:
        cursor.execute("ALTER TABLE resumes ADD COLUMN key_strengths JSON;")
    except Exception as e:
        print(f"key_strengths column: {e}")
        
    try:
        cursor.execute("ALTER TABLE resumes ADD COLUMN market_readiness FLOAT DEFAULT 85.0;")
    except Exception as e:
        print(f"market_readiness column: {e}")
        
    conn.commit()
    conn.close()
    print("Database schema updated successfully.")
else:
    print("Database file not found. Re-run app to create it.")
