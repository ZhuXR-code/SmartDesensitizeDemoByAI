from pydantic_settings import BaseSettings
from typing import Optional
import os


class Settings(BaseSettings):
    APP_NAME: str = "敏感信息脱敏平台"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True
    
    DATABASE_URL: str = "sqlite:///./data/desensitization.db"
    
    MYSQL_HOST: str = "localhost"
    MYSQL_PORT: int = 3308
    MYSQL_USER: str = "root"
    MYSQL_PASSWORD: str = "msps"
    MYSQL_DATABASE: str = "desensitization"
    
    SECRET_KEY: str = "your-secret-key-change-this-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 480
    
    UPLOAD_DIR: str = "./uploads"
    MAX_UPLOAD_SIZE: int = 104857600
    
    LOG_LEVEL: str = "INFO"
    LOG_DIR: str = "./logs"
    
    DATA_RETENTION_DAYS: int = 30
    TEMP_FILE_RETENTION_HOURS: int = 24
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
