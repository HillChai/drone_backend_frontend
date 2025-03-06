from datetime import datetime
from database import Base
from sqlalchemy import Column, Integer, String, ForeignKey, JSON, DateTime, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

class Dataset(Base):
    __tablename__ = "datasets"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String, nullable=False, unique=True)  # 避免重复数据集名称
    description = Column(String, nullable=True)  
    file_path = Column(String, nullable=False)  # unique=True 视业务需求
    created_at = Column(DateTime, server_default=func.now())  # 确保数据库层自动填充时间戳


class Algorithm(Base):
    __tablename__ = "algorithms"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String, nullable=False) 
    description = Column(String, nullable=True)  # 保留 String 类型，避免 Text 过大
    file_path = Column(String, nullable=False, unique=True)  # 确保目录路径唯一
    created_at = Column(DateTime, server_default=func.now())  # 数据库自动填充时间

    # **组合唯一约束**
    __table_args__ = (UniqueConstraint("name", "file_path", name="uq_algorithm_name_path"),)


class History(Base):
    __tablename__ = "history"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    dataset_id = Column(Integer, ForeignKey("datasets.id", ondelete="CASCADE"))
    algorithm_id = Column(Integer, ForeignKey("algorithms.id", ondelete="CASCADE"))
    status = Column(String, nullable=False, default="pending")  # 训练/推理状态
    results_path = Column(String, nullable=True)  # 训练或推理结果存储路径（如果有文件）
    created_at = Column(DateTime, server_default=func.now())  # 记录任务开始时间
    completed_at = Column(DateTime, nullable=True)  # 记录任务完成时间

    dataset = relationship("Dataset")
    algorithm = relationship("Algorithm")
