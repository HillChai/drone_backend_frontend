from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class AlgorithmBase(BaseModel):
    name: str
    description: Optional[str] = None
    file_path: str  # 作为算法的主目录

class AlgorithmCreate(AlgorithmBase):
    pass

class AlgorithmResponse(AlgorithmBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True  # ✅ Pydantic v2 适配 SQLAlchemy
