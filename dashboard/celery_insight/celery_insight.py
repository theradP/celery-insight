import reflex as rx
from celery_insight.pages.index import index
from celery_insight.pages.tasks import tasks
from celery_insight.pages.workers import workers
from celery_insight.pages.task_detail import task_detail
from celery_insight.pages.queues import queues

# The App instance - dark theme via Radix + custom stylesheet
app = rx.App(
    theme=rx.theme(
        appearance="dark",
        has_background=True,
        radius="medium",
        accent_color="blue",
        gray_color="slate",
    ),
    stylesheets=[
        "https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap",
        "/celery_insight.css",
    ],
)
