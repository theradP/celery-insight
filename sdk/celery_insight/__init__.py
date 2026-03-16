import logging

logger = logging.getLogger("celery_insight_sdk")

def enable_monitoring(celery_app):
    """
    Enables advanced Celery monitoring by ensuring the worker 
    is configured to send task-related events continuously.
    """
    try:
        # Enable task events to be sent to the broker
        celery_app.conf.worker_send_task_events = True
        
        # Enable events per task type (ensures full lifecycle is tracked)
        celery_app.conf.task_send_sent_event = True
        celery_app.conf.task_track_started = True
        
        logger.info("Celery Insight monitoring initialized successfully.")
    except Exception as e:
        logger.error(f"Failed to initialize Celery Insight monitoring: {e}")
