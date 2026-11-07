# Multi-stage / lightweight Python 3.10 slim runtime
FROM python:3.10-slim

# Prevent Python from writing .pyc files and enable unbuffered logging
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app

WORKDIR /app

# Install minimal OS dependencies required for FAISS and healthcheck
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy backend requirements and install dependencies cleanly
COPY requirements-docker.txt requirements.txt
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy backend application source code
COPY backend/ ./backend/

# Ensure required runtime directories exist for host volume mounts
RUN mkdir -p /app/data /app/storage/db

# Expose FastAPI default port
EXPOSE 8000

# Healthcheck to verify the FastAPI server is responsive
HEALTHCHECK --interval=30s --timeout=10s --retries=3 --start-period=10s \
    CMD curl -f http://localhost:8000/docs || exit 1

# Launch FastAPI ASGI server with Uvicorn
CMD ["uvicorn", "backend.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
