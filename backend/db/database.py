"""数据库引擎和会话管理（FastAPI 依赖注入模式）"""
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

# 使用绝对路径解析 rental.db（在项目根目录下）
_PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DB_PATH = os.path.join(_PROJECT_ROOT, "rental.db")
DATABASE_URL = f"sqlite:///{DB_PATH}"

engine = create_engine(DATABASE_URL, echo=False, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine)


def get_db() -> Session:
    """FastAPI 依赖注入：每个请求获取独立数据库会话，用完自动关闭"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
