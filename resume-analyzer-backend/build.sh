#!/usr/bin/env bash
# Exit on error
set -o errexit

# Install python requirements
pip install --upgrade pip
pip install -r requirements.txt

# Download NLP models (required for analyzing roles/matching)
python -m spacy download en_core_web_sm

# Initialize database (creates app.db if it doesn't exist)
# python -c "from app.db.base import Base; from app.db.session import engine; Base.metadata.create_all(bind=engine)"
# Actually backend autoloads it, so no need for explicit create unless using alembic
