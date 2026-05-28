import os
import sys
import joblib
import pandas as pd

# Khắc phục vấn đề import cấu hình
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from config import MODEL_DIR

def run_pipeline_validation():
    print("=== 🤖 AI DEVOPS SYSTEM: KIỂM TRA CHẤT LƯỢNG COMMIT TỰ ĐỘNG ===")
    
    model_path = os.path.join(MODEL_DIR, "chot1_model.pkl")
    features_path = os.path.join(MODEL_DIR, "chot1_features.pkl")
    
    if not os.path.exists(model_path):
        print("❌ Lỗi: Không tìm thấy file mô hình AI tại saved_models/")
        sys.exit(1) # Báo lỗi cho GitHub Actions dừng pipeline

    # 1. Giả lập quá trình công cụ Static Analysis (như Radon/Lizard) quét file code vừa commit
    # Trong thực tế, bạn sẽ chạy lệnh quét để ra số, ở đây ta lấy mẫu một commit có cấu trúc phức tạp nguy cơ lỗi
    current_commit_metrics = {
        'loc': 65.0, 'v(g)': 12.0, 'ev(g)': 4.0, 'iv(g)': 8.0, 
        'n': 145.0, 'v': 850.00, 'l': 0.06, 'd': 18.50, 
        'i': 45.00, 'e': 15000.0, 'b': 0.28, 't': 800.00,
        'locode': 45, 'locomment': 10, 'loblank': 8, 'loccodeandcomment': 2,
        'uniq_op': 15, 'uniq_opnd': 25, 'total_op': 85, 'total_opnd': 60, 'branchcount': 23
    }
    
    # 2. Chuẩn hóa dữ liệu tương thích với mô hình AI
    input_df = pd.DataFrame([current_commit_metrics])
    input_df.columns = input_df.columns.str.strip().str.lower()
    
    model = joblib.load(model_path)
    feature_names = joblib.load(features_path)
    
    # Sắp xếp đúng thứ tự đặc trưng
    input_df = input_df[[col for col in feature_names if col in input_df.columns]]
    
    # 3. AI đưa ra quyết định
    prediction = int(model.predict(input_df)[0])
    
    print(f"\n📊 [AI DIAGNOSIS] KẾT QUẢ ĐÁNH GIÁ MỨC ĐỘ RỦI RO: NHÃN {prediction}")
    
    if prediction == 2:
        print("❌ [CRITICAL WARNING] Phát hiện cấu trúc chứa lỗi logic nghiêm trọng (Mức 2).")
        print("🛑 THÔNG BÁO: Tự động BLOCK COMMIT. Vui lòng kiểm tra và refactor lại code!")
        sys.exit(1) # Trả về code lỗi hòng bẻ gãy GitHub Actions workflow
    elif prediction == 1:
        print("⚠️ [WARNING] Cảnh báo: Mã nguồn có dấu hiệu phức tạp, vi phạm chuẩn NIST (Mức 1).")
        print("⚠️ THÔNG BÁO: Chấp nhận tích hợp nhưng gắn tag REVIEW REQUIRED.")
        sys.exit(0)
    else:
        print("✅ [SUCCESS] Mã nguồn sạch, tối ưu và an toàn (Mức 0).")
        print("🚀 THÔNG BÁO: CHẤP NHẬN HOÀN TOÀN (AUTO APPROVE).")
        sys.exit(0)

if __name__ == "__main__":
    run_pipeline_validation()