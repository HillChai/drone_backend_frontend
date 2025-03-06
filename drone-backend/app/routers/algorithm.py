from minio_client import upload_file_to_minio
from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, Form
from sqlalchemy.orm import Session
from database import get_db
from cruds import create_algorithm, get_algorithm, delete_algorithm
from schemas import AlgorithmCreate, AlgorithmResponse
from typing import List
from models import Algorithm
from cruds import save_algorithm_to_db


router = APIRouter(
    prefix="/algorithms",
    tags=["algorithms"]
)

@router.post("/", response_model=AlgorithmResponse)
def create_algorithm_api(algorithm: AlgorithmCreate, db: Session = Depends(get_db)):
    """创建算法（避免 `name + file_path` 重复）"""
    existing_algorithm = db.query(Algorithm).filter(
        Algorithm.name == algorithm.name,
        Algorithm.file_path == algorithm.file_path
    ).first()

    if existing_algorithm:
        raise HTTPException(status_code=400, detail="Algorithm already exists with this name and file_path")

    return create_algorithm(db, algorithm)

@router.get("/", response_model=dict)
def get_algorithms(
    db: Session = Depends(get_db),
    page: int = Query(1, alias="page"),
    limit: int = Query(10, alias="limit"),
):
    """获取分页算法"""
    total = db.query(Algorithm).count()
    items = db.query(Algorithm).offset((page - 1) * limit).limit(limit).all()

    return {
        "total": total,
        "items": [AlgorithmResponse.model_validate(algorithm) for algorithm in items]
    }

@router.get("/{algorithm_id}", response_model=AlgorithmResponse)
def read_algorithm_api(algorithm_id: int, db: Session = Depends(get_db)):
    """根据ID获取算法"""
    algorithm = get_algorithm(db, algorithm_id)
    if not algorithm:
        raise HTTPException(status_code=404, detail="Algorithm not found")
    return algorithm

@router.delete("/{algorithm_id}")
def delete_algorithm_api(algorithm_id: int, db: Session = Depends(get_db)):
    """删除算法"""
    if not delete_algorithm(db, algorithm_id):
        raise HTTPException(status_code=404, detail="Algorithm not found")
    return {"message": "Algorithm deleted successfully"}


@router.post("/upload-algorithm/")
async def upload_algorithm(file: UploadFile):
    """ 上传 Python 代码到 MinIO """
    file_url = upload_file_to_minio(file)
    return {"file_url": file_url}

@router.post("/save-algorithm/")
async def save_algorithm(name: str = Form(...), file_url: str = Form(...)):
    """ 保存算法信息到数据库 """
    algo_id = save_algorithm_to_db(name, file_url)
    return {"message": "Algorithm saved successfully", "id": algo_id}