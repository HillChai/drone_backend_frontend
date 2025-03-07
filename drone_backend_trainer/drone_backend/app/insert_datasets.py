from sqlalchemy.orm import Session
from models import Dataset
from database import SessionLocal

# **连接 PostgreSQL**
db: Session = SessionLocal()

# **手动定义要插入的数据集路径**
dataset_entries = [
    {
        "name": "dronerf_vits",
        "description": "适用于 VITs 训练",
        "file_path": "minio://drone-system/datasets/dronerf_vits/"
    },
    {
        "name": "cardrf_vits",
        "description": "适用于 VITs 推理测试",
        "file_path": "minio://drone-system/datasets/cardrf_vits/"
    },
    {
        "name": "dronerf_machine_learning",
        "description": "适用于 ML 训练",
        "file_path": "minio://drone-system/datasets/dronerf_machine_learning/"
    },
    {
        "name": "cardrf_machine_learning",
        "description": "适用于 ML 推理测试",
        "file_path": "minio://drone-system/datasets/cardrf_machine_learning/"
    }
]

# **插入数据**
for entry in dataset_entries:
    dataset = Dataset(
        name=entry["name"],
        description=entry["description"],
        file_path=entry["file_path"]
    )
    db.add(dataset)
    print(f"✅ 插入数据集: {entry['name']} -> {entry['file_path']}")

# **提交事务**
db.commit()
db.close()

print("🚀 所有数据集已插入 PostgreSQL！")
