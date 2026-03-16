import os
import json
import time
import logging
from datetime import datetime, timezone
import redis
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from db.models import Base, Task, TaskEvent, Worker

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("celery_processor")

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://celery_insight:secretpassword@localhost:5432/celery_insight_db")
REDIS_URL = os.getenv("REDIS_STREAM_URL", "redis://localhost:6379/0")
STREAM_NAME = "celery-events"
GROUP_NAME = "processor_group"
CONSUMER_NAME = "processor_1"

# Database Setup
engine = create_engine(DATABASE_URL)
Base.metadata.create_all(bind=engine)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Redis Setup
try:
    r = redis.from_url(REDIS_URL)
    # Create consumer group if it doesn't exist
    try:
        r.xgroup_create(STREAM_NAME, GROUP_NAME, mkstream=True)
        logger.info(f"Created consumer group {GROUP_NAME} for stream {STREAM_NAME}")
    except redis.exceptions.ResponseError as e:
        if "BUSYGROUP" not in str(e):
            raise
except Exception as e:
    logger.error(f"Failed to connect to Redis: {e}")
    exit(1)

def process_events():
    db = SessionLocal()
    try:
        while True:
            # Read from stream (block for 2 seconds)
            events = r.xreadgroup(GROUP_NAME, CONSUMER_NAME, {STREAM_NAME: ">"}, count=100, block=2000)
            
            if not events:
                continue

            for stream, messages in events:
                for message_id, payload in messages:
                    # 'payload' is dict of bytes to bytes
                    event_type = payload.get(b'type', b'').decode('utf-8')
                    try:
                        raw_data = json.loads(payload.get(b'data', b'{}').decode('utf-8'))
                        normalized = json.loads(payload.get(b'normalized', b'{}').decode('utf-8'))
                    except Exception as parse_e:
                        logger.error(f"Failed to parse JSON for message {message_id}: {parse_e}")
                        r.xack(STREAM_NAME, GROUP_NAME, message_id)
                        continue

                    # 1. Save raw event
                    task_id = normalized.get("task_id")
                    if task_id:
                        db_event = TaskEvent(
                            task_id=task_id,
                            event_type=event_type,
                            timestamp=datetime.fromtimestamp(normalized.get("timestamp"), tz=timezone.utc),
                            metadata_json=raw_data
                        )
                        db.add(db_event)

                    # 2. Update Worker State
                    worker_id = normalized.get("worker")
                    if worker_id:
                        worker = db.query(Worker).filter(Worker.worker_id == worker_id).first()
                        if not worker:
                            worker = Worker(worker_id=worker_id, hostname=worker_id, status="online")
                            db.add(worker)
                        
                        worker.last_heartbeat = datetime.now(timezone.utc)
                        # Heartbeat metrics update (if available)
                        if event_type == "worker-heartbeat":
                            worker.status = "online"
                            worker.active_tasks = raw_data.get('active', 0)
                        elif event_type == "worker-offline":
                            worker.status = "offline"

                    # 3. Update Task State
                    if task_id:
                        task = db.query(Task).filter(Task.task_id == task_id).first()
                        if not task:
                            task = Task(
                                task_id=task_id, 
                                task_name=normalized.get("task_name"),
                                worker_id=worker_id
                            )
                            db.add(task)

                        task.state = getattr(task, 'state', None) # Current state
                        # Simple state machine approximation
                        if event_type == "task-received":
                            task.received_at = datetime.fromtimestamp(normalized.get("timestamp"), tz=timezone.utc)
                            task.state = "RECEIVED"
                            task.task_name = normalized.get("task_name") # Often full info is here
                        elif event_type == "task-started":
                            task.started_at = datetime.fromtimestamp(normalized.get("timestamp"), tz=timezone.utc)
                            task.state = "STARTED"
                        elif event_type == "task-succeeded":
                            task.completed_at = datetime.fromtimestamp(normalized.get("timestamp"), tz=timezone.utc)
                            task.state = "SUCCESS"
                            task.runtime = raw_data.get("runtime")
                        elif event_type == "task-failed":
                            task.completed_at = datetime.fromtimestamp(normalized.get("timestamp"), tz=timezone.utc)
                            task.state = "FAILURE"
                            task.exception = raw_data.get("exception")
                        elif event_type == "task-retried":
                            task.state = "RETRY"
                            task.retries = (task.retries or 0) + 1
                            task.exception = raw_data.get("exception")

                    # Commit chunk and ack
                    db.commit()
                    r.xack(STREAM_NAME, GROUP_NAME, message_id)
                    
    except Exception as e:
        logger.error(f"Processor loop error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    logger.info("Starting Redis Stream Processor...")
    # Small delay to ensure DB is up during docker-compose start
    time.sleep(5)
    process_events()
