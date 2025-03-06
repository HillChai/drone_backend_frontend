from sqlalchemy.orm import Session
from models import Algorithm
from schemas import AlgorithmCreate
from database import get_db

def create_algorithm(db: Session, algorithm: AlgorithmCreate):
    """创建新的算法（避免重复插入相同 `name` + `file_path` 组合）"""
    existing_algorithm = db.query(Algorithm).filter(
        Algorithm.name == algorithm.name,
        Algorithm.file_path == algorithm.file_path
    ).first()

    if existing_algorithm:
        print(f"⚠️ 该算法已存在: {algorithm.name} ({algorithm.file_path})")
        return existing_algorithm  # 返回已有算法，避免重复插入

    db_algorithm = Algorithm(**algorithm.model_dump())  # Pydantic v2 兼容
    db.add(db_algorithm)
    db.commit()
    db.refresh(db_algorithm)
    return db_algorithm

def get_algorithms(db: Session):
    """获取所有算法"""
    return db.query(Algorithm).all()

def get_algorithm(db: Session, algorithm_id: int):
    """根据ID获取算法"""
    return db.query(Algorithm).filter(Algorithm.id == algorithm_id).first()

def delete_algorithm(db: Session, algorithm_id: int):
    """根据ID删除算法"""
    algorithm = db.query(Algorithm).filter(Algorithm.id == algorithm_id).first()
    if algorithm:
        db.delete(algorithm)
        db.commit()
        return True
    return False

def save_algorithm_to_db(db: Session, name: str, file_url: str):
    """存储算法信息到数据库"""
    algorithm = Algorithm(name=name, file_path=file_url)
    db.add(algorithm)
    db.commit()
    db.refresh(algorithm)
    return algorithm.id
