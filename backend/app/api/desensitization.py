import os
import time
import uuid
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Optional, Dict

from app.db.database import get_db
from app.models.desensitization import DesensitizationRule, DesensitizationKey, DesensitizationTask, DesensitizationResult
from app.models.dataset import Dataset
from app.schemas.desensitization import (
    DesensitizationRuleCreate, DesensitizationRuleResponse,
    DesensitizationTaskCreate, DesensitizationTaskResponse,
    PreviewRequest
)
from app.schemas.common import ResponseModel
from app.services.desensitization_engine import DesensitizationEngine
from app.services.data_service import DataService
from app.services.report_generator import ReportGenerator
from app.core.config import settings
from app.core.logger import get_logger

router = APIRouter(prefix="/api/desensitization", tags=["数据脱敏"])
logger = get_logger(__name__)


def get_builtin_rules():
    engine = DesensitizationEngine()
    return engine.BUILTIN_RULES


@router.get("/rules", response_model=ResponseModel)
async def list_rules(
    language: Optional[str] = None,
    category: Optional[str] = None,
    db: Session = Depends(get_db)
):
    from app.models.desensitization import DesensitizationResult
    
    builtin = get_builtin_rules()
    custom_rules = db.query(DesensitizationRule).filter(
        DesensitizationRule.is_active == True).all()
    
    # 统计每个规则的使用次数（从脱敏结果表中）
    usage_stats = db.query(
        DesensitizationResult.rule_id,
        __import__('sqlalchemy').func.count(DesensitizationResult.id).label('count')
    ).group_by(DesensitizationResult.rule_id).all()
    
    usage_map = {stat.rule_id: stat.count for stat in usage_stats}
    
    all_rules = []
    builtin_ids = set()  # 记录已添加的内置规则ID
    
    # 先添加内置规则
    for r in builtin:
        if language and r["language"] != language and r["language"] != "all":
            continue
        if category and r["category"] != category:
            continue
        rule_data = {
            "id": r["id"],
            "name": r["name"],
            "language": r["language"],
            "category": r["category"],
            "method": r["method"],
            "desensitization_method": r["desensitization_method"],
            "description": r.get("description", ""),
            "example": r.get("example", {}),
            "usage_count": usage_map.get(r["id"], 0),  # 从统计中获取使用次数
            "is_builtin": True
        }
        all_rules.append(rule_data)
        builtin_ids.add(r["id"])
    
    # 再添加自定义规则，跳过与内置规则同名的规则
    for r in custom_rules:
        if language and r.language != language and r.language != "all":
            continue
        if category and r.category != category:
            continue
        
        # 检查是否与内置规则同名，如果同名则跳过
        if r.name in [br["name"] for br in builtin]:
            print(f"[WARNING] 跳过重复的自定义规则: {r.name} (ID: {r.id})")
            continue
        
        all_rules.append({
            "id": r.id + 10000,
            "name": r.name,
            "language": r.language,
            "category": r.category,
            "method": r.method,
            "desensitization_method": r.desensitization_method,
            "description": r.description,
            "example": r.example if hasattr(r, 'example') and r.example else {},
            "usage_count": getattr(r, 'usage_count', 0) or 0,  # 安全获取使用次数
            "is_builtin": False
        })
    
    print(f"[DEBUG] 返回规则总数: {len(all_rules)}, 内置: {len(builtin_ids)}, 自定义: {len(all_rules) - len(builtin_ids)}")
    return ResponseModel(data=all_rules)


@router.post("/rules", response_model=ResponseModel)
async def create_rule(data: DesensitizationRuleCreate, db: Session = Depends(get_db)):
    rule = DesensitizationRule(
        name=data.name,
        description=data.description,
        language=data.language,
        category=data.category,
        method=data.method,
        config=data.config,
        is_builtin=False
    )
    db.add(rule)
    db.commit()
    db.refresh(rule)
    return ResponseModel(data={"id": rule.id, "name": rule.name})


@router.get("/keys", response_model=ResponseModel)
async def list_keys(db: Session = Depends(get_db)):
    keys = db.query(DesensitizationKey).filter(DesensitizationKey.is_active == True).all()
    if not keys:
        for i in range(1, 31):
            key = DesensitizationKey(
                alias=f"密钥-{i:02d}",
                key_hash=f"builtin_key_hash_{i}",
                description=f"系统内置密钥 {i}"
            )
            db.add(key)
        db.commit()
        keys = db.query(DesensitizationKey).filter(DesensitizationKey.is_active == True).all()
    
    return ResponseModel(data=[{
        "id": k.id,
        "alias": k.alias,
        "description": k.description
    } for k in keys])


@router.post("/auto-detect", response_model=ResponseModel)
async def auto_detect_rules(
    dataset_id: int,
    sample_size: int = 50,
    db: Session = Depends(get_db)
):
    """自动检测数据集字段的合适脱敏规则"""
    from app.models.dataset import Dataset
    from app.services.data_service import DataService
    from app.services.detection_engine import DetectionEngine
    
    dataset = db.query(Dataset).filter(
        Dataset.id == dataset_id, Dataset.is_active == True).first()
    if not dataset or not dataset.file_path:
        raise HTTPException(status_code=404, detail="数据集不存在")
    
    try:
        # 读取数据样本
        df = DataService.read_file(dataset.file_path)
        sample_df = df.head(sample_size)
        
        # 使用检测引擎分析每个字段
        detection_engine = DetectionEngine()
        field_suggestions = {}
        
        for col in sample_df.columns:
            # 获取该列的非空样本数据
            samples = sample_df[col].dropna().astype(str).tolist()[:20]
            if not samples:
                continue
            
            # 对每个样本进行检测
            all_matches = []
            for sample in samples:
                matches = detection_engine.scan_text(sample, column_name=col)
                all_matches.extend(matches)
            
            if all_matches:
                # 统计最匹配的规则
                rule_counts = {}
                for match in all_matches:
                    rule_key = match.rule_id
                    if rule_key not in rule_counts:
                        rule_counts[rule_key] = {
                            'count': 0,
                            'rule_name': match.rule_name,
                            'language': match.detected_language,
                            'confidence': match.confidence
                        }
                    rule_counts[rule_key]['count'] += 1
                
                # 选择出现次数最多的规则
                best_rule_id = max(rule_counts, key=lambda k: rule_counts[k]['count'])
                best_rule = rule_counts[best_rule_id]
                
                # 根据规则ID找到对应的脱敏规则
                desensitization_rule = find_desensitization_rule_by_detection_rule(best_rule_id)
                
                field_suggestions[col] = {
                    'column': col,
                    'language': best_rule['language'],
                    'detected_type': best_rule['rule_name'],
                    'rule_id': desensitization_rule['id'] if desensitization_rule else None,
                    'rule_name': desensitization_rule['name'] if desensitization_rule else None,
                    'desensitization_method': desensitization_rule['desensitization_method'] if desensitization_rule else None,
                    'confidence': round(best_rule['confidence'], 2),
                    'sample_count': len(samples)
                }
            else:
                # 没有检测到敏感信息，建议使用完全遮盖
                field_suggestions[col] = {
                    'column': col,
                    'language': 'all',
                    'detected_type': '未知类型',
                    'rule_id': 1,  # 完全遮盖
                    'rule_name': '完全遮盖',
                    'desensitization_method': 'full_mask',
                    'confidence': 0.5,
                    'sample_count': len(samples)
                }
        
        return ResponseModel(data=field_suggestions)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


def find_desensitization_rule_by_detection_rule(detection_rule_id: int) -> Optional[Dict]:
    """根据检测规则ID找到对应的脱敏规则"""
    # 检测规则和脱敏规则的映射关系
    mapping = {
        # 手机号
        1: {'id': 3, 'name': '手机号仿真', 'desensitization_method': 'simulation'},  # 中文手机号检测 -> 手机号仿真
        15: {'id': 14, 'name': '手机号部分遮盖', 'desensitization_method': 'partial_mask'},  # 美国手机号 -> 手机号部分遮盖
        19: {'id': 14, 'name': '手机号部分遮盖', 'desensitization_method': 'partial_mask'},  # 日本手机号
        22: {'id': 14, 'name': '手机号部分遮盖', 'desensitization_method': 'partial_mask'},  # 韩国手机号
        25: {'id': 14, 'name': '手机号部分遮盖', 'desensitization_method': 'partial_mask'},  # 法国手机号
        28: {'id': 14, 'name': '手机号部分遮盖', 'desensitization_method': 'partial_mask'},  # 德国手机号
        
        # 身份证/证件号
        2: {'id': 4, 'name': '身份证号仿真', 'desensitization_method': 'simulation'},  # 中国身份证
        23: {'id': 15, 'name': '身份证号部分遮盖', 'desensitization_method': 'partial_mask'},  # 韩国身份证
        
        # 姓名
        3: {'id': 2, 'name': '姓名仿真', 'desensitization_method': 'simulation'},  # 中文姓名
        6: {'id': 8, 'name': '英文姓名仿真', 'desensitization_method': 'simulation'},  # 英文姓名
        9: {'id': 9, 'name': '日文姓名仿真', 'desensitization_method': 'simulation'},  # 日文姓名
        10: {'id': 10, 'name': '韩文姓名仿真', 'desensitization_method': 'simulation'},  # 韩文姓名
        11: {'id': 11, 'name': '法文姓名仿真', 'desensitization_method': 'simulation'},  # 法文姓名
        12: {'id': 12, 'name': '德文姓名仿真', 'desensitization_method': 'simulation'},  # 德文姓名
        
        # 银行卡/信用卡
        4: {'id': 5, 'name': '银行卡号仿真', 'desensitization_method': 'simulation'},  # 中国银行卡
        14: {'id': 5, 'name': '银行卡号仿真', 'desensitization_method': 'simulation'},  # 信用卡
        
        # 邮箱
        7: {'id': 19, 'name': '邮箱部分遮盖', 'desensitization_method': 'partial_mask'},  # 邮箱
        
        # 地址
        5: {'id': 6, 'name': '地址仿真', 'desensitization_method': 'simulation'},  # 中文地址
        18: {'id': 17, 'name': '地址部分遮盖', 'desensitization_method': 'partial_mask'},  # 英文地址
        21: {'id': 17, 'name': '地址部分遮盖', 'desensitization_method': 'partial_mask'},  # 日文地址
        24: {'id': 17, 'name': '地址部分遮盖', 'desensitization_method': 'partial_mask'},  # 韩文地址
        27: {'id': 17, 'name': '地址部分遮盖', 'desensitization_method': 'partial_mask'},  # 法文地址
        30: {'id': 17, 'name': '地址部分遮盖', 'desensitization_method': 'partial_mask'},  # 德文地址
        
        # SSN
        8: {'id': 15, 'name': '身份证号部分遮盖', 'desensitization_method': 'partial_mask'},  # 美国SSN
        
        # IP地址
        16: {'id': 20, 'name': '通用等长遮盖', 'desensitization_method': 'partial_mask'},  # IP地址
        
        # URL
        17: {'id': 20, 'name': '通用等长遮盖', 'desensitization_method': 'partial_mask'},  # URL
    }
    
    return mapping.get(detection_rule_id)


@router.post("/preview", response_model=ResponseModel)
async def preview_desensitization(data: PreviewRequest, db: Session = Depends(get_db)):
    dataset = db.query(Dataset).filter(
        Dataset.id == data.dataset_id, Dataset.is_active == True).first()
    if not dataset or not dataset.file_path:
        raise HTTPException(status_code=404, detail="数据集不存在")
    
    try:
        df = DataService.read_file(dataset.file_path)
        engine = DesensitizationEngine()
        
        for key in db.query(DesensitizationKey).all():
            engine.set_key(key.id, key.key_hash)
        
        # 自动识别模式
        if data.auto_detect:
            previews = engine.preview_auto_desensitization(
                df, data.key_id, data.limit)
        else:
            # 手动配置模式
            previews = engine.preview_desensitization(
                df, data.field_rules, data.key_id, data.limit)
        
        return ResponseModel(data=previews)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


def run_desensitization_task(task_id: int, db: Session):
    task = db.query(DesensitizationTask).filter(DesensitizationTask.id == task_id).first()
    if not task:
        return
    
    task.status = "running"
    task.started_at = __import__('datetime').datetime.now()
    db.commit()
    
    try:
        dataset = db.query(Dataset).filter(Dataset.id == task.dataset_id).first()
        if not dataset or not dataset.file_path:
            raise ValueError("数据集不存在")
        
        df = DataService.read_file(dataset.file_path)
        task.total_rows = len(df)
        db.commit()
        
        engine = DesensitizationEngine()
        for key in db.query(DesensitizationKey).all():
            engine.set_key(key.id, key.key_hash)
        
        def progress_callback(current, total):
            task.progress = round(current / total * 100, 2)
            task.processed_rows = current
            db.commit()
        
        # 检查是否为自动识别模式
        is_auto_detect = task.logs and "auto_detect=true" in task.logs
        
        if is_auto_detect:
            # 自动识别模式：使用preview_auto_desensitization的逻辑处理全量数据
            result_df, matches = engine.process_auto_desensitization(
                df, task.key_id, progress_callback)
        else:
            # 手动配置模式
            result_df, matches = engine.process_dataframe(
                df, task.field_rules, task.key_id, progress_callback)
        
        task.progress = 100.0
        task.processed_rows = task.total_rows
        
        timestamp = int(time.time())
        output_filename = DataService.generate_temp_filename(
            dataset.name, f"脱敏后_{timestamp}")
        
        if task.output_mode == "copy":
            ext = os.path.splitext(dataset.file_path)[1] or ".csv"
            output_path = os.path.join(settings.UPLOAD_DIR, output_filename + ext)
            file_format = ext.lstrip(".")
            DataService.save_to_file(result_df, output_path, file_format)
            task.output_path = output_path
        else:
            temp_path = os.path.join(settings.UPLOAD_DIR, output_filename + ".csv")
            DataService.save_to_file(result_df, temp_path, "csv")
            task.temp_file_path = temp_path
        
        for match in matches[:1000]:
            result = DesensitizationResult(
                task_id=task.id,
                dataset_id=task.dataset_id,
                column_name=match.column_name,
                original_value=match.original_value[:100],
                desensitized_value=match.desensitized_value[:100],
                rule_id=match.rule_id,
                rule_name=match.rule_name,
                row_index=match.row_index
            )
            db.add(result)
        
        task.status = "completed"
        task.completed_at = __import__('datetime').datetime.now()
        task.duration_seconds = round(
            (task.completed_at - task.started_at).total_seconds(), 3)
        db.commit()
        
    except Exception as e:
        task.status = "failed"
        task.logs = str(e)
        db.commit()


@router.post("/tasks", response_model=ResponseModel)
async def create_desensitization_task(
    data: DesensitizationTaskCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    task = DesensitizationTask(
        name=data.name,
        dataset_id=data.dataset_id,
        source_type=data.source_type,
        detection_task_id=data.detection_task_id,
        field_rules=data.field_rules,
        output_mode=data.output_mode,
        key_id=data.key_id,
        status="pending"
    )
    
    # 保存auto_detect标记到logs字段（临时方案）
    if data.auto_detect:
        task.logs = "auto_detect=true"
    
    db.add(task)
    db.commit()
    db.refresh(task)
    
    background_tasks.add_task(run_desensitization_task, task.id, db)
    
    return ResponseModel(data={"id": task.id, "status": "pending"})


@router.get("/tasks", response_model=ResponseModel)
async def list_tasks(
    page: int = 1,
    page_size: int = 20,
    db: Session = Depends(get_db)
):
    total = db.query(DesensitizationTask).count()
    tasks = db.query(DesensitizationTask).order_by(
        DesensitizationTask.created_at.desc()).offset(
        (page - 1) * page_size).limit(page_size).all()
    
    items = []
    for t in tasks:
        item = {
            "id": t.id,
            "name": t.name,
            "dataset_id": t.dataset_id,
            "status": t.status,
            "progress": t.progress,
            "processed_rows": t.processed_rows,
            "total_rows": t.total_rows,
            "output_mode": t.output_mode,
            "output_path": t.output_path,
            "temp_file_path": t.temp_file_path,
            "started_at": t.started_at.isoformat() if t.started_at else None,
            "completed_at": t.completed_at.isoformat() if t.completed_at else None,
            "duration_seconds": t.duration_seconds,
            "created_at": t.created_at.isoformat() if t.created_at else None
        }
        # 安全地添加 report_path 字段（如果存在）
        try:
            item["report_path"] = getattr(t, 'report_path', None)
        except:
            item["report_path"] = None
        items.append(item)
    
    return ResponseModel(data={
        "total": total,
        "page": page,
        "page_size": page_size,
        "items": items
    })


@router.get("/tasks/{task_id}", response_model=ResponseModel)
async def get_task(task_id: int, db: Session = Depends(get_db)):
    task = db.query(DesensitizationTask).filter(DesensitizationTask.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="任务不存在")
    
    result = {
        "id": task.id,
        "name": task.name,
        "status": task.status,
        "progress": task.progress,
        "processed_rows": task.processed_rows,
        "total_rows": task.total_rows,
        "output_mode": task.output_mode,
        "output_path": task.output_path,
        "temp_file_path": task.temp_file_path,
        "logs": task.logs,
        "started_at": task.started_at.isoformat() if task.started_at else None,
        "completed_at": task.completed_at.isoformat() if task.completed_at else None,
        "duration_seconds": task.duration_seconds
    }
    # 安全地添加 report_path 字段（如果存在）
    try:
        result["report_path"] = getattr(task, 'report_path', None)
    except:
        result["report_path"] = None
    
    return ResponseModel(data=result)


@router.get("/tasks/{task_id}/download")
async def download_result(task_id: int, db: Session = Depends(get_db)):
    from fastapi.responses import FileResponse
    
    task = db.query(DesensitizationTask).filter(DesensitizationTask.id == task_id).first()
    if not task or task.status != "completed":
        raise HTTPException(status_code=400, detail="任务不存在或未完成")
    
    file_path = task.output_path or task.temp_file_path
    if not file_path or not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="文件不存在")
    
    return FileResponse(
        file_path,
        filename=os.path.basename(file_path),
        media_type="application/octet-stream"
    )


@router.get("/tasks/{task_id}/results", response_model=ResponseModel)
async def get_task_results(
    task_id: int,
    page: int = 1,
    page_size: int = 50,
    db: Session = Depends(get_db)
):
    total = db.query(DesensitizationResult).filter(
        DesensitizationResult.task_id == task_id).count()
    results = db.query(DesensitizationResult).filter(
        DesensitizationResult.task_id == task_id).offset(
        (page - 1) * page_size).limit(page_size).all()
    
    return ResponseModel(data={
        "total": total,
        "page": page,
        "page_size": page_size,
        "items": [{
            "id": r.id,
            "row_index": r.row_index,
            "column_name": r.column_name,
            "original_value": r.original_value,
            "desensitized_value": r.desensitized_value,
            "rule_name": r.rule_name
        } for r in results]
    })


@router.post("/tasks/{task_id}/generate-report", response_model=ResponseModel)
async def generate_report(task_id: int, db: Session = Depends(get_db)):
    """为脱敏任务生成报告"""
    
    task = db.query(DesensitizationTask).filter(DesensitizationTask.id == task_id).first()
    if not task or task.status != "completed":
        raise HTTPException(status_code=400, detail="任务不存在或未完成")
    
    # 检查是否有脱敏结果数据
    result_count = db.query(DesensitizationResult).filter(
        DesensitizationResult.task_id == task_id).count()
    
    if result_count == 0:
        raise HTTPException(status_code=400, detail="没有脱敏结果数据，无法生成报告")

    try:
        results = db.query(DesensitizationResult).filter(
            DesensitizationResult.task_id == task_id).all()

        # 生成报告
        generator = ReportGenerator(db)
        
        timestamp = int(time.time())
        unique_id = str(uuid.uuid4())[:8]
        
        # 生成HTML报告
        html_filename = f"report_{unique_id}_{timestamp}.html"
        html_path = os.path.join(settings.UPLOAD_DIR, "reports", html_filename)
        html_path = generator.generate_desensitization_html_report(task, results)
        
        # 尝试保存报告路径到数据库（如果字段存在）
        try:
            task.report_path = html_path
            db.commit()
        except:
            pass  # 如果字段不存在，忽略错误
        
        return ResponseModel(data={
            "report_path": html_path,
            "download_url": f"/api/desensitization/tasks/{task_id}/download-report"
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"生成报告失败: {str(e)}")


@router.get("/tasks/{task_id}/download-report")
async def download_report(
    task_id: int,
    report_format: str = "html",
    db: Session = Depends(get_db)
):
    """下载脱敏任务报告 - 支持 HTML/Markdown 格式"""
    from fastapi.responses import FileResponse
    
    task = db.query(DesensitizationTask).filter(DesensitizationTask.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="任务不存在")
    
    if report_format not in ("html", "markdown"):
        raise HTTPException(status_code=400, detail=f"不支持的格式: {report_format}，仅支持 html/markdown")
    
    try:
        results = db.query(DesensitizationResult).filter(
            DesensitizationResult.task_id == task_id).all()
        
        generator = ReportGenerator(db)
        report_dir = os.path.join(settings.UPLOAD_DIR, "reports")
        os.makedirs(report_dir, exist_ok=True)
        
        timestamp = int(time.time())
        unique_id = str(uuid.uuid4())[:8]
        
        if report_format == "html":
            filename = f"report_{unique_id}_{timestamp}.html"
            filepath = os.path.join(report_dir, filename)
            filepath = generator.generate_desensitization_html_report(task, results)
            return FileResponse(
                filepath,
                filename=os.path.basename(filepath),
                media_type="text/html",
                headers={"Content-Disposition": f"inline; filename=\"{os.path.basename(filepath)}\""}
            )
        else:
            filename = f"report_{unique_id}_{timestamp}.md"
            filepath = os.path.join(report_dir, filename)
            filepath = generator.generate_desensitization_markdown_report(task, results)
            return FileResponse(
                filepath,
                filename=os.path.basename(filepath),
                media_type="text/markdown"
            )
    except Exception as e:
        import traceback
        logger.error(f"生成/下载报告失败 | task_id={task_id} | format={report_format} | {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"生成报告失败: {str(e)}")
