import pandas as pd
import numpy as np
import sys
import os
import joblib
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, accuracy_score
from sklearn.preprocessing import LabelEncoder
from sklearn.ensemble import RandomForestClassifier, VotingClassifier
from sklearn.utils.class_weight import compute_sample_weight
from imblearn.over_sampling import SMOTE
import xgboost as xgb

# Khắc phục vấn đề import cấu hình từ thư mục gốc
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from config import K8S_PROCESSED, MODEL_DIR

def train_model_chot2_improved():
    print("=== 🚀 QUY TRÌNH HUẤN LUYỆN MÔ HÌNH VỚI DỮ LIỆU ĐÃ ĐỒNG BỘ ===")
    
    if not os.path.exists(K8S_PROCESSED):
        print(f"❌ Không tìm thấy file dữ liệu sạch tại {K8S_PROCESSED}. Hãy chạy file build_features_chot2.py trước!")
        return

    # Tải dữ liệu đã tiền xử lý
    df = pd.read_csv(K8S_PROCESSED)
    
    # Loại bỏ các cột không dùng làm thuộc tính học tập trực tiếp (Tránh rò rỉ dữ liệu)
    drop_cols = ['timestamp', 'pod_name', 'node_name', 'risk_level', 'pod_status', 'event_message', 'event_type']
    X = df.drop(columns=[col for col in drop_cols if col in df.columns], errors='ignore')
    y = df['risk_level']
    
    # Kiểm tra số lượng lớp thực tế thu được từ file dữ liệu sạch
    unique_classes = np.unique(y)
    num_classes = len(unique_classes)
    print(f"📊 Số lượng nhãn mục tiêu thực tế đưa vào huấn luyện: {num_classes} lớp ({unique_classes})")

    # Lưu danh sách tên các đặc trưng phục vụ cho việc suy luận sau này
    feature_names = X.columns.tolist()

    # Phân tách tập Train và Test (80% / 20%) theo đúng tỷ lệ phân phối nhãn ban đầu (stratify)
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
    
    # Áp dụng SMOTE để tạo mẫu ảo tăng cường cho các lớp thiểu số (Mức 0 và Mức 1)
    print("⏳ Đang kích hoạt SMOTE cân bằng dữ liệu học tập...")
    min_samples = y_train.value_counts().min()
    k_neighbors = min(5, min_samples - 1) if min_samples > 1 else 1
    
    smote = SMOTE(random_state=42, k_neighbors=k_neighbors)
    X_resampled, y_resampled = smote.fit_resample(X_train, y_train)
    
    # Tính toán trọng số mẫu phạt (Sample Weights) để triệt tiêu hoàn toàn sự thiên vị thuật toán
    sample_weights = compute_sample_weight(class_weight='balanced', y=y_resampled)
    
    print("⏳ Đang huấn luyện mô hình kết hợp Voting Classifier (Random Forest + XGBoost)...")
    rf = RandomForestClassifier(n_estimators=200, max_depth=10, random_state=42, n_jobs=-1)
    
    # Định cấu hình XGBoost thích ứng động theo số lượng class thực tế
    xgb_model = xgb.XGBClassifier(
        n_estimators=200, 
        learning_rate=0.05, 
        max_depth=6, 
        objective='multi:softprob',
        num_class=num_classes,
        random_state=42,
        eval_metric='mlogloss'
    )
    
    # Tạo mô hình đồng thuận dựa trên xác suất dự đoán (Soft Voting)
    ensemble = VotingClassifier(estimators=[('rf', rf), ('xgb', xgb_model)], voting='soft')
    
    # Tiến hành Fit mô hình với trọng số đã cân bằng gắt gao
    ensemble.fit(X_resampled, y_resampled, sample_weight=sample_weights)
    
    # Dự đoán và kiểm thử hiệu năng mô hình trên tập Test độc lập
    y_pred = ensemble.predict(X_test)
    
    print("\n" + "="*20 + " BÁO CÁO PHÂN LOẠI CUỐI CÙNG " + "="*20)
    print(f"🎯 ĐỘ CHÍNH XÁC ĐẠT ĐƯỢC: {accuracy_score(y_test, y_pred) * 100:.2f}%")
    
    # Bản đồ hóa nhãn trực quan nếu đủ 3 mức chuẩn
    target_names = ['Thấp (0)', 'Trung bình (1)', 'Cao (2)'] if num_classes == 3 else [f'Mức {i}' for i in unique_classes]
    print(classification_report(y_test, y_pred, target_names=target_names, zero_division=0))
    print("="*69)
    
    # Xuất và nén các file mô hình ra thư mục saved_models
    os.makedirs(MODEL_DIR, exist_ok=True)
    joblib.dump(ensemble, os.path.join(MODEL_DIR, "chot2_model.pkl"))
    joblib.dump(feature_names, os.path.join(MODEL_DIR, "chot2_features.pkl"))
    
    print("✅ Hệ thống: Đã cập nhật thành công và lưu mô hình tối ưu nhất vào thư mục saved_models!")

if __name__ == "__main__":
    train_model_chot2_improved()