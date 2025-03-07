from cruds import update_algorithm, get_algorithm_by_name
from minio_client import check_file_exists, get_algorithm_code, list_algorithm_files, upload_file_to_minio
from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, Form, File
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

@router.get("/list-algorithm-files/")
def list_algorithm_files_api(prefix: str = Query(..., description="MinIO 文件路径前缀")):
    """返回匹配的所有算法文件"""
    files = list_algorithm_files(prefix)
    if not files:
        raise HTTPException(status_code=404, detail="未找到相关算法文件")
    return {"files": files}

@router.get("/{algorithm_id:int}", response_model=AlgorithmResponse)
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


@router.post("/save-algorithm/")
async def save_algorithm(
    name: str = Form(...), 
    file: UploadFile = File(...), 
    db: Session = Depends(get_db)
):
    """ 上传或替换 MinIO 文件，并更新 PostgreSQL 记录 """
    
    # 1. 生成 MinIO 存储路径
    file_url = f"algorithms/{name}"
    exists = check_file_exists(file_url)  # 检查 MinIO 是否已有该文件

    # 2. 上传或替换 MinIO 文件
    uploaded_url = upload_file_to_minio(file, file_url, replace=True)

    # 3. 查询数据库是否已有该算法
    existing_algo = get_algorithm_by_name(db, name)

    if existing_algo:
        # 4. 更新数据库
        update_algorithm(db, existing_algo.id, name, uploaded_url)
        return {"message": "Algorithm updated successfully", "id": existing_algo.id, "file_url": uploaded_url}
    else:
        # 5. 插入新算法
        algo_id = save_algorithm_to_db(db, name, uploaded_url)
        return {"message": "Algorithm saved successfully", "id": algo_id, "file_url": uploaded_url}

@router.get("/get-algorithm-code/")
def get_algorithm_code_api(file_path: str):
    """获取 MinIO 里的算法代码"""
    code = get_algorithm_code(file_path)
    if not code:
        raise HTTPException(status_code=404, detail="算法代码不存在或无法读取")
    return {"code": code}


@router.put("/update-algorithm/{algorithm_id}")
def update_algorithm_api(algorithm_id: int, name: str = Form(...), file_url: str = Form(...), db: Session = Depends(get_db)):
    """更新算法信息（更新 name 和 file_path）"""
    updated_algorithm = update_algorithm(db, algorithm_id, name, file_url)
    if not updated_algorithm:
        raise HTTPException(status_code=404, detail="Algorithm not found")
    return {"message": "算法更新成功", "algorithm": AlgorithmResponse.model_validate(updated_algorithm)}



