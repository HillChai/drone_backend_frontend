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
    url = "http://drone_trainer:8001/train_progress"  # 训练容器的 SSE 接口
    try:
        with requests.get(url, stream=True) as response:
            for line in response.iter_lines():
                if line:
                    data = line.decode("utf-8").replace("data: ", "")
                    print("收到训练数据:", data)
                    global training_status
                    training_status = eval(data)  # 存入全局变量
                    yield f"data: {data}\n\n"
    except Exception as e:
        print(f"SSE 连接失败: {e}")

@app.get("/subscribe")
async def subscribe():
    return StreamingResponse(stream_sse(), media_type="text/event-stream")

@app.get("/status")
async def get_status():
    """获取当前训练状态"""
    return training_status


# 使用 Windows 远程 API 连接 Docker
DOCKER_API_URL = "tcp://host.docker.internal:2375"

try:
    client = docker.DockerClient(base_url=DOCKER_API_URL)
    print("✅ 成功连接到 Docker API")
except Exception as e:
    print(f"❌ 连接 Docker 失败: {e}")

# 容器信息
CONTAINER_NAME = "ml_dronerf"
IMAGE_NAME = "crpi-9994gc03c1aikjap.cn-hangzhou.personal.cr.aliyuncs.com/radio_fingerprinting/ml_dronerf:latest"
MOUNT_ALGORITHMS = "/drone_system_material/algorithms"
MOUNT_DATASETS = "/drone_system_material/datasets/dronerf_machine_learning"
HOST_ALGORITHMS = "D:\\drone_system_material\\algorithms\\dronerf_machine_learning"
HOST_DATASETS = "D:\\drone_system_material\\datasets\\dronerf_machine_learning"

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
            },
            command="/bin/bash",
        )

        return {"message": "容器已启动", "container_id": container.id}
    except Exception as e:
        return {"error": str(e)}

@app.post("/run_training_script")
def run_training_script():
    """ 在运行的容器内执行训练命令 """
    try:
        container = client.containers.get(CONTAINER_NAME)
        exec_result = container.exec_run("python3 /drone_system_material/algorithms/catboost/best_catboost.py")
        return {"message": "训练任务已启动", "stdout": exec_result.output.decode("utf-8")}
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