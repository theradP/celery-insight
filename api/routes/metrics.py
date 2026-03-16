from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from db.models import Task, Worker
from api.dependencies import get_db

router = APIRouter()

@router.get("/overview")
def get_overview(db: Session = Depends(get_db)):
    # Calculate simple high-level stats for the dashboard widgets
    active_workers = db.query(Worker).filter(Worker.status == "online").count()
    failed_tasks = db.query(Task).filter(Task.state == "FAILURE").count()
    total_tasks = db.query(Task).count()
    
    # Very basic queue proxy: just active tasks
    queue_backlog = db.query(Task).filter(
        Task.state.in_(["RECEIVED", "STARTED", "RETRY"])
    ).count()
    
    avg_runtime = db.query(func.avg(Task.runtime)).filter(Task.runtime.is_not(None)).scalar() or 0.0
    
    return {
        "active_workers": active_workers,
        "failed_tasks": failed_tasks,
        "total_tasks": total_tasks,
        "queue_backlog": queue_backlog,
        "avg_runtime": round(avg_runtime, 4)
    }

@router.get("/throughput")
def get_throughput(range: str = "30m", db: Session = Depends(get_db)):
    from datetime import datetime, timedelta
    
    # Define range and granularity
    if range == "1h":
        delta = timedelta(hours=1)
        trunc = "minute"
    elif range == "24h":
        delta = timedelta(days=1)
        trunc = "hour"
    elif range == "7d":
        delta = timedelta(days=7)
        trunc = "day"
    else: # Default 30m
        delta = timedelta(minutes=30)
        trunc = "minute"
        
    cutoff = datetime.utcnow() - delta
    
    # Use explicit expression for grouping
    minute_trunc = func.date_trunc(trunc, Task.received_at)
    
    stats = db.query(
        minute_trunc.label('minute'),
        func.count(Task.task_id).label('count')
    ).filter(
        Task.received_at >= cutoff
    ).group_by(
        minute_trunc
    ).order_by(
        minute_trunc
    ).all()
    
    return [
        {"timestamp": row.minute.isoformat(), "count": row.count}
        for row in stats
    ]
