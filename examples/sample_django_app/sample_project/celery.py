import os
from celery import Celery
import sys

# Add the SDK path so this sample app can import it
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))
from sdk.celery_insight import enable_monitoring

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sample_project.settings')

app = Celery('sample_project')
app.config_from_object('django.conf:settings', namespace='CELERY')

enable_monitoring(app)

app.autodiscover_tasks()
