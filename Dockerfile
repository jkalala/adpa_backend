# Use Python 3.9 as base image
FROM python:3.9-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    DEBIAN_FRONTEND=noninteractive

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        build-essential \
        python3-dev \
        libpq-dev \
        netcat-traditional \
        postgresql-client \
        dnsutils \
        iputils-ping \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first to leverage Docker cache
COPY ./adpa_backend/requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt && \
    pip install --no-cache-dir django-filter==23.5  # Add explicit installation

# Copy the entrypoint script
COPY ./adpa_backend/docker-entrypoint.sh .
RUN chmod +x docker-entrypoint.sh

# Copy the project files
COPY ./adpa_backend .

# Run entrypoint script
ENTRYPOINT ["./docker-entrypoint.sh"] 