import os
import json
import time
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime

from app.db.database import get_db
from app.models.ai import AiConfig, AiDetectionTask, AiDetectionResult, AiDesensitizationTask, AiDesensitizationResult
from app.models.dataset import Dataset
from app.schemas.ai import AiConfigCreate, AiConfigUpdate, AiConfigTest, AiDetectionTaskCreate, AiDesensitizationCreate
from app.schemas.common import ResponseModel
from app.services.ai_service import AiService
from app.services.data_service import DataService
from app.core.logger import get_logger

logger = get_logger(__name__)
router = APIRouter(prefix="/api/ai", tags=["AI智能识别与脱敏"])


@router.get("/configs", response_model=ResponseModel)
async def list_configs(db: Session = Depends(get_db)):
    configs = db.query(AiConfig).order_by(AiConfig.created_at.desc()).all()
    return ResponseModel(data=[{
        "id": c.id,
        "alias": c.alias or "",
        "provider": c.provider,
        "model_name": c.model_name,
        "api_base_url": c.api_base_url,
        "enable_web_search": c.enable_web_search,
        "temperature": c.temperature,
        "max_tokens": c.max_tokens,
        "is_active": c.is_active,
        "has_key": bool(c.api_key),
        "created_at": c.created_at.isoformat() if c.created_at else None
    } for c in configs])


@router.get("/config", response_model=ResponseModel)
async def get_active_config(db: Session = Depends(get_db)):
    config = db.query(AiConfig).filter(AiConfig.is_active == True).first()
    if not config:
        return ResponseModel(data={
            "provider": "openai", "model_name": "gpt-4o-mini",
            "api_key": "", "api_base_url": "",
            "enable_web_search": False, "temperature": 0.3, "max_tokens": 4096,
            "has_key": False
        })
    return ResponseModel(data={
        "id": config.id,
        "alias": config.alias or "",
        "provider": config.provider,
        "model_name": config.model_name,
        "api_key": config.api_key[:8] + "****" if config.api_key else "",
        "api_base_url": config.api_base_url,
        "enable_web_search": config.enable_web_search,
        "temperature": config.temperature,
        "max_tokens": config.max_tokens,
        "has_key": bool(config.api_key),
        "created_at": config.created_at.isoformat() if config.created_at else None
    })


@router.get("/config/{config_id}", response_model=ResponseModel)
async def get_config_detail(config_id: int, db: Session = Depends(get_db)):
    """获取单个配置的详细信息（包含完整密钥）"""
    config = db.query(AiConfig).filter(AiConfig.id == config_id).first()
    if not config:
        raise HTTPException(status_code=404, detail="配置不存在")
    return ResponseModel(data={
        "id": config.id,
        "alias": config.alias or "",
        "provider": config.provider,
        "model_name": config.model_name,
        "api_key": config.api_key,  # 返回完整密钥
        "api_base_url": config.api_base_url,
        "enable_web_search": config.enable_web_search,
        "temperature": config.temperature,
        "max_tokens": config.max_tokens,
        "is_active": config.is_active,
        "has_key": bool(config.api_key),
        "created_at": config.created_at.isoformat() if config.created_at else None
    })


@router.post("/config", response_model=ResponseModel)
async def save_config(data: AiConfigCreate, db: Session = Depends(get_db)):
    existing = db.query(AiConfig).filter(AiConfig.is_active == True).first()
    if existing:
        existing.is_active = False
        db.commit()

    config = AiConfig(
        alias=data.alias or "",
        provider=data.provider,
        model_name=data.model_name,
        api_key=data.api_key,
        api_base_url=data.api_base_url or "",
        enable_web_search=data.enable_web_search,
        temperature=data.temperature,
        max_tokens=data.max_tokens,
        is_active=True
    )
    db.add(config)
    db.commit()
    db.refresh(config)
    logger.info(f"AI配置已保存 | 名称: {data.alias} | 提供商: {data.provider} | 模型: {data.model_name}")
    return ResponseModel(data={"id": config.id, "alias": config.alias, "message": "AI配置保存成功"})


@router.put("/config/{config_id}", response_model=ResponseModel)
async def update_config(config_id: int, data: AiConfigUpdate, db: Session = Depends(get_db)):
    config = db.query(AiConfig).filter(AiConfig.id == config_id).first()
    if not config:
        raise HTTPException(status_code=404, detail="配置不存在")

    update_data = data.model_dump(exclude_none=True)
    # 如果api_key为空字符串或'********'，则不更新密钥
    if 'api_key' in update_data:
        if update_data['api_key'] == '' or update_data['api_key'] == '********':
            del update_data['api_key']
    
    for key, val in update_data.items():
        setattr(config, key, val)
    config.updated_at = datetime.now()
    db.commit()
    logger.info(f"AI配置已更新 | ID: {config_id}")
    return ResponseModel(data={"message": "配置更新成功"})


@router.delete("/config/{config_id}", response_model=ResponseModel)
async def delete_config(config_id: int, db: Session = Depends(get_db)):
    config = db.query(AiConfig).filter(AiConfig.id == config_id).first()
    if not config:
        raise HTTPException(status_code=404, detail="配置不存在")
    db.delete(config)
    db.commit()
    logger.info(f"AI配置已删除 | ID: {config_id}")
    return ResponseModel(data={"message": "配置已删除"})


@router.post("/config/{config_id}/activate", response_model=ResponseModel)
async def activate_config(config_id: int, db: Session = Depends(get_db)):
    config = db.query(AiConfig).filter(AiConfig.id == config_id).first()
    if not config:
        raise HTTPException(status_code=404, detail="配置不存在")

    db.query(AiConfig).filter(AiConfig.is_active == True).update({"is_active": False})
    config.is_active = True
    db.commit()
    logger.info(f"AI配置已设为默认 | ID: {config_id}")
    return ResponseModel(data={"message": "已设为默认配置"})


@router.post("/test", response_model=ResponseModel)
async def test_connection(data: AiConfigTest):
    try:
        import requests as req
        base_url = data.api_base_url.rstrip("/") if data.api_base_url else "https://api.openai.com"
        if not base_url.startswith("http"):
            base_url = f"https://{base_url}"
        url = f"{base_url}/v1/chat/completions"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {data.api_key}"
        }
        payload = {
            "model": data.model_name,
            "messages": [{"role": "user", "content": data.test_text or "Hello"}],
            "temperature": data.temperature,
            "max_tokens": 50
        }
        resp = req.post(url, headers=headers, json=payload, timeout=30)
        if resp.status_code == 200:
            result = resp.json()
            reply = result["choices"][0]["message"]["content"]
            return ResponseModel(data={
                "success": True,
                "message": "连接成功！模型返回: " + reply[:100]
            })
        else:
            err = resp.json()
            return ResponseModel(code=400, data={
                "success": False,
                "message": f"连接失败 ({resp.status_code}): {err.get('error', {}).get('message', '未知错误')}"
            })
    except Exception as e:
        return ResponseModel(code=400, data={
            "success": False,
            "message": f"连接异常: {str(e)}"
        })


@router.post("/config/{config_id}/test", response_model=ResponseModel)
async def test_config_by_id(config_id: int, db: Session = Depends(get_db)):
    config = db.query(AiConfig).filter(AiConfig.id == config_id).first()
    if not config:
        raise HTTPException(status_code=404, detail="配置不存在")
    test_data = AiConfigTest(
        provider=config.provider,
        model_name=config.model_name,
        api_key=config.api_key,
        api_base_url=config.api_base_url or "",
        temperature=config.temperature,
        max_tokens=config.max_tokens
    )
    return await test_connection(test_data)


@router.get("/models", response_model=ResponseModel)
async def list_models():
    models = [
        {"provider": "openai", "label": "OpenAI", "base_url": "https://api.openai.com", "models": [
            {"name": "gpt-4o", "label": "GPT-4o"},
            {"name": "gpt-4o-mini", "label": "GPT-4o Mini（推荐）"},
            {"name": "gpt-4-turbo", "label": "GPT-4 Turbo"},
            {"name": "o1-mini", "label": "O1 Mini"},
            {"name": "o1-preview", "label": "O1 Preview"}
        ]},
        {"provider": "deepseek", "label": "DeepSeek", "base_url": "https://api.deepseek.com", "models": [
            {"name": "deepseek-chat", "label": "DeepSeek V3（通用对话）"},
            {"name": "deepseek-reasoner", "label": "DeepSeek R1（深度推理）"},
            {"name": "deepseek-v4-pro", "label": "DeepSeek V4 Pro（最新旗舰）"},
            {"name": "deepseek-v4-flash", "label": "DeepSeek V4 Flash（快速版）"}
        ]},
        {"provider": "qwen", "label": "阿里千问", "base_url": "https://dashscope.aliyuncs.com/compatible-mode", "models": [
            {"name": "qwen-plus", "label": "Qwen-Plus（推荐）"},
            {"name": "qwen-max", "label": "Qwen-Max（最强）"},
            {"name": "qwen-turbo", "label": "Qwen-Turbo（快速经济）"}
        ]},
        {"provider": "kimi", "label": "月之暗面 Kimi", "base_url": "https://api.moonshot.cn", "models": [
            {"name": "moonshot-v1-8k", "label": "Kimi v1-8K"},
            {"name": "moonshot-v1-32k", "label": "Kimi v1-32K"},
            {"name": "moonshot-v1-128k", "label": "Kimi v1-128K（超长上下文）"}
        ]},
        {"provider": "zhipu", "label": "智谱 GLM", "base_url": "https://open.bigmodel.cn/api/paas/v4", "models": [
            {"name": "glm-4-plus", "label": "GLM-4-Plus（推荐）"},
            {"name": "glm-4-air", "label": "GLM-4-Air（快速）"},
            {"name": "glm-4-flash", "label": "GLM-4-Flash（免费）"}
        ]},
        {"provider": "baidu", "label": "百度文心", "base_url": "https://aip.baidubce.com", "models": [
            {"name": "ernie-4.0-8k", "label": "ERNIE 4.0（最强）"},
            {"name": "ernie-3.5-8k", "label": "ERNIE 3.5"},
            {"name": "ernie-speed-128k", "label": "ERNIE Speed（快速128K）"}
        ]},
        {"provider": "azure", "label": "Azure OpenAI", "base_url": "", "models": [
            {"name": "gpt-4o", "label": "GPT-4o"},
            {"name": "gpt-4o-mini", "label": "GPT-4o Mini"},
            {"name": "gpt-4", "label": "GPT-4"}
        ]},
        {"provider": "custom", "label": "自定义（兼容OpenAI协议）", "base_url": "", "models": [
            {"name": "custom", "label": "自定义模型"}
        ]}
    ]
    return ResponseModel(data=models)


@router.post("/detect", response_model=ResponseModel)
async def create_detection_task(
    data: AiDetectionTaskCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    dataset = db.query(Dataset).filter(Dataset.id == data.dataset_id).first()
    if not dataset:
        raise HTTPException(status_code=404, detail="数据集不存在")

    config_id = data.ai_config_id
    if not config_id:
        active = db.query(AiConfig).filter(AiConfig.is_active == True).first()
        if active:
            config_id = active.id

    task = AiDetectionTask(
        name=data.name,
        dataset_id=data.dataset_id,
        dataset_name=dataset.name,
        enable_web_search=data.enable_web_search,
        prompt_template=data.custom_prompt or ""
    )
    db.add(task)
    db.commit()
    db.refresh(task)

    df = DataService.read_file(dataset.file_path)
    rows = df.to_dict("records")
    columns = list(df.columns)

    svc = AiService(db, config_id=config_id)
    config = db.query(AiConfig).filter(AiConfig.id == config_id).first() if config_id else None
    if config:
        task.model_used = f"{config.alias or config.provider}/{config.model_name}"
        db.commit()

    background_tasks.add_task(svc.run_detection, task.id, rows, columns)
    return ResponseModel(data={"id": task.id, "name": task.name, "status": "pending"})


@router.get("/detect/tasks", response_model=ResponseModel)
async def list_detection_tasks(db: Session = Depends(get_db)):
    tasks = db.query(AiDetectionTask).order_by(AiDetectionTask.created_at.desc()).limit(50).all()
    return ResponseModel(data=[{
        "id": t.id,
        "name": t.name,
        "dataset_name": t.dataset_name,
        "status": t.status,
        "progress": t.progress,
        "total_rows": t.total_rows,
        "found_count": t.found_count,
        "enable_web_search": t.enable_web_search,
        "model_used": t.model_used,
        "duration_seconds": t.duration_seconds,
        "result_summary": t.result_summary,
        "created_at": t.created_at.isoformat() if t.created_at else None,
        "completed_at": t.completed_at.isoformat() if t.completed_at else None
    } for t in tasks])


@router.get("/detect/tasks/{task_id}", response_model=ResponseModel)
async def get_detection_task(task_id: int, db: Session = Depends(get_db)):
    task = db.query(AiDetectionTask).filter(AiDetectionTask.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="任务不存在")
    results = db.query(AiDetectionResult).filter(
        AiDetectionResult.task_id == task_id,
        AiDetectionResult.is_sensitive == True
    ).all()
    return ResponseModel(data={
        "task": {
            "id": task.id, "name": task.name, "dataset_name": task.dataset_name,
            "status": task.status, "progress": task.progress, "total_rows": task.total_rows,
            "found_count": task.found_count, "enable_web_search": task.enable_web_search,
            "model_used": task.model_used, "duration_seconds": task.duration_seconds,
            "result_summary": task.result_summary,
            "created_at": task.created_at.isoformat() if task.created_at else None,
            "completed_at": task.completed_at.isoformat() if task.completed_at else None
        },
        "results": [{
            "id": r.id, "row_index": r.row_index, "column_name": r.column_name,
            "original_value": r.original_value, "sensitive_type": r.sensitive_type,
            "confidence": r.confidence, "risk_level": r.risk_level,
            "regulation_ref": r.regulation_ref, "llm_reasoning": r.llm_reasoning,
            "desensitization_suggestion": r.desensitization_suggestion,
            "reviewed": r.reviewed,
            "review_result": r.review_result,
            "review_reason": r.review_reason,
            "reviewed_at": r.reviewed_at.isoformat() if r.reviewed_at else None
        } for r in results]
    })


@router.post("/detect/tasks/{task_id}/cancel", response_model=ResponseModel)
async def cancel_detection_task(task_id: int, db: Session = Depends(get_db)):
    """取消正在运行的AI检测任务"""
    from app.services.task_manager import task_manager
    
    task = db.query(AiDetectionTask).filter(AiDetectionTask.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="任务不存在")
    
    if task.status != "running":
        raise HTTPException(status_code=400, detail=f"任务状态为 {task.status}，无法取消")
    
    # 请求取消任务
    task_manager.request_cancel(task_id)
    logger.info(f"用户请求取消任务 | 任务ID: {task_id} | 任务名称: {task.name}")
    
    return ResponseModel(data={
        "message": "取消请求已提交，任务将在当前处理完成后停止",
        "task_id": task_id
    })


@router.delete("/detect/tasks/clear", response_model=ResponseModel)
async def clear_all_detection_tasks(db: Session = Depends(get_db)):
    """清空所有AI检测任务及其结果"""
    # 先删除所有检测结果
    deleted_results = db.query(AiDetectionResult).delete()
    # 再删除所有检测任务
    deleted_tasks = db.query(AiDetectionTask).delete()
    
    db.commit()
    
    logger.info(f"清空所有检测任务 | 删除任务数: {deleted_tasks}, 删除结果数: {deleted_results}")
    
    return ResponseModel(data={
        "message": f"已清空 {deleted_tasks} 个任务和 {deleted_results} 条检测结果",
        "deleted_tasks": deleted_tasks,
        "deleted_results": deleted_results
    })


@router.delete("/detect/tasks/{task_id}", response_model=ResponseModel)
async def delete_detection_task(task_id: int, db: Session = Depends(get_db)):
    """删除单个AI检测任务及其结果"""
    task = db.query(AiDetectionTask).filter(AiDetectionTask.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="任务不存在")
    
    # 先删除该任务的所有检测结果
    deleted_results = db.query(AiDetectionResult).filter(
        AiDetectionResult.task_id == task_id
    ).delete()
    
    # 再删除任务
    db.delete(task)
    db.commit()
    
    logger.info(f"删除检测任务 | 任务ID: {task_id} | 任务名称: {task.name} | 删除结果数: {deleted_results}")
    
    return ResponseModel(data={
        "message": f"已删除任务 '{task.name}' 及 {deleted_results} 条检测结果",
        "task_id": task_id,
        "deleted_results": deleted_results
    })


@router.get("/detect/results/{task_id}/export", response_model=ResponseModel)
async def export_detection_results(task_id: int, db: Session = Depends(get_db)):
    import pandas as pd
    task = db.query(AiDetectionTask).filter(AiDetectionTask.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="任务不存在")
    results = db.query(AiDetectionResult).filter(
        AiDetectionResult.task_id == task_id,
        AiDetectionResult.is_sensitive == True
    ).all()
    if not results:
        raise HTTPException(status_code=400, detail="没有检测结果可导出")
    rows = [{
        "行号": r.row_index, "列名": r.column_name, "原始值": r.original_value,
        "敏感类型": r.sensitive_type, "置信度": r.confidence, "风险等级": r.risk_level,
        "法规依据": r.regulation_ref, "AI推理": r.llm_reasoning, "脱敏建议": r.desensitization_suggestion
    } for r in results]
    output_dir = "uploads/reports"
    os.makedirs(output_dir, exist_ok=True)
    output_path = f"{output_dir}/ai_detection_{task_id}_{int(time.time())}.xlsx"
    df = pd.DataFrame(rows)
    df.to_excel(output_path, index=False)
    return ResponseModel(data={"file_path": output_path, "rows": len(rows)})


@router.get("/detect/tasks/{task_id}/report/html", response_model=ResponseModel)
async def generate_html_report(task_id: int, db: Session = Depends(get_db)):
    """生成HTML格式的检测报告"""
    from app.services.report_generator import ReportGenerator
    
    task = db.query(AiDetectionTask).filter(AiDetectionTask.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="任务不存在")
    
    results = db.query(AiDetectionResult).filter(
        AiDetectionResult.task_id == task_id,
        AiDetectionResult.is_sensitive == True
    ).all()
    
    if not results:
        raise HTTPException(status_code=400, detail="没有检测结果可生成报告")
    
    # 生成HTML报告
    report_gen = ReportGenerator(db)
    html_path = report_gen.generate_html_report(task, results)
    
    return ResponseModel(data={
        "file_path": html_path,
        "message": "HTML报告生成成功"
    })


@router.get("/detect/tasks/{task_id}/report/markdown", response_model=ResponseModel)
async def generate_markdown_report(task_id: int, db: Session = Depends(get_db)):
    """生成Markdown格式的检测报告"""
    from app.services.report_generator import ReportGenerator
    
    task = db.query(AiDetectionTask).filter(AiDetectionTask.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="任务不存在")
    
    results = db.query(AiDetectionResult).filter(
        AiDetectionResult.task_id == task_id,
        AiDetectionResult.is_sensitive == True
    ).all()
    
    if not results:
        raise HTTPException(status_code=400, detail="没有检测结果可生成报告")
    
    # 生成Markdown报告
    report_gen = ReportGenerator(db)
    md_path = report_gen.generate_markdown_report(task, results)
    
    return ResponseModel(data={
        "file_path": md_path,
        "message": "Markdown报告生成成功"
    })


@router.delete("/desensitize/tasks/clear", response_model=ResponseModel)
async def clear_all_desensitization_tasks(db: Session = Depends(get_db)):
    deleted_results = db.query(AiDesensitizationResult).delete()
    deleted_tasks = db.query(AiDesensitizationTask).delete()
    db.commit()
    logger.info(f"清空所有脱敏任务 | 删除任务数: {deleted_tasks}, 删除结果数: {deleted_results}")
    return ResponseModel(data={
        "message": f"已清空 {deleted_tasks} 个任务和 {deleted_results} 条脱敏结果",
        "deleted_tasks": deleted_tasks,
        "deleted_results": deleted_results
    })


@router.delete("/desensitize/tasks/{task_id}", response_model=ResponseModel)
async def delete_desensitization_task(task_id: int, db: Session = Depends(get_db)):
    """删除单个AI脱敏任务及其结果"""
    task = db.query(AiDesensitizationTask).filter(AiDesensitizationTask.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="任务不存在")
    
    # 先删除该任务的所有脱敏结果
    deleted_results = db.query(AiDesensitizationResult).filter(
        AiDesensitizationResult.task_id == task_id
    ).delete()
    
    # 再删除任务
    db.delete(task)
    db.commit()
    
    logger.info(f"删除脱敏任务 | 任务ID: {task_id} | 任务名称: {task.name} | 删除结果数: {deleted_results}")
    
    return ResponseModel(data={
        "message": f"已删除任务 '{task.name}' 及 {deleted_results} 条脱敏结果",
        "task_id": task_id,
        "deleted_results": deleted_results
    })
@router.post("/desensitize", response_model=ResponseModel)
async def create_desensitization_task(
    data: AiDesensitizationCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    det_task = db.query(AiDetectionTask).filter(AiDetectionTask.id == data.detection_task_id).first()
    if not det_task:
        raise HTTPException(status_code=404, detail="检测任务不存在")
    task = AiDesensitizationTask(
        name=data.name, detection_task_id=data.detection_task_id,
        mode=data.mode, output_file_format=data.output_format,
        ai_config_id=data.ai_config_id  # 保存选择的AI配置ID
    )
    db.add(task)
    db.commit()
    db.refresh(task)
    svc = AiService(db)
    background_tasks.add_task(svc.run_desensitization, task.id, data.detection_task_id, data.mode, data.ai_config_id)
    return ResponseModel(data={"id": task.id, "name": task.name, "status": "pending", "mode": data.mode})


@router.get("/desensitize/tasks", response_model=ResponseModel)
async def list_desensitization_tasks(db: Session = Depends(get_db)):
    tasks = db.query(AiDesensitizationTask).order_by(AiDesensitizationTask.created_at.desc()).limit(50).all()
    return ResponseModel(data=[{
        "id": t.id, "name": t.name, "detection_task_id": t.detection_task_id,
        "mode": t.mode, "status": t.status, "progress": t.progress,
        "total_rows": t.total_rows, "processed_rows": t.processed_rows,
        "output_file_path": t.output_file_path, "duration_seconds": t.duration_seconds,
        "created_at": t.created_at.isoformat() if t.created_at else None,
        "completed_at": t.completed_at.isoformat() if t.completed_at else None
    } for t in tasks])


@router.get("/desensitize/tasks/{task_id}", response_model=ResponseModel)
async def get_desensitization_task(task_id: int, db: Session = Depends(get_db)):
    task = db.query(AiDesensitizationTask).filter(AiDesensitizationTask.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="任务不存在")
    results = db.query(AiDesensitizationResult).filter(
        AiDesensitizationResult.task_id == task_id
    ).all()
    return ResponseModel(data={
        "task": {
            "id": task.id, "name": task.name, "detection_task_id": task.detection_task_id,
            "mode": task.mode, "status": task.status, "progress": task.progress,
            "total_rows": task.total_rows, "processed_rows": task.processed_rows,
            "output_file_path": task.output_file_path, "output_file_pure_path": task.output_file_pure_path or "",
            "duration_seconds": task.duration_seconds,
            "created_at": task.created_at.isoformat() if task.created_at else None,
            "completed_at": task.completed_at.isoformat() if task.completed_at else None
        },
        "results": [{
            "id": r.id, "row_index": r.row_index, "column_name": r.column_name,
            "original_value": r.original_value, "desensitized_value": r.desensitized_value,
            "method": r.method,
            "ai_original_is_sensitive": r.ai_original_is_sensitive,
            "ai_original_sensitive_type": r.ai_original_sensitive_type,
            "review_result": r.review_result,
            "review_status": r.review_status
        } for r in results]
    })


@router.get("/desensitize/tasks/{task_id}/report/html", response_model=ResponseModel)
async def generate_desensitization_html_report(task_id: int, db: Session = Depends(get_db)):
    from app.services.report_generator import ReportGenerator
    task = db.query(AiDesensitizationTask).filter(AiDesensitizationTask.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="任务不存在")
    results = db.query(AiDesensitizationResult).filter(
        AiDesensitizationResult.task_id == task_id
    ).all()
    if not results:
        raise HTTPException(status_code=400, detail="没有脱敏结果可生成报告")
    report_gen = ReportGenerator(db)
    html_path = report_gen.generate_desensitization_html_report(task, results)
    return ResponseModel(data={"file_path": html_path, "message": "HTML报告生成成功"})


@router.get("/desensitize/tasks/{task_id}/report/markdown", response_model=ResponseModel)
async def generate_desensitization_markdown_report(task_id: int, db: Session = Depends(get_db)):
    from app.services.report_generator import ReportGenerator
    task = db.query(AiDesensitizationTask).filter(AiDesensitizationTask.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="任务不存在")
    results = db.query(AiDesensitizationResult).filter(
        AiDesensitizationResult.task_id == task_id
    ).all()
    if not results:
        raise HTTPException(status_code=400, detail="没有脱敏结果可生成报告")
    report_gen = ReportGenerator(db)
    md_path = report_gen.generate_desensitization_markdown_report(task, results)
    return ResponseModel(data={"file_path": md_path, "message": "Markdown报告生成成功"})


@router.get("/report/{file_path:path}/preview")
async def preview_report(file_path: str):
    file_full_path = os.path.join("uploads/reports", os.path.basename(file_path))
    if not os.path.exists(file_full_path):
        raise HTTPException(status_code=404, detail="报告文件不存在")
    with open(file_full_path, 'r', encoding='utf-8') as f:
        content = f.read()
    from fastapi.responses import HTMLResponse
    return HTMLResponse(content=content, status_code=200)


@router.post("/detect/results/{result_id}/review", response_model=ResponseModel)
async def review_detection_result(
    result_id: int,
    data: dict,
    db: Session = Depends(get_db)
):
    """人工复核检测结果"""
    from sqlalchemy import func
    from app.models.user import User
    
    result = db.query(AiDetectionResult).filter(AiDetectionResult.id == result_id).first()
    if not result:
        raise HTTPException(status_code=404, detail="检测结果不存在")
    
    review_result = data.get("review_result")
    review_reason = data.get("review_reason", "")
    
    result.reviewed = True
    result.review_result = review_result
    result.review_reason = review_reason
    result.reviewed_at = datetime.now()
    
    current_user_id = data.get("user_id")
    if current_user_id:
        result.reviewed_by = current_user_id
    
    db.commit()
    
    logger.info(f"人工复核检测结果 | 结果ID: {result_id} | 复核结果: {review_result} | 理由: {review_reason}")
    
    return ResponseModel(data={
        "message": "复核成功",
        "result_id": result_id,
        "reviewed": result.reviewed,
        "review_result": result.review_result
    })


@router.get("/detect/tasks/{task_id}/review/stats", response_model=ResponseModel)
async def get_review_stats(task_id: int, db: Session = Depends(get_db)):
    """获取检测任务的复核统计"""
    results = db.query(AiDetectionResult).filter(
        AiDetectionResult.task_id == task_id
    ).all()
    
    total = len(results)
    reviewed = sum(1 for r in results if r.reviewed)
    unreviewed = total - reviewed
    reviewed_sensitive = sum(1 for r in results if r.reviewed and r.review_result)
    reviewed_non_sensitive = sum(1 for r in results if r.reviewed and not r.review_result)
    ai_sensitive = sum(1 for r in results if r.is_sensitive)
    ai_non_sensitive = total - ai_sensitive
    
    return ResponseModel(data={
        "total": total,
        "reviewed": reviewed,
        "unreviewed": unreviewed,
        "reviewed_sensitive": reviewed_sensitive,
        "reviewed_non_sensitive": reviewed_non_sensitive,
        "ai_sensitive": ai_sensitive,
        "ai_non_sensitive": ai_non_sensitive
    })
