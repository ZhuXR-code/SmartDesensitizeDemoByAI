from sqlalchemy import create_engine, event
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.core.config import settings
import os

if settings.DATABASE_URL and ("mysql" in settings.DATABASE_URL or "postgresql" in settings.DATABASE_URL):
    db_url = settings.DATABASE_URL
elif settings.DATABASE_URL and "sqlite" in settings.DATABASE_URL:
    db_url = settings.DATABASE_URL
    db_dir = os.path.dirname(db_url.replace("sqlite:///.", "."))
    if db_dir:
        os.makedirs(db_dir, exist_ok=True)
else:
    db_url = f"mysql+pymysql://{settings.MYSQL_USER}:{settings.MYSQL_PASSWORD}@{settings.MYSQL_HOST}:{settings.MYSQL_PORT}/{settings.MYSQL_DATABASE}?charset=utf8mb4"

engine = create_engine(
    db_url,
    connect_args={"check_same_thread": False} if "sqlite" in db_url else {},
    pool_pre_ping=True,
    echo=settings.DEBUG
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    Base.metadata.create_all(bind=engine)
