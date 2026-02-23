FROM python:3.10-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application source
COPY . .

# Expose port (Documentation only, Railway/Render use the PORT env var)
RUN python -m spacy download en_core_web_sm
EXPOSE 8000

# Run commands
CMD ["python", "main.py"]
