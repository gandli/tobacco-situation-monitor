# TSM - Tobacco Situation Monitor
# Multi-stage Docker build for optimized production image

# =====================
# Build stage
# =====================
FROM python:3.12-slim AS builder

WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Create virtual environment
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Install dependencies
COPY pyproject.toml .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir .

# =====================
# Production stage
# =====================
FROM python:3.12-slim AS production

WORKDIR /app

# Create non-root user for security
RUN groupadd --gid 1000 tsm && \
    useradd --uid 1000 --gid tsm --shell /bin/bash --create-home tsm

# Copy virtual environment from builder
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copy application code
COPY --chown=tsm:tsm . .

# Create necessary directories
RUN mkdir -p /app/data /app/logs && \
    chown -R tsm:tsm /app/data /app/logs

# Switch to non-root user
USER tsm

# Environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    TSM_DATABASE_PATH=/app/data/tsm.db \
    TSM_LOG_FILE=/app/logs/tsm.log

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health/')" || exit 1

# Run the application
CMD ["uvicorn", "tsm.main:app", "--host", "0.0.0.0", "--port", "8000"]