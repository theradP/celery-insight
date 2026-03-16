# Celery Insight — Developer Documentation

Welcome to the development guide for **Celery Insight**. This document provides an in-depth look at the system architecture, component responsibilities, and instructions on how to extend the platform for your own use cases.

---

## 🏗 Architecture Overview

Celery Insight follows a decoupled, event-driven architecture to ensure scalability and minimal impact on your production Celery workers.

```mermaid
graph TD
    subgraph "Production Environment"
        CW[Celery Worker + SDK] -- Events --> CB[Celery Broker (Redis)]
    end

    subgraph "Celery Insight Infrastructure"
        COL[Collector] -- Subscribes --> CB
        COL -- Publishes --> RS[Redis Stream]
        PROC[Processor] -- Consumes --> RS
        PROC -- Writes --> DB[(PostgreSQL / TimescaleDB)]
        API[FastAPI Server] -- Queries --> DB
        DASH[Reflex Dashboard] -- REST / WS --> API
    end
```

### Data Flow
1.  **Instrumentation**: The SDK enables `worker_send_task_events` on your Celery app.
2.  **Collection**: The **Collector** listens to the broker's event broadcast and pushes normalized payloads into a **Redis Stream**.
3.  **Processing**: The **Processor** consumes the stream, maintains worker state, and persists task lifecycles to **PostgreSQL**.
4.  **Presentation**: The **API** provides structured access to the data, which the **Reflex Dashboard** visualizes.

---

## 🧩 Component Breakdown

### 1. SDK (`sdk/`)
A lightweight wrapper that configures standard Celery settings.
- **Key Logic**: Sets `task_track_started = True` and `worker_send_task_events = True`.
- **Extension**: If you need to capture custom metadata, you would extend the `enable_monitoring` function to inject custom signal handlers (e.g., `before_task_publish`).

### 2. Collector (`collector/`)
A standalone Python process using Celery's `Receiver`.
- **Responsibility**: It acts as a bridge. It converts ephemeral Celery events into a persistent Redis Stream.
- **Normalization**: Standardizes fields like `task_id`, `worker_hostname`, and `timestamp`.

### 3. Processor (`processor/`)
The "brain" of the system.
- **Consumer Group**: Uses Redis Consumer Groups (`xreadgroup`) to ensure idempotent processing and horizontal scalability.
- **State Machine**: Approximates the task lifecycle (Received -> Started -> Success/Failure) and calculates runtimes.

### 4. API (`api/`)
A FastAPI application serving as the data abstraction layer.
- **Structure**: Modular routes in `api/routes/` (Tasks, Workers, Metrics).
- **Extensibility**: Add new endpoints here to expose deep-dive analytics or custom filters.

### 5. Dashboard (`dashboard/`)
Built with [Reflex](https://reflex.dev), a pure Python frontend framework.
- **State management**: `AppState` in `state.py` handles background data fetching.
- **Modern UI**: Uses custom CSS in `assets/` and premium components.

---

## 🚀 How to Add New Functionality

### Example: Adding a "P95 Wait Time" Metric

#### Step 1: Update Database Schema
Modify `db/models.py` to include new fields if persistent tracking is required, or add a new aggregation model.
```python
class QueueMetric(Base):
    # ... existing fields
    p95_wait_time = Column(Float, nullable=True)
```

#### Step 2: Update the Processor
Modify `processor/main.py` to calculate the new metric during the event loop.
```python
# In the task-started handler:
wait_time = (started_at - received_at).total_seconds()
# logic to calculate P95 and update DB...
```

#### Step 3: Expose via API
Add a new field to the Pydantic schemas and update the route in `api/routes/metrics.py`.
```python
@router.get("/overview")
def get_overview(db: Session = Depends(get_db)):
    # ... aggregation logic
    return {"p95_wait_time": 1.2, ...}
```

#### Step 4: Update the Dashboard
1.  Update `AppState` in `dashboard/celery_insight/state.py` to include the new field in `overview_data`.
2.  Add a new `stat_card` to `dashboard/celery_insight/pages/index.py`.

---

## 🛠 Local Development Workflow

### environment Setup
We recommend using **Docker Compose** for the full stack.

```bash
# Start all services
docker-compose up -d

# View logs for a specific component
docker-compose logs -f processor

# Rebuild a component after code changes
docker-compose up -d --build dashboard
```

### Debugging Tips
- **Redis Inspection**: Use `docker exec -it celery-insights_redis_1 redis-cli` then `XREAD STREAMS celery-events 0` to see raw events.
- **Database Inspection**: Use any Postgres client to connect to `localhost:5432` (User: `celery_insight`, Pass: `secretpassword`).
- **Reflex Dev Mode**: For faster UI iteration, use `reflex run` locally if you have the environment configured.

---

## ⚡️ Best Practices
- **Idempotency**: Always ensure the Processor can handle duplicate events (common in distributed systems).
- **Async API**: Use `httpx.AsyncClient` in the Reflex dashboard to prevent UI blocking.
- **Non-blocking Processors**: Keep the Processor loop fast. For heavy analytical queries, use background database views or Materialized Views.
