FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application source code
COPY . .

# Expose port
EXPOSE 8000

# Seed DB and launch FastAPI app
CMD ["sh", "-c", "python scripts/seed_db.py && uvicorn app.main:app --host 0.0.0.0 --port 8000"]
