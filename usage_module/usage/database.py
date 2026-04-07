"""数据库连接与会话 — 仅在使用自带 user_llm_usage 表时需要"""
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from usage.config import settings

# 未配置 DATABASE_URL 时由接入方传入 db session，不创建 engine
engine = None
SessionLocal = None
Base = declarative_base()

if settings.DATABASE_URL:
    engine = create_engine(
        settings.DATABASE_URL,
        pool_pre_ping=True,
        echo=False,
    )
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    """依赖注入：获取 DB 会话。需设置 USAGE_DATABASE_URL；或由接入方 dependency_overrides 替换。"""
    if SessionLocal is None:
        raise RuntimeError(
            "usage_module: USAGE_DATABASE_URL not set. Set it to your DB URL or override usage.deps.get_db with your get_db."
        )
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """创建本模块声明的表（user_llm_usage、usage_records）"""
    if engine is None:
        return
    from usage import models  # noqa: F401
    Base.metadata.create_all(bind=engine)
