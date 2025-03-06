from fastapi import FastAPI
from routers import dataset, algorithm, history  # 确保 import 的是正确的 router 名称
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="无人机检测分类系统 API")

# 允许跨域
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 允许所有前端访问
    allow_credentials=True,
    allow_methods=["*"],  # 允许所有 HTTP 方法 (GET, POST, DELETE, etc.)
    allow_headers=["*"],  # 允许所有 HTTP 头
)

# ✅ 删除 `Base.metadata.create_all(bind=engine)`，避免和 Alembic 迁移冲突

# 注册 API 路由
app.include_router(dataset.router)
app.include_router(algorithm.router)
app.include_router(history.router)

@app.get("/")
def read_root():
    return {"message": "无人机检测分类系统 API 正在运行"}
