from cruds import update_algorithm, get_algorithm_by_name
from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, Form, File
from sqlalchemy.orm import Session
from database import get_db
from cruds import create_algorithm, get_algorithm, delete_algorithm
from schemas import AlgorithmCreate, AlgorithmResponse
from typing import List
from models import Algorithm
from cruds import save_algorithm_to_db
import os
import shutil

router = APIRouter(
    prefix="/algorithms",
    tags=["algorithms"]
)

@router.post("/", response_model=AlgorithmResponse)
def create_algorithm(algorithm: AlgorithmCreate, db: Session = Depends(get_db)):
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
def list_algorithm_files(prefix: str = Query(..., description="文件名前缀")):
    """返回匹配前缀的所有本地存储算法文件"""
    directory = prefix.rstrip("/")  # 确保去掉末尾 `/`

    if not os.path.exists(directory):
        raise HTTPException(status_code=500, detail=f"存储路径不存在: {directory}")

    if not os.path.isdir(directory):
        raise HTTPException(status_code=400, detail=f"路径不是一个目录: {directory}")

    # 筛选匹配前缀的文件
    files = [
        f for f in os.listdir(directory)
    ]

    if not files:
        raise HTTPException(status_code=404, detail="未找到符合条件的算法文件")

    return {"files": files}

@router.get("/{algorithm_id:int}", response_model=AlgorithmResponse)
def read_algorithm(algorithm_id: int, db: Session = Depends(get_db)):
    """根据ID获取算法"""
    algorithm = get_algorithm(db, algorithm_id)
    if not algorithm:
        raise HTTPException(status_code=404, detail="Algorithm not found")
    return algorithm

@router.delete("/{algorithm_id}")
def delete_algorithm(algorithm_id: int, db: Session = Depends(get_db)):
    """删除算法"""
    if not delete_algorithm(db, algorithm_id):
        raise HTTPException(status_code=404, detail="Algorithm not found")
    return {"message": "Algorithm deleted successfully"}


@router.post("/save-algorithm/")
async def save_algorithm(
    name: str = Form(...), 
    file: UploadFile = File(...), 
    file_path: str = Form(...),  # 让前端传入完整路径
    db: Session = Depends(get_db)
    ):

    directory = os.path.dirname(file_path)

    if not os.path.exists(directory):
        os.makedirs(directory)
    # 2. 保存文件到本地
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    # 3. 查询数据库是否已有该算法
    existing_algo = get_algorithm_by_name(db, name)
    if existing_algo:
        # 4. 更新数据库
        update_algorithm(db, existing_algo.id, name, file_path)
        return {"message": "Algorithm updated successfully", "id": existing_algo.id, "file_path": file_path}
    else:
        # 5. 插入新算法
        algo_id = save_algorithm_to_db(db, name, file_path)
        return {"message": "Algorithm saved successfully", "id": algo_id, "file_path": file_path}
    
@router.get("/get-algorithm-code/")
def get_algorithm_code(file_path: str):
    """获取本地存储的算法代码"""
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="算法代码不存在或无法读取")

    with open(file_path, "r", encoding="utf-8") as f:
        code = f.read()

    return {"code": code}


@router.put("/update-algorithm/{algorithm_id}")
def update_algorithm(algorithm_id: int, name: str = Form(...), file_path: str = Form(...), db: Session = Depends(get_db)):
    """更新算法信息（更新 name 和 file_path）"""
    updated_algorithm = update_algorithm(db, algorithm_id, name, file_path)
    if not updated_algorithm:
        raise HTTPException(status_code=404, detail="Algorithm not found")
    return {"message": "算法更新成功", "algorithm": AlgorithmResponse.model_validate(updated_algorithm)}




