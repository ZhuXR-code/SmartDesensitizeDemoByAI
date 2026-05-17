from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.db.database import get_db
from app.models.detection import DetectionTask, DetectionResult
from app.models.desensitization import DesensitizationTask
from app.models.dataset import Dataset
from app.schemas.common import ResponseModel

router = APIRouter(prefix="/api/dashboard", tags=["首页仪表盘"])


@router.get("/stats", response_model=ResponseModel)
async def get_dashboard_stats(db: Session = Depends(get_db)):
    total_datasets = db.query(Dataset).filter(Dataset.is_active == True).count()
    total_detection_tasks = db.query(DetectionTask).count()
    total_desensitization_tasks = db.query(DesensitizationTask).count()
    total_sensitive_found = db.query(DetectionResult).count()
    
    recent_detection = db.query(DetectionTask).order_by(
        DetectionTask.created_at.desc()).limit(5).all()
    recent_desensitization = db.query(DesensitizationTask).order_by(
        DesensitizationTask.created_at.desc()).limit(5).all()
    
    detection_by_type = db.query(
        DetectionResult.rule_name,
        func.count(DetectionResult.id).label("count")
    ).group_by(DetectionResult.rule_name).all()
    
    return ResponseModel(data={
        "overview": {
            "total_datasets": total_datasets,
            "total_detection_tasks": total_detection_tasks,
            "total_desensitization_tasks": total_desensitization_tasks,
            "total_sensitive_found": total_sensitive_found
        },
        "recent_tasks": {
            "detection": [{
                "id": t.id,
                "name": t.name,
                "status": t.status,
                "progress": t.progress,
                "found_count": t.found_count,
                "created_at": t.created_at.isoformat() if t.created_at else None
            } for t in recent_detection],
            "desensitization": [{
                "id": t.id,
                "name": t.name,
                "status": t.status,
                "progress": t.progress,
                "processed_rows": t.processed_rows,
                "created_at": t.created_at.isoformat() if t.created_at else None
            } for t in recent_desensitization]
        },
        "sensitive_type_distribution": [{
            "name": name,
            "count": count
        } for name, count in detection_by_type]
    })
