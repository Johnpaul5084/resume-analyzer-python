FROM python:3.10-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application source
COPY . .

# Expose port
EXPOSE 8000

# Run commands
CMD ["gunicorn", "-k", "uvicorn.workers.UvicornWorker", "-w", "2", "app.main:app", "--bind", "0.0.0.0:8000"]
