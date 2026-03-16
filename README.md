# Celery Insight

Production-grade observability platform for Celery clusters.

> "Flower shows what is happening. Celery Insight shows why."

## Features
- Real-time task timelines
- Distributed worker health monitoring
- Queue throughput and latency
- Retry pattern detection and failure analysis
- Built 100% in Python (FastAPI backend + Reflex frontend)

## Architecture

1. **Celery Event Broker** (e.g., Redis)
2. **Collector**: Subscribes to Celery events and pushes to a Redis Stream buffer.
3. **Processor**: Consumes the Redis Stream, calculates metrics, and updates PostgreSQL.
4. **API**: Standalone FastAPI server providing REST endpoints for tasks, workers, and metrics.
5. **Dashboard**: Reflex-based frontend client that queries the API.

## Quickstart (Development)

1. **Start the Infrastructure**
   ```bash
   docker-compose up --build
   ```

2. **Access the Dashboard**
   Navigate to `http://localhost:3000` in your browser.

3. **Access the API Docs**
   Navigate to `http://localhost:8000/docs` in your browser.

## Running the Sample Application

To generate test data, you can run the included dummy Django project.

**Terminal 1: Start the sample Celery worker**
```bash
cd examples/sample_django_app
# On Windows, add -P solo to avoid multiprocessing issues:
celery -A sample_project worker -l INFO -P solo
# On Linux/macOS:
# celery -A sample_project worker -l INFO
```

**Terminal 2: Run the test data generator**
```bash
cd examples/sample_django_app
python run_test_data.py
```

Watch the dashboard update in real-time!
