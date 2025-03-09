from fastapi import FastAPI
from routers import dataset, algorithm, history  # 确保 import 的是正确的 router 名称
from fastapi.middleware.cors import CORSMiddleware
import requests
import asyncio
from starlette.responses import StreamingResponse
import docker
import os

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



# 存储训练状态
training_status = {"epoch": 0, "accuracy": 0.0, "loss": 0.0}

async def stream_sse():
    """ 监听 `drone_trainer` 训练日志 """
    url = "http://drone_trainer:8001/train_progress"
    try:
        with requests.get(url, stream=True) as response:
            for line in response.iter_lines():
                if line:
                    data = line.decode("utf-8").replace("data: ", "")
                    print("📩 收到训练数据:", data)
                    global training_status
                    training_status = eval(data)  # 存入全局变量
    except Exception as e:
        print(f"❌ SSE 连接失败: {e}")

@app.get("/subscribe")
async def subscribe():
    return StreamingResponse(stream_sse(), media_type="text/event-stream")

@app.get("/status")
async def get_status():
    """获取当前训练状态"""
    return training_status


# 使用 Ubuntu 远程 API 连接 Docker
DOCKER_API_URL = "unix://var/run/docker.sock"

try:
    client = docker.DockerClient(base_url=DOCKER_API_URL)
    print("✅ 成功连接到 Docker API")
except Exception as e:
    print(f"❌ 连接 Docker 失败: {e}")

# 容器信息
CONTAINER_NAME = "cardrf"
IMAGE_NAME = "cardrf:latest"
MOUNT_ALGORITHMS = "/CardRF"
MOUNT_DATASETS = "/CardRFDataset"
MOUNT_RESULTS = "/SaveFolders"
HOST_ALGORITHMS = "/home/ccc/npz/MultiViTOnRFDatasets/DeepLearning/CardRF"
HOST_DATASETS = "/mnt/ssd/CardRFDataset"
HOST_RESULTS = "/home/ccc/npz/DeepLearning/CardRF"

@app.post("/start_training")
def start_training():
    """ 启动容器并运行 CatBoost 训练 """
    try:
        # 先检查容器是否已存在
        existing_containers = client.containers.list(all=True, filters={"name": CONTAINER_NAME})
        if existing_containers:
            return {"message": "容器已经存在，请先停止"}

        # 运行容器
        container = client.containers.run(
            IMAGE_NAME,
            name=CONTAINER_NAME,
            detach=True,
            tty=True,
            stdin_open=True,
            runtime="nvidia",  # 让 GPU 可用
            volumes={
                HOST_ALGORITHMS: {'bind': MOUNT_ALGORITHMS, 'mode': 'rw'},
                HOST_DATASETS: {'bind': MOUNT_DATASETS, 'mode': 'rw'},
                HOST_RESULTS: {'bind': MOUNT_RESULTS, 'mode': 'rw'},
            },
            command="/bin/bash",
        )

        return {"message": "容器已启动", "container_id": container.id}
    except Exception as e:
        return {"error": str(e)}

# @app.post("/run_training_script")
# async def run_training_script():
#     try:
#         container = client.containers.get(CONTAINER_NAME)
#         # ✅ 让日志写入 /dev/stdout，使 `docker logs` 可见
#         command = "python3 /CardRF/Recommend/MyTrain.py"
#         exec_result = container.exec_run(
#             ["sh", "-c", command],
#             stream=True
#         )
#         return StreamingResponse(exec_result.output, media_type="text/event-stream")
#     except Exception as e:
#         return {"error": str(e)}

import re

@app.post("/run_training_script")
async def run_training_script():
    try:
        container = client.containers.get(CONTAINER_NAME)
        command = "python3 /CardRF/Recommend/MyTrain.py"
        
        exec_result = container.exec_run(
            ["sh", "-c", command],
            stream=True
        )

        def filter_logs():
            """
            过滤 loss 和 accuracy 相关的信息，并发送给前端
            """
            loss_pattern = re.compile(r"loss:\s*([\d\.]+)", re.IGNORECASE)
            acc_pattern = re.compile(r"accuracy:\s*([\d\.]+)", re.IGNORECASE)

            for line in exec_result.output:
                decoded_line = line.decode("utf-8").strip()
                
                loss_match = loss_pattern.search(decoded_line)
                acc_match = acc_pattern.search(decoded_line)

                if loss_match or acc_match:
                    yield decoded_line + "\n"  # 只发送匹配的内容

        return StreamingResponse(filter_logs(), media_type="text/event-stream")

    except Exception as e:
        return {"error": str(e)}


@app.post("/stop_training")
def stop_training():
    """ 停止并删除容器 """
    try:
        container = client.containers.get(CONTAINER_NAME)
        container.stop()
        container.remove()
        return {"message": "容器已停止并删除"}
    except Exception as e:
        return {"error": str(e)}

@app.get("/status_training")
def status_training():
    """ 查询容器状态 """
    try:
        container = client.containers.get(CONTAINER_NAME)
        return {"status": container.status}
    except Exception as e:
        return {"error": "容器未运行"}