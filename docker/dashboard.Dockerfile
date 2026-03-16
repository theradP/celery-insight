FROM python:3.12-slim

WORKDIR /app
ENV PYTHONPATH=/app

RUN apt-get update && apt-get install -y unzip curl && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir reflex httpx

COPY dashboard /app

RUN reflex init

# Reflex initiates its own internal backend, typically 8000. 
# We'll run it explicitly. 
CMD ["sh", "-c", "reflex run ${REFLEX_ENV:+--env $REFLEX_ENV} --backend-port ${REFLEX_BACKEND_PORT:-8000} --backend-host ${REFLEX_BACKEND_HOST:-0.0.0.0}"]
