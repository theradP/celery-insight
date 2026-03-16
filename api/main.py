from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routes import tasks, workers, metrics, queues

app = FastAPI(title="Celery Insight API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(tasks.router, prefix="/tasks", tags=["Tasks"])
app.include_router(workers.router, prefix="/workers", tags=["Workers"])
app.include_router(metrics.router, prefix="/metrics", tags=["Metrics"])
app.include_router(queues.router, prefix="/queues", tags=["Queues"])

@app.get("/health")
def health_check():
    return {"status": "healthy"}
