import reflex as rx
import os

config = rx.Config(
    app_name="celery_insight",
    telemetry_enabled=False,
    backend_port=8000,
    backend_host="0.0.0.0",
    disable_plugins=["reflex.plugins.sitemap.SitemapPlugin"],
    api_url="http://localhost:8888",
    cors_allowed_origins=["*"],
)
