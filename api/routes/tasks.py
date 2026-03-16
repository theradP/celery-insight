from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import List, Optional
import datetime

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from db.models import Task, TaskEvent
from api.dependencies import get_db

router = APIRouter()

@router.get("/")
def get_tasks(
    limit: int = Query(50, ge=1, le=500),
    offset: int = 0,
    state: Optional[str] = None,
    task_name: Optional[str] = None,
    worker_id: Optional[str] = None,
    db: Session = Depends(get_db)
):
    query = db.query(Task)
    if state:
        query = query.filter(Task.state == state)
    if task_name:
        query = query.filter(Task.task_name.ilike(f"%{task_name}%"))
    if worker_id:
        query = query.filter(Task.worker_id == worker_id)
        
    tasks = query.order_by(desc(Task.received_at)).offset(offset).limit(limit).all()
    
    # We serialize manually for simplicity instead of defining full Pydantic models here
    return [{
        "task_id": t.task_id,
        "task_name": t.task_name,
        "state": t.state,
        "worker_id": t.worker_id,
        "runtime": t.runtime,
        "retries": t.retries,
        "received_at": t.received_at.isoformat() if t.received_at else None,
        "completed_at": t.completed_at.isoformat() if t.completed_at else None,
        "exception": t.exception
    } for t in tasks]

@router.get("/{task_id}")
def get_task(task_id: str, db: Session = Depends(get_db)):
    task = db.query(Task).filter(Task.task_id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
        
    events = db.query(TaskEvent).filter(TaskEvent.task_id == task_id).order_by(TaskEvent.timestamp).all()
    
    return {
        "task": {
            "task_id": task.task_id,
            "task_name": task.task_name,
            "state": task.state,
            "runtime": task.runtime,
            "exception": task.exception
        },
        "timeline": [
            {
                "event_type": e.event_type,
                "timestamp": e.timestamp.isoformat(),
                "metadata": e.metadata_json
            } for e in events
        ]
    }
