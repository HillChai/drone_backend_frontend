from minio import Minio

# 连接 MinIO 服务器
minio_client = Minio(
    "minio:9000",
    access_key="minioadmin",
    secret_key="minio123",
    secure=False
)

bucket_name = "drone-system"

# **列出存储桶中的所有对象**
objects = minio_client.list_objects(bucket_name, recursive=True)

# **删除所有对象**
for obj in objects:
    minio_client.remove_object(bucket_name, obj.object_name)
    print(f"🗑 已删除: {obj.object_name}")

print(f"✅ 存储桶 {bucket_name} 已清空！")
