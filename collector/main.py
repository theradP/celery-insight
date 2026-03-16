import os
import json
import logging
from celery import Celery
import redis

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("celery_collector")

broker_url = os.getenv("CELERY_BROKER_URL", "redis://localhost:6379/0")
redis_url = os.getenv("REDIS_STREAM_URL", "redis://localhost:6379/0")
stream_name = "celery-events"

try:
    r = redis.from_url(redis_url)
except Exception as e:
    logger.error(f"Could not connect to Redis for stream writing: {e}")
    exit(1)

def on_event(event):
    """Normalize and push Celery events to Redis Streams."""
    try:
        # Standardize the structure slightly 
        event_dict = dict(event)
        
        # Ensure timestamp exists
        if 'timestamp' not in event_dict:
            import time
            event_dict['timestamp'] = time.time()
            
        event_type = event_dict.get('type')
        if not event_type:
            return
            
        # Basic normalization for standard fields
        normalized = {
            "event_type": event_type,
            "task_id": event_dict.get('uuid', ''),
            "task_name": event_dict.get('name', ''),
            "worker": event_dict.get('hostname', ''),
            "timestamp": event_dict.get('timestamp', 0)
        }
        
        # Keep the full payload as metadata JSON
        payload = {
            "type": event_type,
            "data": json.dumps(event_dict),
            "normalized": json.dumps(normalized)
        }

        # Publish to Redis Stream
        message_id = r.xadd(stream_name, payload)
        logger.debug(f"Pushed {event_type} to stream '{stream_name}' with id {message_id}")
        
    except Exception as e:
        logger.error(f"Error processing event: {e}")

def start_collector():
    logger.info(f"Connecting to Celery Broker at {broker_url}...")
    app = Celery(broker_url=broker_url)

    with app.connection() as connection:
        logger.info("Connected. Starting event listener...")
        recv = app.events.Receiver(connection, handlers={
            '*': on_event, # Catch all events
        })
        recv.capture(limit=None, timeout=None, wakeup=True)

if __name__ == "__main__":
    start_collector()
