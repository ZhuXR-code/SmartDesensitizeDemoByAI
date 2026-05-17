import os
import time
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from typing import Optional, Dict, Any

from app.db.database import get_db
from app.models.dataset import Dataset
from app.models.desensitization import DesensitizationTask
from app.schemas.common import ResponseModel
from app.services.report_generator import ReportGenerator
from app.services.data_service import DataService
from app.core.config import settings

router = APIRouter(prefix="/api/reports", tags=["规则校验报告"])


@router.post("/generate", response_model=ResponseModel)
async def generate_report(
    data: dict,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    dataset_id = data.get("dataset_id")
    field_rules = data.get("field_rules", {})
    report_name = data.get("report_name", "脱敏规则校验报告")
    output_format = data.get("output_format", "json")

    dataset = db.query(Dataset).filter(
        Dataset.id == dataset_id, Dataset.is_active == True
    ).first()
    if not dataset or not dataset.file_path:
        raise HTTPException(status_code=404, detail="数据集不存在")

    if not os.path.exists(dataset.file_path):
        raise HTTPException(status_code=404, detail="数据文件不存在")

    try:
        generator = ReportGenerator()
        report = generator.generate_report(
            dataset_path=dataset.file_path,
            field_rules=field_rules,
            dataset_name=dataset.name,
            report_name=report_name
        )

        timestamp = int(time.time())
        output_dir = os.path.join(settings.UPLOAD_DIR, "reports")
        os.makedirs(output_dir, exist_ok=True)

        if output_format == "html":
            output_path = os.path.join(output_dir, f"report_{report.report_id}_{timestamp}.html")
            generator.export_html(report, output_path)
        else:
            output_path = os.path.join(output_dir, f"report_{report.report_id}_{timestamp}.json")
            generator.export_json(report, output_path)

        return ResponseModel(data={
            "report_id": report.report_id,
            "report_name": report.report_name,
            "dataset_name": report.dataset_name,
            "created_at": report.created_at,
            "summary": report.summary,
            "performance": {
                "total_rows": report.performance.total_rows,
                "total_columns": report.performance.total_columns,
                "detection_time_ms": report.performance.detection_time_ms,
                "desensitization_time_ms": report.performance.desensitization_time_ms,
                "total_time_ms": report.performance.total_time_ms,
                "rows_per_second": report.performance.rows_per_second,
                "memory_peak_mb": report.performance.memory_peak_mb
            },
            "rule_coverage": [
                {
                    "rule_id": r.rule_id,
                    "rule_name": r.rule_name,
                    "rule_type": r.rule_type,
                    "matched_count": r.matched_count,
                    "matched_rows": r.matched_rows,
                    "coverage_rate": r.coverage_rate
                } for r in report.rule_coverage
            ],
            "accuracy_details": [
                {
                    "column_name": a.column_name,
                    "rule_id": a.rule_id,
                    "rule_name": a.rule_name,
                    "total_values": a.total_values,
                    "desensitized_count": a.desensitized_count,
                    "accuracy_rate": a.accuracy_rate,
                    "sample_original": a.sample_original,
                    "sample_desensitized": a.sample_desensitized
                } for a in report.accuracy_details
            ],
            "recommendations": report.recommendations,
            "file_path": output_path,
            "download_url": f"/api/reports/download/{os.path.basename(output_path)}"
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"报告生成失败: {str(e)}")


@router.get("/download/{filename}")
async def download_report(filename: str):
    from fastapi.responses import FileResponse

    output_dir = os.path.join(settings.UPLOAD_DIR, "reports")
    file_path = os.path.join(output_dir, filename)

    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="报告文件不存在")

    ext = os.path.splitext(filename)[1]
    media_type = "text/html" if ext == ".html" else "application/json"

    return FileResponse(
        file_path,
        filename=filename,
        media_type=media_type
    )


@router.post("/task/{task_id}", response_model=ResponseModel)
async def generate_task_report(
    task_id: int,
    data: Optional[dict] = None,
    db: Session = Depends(get_db)
):
    task = db.query(DesensitizationTask).filter(DesensitizationTask.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="任务不存在")

    dataset = db.query(Dataset).filter(Dataset.id == task.dataset_id).first()
    if not dataset or not dataset.file_path:
        raise HTTPException(status_code=404, detail="数据集不存在")

    if not os.path.exists(dataset.file_path):
        raise HTTPException(status_code=404, detail="数据文件不存在")

    try:
        generator = ReportGenerator()
        report = generator.generate_report(
            dataset_path=dataset.file_path,
            field_rules=task.field_rules,
            dataset_name=dataset.name,
            report_name=f"任务 {task.name} 的脱敏校验报告"
        )

        output_format = (data or {}).get("output_format", "json")
        timestamp = int(time.time())
        output_dir = os.path.join(settings.UPLOAD_DIR, "reports")
        os.makedirs(output_dir, exist_ok=True)

        if output_format == "html":
            output_path = os.path.join(output_dir, f"task_report_{task_id}_{timestamp}.html")
            generator.export_html(report, output_path)
        else:
            output_path = os.path.join(output_dir, f"task_report_{task_id}_{timestamp}.json")
            generator.export_json(report, output_path)

        return ResponseModel(data={
            "task_id": task_id,
            "report_id": report.report_id,
            "summary": report.summary,
            "performance": {
                "total_rows": report.performance.total_rows,
                "total_columns": report.performance.total_columns,
                "detection_time_ms": report.performance.detection_time_ms,
                "desensitization_time_ms": report.performance.desensitization_time_ms,
                "total_time_ms": report.performance.total_time_ms,
                "rows_per_second": report.performance.rows_per_second,
                "memory_peak_mb": report.performance.memory_peak_mb
            },
            "rule_coverage": [
                {
                    "rule_id": r.rule_id,
                    "rule_name": r.rule_name,
                    "coverage_rate": r.coverage_rate
                } for r in report.rule_coverage
            ],
            "accuracy_details": [
                {
                    "column_name": a.column_name,
                    "accuracy_rate": a.accuracy_rate,
                    "sample_original": a.sample_original,
                    "sample_desensitized": a.sample_desensitized
                } for a in report.accuracy_details
            ],
            "recommendations": report.recommendations,
            "file_path": output_path,
            "download_url": f"/api/reports/download/{os.path.basename(output_path)}"
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"报告生成失败: {str(e)}")
