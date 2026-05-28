# src/config.py
import os

# Lấy đường dẫn gốc của toàn bộ dự án (Thư mục AI-DEVOPS-RISK-DETECTION)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Khai báo các thư mục lõi
RAW_DATA_DIR = os.path.join(BASE_DIR, "data", "raw")
PROCESSED_DATA_DIR = os.path.join(BASE_DIR, "data", "processed")
MODEL_DIR = os.path.join(BASE_DIR, "saved_models")

# Khai báo file thô (Input)
JM1_RAW = os.path.join(RAW_DATA_DIR, "jm1.csv")
K8S_PERFORMANCE = os.path.join(RAW_DATA_DIR, "kubernetes_performance_metrics_dataset.csv")
K8S_ALLOCATION = os.path.join(RAW_DATA_DIR, "kubernetes_resource_allocation_dataset.csv")

# Khai báo file sạch (Output)
JM1_PROCESSED = os.path.join(PROCESSED_DATA_DIR, "chot1_processed.csv")
K8S_PROCESSED = os.path.join(PROCESSED_DATA_DIR, "chot2_processed.csv")