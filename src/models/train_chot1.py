import pandas as pd
import numpy as np
import sys
import os
import joblib
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, accuracy_score
from sklearn.ensemble import RandomForestClassifier, StackingClassifier
from sklearn.linear_model import LogisticRegression
from imblearn.over_sampling import SMOTE
import xgboost as xgb

# Khắc phục vấn đề import cấu hình từ thư mục gốc
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from config import JM1_PROCESSED, MODEL_DIR

def train_model_chot1_advanced():
    print("=== 🎓 QUY TRÌNH HUẤN LUYỆN CHỐT 1: PHIÊN BẢN ĐỒ ÁN THỰC CHIẾN PRO ===")
    
    if not os.path.exists(JM1_PROCESSED):
        print(f"❌ Không tìm thấy file dữ liệu tại {JM1_PROCESSED}. Hãy chạy build_features_chot1.py trước!")
        return

    # 1. Tải dữ liệu siêu sạch đã xử lý ở Phương án B
    df = pd.read_csv(JM1_PROCESSED)
    
    # Ở phiên bản ứng dụng cao này, chúng ta GIỮ LẠI loc và v(g) nhưng loại bỏ hoàn toàn 'defects'
    # Điều này giúp mô hình chạy cực tốt trên môi trường Commit thực tế của Git
    drop_cols = ['risk_level', 'defects']
    X = df.drop(columns=[col for col in drop_cols if col in df.columns], errors='ignore')
    y = df['risk_level']
    
    unique_classes = np.unique(y)
    num_classes = len(unique_classes)
    feature_names = X.columns.tolist()

    print(f"📐 Số lượng đặc trưng đưa vào huấn luyện thực chiến: {len(feature_names)} thuộc tính.")
    print(f"📋 Các biến đầu vào bao gồm cả cấu trúc dòng code:\n -> {feature_names}")

    # Chia tập dữ liệu Train/Test (80/20) đảm bảo cân bằng nhãn bằng Stratify
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
    
    # Sử dụng SMOTE-Tomek hoặc SMOTE chuẩn để xử lý mất cân bằng nhãn
    print("⏳ Kích hoạt bộ cân bằng dữ liệu SMOTE...")
    min_samples = y_train.value_counts().min()
    k_neighbors = min(5, min_samples - 1) if min_samples > 1 else 1
    smote = SMOTE(random_state=42, k_neighbors=k_neighbors)
    X_resampled, y_resampled = smote.fit_resample(X_train, y_train)
    
    # === 🧠 KIẾN TRÚC ENSEMBLE STACKING ĐA TẦNG (CẢI TIẾN ỨNG DỤNG) ===
    print("⏳ Đang thiết lập hệ thống học máy xếp tầng (Stacking Architecture)...")
    
    # Các mô hình nền tảng (Base Estimators)
    base_learners = [
        ('rf', RandomForestClassifier(n_estimators=300, max_depth=12, random_state=42, n_jobs=-1)),
        ('xgb', xgb.XGBClassifier(
            n_estimators=300, 
            learning_rate=0.05, 
            max_depth=6, 
            objective='multi:softprob',
            num_class=num_classes,
            random_state=42,
            eval_metric='mlogloss'
        ))
    ]
    
    # Mô hình meta tối ưu cuối cùng (Meta Learner)
    meta_learner = LogisticRegression(max_iter=1000, random_state=42)
    
    # Khởi tạo mô hình Stacking
    model = StackingClassifier(
        estimators=base_learners,
        final_estimator=meta_learner,
        cv=5,
        n_jobs=-1
    )
    
    # Huấn luyện mô hình tổng thể
    print("🚀 Mô hình đang thực hiện tối ưu hóa trọng số toán học...")
    model.fit(X_resampled, y_resampled)
    
    # Đánh giá kết quả trên tập Test độc lập
    y_pred = model.predict(X_test)
    
    print("\n" + "="*20 + " BÁO CÁO PHÂN LOẠI THỰC CHIẾN ĐỒ ÁN (CHỐT 1) " + "="*20)
    print(f"🎯 ĐỘ CHÍNH XÁC ĐẠT ĐƯỢC (ACCURACY): {accuracy_score(y_test, y_pred) * 100:.2f}%")
    
    target_names = ['Thấp (0)', 'Trung bình (1)', 'Cao (2)'] if num_classes == 3 else [f'Mức {i}' for i in unique_classes]
    print(classification_report(y_test, y_pred, target_names=target_names, zero_division=0))
    print("="*69)
    
    # Lưu trữ mô hình và danh sách đặc trưng phục vụ API kết nối cổng Commit (Git Webhook)
    os.makedirs(MODEL_DIR, exist_ok=True)
    joblib.dump(model, os.path.join(MODEL_DIR, "chot1_model.pkl"))
    joblib.dump(feature_names, os.path.join(MODEL_DIR, "chot1_features.pkl"))
    print("✅ Đã xuất file chot1_model.pkl và chot1_features.pkl sẵn sàng tích hợp CI/CD!")

if __name__ == "__main__":
    train_model_chot1_advanced()