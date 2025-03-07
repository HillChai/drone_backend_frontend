from sqlalchemy.orm import Session
from models import History
from schemas import HistoryCreate
from datetime import datetime

def create_history(db: Session, history: HistoryCreate):
    """创建历史记录"""
    db_history = History(**history.model_dump())  # Pydantic v2 兼容
    db.add(db_history)
    db.commit()
    db.refresh(db_history)
    return db_history

def get_histories(db: Session):
    """获取所有历史记录"""
    return db.query(History).all()

def get_history(db: Session, history_id: int):
    """根据ID获取历史记录"""
    return db.query(History).filter(History.id == history_id).first()

def update_history_status(db: Session, history_id: int, new_status: str):
    """更新历史记录的状态"""
    history = db.query(History).filter(History.id == history_id).first()
    if history:
        history.status = new_status
        db.commit()
        db.refresh(history)
        return history
    return None

def update_history_results(db: Session, history_id: int, results_path: str):
    """更新历史记录的推理/训练结果路径，并标记完成时间"""
    history = db.query(History).filter(History.id == history_id).first()
    if history:
        history.results_path = results_path
        history.completed_at = datetime.now()
        db.commit()
        db.refresh(history)
        return history
    return None

def delete_history(db: Session, history_id: int):
    """根据ID删除历史记录"""
    history = db.query(History).filter(History.id == history_id).first()
    if history:
        db.delete(history)
        db.commit()
        return True
    return False
