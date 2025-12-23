# Multi-stage build for Semantic Mapper Backend

# ===== Builder Stage =====
FROM python:3.11-slim as builder

# Set working directory
WORKDIR /build

# Install system dependencies for building Python packages
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    make \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy dependency files
COPY backend/requirements.txt /build/backend/requirements.txt
COPY pyproject.toml /build/pyproject.toml
COPY src/ /build/src/

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip setuptools wheel && \
    pip install --no-cache-dir -r /build/backend/requirements.txt && \
    pip install --no-cache-dir -e /build

# ===== Runtime Stage =====
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install runtime system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy Python packages from builder
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy application code
COPY backend/ /app/backend/
COPY src/ /app/src/

# Create storage directory for uploaded files
RUN mkdir -p /app/storage/uploads && \
    chmod -R 755 /app/storage

# Set Python path to include both backend and src
ENV PYTHONPATH="/app:/app/backend:/app/src:${PYTHONPATH}"
ENV PYTHONUNBUFFERED=1

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8000/api/health || exit 1

# Run the application
CMD ["uvicorn", "backend.api.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
