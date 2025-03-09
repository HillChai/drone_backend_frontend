from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class HistoryBase(BaseModel):
    dataset_id: int
    algorithm_id: int
    status: str = "pending"
    results_path: Optional[str] = None  # 训练/推理结果存储路径

class HistoryCreate(HistoryBase):
    pass

class HistoryResponse(HistoryBase):
    id: int
    created_at: datetime
    completed_at: Optional[datetime] = None

    class Config:
        from_attributes = True  # ✅ 适配 FastAPI
