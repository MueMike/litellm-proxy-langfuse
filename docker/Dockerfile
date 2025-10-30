# Multi-stage Dockerfile for LiteLLM Proxy with LangFuse

# Build stage
FROM python:3.11-slim as builder

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir --user -r requirements.txt

# Runtime stage
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install runtime dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user first
RUN useradd -m -u 1000 litellm

# Copy Python dependencies from builder to litellm user's home
COPY --from=builder /root/.local /home/litellm/.local

# Copy application code
COPY src/ ./src/
COPY config/ ./config/
COPY pyproject.toml .

# Change ownership of all files
RUN chown -R litellm:litellm /app /home/litellm/.local

# Make sure scripts in .local are usable
ENV PATH=/home/litellm/.local/bin:$PATH

# Switch to non-root user
USER litellm

# Expose ports
EXPOSE 8000 9090

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Run the application
CMD ["python", "-m", "uvicorn", "src.proxy.server:create_app", "--factory", "--host", "0.0.0.0", "--port", "8000"]
