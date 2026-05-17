from typing import Dict, List, Any, Optional
import pandas as pd
from urllib.parse import quote_plus
import time

from app.core.logger import get_logger, log_db_operation, log_exception

logger = get_logger(__name__)


class DatabaseConnector:
    def __init__(self, db_type: str, host: str, port: int, username: str, 
                 password: str, database: str):
        self.db_type = db_type
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.database = database
        self.engine = None
    
    def _get_connection_string(self) -> str:
        if self.db_type == "mysql":
            conn_str = f"mysql+pymysql://{self.username}:{quote_plus(self.password)}@{self.host}:{self.port}/{self.database}"
        elif self.db_type == "postgresql":
            conn_str = f"postgresql://{self.username}:{quote_plus(self.password)}@{self.host}:{self.port}/{self.database}"
        elif self.db_type == "oracle":
            conn_str = f"oracle+cx_oracle://{self.username}:{quote_plus(self.password)}@{self.host}:{self.port}/{self.database}"
        elif self.db_type == "sqlserver":
            conn_str = f"mssql+pymssql://{self.username}:{quote_plus(self.password)}@{self.host}:{self.port}/{self.database}"
        else:
            raise ValueError(f"不支持的数据库类型: {self.db_type}")
        
        logger.debug(f"生成连接字符串 | 类型: {self.db_type} | 主机: {self.host}:{self.port}")
        return conn_str
    
    def test_connection(self) -> bool:
        start_time = time.time()
        logger.info(f"测试数据库连接 | 类型: {self.db_type} | 主机: {self.host}:{self.port} | 数据库: {self.database}")
        
        try:
            from sqlalchemy import create_engine, text
            self.engine = create_engine(self._get_connection_string(), pool_pre_ping=True)
            
            logger.debug("正在执行测试查询...")
            with self.engine.connect() as conn:
                result = conn.execute(text("SELECT 1"))
                result.fetchone()
            
            duration = (time.time() - start_time) * 1000
            log_db_operation(logger, "TEST_CONNECTION", self.database, f"连接测试成功", duration)
            logger.info(f"✅ 数据库连接成功 | 耗时: {duration:.2f}ms")
            return True
        except Exception as e:
            duration = (time.time() - start_time) * 1000
            log_exception(logger, "test_connection", e, {
                "db_type": self.db_type,
                "host": f"{self.host}:{self.port}",
                "database": self.database,
                "duration_ms": duration
            })
            print(f"数据库连接测试失败: {e}")
            return False
    
    def execute_query(self, query: str) -> pd.DataFrame:
        start_time = time.time()
        logger.debug(f"执行SQL查询 | 查询长度: {len(query)} 字符")
        
        if not self.engine:
            from sqlalchemy import create_engine
            self.engine = create_engine(self._get_connection_string(), pool_pre_ping=True)
        
        try:
            df = pd.read_sql(query, self.engine)
            duration = (time.time() - start_time) * 1000
            
            log_db_operation(logger, "QUERY", "custom", f"返回{len(df)}行,{len(df.columns)}列", duration)
            logger.info(f"✅ SQL查询完成 | 返回行数: {len(df)} | 耗时: {duration:.2f}ms")
            
            return df
        except Exception as e:
            log_exception(logger, "execute_query", e, {"query_length": len(query)})
            raise
    
    def get_tables(self) -> List[str]:
        start_time = time.time()
        logger.info(f"获取数据库表列表 | 数据库: {self.database}")
        
        if not self.engine:
            from sqlalchemy import create_engine
            self.engine = create_engine(self._get_connection_string(), pool_pre_ping=True)
        
        try:
            from sqlalchemy import inspect
            inspector = inspect(self.engine)
            tables = inspector.get_table_names()
            duration = (time.time() - start_time) * 1000
            
            log_db_operation(logger, "GET_TABLES", self.database, f"获取到{len(tables)}个表", duration)
            logger.info(f"✅ 获取表列表成功 | 表数量: {len(tables)} | 表名: {tables} | 耗时: {duration:.2f}ms")
            
            return tables
        except Exception as e:
            log_exception(logger, "get_tables", e, {"database": self.database})
            raise
    
    def read_table(self, table_name: str) -> pd.DataFrame:
        start_time = time.time()
        logger.info(f"读取表数据 | 表名: {table_name}")
        
        if not self.engine:
            from sqlalchemy import create_engine
            self.engine = create_engine(self._get_connection_string(), pool_pre_ping=True)
        
        try:
            df = pd.read_sql_table(table_name, self.engine)
            duration = (time.time() - start_time) * 1000
            
            log_db_operation(logger, "READ_TABLE", table_name, f"读取{len(df)}行,{len(df.columns)}列", duration)
            logger.info(f"✅ 读取表成功 | 表: {table_name} | 行数: {len(df)} | 列数: {len(df.columns)} | 耗时: {duration:.2f}ms")
            
            return df
        except Exception as e:
            log_exception(logger, f"read_table({table_name})", e)
            raise
    
    def write_table(self, df: pd.DataFrame, table_name: str, if_exists: str = "replace") -> bool:
        start_time = time.time()
        logger.info(f"写入数据到表 | 目标表: {table_name} | 数据行数: {len(df)} | 模式: {if_exists}")
        
        if not self.engine:
            from sqlalchemy import create_engine
            self.engine = create_engine(self._get_connection_string(), pool_pre_ping=True)
        
        try:
            df.to_sql(table_name, self.engine, if_exists=if_exists, index=False)
            duration = (time.time() - start_time) * 1000
            
            log_db_operation(logger, "WRITE_TABLE", table_name, f"写入{len(df)}行,模式:{if_exists}", duration)
            logger.info(f"✅ 写入表成功 | 表: {table_name} | 行数: {len(df)} | 耗时: {duration:.2f}ms")
            
            return True
        except Exception as e:
            log_exception(logger, f"write_table({table_name})", e, {"rows": len(df), "mode": if_exists})
            print(f"写入表失败: {e}")
            return False
