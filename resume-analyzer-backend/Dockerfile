FROM python:3.10-slim

WORKDIR /app

# Install system dependencies (needed for spacy and other heavy libs)
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install dependencies
COPY requirements.txt .
RUN pip install --upgrade pip setuptools wheel
RUN pip install --no-cache-dir -r requirements.txt

# Download spacy model
RUN python -m spacy download en_core_web_sm

# Copy application source
COPY . .

# Expose port
EXPOSE 10000

# Run commands
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "10000"]
