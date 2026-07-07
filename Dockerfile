# ── Stage 1: Build the React frontend ─────────────────────────────────────────
FROM node:20-alpine AS frontend-build

WORKDIR /app/frontend

# Install dependencies (cache layer)
COPY frontend/package.json frontend/package-lock.json ./
RUN npm ci --silent

# Copy source and build
COPY frontend/ ./
# Inject the API URL at build time (override with --build-arg or env on Render)
ARG REACT_APP_API_URL=http://localhost:8000
ENV REACT_APP_API_URL=$REACT_APP_API_URL
RUN npm run build

# ── Stage 2: FastAPI backend (serves API + static frontend) ────────────────────
FROM python:3.11-slim AS backend

# Security: run as non-root
RUN addgroup --system appgroup && adduser --system --ingroup appgroup appuser

WORKDIR /app

# Install Python dependencies
COPY backend/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend source
COPY backend/ ./

# Copy built frontend into a 'static' folder so FastAPI can serve it
COPY --from=frontend-build /app/frontend/build ./static

# Expose the port Render / Cloud Run injects via $PORT (default 8000 locally)
ENV PORT=8000
EXPOSE 8000

# Switch to non-root user
USER appuser

# Start uvicorn; $PORT is supplied by the runtime
CMD ["sh", "-c", "uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000}"]
