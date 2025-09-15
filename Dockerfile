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
COPY requirements-asgi.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements-asgi.txt

# Copy application code
COPY . .

# Expose port
EXPOSE $PORT

# Start command
CMD uvicorn asgi_app:app --host 0.0.0.0 --port $PORT --workers 1
