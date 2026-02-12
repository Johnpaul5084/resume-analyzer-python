import requests
import json

BASE_URL = "http://localhost:8000/api/v1/jobs"

def test_recommendations():
    # We need a resume ID first, or just check if it allows us to hit the endpoint.
    # The endpoint is /recommendations/{resume_id}.
    # We can try to hit /jobs/ endpoint (create job) or just assume if backend is up it's fine.
    # But let's verify if the seeding worked, by checking if the DB has jobs.
    # Currently we don't have a GET all jobs endpoint exposed.
    # We can rely on the fact that if we upload a resume, we get recommendations.
    
    # Or simpler: let's query the DB directly using sqlite3 to see if jobs are there.
    import sqlite3
    try:
        conn = sqlite3.connect("resume-analyzer-backend/resume_analyzer.db")
        cursor = conn.cursor()
        cursor.execute("SELECT count(*) FROM job_descriptions")
        count = cursor.fetchone()[0]
        print(f"Job descriptions count in DB: {count}")
        
        cursor.execute("SELECT title, company, location, salary_range FROM job_descriptions LIMIT 1")
        row = cursor.fetchone()
        print(f"Sample job: {row}")
        
        conn.close()
    except Exception as e:
        print(f"Error checking DB: {e}")

if __name__ == "__main__":
    test_recommendations()
