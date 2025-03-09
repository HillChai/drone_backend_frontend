from sqlalchemy.orm import Session
from models import History, Dataset, Algorithm
from database import SessionLocal
import random
from datetime import datetime, timedelta

# **连接 PostgreSQL**
db: Session = SessionLocal()

# **查询所有数据集和算法**
datasets = db.query(Dataset).all()
algorithms = db.query(Algorithm).all()

if not algorithms:
    print("⚠️ 数据库中没有算法，无法生成历史数据！")
    exit()

# **任务状态选项**
status_choices = ["completed", "failed"]

# **生成 20 条历史数据**
history_entries = []
for _ in range(20):
    dataset = random.choice(datasets) if datasets and random.random() > 0.2 else None  # 80% 有 dataset_id, 20% 为 NULL
    algorithm = random.choice(algorithms)
    
    created_at = datetime.utcnow() - timedelta(days=random.randint(1, 30))  # 1-30 天内的任务
    completed_at = created_at + timedelta(hours=random.randint(1, 5))  # 70% 任务完成
    status = random.choice(status_choices)
        
    results_path = f"/home/ccc/drone_system_material/results/{algorithm.name}.txt" if status == "completed" else None

    history_entries.append(
        History(
            dataset_id=dataset.id if dataset else None,
            algorithm_id=algorithm.id,
            status=status,
            results_path=results_path,
            created_at=created_at,
            completed_at=completed_at
        )
    )

# **批量插入数据**
db.bulk_save_objects(history_entries)
db.commit()
db.close()

print(f"🚀 成功插入 {len(history_entries)} 条历史数据，其中部分 dataset_id 为空！")
