from celery import shared_task
import time
import random

@shared_task
def process_data(data_id):
    """A task that typically succeeds but takes variable time."""
    time_to_sleep = random.uniform(0.5, 3.0)
    time.sleep(time_to_sleep)
    return f"Processed {data_id} in {time_to_sleep:.2f}s"

@shared_task(bind=True, max_retries=3)
def unstable_api_call(self):
    """A task that fails often to demonstrate retries and failures."""
    time.sleep(1)
    if random.random() < 0.7:  # 70% chance to fail
        try:
            raise Exception("API Connection Timeout")
        except Exception as exc:
            raise self.retry(exc=exc, countdown=2)
    return "API Call Succeeded!"

@shared_task
def heavy_computation():
    """A long running task to show up as 'Started' or in progress."""
    time.sleep(10)
    return "Computation Complete"
