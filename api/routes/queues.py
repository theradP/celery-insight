from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func, case

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from db.models import Task
from api.dependencies import get_db

router = APIRouter()

@router.get("/")
def get_queues(db: Session = Depends(get_db)):
    """Get per-queue statistics derived from tasks table."""
    # Group tasks by queue_name and compute stats
    queue_stats = db.query(
        func.coalesce(Task.queue_name, "celery").label("queue_name"),
        func.count(Task.task_id).label("total_tasks"),
        func.count(case((Task.state.in_(["RECEIVED", "STARTED", "RETRY"]), 1))).label("pending_tasks"),
        func.count(case((Task.state == "SUCCESS", 1))).label("completed_tasks"),
        func.count(case((Task.state == "FAILURE", 1))).label("failed_tasks"),
        func.avg(Task.runtime).label("avg_runtime"),
    ).group_by(func.coalesce(Task.queue_name, "celery")).all()

    return [
        {
            "queue_name": row.queue_name or "celery",
            "total_tasks": row.total_tasks,
            "pending_tasks": row.pending_tasks,
            "completed_tasks": row.completed_tasks,
            "failed_tasks": row.failed_tasks,
            "avg_runtime": round(row.avg_runtime, 4) if row.avg_runtime else 0.0,
        }
        for row in queue_stats
    ]
