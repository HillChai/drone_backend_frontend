from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class DatasetBase(BaseModel):
    name: str
    description: Optional[str] = None
    file_path: str

class DatasetCreate(DatasetBase):
    pass

class DatasetResponse(DatasetBase):
    id: int
    name: str
    created_at: datetime

    class Config:
        from_attributes = True  # ✅ 确保 FastAPI 能转换 SQLAlchemy 对象
