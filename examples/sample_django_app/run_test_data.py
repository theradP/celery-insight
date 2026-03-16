import os
import time
import random

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sample_project.settings')
import django
django.setup()

from tasks.tasks import process_data, unstable_api_call, heavy_computation

print("Starting test task generator...")

while True:
    # Trigger a mix of tasks
    
    # Fast successful tasks
    for _ in range(random.randint(2, 5)):
        process_data.delay(random.randint(100, 999))
        
    # Unstable tasks that might fail/retry
    if random.random() < 0.3:
        unstable_api_call.delay()
        
    # Slow tasks
    if random.random() < 0.1:
        heavy_computation.delay()
        
    time.sleep(random.uniform(0.5, 2.0))
