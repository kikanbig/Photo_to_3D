# Lightweight Dockerfile for Railway deployment
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements-ultra-minimal.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements-ultra-minimal.txt

# Copy application code
COPY . .

# Expose port
EXPOSE $PORT

# Start command
CMD uvicorn app.main:app --host 0.0.0.0 --port $PORT --workers 1
