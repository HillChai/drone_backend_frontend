from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from database import get_db
from cruds import (
    create_history, get_histories, get_history, 
    update_history_status, update_history_results, delete_history
)
from schemas import HistoryCreate, HistoryResponse
from typing import List
from models import History

router = APIRouter(
    prefix="/history",
    tags=["history"]
)

@router.post("/", response_model=HistoryResponse)
def create_history(history: HistoryCreate, db: Session = Depends(get_db)):
    """创建历史记录"""
    return create_history(db, history)

@router.get("/", response_model=dict)
def read_histories(
    db: Session = Depends(get_db),
    page: int = Query(1, alias="page"),
    limit: int = Query(10, alias="limit"),
    ):
    """获取分页算法"""
    total = db.query(History).count()
    items = db.query(History).offset((page - 1) * limit).limit(limit).all()
    """获取所有历史记录"""
    return {
        "total": total,
        "items": [HistoryResponse.model_validate(history) for history in items]
    }

@router.get("/{history_id:int}", response_model=HistoryResponse)
def read_history(history_id: int, db: Session = Depends(get_db)):
    """根据ID获取历史记录"""
    history = get_history(db, history_id)
    if not history:
        raise HTTPException(status_code=404, detail="History not found")
    return history

@router.put("/{history_id}/status")
def update_history_status(history_id: int, new_status: str, db: Session = Depends(get_db)):
    """更新历史记录状态"""
    history = update_history_status(db, history_id, new_status)
    if not history:
        raise HTTPException(status_code=404, detail="History not found")
    return history

@router.put("/{history_id}/results")
def update_history_results(history_id: int, results_path: str, db: Session = Depends(get_db)):
    """更新历史记录的推理/训练结果路径，并记录完成时间"""
    history = update_history_results(db, history_id, results_path)
    if not history:
        raise HTTPException(status_code=404, detail="History not found")
    return history

@router.delete("/{history_id}")
def delete_history(history_id: int, db: Session = Depends(get_db)):
    """删除历史记录"""
    if not delete_history(db, history_id):
        raise HTTPException(status_code=404, detail="History not found")
    return {"message": "History deleted successfully"}
