from minio import Minio
import os
import uuid

MINIO_ENDPOINT = os.getenv("MINIO_ENDPOINT", "http://minio:9000")
MINIO_ACCESS_KEY = os.getenv("MINIO_ACCESS_KEY", "minioadmin")
MINIO_SECRET_KEY = os.getenv("MINIO_SECRET_KEY", "minio123")

minio_client = Minio(
    MINIO_ENDPOINT.replace("http://", "").replace("https://", ""),
    access_key=MINIO_ACCESS_KEY,
    secret_key=MINIO_SECRET_KEY,
    secure=False
)

BUCKET_NAME = "drone-system"

def upload_file_to_minio(file):
    """上传文件到 MinIO 并返回 URL"""
    file_name = f"algorithm-{uuid.uuid4()}.py"
    minio_client.put_object(BUCKET_NAME, file_name, file.file, length=-1, part_size=10 * 1024 * 1024)

    return f"http://minio-server:9000/{BUCKET_NAME}/{file_name}"