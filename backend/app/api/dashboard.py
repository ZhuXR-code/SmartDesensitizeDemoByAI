from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.db.database import get_db
from app.models.detection import DetectionTask, DetectionResult
from app.models.desensitization import DesensitizationTask
from app.models.dataset import Dataset
from app.models.ai import AiDetectionTask, AiDetectionResult, AiDesensitizationTask
from app.schemas.common import ResponseModel

router = APIRouter(prefix="/api/dashboard", tags=["首页仪表盘"])


@router.get("/stats", response_model=ResponseModel)
async def get_dashboard_stats(db: Session = Depends(get_db)):
    total_datasets = db.query(Dataset).filter(Dataset.is_active == True).count()
    total_detection_tasks = db.query(DetectionTask).count()
    total_desensitization_tasks = db.query(DesensitizationTask).count()
    total_sensitive_found = db.query(DetectionResult).count()
    
    # AI相关统计
    total_ai_detection_tasks = db.query(AiDetectionTask).count()
    total_ai_desensitization_tasks = db.query(AiDesensitizationTask).count()
    total_ai_sensitive_found = db.query(AiDetectionResult).filter(AiDetectionResult.is_sensitive == True).count()
    
    recent_detection = db.query(DetectionTask).order_by(
        DetectionTask.created_at.desc()).limit(5).all()
    recent_desensitization = db.query(DesensitizationTask).order_by(
        DesensitizationTask.created_at.desc()).limit(5).all()
    
    # AI最近任务
    recent_ai_detection = db.query(AiDetectionTask).order_by(
        AiDetectionTask.created_at.desc()).limit(5).all()
    recent_ai_desensitization = db.query(AiDesensitizationTask).order_by(
        AiDesensitizationTask.created_at.desc()).limit(5).all()
    
    detection_by_type = db.query(
        DetectionResult.rule_name,
        func.count(DetectionResult.id).label("count")
    ).group_by(DetectionResult.rule_name).all()
    
    ai_sensitive_type_dist = db.query(
        AiDetectionResult.sensitive_type,
        func.count(AiDetectionResult.id).label("count")
    ).filter(AiDetectionResult.is_sensitive == True).group_by(AiDetectionResult.sensitive_type).all()
    
    return ResponseModel(data={
        "overview": {
            "total_datasets": total_datasets,
            "total_detection_tasks": total_detection_tasks,
            "total_desensitization_tasks": total_desensitization_tasks,
            "total_sensitive_found": total_sensitive_found,
            "total_ai_detection_tasks": total_ai_detection_tasks,
            "total_ai_desensitization_tasks": total_ai_desensitization_tasks,
            "total_ai_sensitive_found": total_ai_sensitive_found
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
            } for t in recent_desensitization],
            "ai_detection": [{
                "id": t.id,
                "name": t.name,
                "dataset_name": t.dataset_name,
                "status": t.status,
                "progress": t.progress,
                "found_count": t.found_count,
                "created_at": t.created_at.isoformat() if t.created_at else None
            } for t in recent_ai_detection],
            "ai_desensitization": [{
                "id": t.id,
                "name": t.name,
                "mode": t.mode,
                "status": t.status,
                "progress": t.progress,
                "total_rows": t.total_rows,
                "processed_rows": t.processed_rows,
                "created_at": t.created_at.isoformat() if t.created_at else None
            } for t in recent_ai_desensitization]
        },
        "sensitive_type_distribution": [{
            "name": name,
            "count": count
        } for name, count in detection_by_type],
        "ai_sensitive_type_distribution": [{
            "name": name,
            "count": count
        } for name, count in ai_sensitive_type_dist]
    })
