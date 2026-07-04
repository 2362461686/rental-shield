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


def init_db():
    """初始化数据库：创建所有表 + 运行迁移"""
    from backend.db.models import Base
    Base.metadata.create_all(bind=engine)
    # 运行 SQLite 迁移（添加新增列和表）
    try:
        from backend.db.migrations import run_migrations
        run_migrations()
    except Exception as e:
        print(f"⚠️  迁移执行失败（可能表已存在）: {e}")


def get_db() -> Session:
    """FastAPI 依赖注入：每个请求获取独立数据库会话，用完自动关闭"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
