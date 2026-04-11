FROM python:3.11-slim

# Metadata
LABEL maintainer="marib-hackathon"
LABEL description="EmailTriage OpenEnv — email triage environment for AI agents"
LABEL version="1.0.0"

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY server/ ./server/
COPY openenv.yaml .

# HuggingFace Spaces uses port 7860
EXPOSE 7860

# Health check so orchestrators know when we're ready
HEALTHCHECK --interval=10s --timeout=5s --start-period=15s --retries=3 \
    CMD curl -f http://localhost:7860/health || exit 1

# Run with uvicorn; single worker is fine for this stateful single-session env
CMD ["uvicorn", "server.main:app", \
     "--host", "0.0.0.0", \
     "--port", "7860", \
     "--workers", "1", \
     "--log-level", "info"]
