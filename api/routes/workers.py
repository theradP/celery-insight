from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import desc

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from db.models import Worker
from api.dependencies import get_db

router = APIRouter()

@router.get("/")
def get_workers(db: Session = Depends(get_db)):
    workers = db.query(Worker).order_by(desc(Worker.last_heartbeat)).all()
    return [{
        "worker_id": w.worker_id,
        "hostname": w.hostname,
        "status": w.status,
        "active_tasks": w.active_tasks,
        "cpu_usage": w.cpu_usage,
        "memory_usage": w.memory_usage,
        "last_heartbeat": w.last_heartbeat.isoformat() if w.last_heartbeat else None
    } for w in workers]
