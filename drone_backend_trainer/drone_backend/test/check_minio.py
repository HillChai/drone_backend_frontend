from minio import Minio

minio_client = Minio(
    "minio:9000",
    access_key="minioadmin",
    secret_key="minio123",
    secure=False
)

bucket_name = "drone-system"
objects = minio_client.list_objects(bucket_name, recursive=True)

# 只打印前 20 条，避免信息太多
for i, obj in enumerate(objects):
    if i >= 20:  # 只显示前 20 个路径
        break
    print(obj.object_name)
