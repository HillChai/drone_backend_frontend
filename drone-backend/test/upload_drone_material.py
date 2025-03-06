import os
from minio import Minio

# 连接 MinIO 服务器
minio_client = Minio(
    "minio:9000",
    access_key="minioadmin",
    secret_key="minio123",
    secure=False  # 如果使用 HTTPS 需要改成 True
)

# **指定存储桶**
bucket_name = "drone-system"
if not minio_client.bucket_exists(bucket_name):
    minio_client.make_bucket(bucket_name)
    print(f"✅ 已创建存储桶: {bucket_name}")

# **指定要上传的本地目录**
local_base_path = r"../drone_system_material"  # ⚠️ 替换为你的文件夹路径

# **遍历文件夹并上传**
for root, _, files in os.walk(local_base_path):
    for file in files:
        # **构造 MinIO 文件路径**
        local_file_path = os.path.join(root, file)
        minio_file_path = os.path.relpath(local_file_path, local_base_path).replace("\\", "/")

        # **上传文件**
        minio_client.fput_object(
            bucket_name,
            minio_file_path,
            local_file_path
        )
        print(f"✅ 已上传: {local_file_path} -> minio://{bucket_name}/{minio_file_path}")

print("🚀 所有文件上传完成！")
