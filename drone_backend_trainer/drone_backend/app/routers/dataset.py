from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from database import get_db
from cruds import create_dataset, get_dataset, delete_dataset
from schemas import DatasetCreate, DatasetResponse
from typing import List
from models import Dataset
from pydantic import BaseModel

router = APIRouter(
    prefix="/datasets",
    tags=["datasets"]
)

@router.post("/", response_model=DatasetResponse)
def create_dataset(dataset: DatasetCreate, db: Session = Depends(get_db)):
    """创建数据集"""
    return create_dataset(db, dataset)

@router.get("/", response_model=dict)
def get_datasets(
    db: Session = Depends(get_db),
    page: int = Query(1, alias="page"),
    limit: int = Query(10, alias="limit"),
):
    """获取分页数据集"""
    total = db.query(Dataset).count()
    items = db.query(Dataset).offset((page - 1) * limit).limit(limit).all()

    # ✅ 确保 `from_attributes=True` 之后，`from_orm()` 可以正常工作
    return {
        "total": total,
        "items": [DatasetResponse.model_validate(dataset) for dataset in items]
    }


@router.get("/{dataset_id}", response_model=DatasetResponse)
def read_dataset(dataset_id: int, db: Session = Depends(get_db)):
    """根据ID获取数据集"""
    dataset = get_dataset(db, dataset_id)
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found")
    return dataset

@router.delete("/{dataset_id}")
def delete_dataset(dataset_id: int, db: Session = Depends(get_db)):
    """删除数据集"""
    if not delete_dataset(db, dataset_id):
        raise HTTPException(status_code=404, detail="Dataset not found")
    return {"message": "Dataset deleted successfully"}

class DatasetUpdateDescription(BaseModel):
    description: str

@router.put("/{dataset_id}/description")
def update_dataset_description(
    dataset_id: int, 
    data: DatasetUpdateDescription, 
    db: Session = Depends(get_db)
):
    """更新数据集的描述"""
    dataset = db.query(Dataset).filter(Dataset.id == dataset_id).first()
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found")
    
    dataset.description = data.description
    db.commit()
    db.refresh(dataset)
    
    return {"message": "Description updated successfully"}