# ── ShieldAI – Backend API Only ───────────────────────────────────────────────
FROM python:3.11-slim

# Security: run as non-root user
RUN addgroup --system appgroup && adduser --system --ingroup appgroup appuser

WORKDIR /app

# Install dependencies first (Docker cache layer)
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy application source
COPY . .

# $PORT is injected by Render / Cloud Run at runtime (default 8000 locally)
ENV PORT=8000
EXPOSE 8000

USER appuser

CMD ["sh", "-c", "uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000}"]
