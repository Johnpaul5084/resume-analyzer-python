from sqlalchemy.orm import Session
from app.models.all_models import JobDescription
import csv
import os

def init_db(db: Session):
    # Check if we already have jobs
    if db.query(JobDescription).first():
        return

    csv_path = "data/job_listings.csv"
    if not os.path.exists(csv_path):
        print(f"Warning: {csv_path} not found. Skipping initial data seeding.")
        return

    print("Seeding database with job listings from CSV...")
    with open(csv_path, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            job = JobDescription(
                title=row['role'],
                company=row['company'],
                location=row['location'],
                salary_range=f"${row['salary_min']} - ${row['salary_max']}",
                posted_date=f"{row['posted_days_ago']} days ago",
                description_text=row['description'], # Using description as text
                required_skills=row['skills'].split(', ') # Parse skills list
            )
            db.add(job)
    
    db.commit()
    print("Database seeded successfully.")
