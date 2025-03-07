from fastapi import FastAPI
from fastapi.responses import StreamingResponse
import os
import subprocess
import threading
import boto3

app = FastAPI()

# MinIO 配置
MINIO_ENDPOINT = os.getenv("MINIO_ENDPOINT", "http://minio:9000")
MINIO_ACCESS_KEY = os.getenv("MINIO_ACCESS_KEY", "minioadmin")
MINIO_SECRET_KEY = os.getenv("MINIO_SECRET_KEY", "minio123")
BUCKET_NAME = os.getenv("BUCKET_NAME", "drone-system")

# 训练临时目录
TMP_DIR = "/app/tmp/"
os.makedirs(TMP_DIR, exist_ok=True)

# MinIO 客户端
s3_client = boto3.client(
    "s3",
    endpoint_url=MINIO_ENDPOINT,
    aws_access_key_id=MINIO_ACCESS_KEY,
    aws_secret_access_key=MINIO_SECRET_KEY
)

# 下载 MinIO 文件
def download_from_minio(minio_path, local_path):
    s3_client.download_file(BUCKET_NAME, minio_path, local_path)

# 训练日志 SSE
def stream_training_logs(script_path, dataset_path, epochs):
    command = ["python", script_path, "--dataset", dataset_path, "--epochs", str(epochs)]
    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

    for line in iter(process.stdout.readline, ""):
        if "loss" in line or "accuracy" in line:
            yield f"data: {line.strip()}\n\n"

    process.wait()
    os.remove(script_path)
    os.remove(dataset_path)

# 训练 API
@app.post("/train")
async def start_training(data: dict):
    script_minio_path = data["script_minio_path"]
    dataset_minio_path = data["dataset_minio_path"]
    epochs = data.get("epochs", 10)

    script_name = os.path.basename(script_minio_path)
    dataset_name = os.path.basename(dataset_minio_path)

    script_local_path = os.path.join(TMP_DIR, script_name)
    dataset_local_path = os.path.join(TMP_DIR, dataset_name)

    download_from_minio(script_minio_path, script_local_path)
    download_from_minio(dataset_minio_path, dataset_local_path)

    threading.Thread(target=stream_training_logs, args=(script_local_path, dataset_local_path, epochs), daemon=True).start()

    return {"message": "Training started", "script": script_name, "dataset": dataset_name, "epochs": epochs}

# SSE 推送训练日志
@app.get("/stream")
async def stream_logs():
    return StreamingResponse(stream_training_logs(), media_type="text/event-stream")
