import logging
import sys
from logging.handlers import RotatingFileHandler, TimedRotatingFileHandler
from pathlib import Path
from datetime import datetime
import os
import traceback


class LoggerConfig:
    _configured = False
    
    @classmethod
    def setup(cls, log_dir: str = "./logs", log_level: str = "INFO", app_name: str = "敏感信息脱敏平台"):
        if cls._configured:
            return
        
        log_path = Path(log_dir)
        log_path.mkdir(parents=True, exist_ok=True)
        
        date_str = datetime.now().strftime("%Y-%m-%d")
        
        root_logger = logging.getLogger()
        root_logger.setLevel(getattr(logging, log_level.upper(), logging.INFO))
        
        if root_logger.handlers:
            for handler in root_logger.handlers[:]:
                root_logger.removeHandler(handler)
        
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.DEBUG)
        console_format = logging.Formatter(
            '%(asctime)s | %(levelname)-8s | %(name)-25s | %(funcName)-20s | L%(lineno)-4d | %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        console_handler.setFormatter(console_format)
        root_logger.addHandler(console_handler)
        
        main_log_file = log_path / f"app_{date_str}.log"
        file_handler = RotatingFileHandler(
            main_log_file,
            maxBytes=50*1024*1024,
            backupCount=30,
            encoding='utf-8'
        )
        file_handler.setLevel(logging.DEBUG)
        file_format = logging.Formatter(
            '%(asctime)s | %(levelname)-8s | %(name)-25s | %(funcName)-20s | L%(lineno)-4d | %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(file_format)
        root_logger.addHandler(file_handler)
        
        error_log_file = log_path / f"error_{date_str}.log"
        error_handler = RotatingFileHandler(
            error_log_file,
            maxBytes=20*1024*1024,
            backupCount=10,
            encoding='utf-8'
        )
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(file_format)
        root_logger.addHandler(error_handler)
        
        api_log_file = log_path / f"api_{date_str}.log"
        api_handler = RotatingFileHandler(
            api_log_file,
            maxBytes=50*1024*1024,
            backupCount=15,
            encoding='utf-8'
        )
        api_handler.setLevel(logging.INFO)
        api_format = logging.Formatter(
            '%(asctime)s | %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        api_handler.setFormatter(api_format)
        api_logger = logging.getLogger('api_access')
        api_logger.addHandler(api_handler)
        api_logger.propagate = False
        
        db_log_file = log_path / f"database_{date_str}.log"
        db_handler = RotatingFileHandler(
            db_log_file,
            maxBytes=30*1024*1024,
            backupCount=10,
            encoding='utf-8'
        )
        db_handler.setLevel(logging.DEBUG)
        db_handler.setFormatter(file_format)
        db_logger = logging.getLogger('database')
        db_logger.addHandler(db_handler)
        db_logger.propagate = False
        
        security_log_file = log_path / f"security_{date_str}.log"
        security_handler = RotatingFileHandler(
            security_log_file,
            maxBytes=20*1024*1024,
            backupCount=30,
            encoding='utf-8'
        )
        security_handler.setLevel(logging.WARNING)
        security_handler.setFormatter(file_format)
        security_logger = logging.getLogger('security')
        security_logger.addHandler(security_handler)
        security_logger.propagate = False
        
        logging.getLogger('sqlalchemy.engine').setLevel(logging.WARNING)
        logging.getLogger('urllib3').setLevel(logging.WARNING)
        
        logger = logging.getLogger(__name__)
        logger.info(f"="*80)
        logger.info(f"{app_name} 日志系统初始化完成")
        logger.info(f"日志级别: {log_level}")
        logger.info(f"日志目录: {log_path.absolute()}")
        logger.info(f"主日志文件: {main_log_file}")
        logger.info(f"错误日志: {error_log_file}")
        logger.info(f"API访问日志: {api_log_file}")
        logger.info(f"数据库操作日志: {db_log_file}")
        logger.info(f"安全审计日志: {security_log_file}")
        logger.info(f"="*80)
        
        cls._configured = True
    
    @classmethod
    def get_logger(cls, name: str) -> logging.Logger:
        return logging.getLogger(name)


def get_logger(name: str = __name__) -> logging.Logger:
    return logging.getLogger(name)


def log_api_request(logger: logging.Logger, method: str, path: str, 
                    client_ip: str = None, query_params: dict = None,
                    request_body: dict = None):
    msg = f"API请求 | {method} {path}"
    if client_ip:
        msg += f" | 客户端IP: {client_ip}"
    if query_params:
        safe_params = {k: v for k, v in query_params.items() 
                      if k not in ['password', 'token', 'secret']}
        if safe_params:
            msg += f" | 参数: {safe_params}"
    logger.info(msg)
    
    api_logger = logging.getLogger('api_access')
    api_logger.info(msg)


def log_api_response(logger: logging.Logger, method: str, path: str,
                     status_code: int, duration_ms: float):
    msg = f"API响应 | {method} {path} | 状态码: {status_code} | 耗时: {duration_ms:.2f}ms"
    logger.debug(msg)
    
    api_logger = logging.getLogger('api_access')
    if status_code >= 400:
        api_logger.warning(msg)
    else:
        api_logger.info(msg)


def log_api_error(logger: logging.Logger, method: str, path: str,
                  error: Exception, status_code: int = 500):
    msg = f"API错误 | {method} {path} | 状态码: {status_code} | 错误: {str(error)}"
    logger.error(msg, exc_info=True)
    
    api_logger = logging.getLogger('api_access')
    api_logger.error(msg)


def log_db_operation(logger: logging.Logger, operation: str, table: str,
                     details: str = None, duration_ms: float = None):
    msg = f"DB操作 | {operation} | 表: {table}"
    if details:
        msg += f" | 详情: {details}"
    if duration_ms:
        msg += f" | 耗时: {duration_ms:.2f}ms"
    logger.debug(msg)
    
    db_logger = logging.getLogger('database')
    db_logger.info(msg)


def log_security_event(logger: logging.Logger, event_type: str,
                       details: str, severity: str = "WARNING",
                       user_id: str = None, ip: str = None):
    msg = f"安全事件 | {event_type}"
    if user_id:
        msg += f" | 用户ID: {user_id}"
    if ip:
        msg += f" | IP: {ip}"
    msg += f" | 详情: {details}"
    
    if severity == "CRITICAL":
        logger.critical(msg)
    elif severity == "ERROR":
        logger.error(msg)
    else:
        logger.warning(msg)
    
    security_logger = logging.getLogger('security')
    security_logger.warning(msg)


def log_exception(logger: logging.Logger, context: str, exception: Exception,
                  extra_data: dict = None):
    msg = f"异常捕获 | 上下文: {context} | 异常类型: {type(exception).__name__} | 异常信息: {str(exception)}"
    if extra_data:
        msg += f" | 额外数据: {extra_data}"
    logger.error(msg, exc_info=True)
