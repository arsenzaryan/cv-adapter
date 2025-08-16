# --- Frontend build stage ---
FROM node:20-alpine AS frontend-builder
WORKDIR /app

# Copy package files first for better caching
COPY frontend/package.json frontend/package-lock.json* ./frontend/
WORKDIR /app/frontend

# Install dependencies (including dev dependencies for build)
RUN npm ci --silent

# Copy frontend source and build
COPY frontend/ ./
RUN npm run build

# --- Backend runtime stage ---
FROM python:3.11-slim AS runtime

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=8000

WORKDIR /app

# Install system dependencies
RUN apt-get update -y && apt-get install -y --no-install-recommends \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Copy and install Python dependencies
COPY backend/requirements.txt ./backend/requirements.txt
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r backend/requirements.txt

# Copy backend source code
COPY backend/ ./backend/

# Create static directory and copy built frontend
RUN mkdir -p ./backend/app/static
COPY --from=frontend-builder /app/frontend/dist/ ./backend/app/static/

# Set working directory to backend
WORKDIR /app/backend

# Expose port (Railway will set the PORT env var)
EXPOSE $PORT

# Use Railway's PORT environment variable with logging
CMD sh -c "echo 'Starting on port:' ${PORT:-8000} && uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000} --log-level info"