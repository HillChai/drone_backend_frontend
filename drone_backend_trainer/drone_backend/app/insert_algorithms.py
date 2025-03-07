from sqlalchemy.orm import Session
from models import Algorithm
from database import SessionLocal

# **连接 PostgreSQL**
db: Session = SessionLocal()

# **手动定义要插入的算法路径**
algorithm_entries = [
    ("catboost", "minio://drone-system/algorithms/cardrf_machine_learning/catboost/", "适用于 ML 分类"),
    ("decision_tree_classifier", "minio://drone-system/algorithms/cardrf_machine_learning/decision_tree_classifier/", "决策树 ML 分类"),
    ("knn", "minio://drone-system/algorithms/cardrf_machine_learning/knn/", "KNN 分类算法"),
    ("lightgbm", "minio://drone-system/algorithms/cardrf_machine_learning/lightgbm/", "LightGBM 训练"),
    ("random_forest", "minio://drone-system/algorithms/cardrf_machine_learning/random_forest/", "随机森林分类"),
    ("svm", "minio://drone-system/algorithms/cardrf_machine_learning/svm/", "支持向量机分类"),
    ("xgboost", "minio://drone-system/algorithms/cardrf_machine_learning/xgboost/", "XGBoost 分类"),

    # **dronerf_machine_learning**
    ("catboost", "minio://drone-system/algorithms/dronerf_machine_learning/catboost/", "适用于 ML 训练"),
    ("decision_tree_classifier", "minio://drone-system/algorithms/dronerf_machine_learning/decision_tree_classifier/", "决策树 ML 分类"),
    ("knn", "minio://drone-system/algorithms/dronerf_machine_learning/knn/", "KNN 分类算法"),
    ("lightgbm", "minio://drone-system/algorithms/dronerf_machine_learning/lightgbm/", "LightGBM 训练"),
    ("random_forest", "minio://drone-system/algorithms/dronerf_machine_learning/random_forest/", "随机森林分类"),
    ("svm", "minio://drone-system/algorithms/dronerf_machine_learning/svm/", "支持向量机分类"),
    ("xgboost", "minio://drone-system/algorithms/dronerf_machine_learning/xgboost/", "XGBoost 分类"),

    # **VITs**
    ("multi_resolution_vits", "minio://drone-system/algorithms/cardrf_vits/multi_resolution_vits/", "适用于 VITs 推理"),
    ("multi_resolution_vits", "minio://drone-system/algorithms/dronerf_vits/multi_resolution_vits/", "适用于 VITs 训练")
]

# **插入数据**
for name, path, description in algorithm_entries:
    algorithm = Algorithm(
        name=name,
        description=description,
        file_path=path
    )
    db.add(algorithm)
    print(f"✅ 插入算法: {name} -> {path}")

# **提交事务**
db.commit()
db.close()

print("🚀 所有算法已插入 PostgreSQL！")
