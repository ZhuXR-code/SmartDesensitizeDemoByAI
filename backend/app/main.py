from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
import os
import time
import traceback

from app.core.config import settings
from app.db.database import init_db
from app.api import dataset, detection, desensitization, dashboard, datasource, report, platform_report, ai
from app.core.logger import LoggerConfig, get_logger, log_api_request, log_api_response, log_api_error

LoggerConfig.setup(
    log_dir=settings.LOG_DIR,
    log_level=settings.LOG_LEVEL,
    app_name=settings.APP_NAME
)

logger = get_logger(__name__)

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="敏感信息识别与脱敏平台 API",
    docs_url="/api/docs",
    redoc_url="/api/redoc"
)

@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    
    client_ip = request.client.host if request.client else "unknown"
    method = request.method
    path = request.url.path
    
    log_api_request(logger, method, path, client_ip=client_ip)
    
    try:
        response = await call_next(request)
        
        process_time = (time.time() - start_time) * 1000
        log_api_response(logger, method, path, response.status_code, process_time)
        
        response.headers["X-Process-Time"] = f"{process_time:.2f}ms"
        return response
        
    except Exception as e:
        process_time = (time.time() - start_time) * 1000
        log_api_error(logger, method, path, e)
        
        logger.error(f"未处理的异常 | 路径: {path} | 异常: {str(e)}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={
                "code": 500,
                "message": f"服务器内部错误: {str(e)}",
                "data": None
            }
        )

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=settings.UPLOAD_DIR), name="uploads")

app.include_router(dashboard.router)
app.include_router(dataset.router)
app.include_router(datasource.router)
app.include_router(detection.router)
app.include_router(desensitization.router)
app.include_router(report.router)
app.include_router(platform_report.router)
app.include_router(ai.router)


@app.on_event("startup")
async def startup_event():
    logger.info("="*80)
    logger.info(f"启动 {settings.APP_NAME} v{settings.APP_VERSION}")
    logger.info(f"数据库连接: {settings.DATABASE_URL}")
    logger.info(f"上传目录: {settings.UPLOAD_DIR}")
    logger.info(f"调试模式: {settings.DEBUG}")
    logger.info("="*80)
    
    try:
        init_db()
        logger.info("✅ 数据库初始化成功")
    except Exception as e:
        logger.error(f"❌ 数据库初始化失败: {e}", exc_info=True)
        raise


@app.get("/api/health")
async def health_check():
    return {"status": "ok", "version": settings.APP_VERSION}


@app.get("/")
async def root():
    return {
        "message": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "docs": "/api/docs"
    }
