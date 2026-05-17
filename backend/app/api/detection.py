import time
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Optional

from app.db.database import get_db
from app.models.detection import DetectionRule, DetectionRuleSet, DetectionTask, DetectionResult
from app.models.dataset import Dataset
from app.schemas.detection import (
    DetectionRuleCreate, DetectionRuleResponse,
    DetectionRuleSetCreate, DetectionRuleSetResponse,
    DetectionTaskCreate, DetectionTaskResponse
)
from app.schemas.common import ResponseModel
from app.services.detection_engine import DetectionEngine
from app.services.data_service import DataService
from app.services.language_detector import LanguageDetector

router = APIRouter(prefix="/api/detection", tags=["敏感数据识别"])


def get_builtin_rules():
    engine = DetectionEngine()
    return engine.BUILTIN_RULES


@router.get("/rules", response_model=ResponseModel)
async def list_rules(
    language: Optional[str] = None,
    rule_type: Optional[str] = None,
    db: Session = Depends(get_db)
):
    builtin = get_builtin_rules()
    custom_rules = db.query(DetectionRule).filter(DetectionRule.is_active == True).all()
    
    all_rules = []
    for r in builtin:
        if language and r["language"] != language:
            continue
        if rule_type and r["rule_type"] != rule_type:
            continue
        all_rules.append({
            "id": r["id"],
            "name": r["name"],
            "language": r["language"],
            "rule_type": r["rule_type"],
            "pattern": r.get("pattern", ""),
            "keywords": r.get("keywords"),
            "example": r.get("example"),
            "is_builtin": True
        })
    
    for r in custom_rules:
        if language and r.language != language:
            continue
        if rule_type and r.rule_type != rule_type:
            continue
        all_rules.append({
            "id": r.id + 10000,
            "name": r.name,
            "language": r.language,
            "rule_type": r.rule_type,
            "pattern": r.pattern,
            "keywords": r.keywords,
            "example": r.example,
            "is_builtin": False
        })
    
    return ResponseModel(data=all_rules)


@router.post("/rules", response_model=ResponseModel)
async def create_rule(data: DetectionRuleCreate, db: Session = Depends(get_db)):
    rule = DetectionRule(
        name=data.name,
        description=data.description,
        language=data.language,
        rule_type=data.rule_type,
        pattern=data.pattern or "",
        keywords=data.keywords,
        example=data.example,
        is_builtin=False
    )
    db.add(rule)
    db.commit()
    db.refresh(rule)
    return ResponseModel(data={"id": rule.id, "name": rule.name})


@router.delete("/rules/{rule_id}", response_model=ResponseModel)
async def delete_rule(rule_id: int, db: Session = Depends(get_db)):
    # 处理前端传来的ID（可能包含10000偏移量）
    actual_id = rule_id - 10000 if rule_id >= 10000 else rule_id
    
    rule = db.query(DetectionRule).filter(DetectionRule.id == actual_id).first()
    if not rule:
        raise HTTPException(status_code=404, detail="规则不存在")
    
    # 不允许删除内置规则
    if rule.is_builtin:
        raise HTTPException(status_code=403, detail="内置规则不可删除")
    
    rule.is_active = False
    db.commit()
    return ResponseModel(message="规则已删除")


@router.put("/rules/{rule_id}", response_model=ResponseModel)
async def update_rule(rule_id: int, data: DetectionRuleCreate, db: Session = Depends(get_db)):
    """更新自定义识别规则"""
    # 处理前端传来的ID（可能包含10000偏移量）
    actual_id = rule_id - 10000 if rule_id >= 10000 else rule_id
    
    rule = db.query(DetectionRule).filter(DetectionRule.id == actual_id).first()
    if not rule:
        raise HTTPException(status_code=404, detail="规则不存在")
    
    # 不允许修改内置规则
    if rule.is_builtin:
        raise HTTPException(status_code=403, detail="内置规则不可修改")
    
    rule.name = data.name
    rule.description = data.description
    rule.language = data.language
    rule.rule_type = data.rule_type
    rule.pattern = data.pattern or ""
    rule.keywords = data.keywords
    rule.example = data.example
    
    db.commit()
    db.refresh(rule)
    
    return ResponseModel(data={"id": rule.id, "name": rule.name}, message="规则更新成功")


@router.get("/rule-sets", response_model=ResponseModel)
async def list_rule_sets(db: Session = Depends(get_db)):
    rule_sets = db.query(DetectionRuleSet).filter(DetectionRuleSet.is_active == True).all()
    return ResponseModel(data=[{
        "id": rs.id,
        "name": rs.name,
        "description": rs.description,
        "rules": rs.rules,
        "rule_count": len(rs.rules) if rs.rules else 0,
        "scenario": rs.scenario,
        "created_at": rs.created_at.isoformat() if rs.created_at else None
    } for rs in rule_sets])


@router.post("/rule-sets", response_model=ResponseModel)
async def create_rule_set(data: DetectionRuleSetCreate, db: Session = Depends(get_db)):
    rule_set = DetectionRuleSet(
        name=data.name,
        description=data.description,
        rules=data.rules,
        scenario=data.scenario
    )
    db.add(rule_set)
    db.commit()
    db.refresh(rule_set)
    return ResponseModel(data={"id": rule_set.id, "name": rule_set.name})


@router.delete("/rule-sets/{rule_set_id}", response_model=ResponseModel)
async def delete_rule_set(rule_set_id: int, db: Session = Depends(get_db)):
    rs = db.query(DetectionRuleSet).filter(DetectionRuleSet.id == rule_set_id).first()
    if not rs:
        raise HTTPException(status_code=404, detail="规则集不存在")
    rs.is_active = False
    db.commit()
    return ResponseModel(message="规则集已删除")


@router.get("/rule-sets/{rule_set_id}", response_model=ResponseModel)
async def get_rule_set_detail(rule_set_id: int, db: Session = Depends(get_db)):
    """获取规则集详情，包含关联的规则信息"""
    from app.models.detection import DetectionRule
    from app.services.detection_engine import DetectionEngine
    
    rs = db.query(DetectionRuleSet).filter(DetectionRuleSet.id == rule_set_id).first()
    if not rs:
        raise HTTPException(status_code=404, detail="规则集不存在")
    
    # 获取内置规则
    engine = DetectionEngine()
    builtin_rules_map = {r["id"]: r for r in engine.BUILTIN_RULES}
    
    # 获取规则集中的所有规则详情
    rules_detail = []
    if rs.rules:
        for rule_id in rs.rules:
            # 先检查是否是内置规则
            if rule_id in builtin_rules_map:
                builtin_rule = builtin_rules_map[rule_id]
                rules_detail.append({
                    "id": builtin_rule["id"],
                    "name": builtin_rule["name"],
                    "language": builtin_rule["language"],
                    "rule_type": builtin_rule["rule_type"],
                    "pattern": builtin_rule.get("pattern", ""),
                    "keywords": builtin_rule.get("keywords"),
                    "example": builtin_rule.get("example"),
                    "is_builtin": True
                })
            else:
                # 再查询自定义规则
                rule = db.query(DetectionRule).filter(
                    DetectionRule.id == rule_id,
                    DetectionRule.is_active == True
                ).first()
                if rule:
                    rules_detail.append({
                        "id": rule.id,
                        "name": rule.name,
                        "language": rule.language,
                        "rule_type": rule.rule_type,
                        "pattern": rule.pattern,
                        "keywords": rule.keywords,
                        "example": rule.example,
                        "is_builtin": False
                    })
    
    return ResponseModel(data={
        "id": rs.id,
        "name": rs.name,
        "description": rs.description,
        "rules": rules_detail,
        "rule_count": len(rules_detail),
        "scenario": rs.scenario,
        "created_at": rs.created_at.isoformat() if rs.created_at else None
    })


@router.put("/rule-sets/{rule_set_id}", response_model=ResponseModel)
async def update_rule_set(
    rule_set_id: int,
    data: DetectionRuleSetCreate,
    db: Session = Depends(get_db)
):
    """更新规则集"""
    rs = db.query(DetectionRuleSet).filter(DetectionRuleSet.id == rule_set_id).first()
    if not rs:
        raise HTTPException(status_code=404, detail="规则集不存在")
    
    rs.name = data.name
    rs.description = data.description
    rs.rules = data.rules
    rs.scenario = data.scenario
    
    db.commit()
    db.refresh(rs)
    
    return ResponseModel(data={"id": rs.id, "name": rs.name}, message="规则集更新成功")


def run_detection_task(task_id: int, db: Session):
    from app.core.logger import get_logger
    logger = get_logger(__name__)
    
    task = db.query(DetectionTask).filter(DetectionTask.id == task_id).first()
    if not task:
        logger.error(f"任务不存在: {task_id}")
        return
    
    logger.info(f"开始执行识别任务 | 任务ID: {task_id} | 名称: {task.name}")
    task.status = "running"
    task.started_at = __import__('datetime').datetime.now()
    db.commit()
    
    try:
        dataset = db.query(Dataset).filter(Dataset.id == task.dataset_id).first()
        if not dataset or not dataset.file_path:
            raise ValueError("数据集不存在")
        
        logger.info(f"读取数据集文件 | 文件路径: {dataset.file_path}")
        df = DataService.read_file(dataset.file_path)
        task.total_rows = len(df)
        db.commit()
        logger.info(f"数据集加载完成 | 总行数: {len(df)} | 列数: {len(df.columns)}")
        
        selected_rules = None
        if task.rule_set_id:
            rule_set = db.query(DetectionRuleSet).filter(
                DetectionRuleSet.id == task.rule_set_id).first()
            if rule_set and rule_set.rules:
                selected_rules = rule_set.rules
                logger.info(f"使用规则集 | 规则集ID: {task.rule_set_id} | 规则数量: {len(selected_rules)}")
        
        engine = DetectionEngine()
        
        def progress_callback(current, total):
            task.progress = round(current / total * 100, 2)
            task.scanned_rows = current
            db.commit()
            # 每扫描10%输出一次日志
            if current % max(1, total // 10) == 0 or current == total:
                logger.info(f"识别进度 | 任务ID: {task_id} | 进度: {task.progress}% | 已扫描: {current}/{total}")
        
        logger.info("开始扫描数据...")
        matches = engine.scan_dataframe(
            df,
            columns=task.scan_columns,
            language_strategy=task.language_strategy,
            selected_rules=selected_rules,
            progress_callback=progress_callback
        )
        
        logger.info(f"扫描完成 | 发现敏感信息: {len(matches)} 条")
        task.found_count = len(matches)
        task.progress = 100.0
        task.scanned_rows = task.total_rows
        
        logger.info("保存识别结果到数据库...")
        for match in matches:
            result = DetectionResult(
                task_id=task.id,
                dataset_id=task.dataset_id,
                row_index=match.row_index,
                column_name=match.column_name,
                detected_language=match.detected_language,
                rule_id=match.rule_id,
                rule_name=match.rule_name,
                rule_type=match.rule_type,
                matched_content=match.matched_content[:100],
                confidence=match.confidence,
                desensitization_suggestion=match.desensitization_suggestion
            )
            db.add(result)
        
        task.status = "completed"
        task.completed_at = __import__('datetime').datetime.now()
        task.duration_seconds = round(
            (task.completed_at - task.started_at).total_seconds(), 3)
        
        lang_dist = LanguageDetector.detect_batch(
            [str(v) for v in df.iloc[:, 0].tolist() if str(v) != "nan"])
        task.language_distribution = lang_dist
        
        db.commit()
        logger.info(f"✅ 识别任务完成 | 任务ID: {task_id} | 耗时: {task.duration_seconds}秒 | 发现: {len(matches)}条敏感信息")
        
    except Exception as e:
        import traceback
        error_msg = f"{str(e)}\n{traceback.format_exc()}"
        task.status = "failed"
        task.logs = error_msg
        db.commit()
        logger.error(f"❌ 识别任务失败 | 任务ID: {task_id} | 错误: {error_msg}")


@router.post("/tasks", response_model=ResponseModel)
async def create_detection_task(
    data: DetectionTaskCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    from app.core.logger import get_logger
    logger = get_logger(__name__)
    
    logger.info(f"创建识别任务请求 | 数据: {data.dict()}")
    
    try:
        task = DetectionTask(
            name=data.name,
            dataset_id=data.dataset_id,
            rule_set_id=data.rule_set_id,
            scan_columns=data.scan_columns,
            language_strategy=data.language_strategy,
            status="pending"
        )
        db.add(task)
        db.commit()
        db.refresh(task)
        
        logger.info(f"任务创建成功 | ID: {task.id} | 名称: {task.name}")
        
        background_tasks.add_task(run_detection_task, task.id, db)
        
        return ResponseModel(data={"id": task.id, "status": "pending"})
    except Exception as e:
        logger.error(f"创建任务失败 | 错误: {str(e)}")
        raise


@router.get("/tasks", response_model=ResponseModel)
async def list_tasks(
    page: int = 1,
    page_size: int = 20,
    db: Session = Depends(get_db)
):
    total = db.query(DetectionTask).count()
    tasks = db.query(DetectionTask).order_by(
        DetectionTask.created_at.desc()).offset(
        (page - 1) * page_size).limit(page_size).all()
    
    return ResponseModel(data={
        "total": total,
        "page": page,
        "page_size": page_size,
        "items": [{
            "id": t.id,
            "name": t.name,
            "dataset_id": t.dataset_id,
            "status": t.status,
            "progress": t.progress,
            "scanned_rows": t.scanned_rows,
            "total_rows": t.total_rows,
            "found_count": t.found_count,
            "started_at": t.started_at.isoformat() if t.started_at else None,
            "completed_at": t.completed_at.isoformat() if t.completed_at else None,
            "duration_seconds": t.duration_seconds,
            "created_at": t.created_at.isoformat() if t.created_at else None
        } for t in tasks]
    })


@router.get("/tasks/{task_id}", response_model=ResponseModel)
async def get_task(task_id: int, db: Session = Depends(get_db)):
    from app.models.dataset import Dataset
    
    task = db.query(DetectionTask).filter(DetectionTask.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="任务不存在")
    
    # 获取数据集信息
    dataset = db.query(Dataset).filter(Dataset.id == task.dataset_id).first()
    
    # 获取规则集信息
    rule_set_info = None
    if task.rule_set_id:
        rule_set = db.query(DetectionRuleSet).filter(
            DetectionRuleSet.id == task.rule_set_id
        ).first()
        if rule_set:
            rule_set_info = {
                "id": rule_set.id,
                "name": rule_set.name,
                "description": rule_set.description,
                "rule_count": len(rule_set.rules) if rule_set.rules else 0
            }
    
    # 计算扫描速度（行/秒）
    scan_speed = 0
    if task.duration_seconds and task.duration_seconds > 0 and task.scanned_rows:
        scan_speed = round(task.scanned_rows / task.duration_seconds, 2)
    
    # 计算敏感数据比例（包含敏感信息的行数 / 总行数）
    sensitivity_rate = 0
    affected_rows = 0  # 包含敏感信息的行数
    if task.total_rows and task.total_rows > 0:
        # 查询去重后的敏感行数
        affected_rows = db.query(DetectionResult.row_index).filter(
            DetectionResult.task_id == task_id
        ).distinct().count()
        sensitivity_rate = round((affected_rows / task.total_rows) * 100, 2)
    
    # 计算风险等级
    risk_level = "low"
    if sensitivity_rate > 50:
        risk_level = "high"
    elif sensitivity_rate > 20:
        risk_level = "medium"
    
    return ResponseModel(data={
        "id": task.id,
        "name": task.name,
        "dataset_id": task.dataset_id,
        "dataset_name": dataset.name if dataset else None,
        "rule_set_id": task.rule_set_id,
        "rule_set_info": rule_set_info,
        "status": task.status,
        "progress": task.progress,
        "scanned_rows": task.scanned_rows,
        "total_rows": task.total_rows,
        "found_count": task.found_count,
        "sensitivity_rate": sensitivity_rate,
        "risk_level": risk_level,
        "scan_speed": scan_speed,
        "language_distribution": task.language_distribution,
        "logs": task.logs,
        "started_at": task.started_at.isoformat() if task.started_at else None,
        "completed_at": task.completed_at.isoformat() if task.completed_at else None,
        "duration_seconds": task.duration_seconds,
        "created_at": task.created_at.isoformat() if task.created_at else None
    })


@router.get("/tasks/{task_id}/results", response_model=ResponseModel)
async def get_task_results(
    task_id: int,
    page: int = 1,
    page_size: int = 50,
    db: Session = Depends(get_db)
):
    total = db.query(DetectionResult).filter(
        DetectionResult.task_id == task_id).count()
    results = db.query(DetectionResult).filter(
        DetectionResult.task_id == task_id).offset(
        (page - 1) * page_size).limit(page_size).all()
    
    return ResponseModel(data={
        "total": total,
        "page": page,
        "page_size": page_size,
        "items": [{
            "id": r.id,
            "row_index": r.row_index,
            "column_name": r.column_name,
            "detected_language": r.detected_language,
            "rule_name": r.rule_name,
            "rule_type": r.rule_type,
            "matched_content": r.matched_content,
            "confidence": r.confidence,
            "desensitization_suggestion": r.desensitization_suggestion
        } for r in results]
    })


@router.post("/tasks/{task_id}/jump-to-desensitization", response_model=ResponseModel)
async def jump_to_desensitization(task_id: int, db: Session = Depends(get_db)):
    task = db.query(DetectionTask).filter(DetectionTask.id == task_id).first()
    if not task or task.status != "completed":
        raise HTTPException(status_code=400, detail="任务不存在或未完成")
    
    results = db.query(DetectionResult).filter(
        DetectionResult.task_id == task_id).all()
    
    columns_to_desensitize = {}
    for r in results:
        if r.column_name not in columns_to_desensitize:
            columns_to_desensitize[r.column_name] = {
                "suggestion": r.desensitization_suggestion,
                "count": 0
            }
        columns_to_desensitize[r.column_name]["count"] += 1
    
    return ResponseModel(data={
        "dataset_id": task.dataset_id,
        "detection_task_id": task.id,
        "columns": columns_to_desensitize,
        "total_found": task.found_count
    })
