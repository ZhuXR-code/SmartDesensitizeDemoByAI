import os
import shutil
import time
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import List, Optional

from app.db.database import get_db
from app.models.dataset import Dataset, DataSource
from app.schemas.dataset import DatasetCreate, DatasetResponse, DataSourceCreate, DataSourceResponse
from app.schemas.common import ResponseModel
from app.services.data_service import DataService
from app.core.config import settings
from app.core.logger import get_logger, log_db_operation, log_exception

logger = get_logger(__name__)

router = APIRouter(prefix="/api/datasets", tags=["数据集管理"])


@router.post("/upload", response_model=ResponseModel)
async def upload_file(
    file: UploadFile = File(...),
    name: Optional[str] = Form(None),
    description: Optional[str] = Form(None),
    encoding: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    start_time = time.time()
    logger.info(f"上传文件 | 文件名: {file.filename} | 数据集名称: {name}")
    
    try:
        os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
        
        file_path = os.path.join(settings.UPLOAD_DIR, file.filename)
        logger.debug(f"保存文件到: {file_path}")
        
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        logger.debug("正在解析文件信息...")
        file_info = DataService.get_file_info(file_path)
        
        dataset_name = name or file.filename
        dataset = Dataset(
            name=dataset_name,
            description=description,
            source_type="file",
            file_path=file_path,
            file_size=file_info.get("file_size"),
            row_count=file_info.get("row_count"),
            column_count=file_info.get("column_count"),
            columns=file_info.get("columns"),
            encoding=encoding or "utf-8",
            preview_data=file_info.get("preview", [])
        )
        
        db.add(dataset)
        db.commit()
        db.refresh(dataset)
        
        duration = (time.time() - start_time) * 1000
        log_db_operation(logger, "INSERT", "datasets", 
                        f"文件上传:{file.filename},行数:{dataset.row_count},列数:{dataset.column_count}", 
                        duration)
        
        logger.info(f"✅ 文件上传成功 | 数据集ID: {dataset.id} | 名称: {dataset_name} | 行数: {dataset.row_count} | 耗时: {duration:.2f}ms")
        
        return ResponseModel(data={
            "id": dataset.id,
            "name": dataset.name,
            "row_count": dataset.row_count,
            "column_count": dataset.column_count,
            "columns": dataset.columns
        })
    except Exception as e:
        log_exception(logger, f"上传文件({file.filename})", e)
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/from-text", response_model=ResponseModel)
async def create_from_text(
    data: dict,
    db: Session = Depends(get_db)
):
    try:
        text = data.get("text", "")
        format_type = data.get("format_type", "csv")
        name = data.get("name", "粘贴数据")
        
        df = DataService.read_from_text(text, format_type)
        
        file_path = os.path.join(settings.UPLOAD_DIR, f"{name}_{int(__import__('time').time())}.csv")
        DataService.save_to_file(df, file_path, "csv")
        
        dataset = Dataset(
            name=name,
            source_type="clipboard",
            file_path=file_path,
            row_count=len(df),
            column_count=len(df.columns),
            columns=list(df.columns),
            preview_data=df.head(5).to_dict("records")
        )
        
        db.add(dataset)
        db.commit()
        db.refresh(dataset)
        
        return ResponseModel(data={
            "id": dataset.id,
            "name": dataset.name,
            "row_count": dataset.row_count,
            "column_count": dataset.column_count,
            "columns": dataset.columns
        })
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/list", response_model=ResponseModel)
async def list_datasets(
    page: int = 1,
    page_size: int = 20,
    db: Session = Depends(get_db)
):
    total = db.query(Dataset).filter(Dataset.is_active == True).count()
    datasets = db.query(Dataset).filter(Dataset.is_active == True).offset(
        (page - 1) * page_size).limit(page_size).all()
    
    return ResponseModel(data={
        "total": total,
        "page": page,
        "page_size": page_size,
        "items": [{
            "id": d.id,
            "name": d.name,
            "source_type": d.source_type,
            "row_count": d.row_count,
            "column_count": d.column_count,
            "columns": d.columns,
            "created_at": d.created_at.isoformat() if d.created_at else None
        } for d in datasets]
    })


@router.get("/{dataset_id}", response_model=ResponseModel)
async def get_dataset(dataset_id: int, db: Session = Depends(get_db)):
    dataset = db.query(Dataset).filter(Dataset.id == dataset_id, Dataset.is_active == True).first()
    if not dataset:
        raise HTTPException(status_code=404, detail="数据集不存在")
    
    return ResponseModel(data={
        "id": dataset.id,
        "name": dataset.name,
        "description": dataset.description,
        "source_type": dataset.source_type,
        "row_count": dataset.row_count,
        "column_count": dataset.column_count,
        "columns": dataset.columns,
        "encoding": dataset.encoding,
        "preview_data": dataset.preview_data,
        "created_at": dataset.created_at.isoformat() if dataset.created_at else None
    })


@router.get("/{dataset_id}/preview", response_model=ResponseModel)
async def preview_dataset(
    dataset_id: int,
    page: int = 1,
    page_size: int = 20,
    db: Session = Depends(get_db)
):
    dataset = db.query(Dataset).filter(Dataset.id == dataset_id, Dataset.is_active == True).first()
    if not dataset or not dataset.file_path:
        raise HTTPException(status_code=404, detail="数据集不存在或文件丢失")
    
    try:
        df = DataService.read_file(dataset.file_path)
        total = len(df)
        start = (page - 1) * page_size
        end = start + page_size
        preview_df = df.iloc[start:end]
        
        return ResponseModel(data={
            "total": total,
            "page": page,
            "page_size": page_size,
            "columns": list(df.columns),
            "data": preview_df.to_dict("records")
        })
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/{dataset_id}", response_model=ResponseModel)
async def delete_dataset(dataset_id: int, db: Session = Depends(get_db)):
    dataset = db.query(Dataset).filter(Dataset.id == dataset_id).first()
    if not dataset:
        raise HTTPException(status_code=404, detail="数据集不存在")
    
    dataset.is_active = False
    db.commit()
    
    return ResponseModel(message="数据集已删除")


@router.post("/data-source", response_model=ResponseModel)
async def create_data_source(data: DataSourceCreate, db: Session = Depends(get_db)):
    source = DataSource(
        name=data.name,
        source_type=data.source_type,
        config=data.config
    )
    db.add(source)
    db.commit()
    db.refresh(source)
    return ResponseModel(data={"id": source.id, "name": source.name})


@router.get("/data-source/list", response_model=ResponseModel)
async def list_data_sources(db: Session = Depends(get_db)):
    sources = db.query(DataSource).filter(DataSource.is_active == True).all()
    return ResponseModel(data=[{
        "id": s.id,
        "name": s.name,
        "source_type": s.source_type,
        "config": s.config,
        "created_at": s.created_at.isoformat() if s.created_at else None
    } for s in sources])
