# docker/api/Dockerfile
FROM python:3.10-slim as builder

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install uv
RUN curl -sL https://github.com/astral-sh/uv/releases/download/0.1.25/uv-installer.sh | bash

# Copy requirements
COPY pyproject.toml uvproject.toml ./

# Install dependencies
RUN uv pip install --no-cache-dir -e .

# Second stage for a smaller final image
FROM python:3.10-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Oracle client (if needed)
# RUN apt-get update && apt-get install -y --no-install-recommends \
#     libaio1 \
#     && rm -rf /var/lib/apt/lists/*
# COPY --from=builder /app/oracle-instantclient/ /usr/lib/oracle/

# Copy the dependencies from the builder stage
COPY --from=builder /usr/local/lib/python3.10/site-packages/ /usr/local/lib/python3.10/site-packages/
COPY --from=builder /usr/local/bin/ /usr/local/bin/

# Set environment variables
ENV PYTHONPATH=/app
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Copy project
COPY . .

# Create log directory
RUN mkdir -p /var/log/app

# Expose port
EXPOSE 8000

# Set entry point
CMD ["gunicorn", "app.main:app", "-k", "uvicorn.workers.UvicornWorker", "-b", "0.0.0.0:8000", "--workers", "4", "--access-logfile", "-"]

