import io
from minio import Minio
from minio.error import S3Error
import os
from fastapi import UploadFile

# MinIO 连接信息
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

def check_file_exists(file_path: str) -> bool:
    """检查 MinIO 中是否已存在文件"""
    try:
        minio_client.stat_object(BUCKET_NAME, file_path)
        return True
    except S3Error:
        return False

def upload_file_to_minio(file: UploadFile, file_path: str, replace: bool = False) -> str:
    """上传文件到 MinIO，若存在则替换"""
    if replace and check_file_exists(file_path):
        minio_client.remove_object(BUCKET_NAME, file_path)  # 先删除已有文件

    file_data = file.file.read()  # 读取文件数据
    file_size = len(file_data)  # 计算文件大小

    # 重新创建 UploadFile 对象
    file.file.seek(0)

    minio_client.put_object(
        bucket_name=BUCKET_NAME,
        object_name=file_path,
        data=io.BytesIO(file_data),
        length=file_size,
        content_type=file.content_type
    )

    return f"{file_path}"


def list_algorithm_files(prefix: str):
    """列出 MinIO 里指定前缀的所有文件"""
    try:
        print(f"📌 正在查找 MinIO 文件，前缀: {prefix}")

        objects = minio_client.list_objects(BUCKET_NAME, prefix=prefix, recursive=True)
        file_list = [obj.object_name for obj in objects]

        print(f"✅ 找到 {len(file_list)} 个文件: {file_list}")
        return file_list
    except Exception as e:
        print(f"❌ MinIO 读取失败: {str(e)}")
        return []



def get_algorithm_code(file_path: str) -> str:
    """从 MinIO 获取算法代码"""
    try:
        response = minio_client.get_object(BUCKET_NAME, file_path)
        return response.read().decode("utf-8")  # 读取并解码代码
    except Exception as e:
        print(f"❌ MinIO 读取失败: {str(e)}")
        return ""
