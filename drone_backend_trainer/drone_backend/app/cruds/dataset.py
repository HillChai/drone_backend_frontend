from sqlalchemy.orm import Session
from models import Dataset
from schemas import DatasetCreate

def create_dataset(db: Session, dataset: DatasetCreate):
    """创建新的数据集"""
    db_dataset = Dataset(**dataset.dict())
    db.add(db_dataset)
    db.commit()
    db.refresh(db_dataset)
    return db_dataset

def get_datasets(db: Session):
    """获取所有数据集"""
    return db.query(Dataset).all()

def get_dataset(db: Session, dataset_id: int):
    """根据ID获取数据集"""
    return db.query(Dataset).filter(Dataset.id == dataset_id).first()

def delete_dataset(db: Session, dataset_id: int):
    """根据ID删除数据集"""
    dataset = db.query(Dataset).filter(Dataset.id == dataset_id).first()
    if dataset:
        db.delete(dataset)
        db.commit()
        return True
    return False
