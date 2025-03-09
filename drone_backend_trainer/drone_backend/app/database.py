from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import os

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://admin:password@db:5432/drone_system")

# 创建数据库引擎
engine = create_engine(DATABASE_URL, echo=True)

# 创建数据库会话
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 基础模型
Base = declarative_base()

# 依赖函数（获取数据库会话）
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
