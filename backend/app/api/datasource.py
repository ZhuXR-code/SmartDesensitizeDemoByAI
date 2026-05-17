from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from pydantic import BaseModel
import time
from datetime import datetime, date
import pandas as pd

from app.db.database import get_db
from app.models.dataset import Dataset, DataSource
from app.schemas.common import ResponseModel
from app.services.db_connector import DatabaseConnector
from app.services.data_service import DataService
from app.core.config import settings
from app.core.logger import get_logger, log_db_operation, log_exception
import os

logger = get_logger(__name__)


def convert_timestamp_to_string(obj):
    """
    递归转换对象中的 Timestamp 类型为字符串
    用于解决 JSON 序列化问题
    """
    if isinstance(obj, dict):
        return {k: convert_timestamp_to_string(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [convert_timestamp_to_string(item) for item in obj]
    elif isinstance(obj, (pd.Timestamp, datetime)):
        return obj.isoformat()
    elif isinstance(obj, date):
        return obj.isoformat()
    else:
        return obj

router = APIRouter(prefix="/api/data-sources", tags=["数据源管理"])


class DBConnectionTestRequest(BaseModel):
    db_type: str
    host: str
    port: int
    username: Optional[str] = None
    password: Optional[str] = None
    database: str


class TablePreviewRequest(BaseModel):
    db_type: str
    host: str
    port: int
    username: str
    password: str
    database: str
    table_name: str
    limit: Optional[int] = 10


class SaveAndImportRequest(BaseModel):
    source_name: str = "未命名数据源"
    db_type: str
    host: str
    port: int
    username: str
    password: str
    database: str
    selected_tables: List[str]
    name_prefix: Optional[str] = ""


class DBConnectionTestResponse(BaseModel):
    success: bool
    message: str


class TableImportRequest(BaseModel):
    source_id: int
    selected_tables: List[str]
    name_prefix: Optional[str] = ""


@router.post("/test-connection", response_model=ResponseModel)
async def test_connection(data: DBConnectionTestRequest):
    start_time = time.time()
    logger.info(f"测试数据库连接 | 类型: {data.db_type} | 主机: {data.host}:{data.port} | 数据库: {data.database} | 用户: {data.username}")
    
    try:
        connector = DatabaseConnector(
            db_type=data.db_type,
            host=data.host,
            port=data.port,
            username=data.username,
            password=data.password,
            database=data.database
        )
        
        logger.debug(f"正在连接数据库...")
        success = connector.test_connection()
        duration = (time.time() - start_time) * 1000
        
        if success:
            logger.info(f"✅ 数据库连接成功 | 耗时: {duration:.2f}ms")
            return ResponseModel(data={"connected": True, "message": "连接成功"})
        else:
            logger.warning(f"❌ 数据库连接失败 | 耗时: {duration:.2f}ms")
            return ResponseModel(code=400, message="连接失败，请检查配置信息")
    except Exception as e:
        duration = (time.time() - start_time) * 1000
        log_exception(logger, "测试数据库连接", e, {"db_type": data.db_type, "host": f"{data.host}:{data.port}", "database": data.database})
        return ResponseModel(code=400, message=f"连接失败: {str(e)}")


@router.post("/tables", response_model=ResponseModel)
async def get_tables(data: DBConnectionTestRequest):
    start_time = time.time()
    logger.info(f"获取数据库表列表 | 类型: {data.db_type} | 主机: {data.host}:{data.port} | 数据库: {data.database}")
    
    try:
        connector = DatabaseConnector(
            db_type=data.db_type,
            host=data.host,
            port=data.port,
            username=data.username,
            password=data.password,
            database=data.database
        )
        
        logger.debug("正在获取表列表...")
        tables = connector.get_tables()
        duration = (time.time() - start_time) * 1000
        
        logger.info(f"✅ 成功获取表列表 | 表数量: {len(tables)} | 表名: {tables} | 耗时: {duration:.2f}ms")
        
        log_db_operation(logger, "SELECT", data.database, f"获取{len(tables)}个表", duration)
        
        return ResponseModel(data={
            "tables": tables,
            "total": len(tables)
        })
    except Exception as e:
        log_exception(logger, "获取数据库表列表", e, {"db_type": data.db_type, "host": f"{data.host}:{data.port}", "database": data.database})
        raise HTTPException(status_code=400, detail=f"获取表列表失败: {str(e)}")


@router.post("/table-preview", response_model=ResponseModel)
async def preview_table(data: TablePreviewRequest):
    start_time = time.time()
    table_name = data.table_name
    limit = data.limit or 10
    
    logger.info(f"预览表数据 | 表名: {table_name} | 预览行数: {limit}")
    
    try:
        connector = DatabaseConnector(
            db_type=data.db_type,
            host=data.host,
            port=data.port,
            username=data.username,
            password=data.password,
            database=data.database
        )

        logger.debug(f"正在读取表: {table_name}...")
        df = connector.read_table(table_name)
        preview_df = df.head(limit)
        duration = (time.time() - start_time) * 1000
        
        logger.info(f"✅ 成功预览表 | 表: {table_name} | 总行数: {len(df)} | 列数: {len(df.columns)} | 耗时: {duration:.2f}ms")
        
        log_db_operation(logger, "SELECT", table_name, f"预览{limit}行,总{len(df)}行", duration)

        return ResponseModel(data={
            "table_name": table_name,
            "total_rows": len(df),
            "columns": list(df.columns),
            "data": preview_df.to_dict("records")
        })
    except Exception as e:
        log_exception(logger, f"预览表数据({table_name})", e, {"table": table_name, "limit": limit})
        raise HTTPException(status_code=400, detail=f"预览表失败: {str(e)}")


@router.post("/save-and-import", response_model=ResponseModel)
async def save_source_and_import_tables(
    data: SaveAndImportRequest,
    db: Session = Depends(get_db)
):
    start_time = time.time()
    
    source_name = data.source_name
    selected_tables = data.selected_tables
    
    logger.info(f"保存数据源并导入表 | 数据源名称: {source_name} | 选择的表: {selected_tables}")
    
    try:
        if not selected_tables:
            logger.warning("未选择任何表进行导入")
            raise HTTPException(status_code=400, detail="请至少选择一个表")

        config = {
            "db_type": data.db_type,
            "host": data.host,
            "port": data.port,
            "username": data.username,
            "password": data.password,
            "database": data.database
        }

        logger.debug(f"正在保存数据源配置到数据库...")
        source = DataSource(
            name=source_name,
            source_type="database",
            config=config
        )
        db.add(source)
        db.commit()
        db.refresh(source)
        
        logger.info(f"✅ 数据源已保存 | ID: {source.id} | 名称: {source.name}")

        connector = DatabaseConnector(
            db_type=data.db_type,
            host=data.host,
            port=data.port,
            username=data.username,
            password=data.password,
            database=data.database
        )

        os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
        imported_datasets = []

        for table_name in selected_tables:
            table_start = time.time()
            logger.info(f"开始导入表: {table_name}")
            
            try:
                df = connector.read_table(table_name)

                safe_table_name = "".join(c for c in table_name if c.isalnum() or c in "_-").strip()
                file_name = f"db_{source.id}_{safe_table_name}_{int(__import__('time').time())}.csv"
                file_path = os.path.join(settings.UPLOAD_DIR, file_name)
                
                logger.debug(f"保存表数据到文件: {file_path}")
                DataService.save_to_file(df, file_path, "csv")

                dataset_name = f"{data.name_prefix}{table_name}" if data.name_prefix else table_name

                # 转换 preview_data 中的 Timestamp 类型
                preview_records = df.head(5).to_dict("records")
                preview_data_converted = convert_timestamp_to_string(preview_records)

                dataset = Dataset(
                    name=dataset_name,
                    description=f"来自数据源 [{source_name}] 的表: {table_name}",
                    source_id=source.id,
                    source_type="database",
                    file_path=file_path,
                    row_count=len(df),
                    column_count=len(df.columns),
                    columns=list(df.columns),
                    preview_data=preview_data_converted
                )
                db.add(dataset)
                db.commit()
                db.refresh(dataset)
                
                table_duration = (time.time() - table_start) * 1000
                log_db_operation(logger, "IMPORT", table_name, 
                               f"行数:{len(df)},列数:{len(df.columns)},文件:{file_name}", 
                               table_duration)
                
                imported_datasets.append({
                    "id": dataset.id,
                    "name": dataset.name,
                    "table_name": table_name,
                    "row_count": dataset.row_count,
                    "column_count": dataset.column_count
                })
                
                logger.info(f"✅ 表导入成功 | 表: {table_name} | 数据集ID: {dataset.id} | 行数: {len(df)} | 耗时: {table_duration:.2f}ms")
                
            except Exception as e:
                log_exception(logger, f"导入表({table_name})", e)
                logger.error(f"❌ 表导入失败: {table_name} | 错误: {str(e)}")
                continue

        total_duration = (time.time() - start_time) * 1000
        
        logger.info(f"="*80)
        logger.info(f"📊 数据源导入完成 | 数据源ID: {source.id} | 成功导入: {len(imported_datasets)}/{len(selected_tables)} 个表 | 总耗时: {total_duration:.2f}ms")
        logger.info(f"="*80)

        return ResponseModel(data={
            "source_id": source.id,
            "source_name": source.name,
            "imported_count": len(imported_datasets),
            "datasets": imported_datasets
        })

    except Exception as e:
        total_duration = (time.time() - start_time) * 1000
        log_exception(logger, "保存并导入数据源", e, {"source_name": source_name, "tables": selected_tables})
        raise HTTPException(status_code=400, detail=f"导入失败: {str(e)}")


@router.get("/list", response_model=ResponseModel)
async def list_data_sources(
    page: int = 1,
    page_size: int = 20,
    db: Session = Depends(get_db)
):
    total = db.query(DataSource).filter(DataSource.is_active == True).count()
    sources = db.query(DataSource).filter(DataSource.is_active == True).offset(
        (page - 1) * page_size).limit(page_size).all()

    return ResponseModel(data={
        "total": total,
        "page": page,
        "page_size": page_size,
        "items": [{
            "id": s.id,
            "name": s.name,
            "source_type": s.source_type,
            "config": {
                "db_type": s.config.get("db_type") if s.config else None,
                "host": s.config.get("host") if s.config else None,
                "port": s.config.get("port") if s.config else None,
                "database": s.config.get("database") if s.config else None,
            },
            "created_at": s.created_at.isoformat() if s.created_at else None
        } for s in sources]
    })


@router.get("/{source_id}/datasets", response_model=ResponseModel)
async def get_source_datasets(source_id: int, db: Session = Depends(get_db)):
    datasets = db.query(Dataset).filter(
        Dataset.source_id == source_id,
        Dataset.is_active == True
    ).all()

    return ResponseModel(data=[{
        "id": d.id,
        "name": d.name,
        "row_count": d.row_count,
        "column_count": d.column_count,
        "columns": d.columns,
        "created_at": d.created_at.isoformat() if d.created_at else None
    } for d in datasets])


class SaveDataSourceRequest(BaseModel):
    name: str
    source_type: str = "database"
    db_type: str
    host: str
    port: int
    username: str
    password: str
    database: str


class UpdateDataSourceRequest(BaseModel):
    name: Optional[str] = None
    db_type: Optional[str] = None
    host: Optional[str] = None
    port: Optional[int] = None
    username: Optional[str] = None
    password: Optional[str] = None
    database: Optional[str] = None


class ImportTablesFromSourceRequest(BaseModel):
    selected_tables: List[str]
    name_prefix: Optional[str] = ""


@router.post("/save", response_model=ResponseModel)
async def save_data_source(data: SaveDataSourceRequest, db: Session = Depends(get_db)):
    start_time = time.time()
    logger.info(f"保存数据源配置 | 名称: {data.name} | 类型: {data.db_type} | 主机: {data.host}:{data.port} | 数据库: {data.database}")

    try:
        config = {
            "db_type": data.db_type,
            "host": data.host,
            "port": data.port,
            "username": data.username,
            "password": data.password,
            "database": data.database
        }

        source = DataSource(
            name=data.name,
            source_type=data.source_type,
            config=config
        )
        db.add(source)
        db.commit()
        db.refresh(source)

        duration = (time.time() - start_time) * 1000
        logger.info(f"✅ 数据源保存成功 | ID: {source.id} | 名称: {source.name} | 耗时: {duration:.2f}ms")

        return ResponseModel(data={
            "id": source.id,
            "name": source.name,
            "message": "数据源配置已保存"
        })

    except Exception as e:
        log_exception(logger, "保存数据源", e, {"name": data.name})
        raise HTTPException(status_code=400, detail=f"保存失败: {str(e)}")


@router.get("/{source_id}", response_model=ResponseModel)
async def get_data_source_detail(source_id: int, db: Session = Depends(get_db)):
    source = db.query(DataSource).filter(
        DataSource.id == source_id,
        DataSource.is_active == True
    ).first()

    if not source:
        raise HTTPException(status_code=404, detail="数据源不存在")

    return ResponseModel(data={
        "id": source.id,
        "name": source.name,
        "source_type": source.source_type,
        "config": source.config,
        "created_at": source.created_at.isoformat() if source.created_at else None
    })


@router.put("/{source_id}", response_model=ResponseModel)
async def update_data_source(source_id: int, data: UpdateDataSourceRequest, db: Session = Depends(get_db)):
    start_time = time.time()
    source = db.query(DataSource).filter(
        DataSource.id == source_id,
        DataSource.is_active == True
    ).first()

    if not source:
        raise HTTPException(status_code=404, detail="数据源不存在")

    try:
        if data.name is not None:
            source.name = data.name

        if data.db_type is not None:
            source.config["db_type"] = data.db_type
        if data.host is not None:
            source.config["host"] = data.host
        if data.port is not None:
            source.config["port"] = data.port
        if data.username is not None:
            source.config["username"] = data.username
        if data.password is not None:
            source.config["password"] = data.password
        if data.database is not None:
            source.config["database"] = data.database

        db.commit()
        db.refresh(source)

        duration = (time.time() - start_time) * 1000
        logger.info(f"✅ 数据源更新成功 | ID: {source_id} | 新名称: {source.name} | 耗时: {duration:.2f}ms")

        return ResponseModel(data={
            "id": source.id,
            "name": source.name,
            "message": "数据源配置已更新"
        })

    except Exception as e:
        log_exception(logger, f"更新数据源({source_id})", e)
        raise HTTPException(status_code=400, detail=f"更新失败: {str(e)}")


@router.post("/{source_id}/test-connection", response_model=ResponseModel)
async def test_saved_connection(source_id: int, db: Session = Depends(get_db)):
    start_time = time.time()
    source = db.query(DataSource).filter(
        DataSource.id == source_id,
        DataSource.is_active == True
    ).first()

    if not source:
        raise HTTPException(status_code=404, detail="数据源不存在")

    config = source.config
    logger.info(f"测试已保存的数据源连接 | ID: {source_id} | 名称: {source.name} | 主机: {config.get('host')}:{config.get('port')}")

    try:
        connector = DatabaseConnector(
            db_type=config["db_type"],
            host=config["host"],
            port=config["port"],
            username=config["username"],
            password=config["password"],
            database=config["database"]
        )

        success = connector.test_connection()
        duration = (time.time() - start_time) * 1000

        if success:
            logger.info(f"✅ 已保存数据源连接成功 | ID: {source_id} | 耗时: {duration:.2f}ms")
            return ResponseModel(data={"connected": True, "message": "连接成功"})
        else:
            logger.warning(f"❌ 已保存数据源连接失败 | ID: {source_id}")
            return ResponseModel(code=400, message="连接失败")

    except Exception as e:
        duration = (time.time() - start_time) * 1000
        log_exception(logger, f"测试已保存数据源({source_id})连接", e)
        return ResponseModel(code=400, message=f"连接失败: {str(e)}")


@router.post("/{source_id}/tables", response_model=ResponseModel)
async def get_saved_source_tables(source_id: int, db: Session = Depends(get_db)):
    start_time = time.time()
    source = db.query(DataSource).filter(
        DataSource.id == source_id,
        DataSource.is_active == True
    ).first()

    if not source:
        raise HTTPException(status_code=404, detail="数据源不存在")

    config = source.config
    logger.info(f"从已保存数据源获取表列表 | ID: {source_id} | 名称: {source.name}")

    try:
        connector = DatabaseConnector(
            db_type=config["db_type"],
            host=config["host"],
            port=config["port"],
            username=config["username"],
            password=config["password"],
            database=config["database"]
        )

        tables = connector.get_tables()
        duration = (time.time() - start_time) * 1000
        
        logger.info(f"✅ 成功获取表列表 | 数据源ID: {source_id} | 表数量: {len(tables)} | 耗时: {duration:.2f}ms")

        return ResponseModel(data={
            "tables": tables,
            "total": len(tables),
            "source_name": source.name
        })

    except Exception as e:
        duration = (time.time() - start_time) * 1000
        log_exception(logger, f"获取已保存数据源({source_id})表列表", e)
        raise HTTPException(status_code=400, detail=f"获取表列表失败: {str(e)}")


@router.post("/{source_id}/table-preview", response_model=ResponseModel)
async def preview_saved_table(source_id: int, preview_data: dict, db: Session = Depends(get_db)):
    start_time = time.time()
    source = db.query(DataSource).filter(
        DataSource.id == source_id,
        DataSource.is_active == True
    ).first()

    if not source:
        raise HTTPException(status_code=404, detail="数据源不存在")

    table_name = preview_data.get("table_name", "unknown")
    limit = preview_data.get("limit", 10)
    config = source.config
    
    logger.info(f"预览已保存数据源的表 | 数据源ID: {source_id} | 表名: {table_name}")

    try:
        connector = DatabaseConnector(
            db_type=config["db_type"],
            host=config["host"],
            port=config["port"],
            username=config["username"],
            password=config["password"],
            database=config["database"]
        )

        df = connector.read_table(table_name)
        preview_df = df.head(limit)
        duration = (time.time() - start_time) * 1000
        
        logger.info(f"✅ 预览表成功 | 表: {table_name} | 总行数: {len(df)} | 耗时: {duration:.2f}ms")

        return ResponseModel(data={
            "table_name": table_name,
            "total_rows": len(df),
            "columns": list(df.columns),
            "data": preview_df.to_dict("records")
        })

    except Exception as e:
        log_exception(logger, f"预览已保存数据源({source_id})的表({table_name})", e)
        raise HTTPException(status_code=400, detail=f"预览失败: {str(e)}")


@router.post("/{source_id}/import-tables", response_model=ResponseModel)
async def import_tables_from_saved_source(
    source_id: int,
    data: ImportTablesFromSourceRequest,
    db: Session = Depends(get_db)
):
    start_time = time.time()
    
    source = db.query(DataSource).filter(
        DataSource.id == source_id,
        DataSource.is_active == True
    ).first()

    if not source:
        raise HTTPException(status_code=404, detail="数据源不存在")

    selected_tables = data.selected_tables
    config = source.config
    
    logger.info(f"从已保存数据源导入表 | 数据源ID: {source_id} | 名称: {source.name} | 表: {selected_tables}")

    if not selected_tables:
        raise HTTPException(status_code=400, detail="请至少选择一个表")

    try:
        connector = DatabaseConnector(
            db_type=config["db_type"],
            host=config["host"],
            port=config["port"],
            username=config["username"],
            password=config["password"],
            database=config["database"]
        )

        os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
        imported_datasets = []

        for table_name in selected_tables:
            table_start = time.time()
            
            try:
                df = connector.read_table(table_name)

                safe_table_name = "".join(c for c in table_name if c.isalnum() or c in "_-").strip()
                file_name = f"db_{source_id}_{safe_table_name}_{int(__import__('time').time())}.csv"
                file_path = os.path.join(settings.UPLOAD_DIR, file_name)
                
                DataService.save_to_file(df, file_path, "csv")

                dataset_name = f"{data.name_prefix}{table_name}" if data.name_prefix else table_name

                dataset = Dataset(
                    name=dataset_name,
                    description=f"来自数据源 [{source.name}] 的表: {table_name}",
                    source_id=source.id,
                    source_type="database",
                    file_path=file_path,
                    row_count=len(df),
                    column_count=len(df.columns),
                    columns=list(df.columns),
                    preview_data=df.head(5).to_dict("records")
                )
                db.add(dataset)
                db.commit()
                db.refresh(dataset)
                
                imported_datasets.append({
                    "id": dataset.id,
                    "name": dataset.name,
                    "table_name": table_name,
                    "row_count": dataset.row_count,
                    "column_count": dataset.column_count
                })
                
                logger.info(f"✅ 表导入成功 | 表: {table_name} | 数据集ID: {dataset.id}")
                
            except Exception as e:
                log_exception(logger, f"导入表({table_name})", e)
                logger.error(f"❌ 表导入失败: {table_name}")
                continue

        total_duration = (time.time() - start_time) * 1000
        
        logger.info(f"📊 导入完成 | 数据源ID: {source_id} | 成功: {len(imported_datasets)}/{len(selected_tables)} | 总耗时: {total_duration:.2f}ms")

        return ResponseModel(data={
            "source_id": source_id,
            "source_name": source.name,
            "imported_count": len(imported_datasets),
            "datasets": imported_datasets
        })

    except Exception as e:
        log_exception(logger, f"从已保存数据源({source_id})导入表", e)
        raise HTTPException(status_code=400, detail=f"导入失败: {str(e)}")


@router.delete("/{source_id}", response_model=ResponseModel)
async def delete_data_source(source_id: int, db: Session = Depends(get_db)):
    source = db.query(DataSource).filter(DataSource.id == source_id).first()
    if not source:
        raise HTTPException(status_code=404, detail="数据源不存在")

    source.is_active = False
    db.commit()

    datasets = db.query(Dataset).filter(Dataset.source_id == source_id).all()
    for d in datasets:
        d.is_active = False
    db.commit()

    return ResponseModel(message="数据源及相关数据集已删除")
