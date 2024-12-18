# Use Python 3.11 slim image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install system dependencies
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        build-essential \
        curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements file
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code and tests
COPY src/ src/
COPY test/ test/

# Create and use non-root user
RUN useradd -m -s /bin/bash app \
    && chown -R app:app /app
USER app

# Set Python path
ENV PYTHONPATH=/app

# Expose port
EXPOSE 8080

# Default command for service
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8080"]