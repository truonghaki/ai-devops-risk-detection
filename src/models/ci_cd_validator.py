import os
import sys
import subprocess
import joblib
import pandas as pd
from radon.visitors import ComplexityVisitor
from radon.metrics import h_visit

# Khắc phục vấn đề import cấu hình từ thư mục gốc hệ thống
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from config import MODEL_DIR

def get_changed_files():
    """ Sử dụng lệnh Git để săn tìm danh sách các file .py vừa được chỉnh sửa hoặc thêm mới """
    try:
        # Lấy danh sách các file biến động giữa Commit hiện tại (HEAD) và Commit trước đó (HEAD~1)
        result = subprocess.run(
            ['git', 'diff', '--name-only', 'HEAD~1', 'HEAD'],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        files = result.stdout.splitlines()
        # Chỉ lọc lấy các file Python (.py) tồn tại thực tế trên ổ đĩa máy ảo
        py_files = [f for f in files if f.endswith('.py') and os.path.exists(f)]
        return py_files
    except Exception as e:
        print(f"⚠️ Cảnh báo hệ thống Git Diff: {e}")
        return []

def analyze_source_code(file_path):
    """ Đọc nội dung file code thực tế và dùng Radon cào ra chỉ số McCabe + Halstead """
    print(f"🔍 Đang tiến hành bóc tách toán học file: {file_path}")
    with open(file_path, 'r', encoding='utf-8') as f:
        code_content = f.read()
    
    # 1. Đo lường độ phức tạp vòng cung Cyclomatic Complexity (McCabe v(g))
    try:
        v = ComplexityVisitor.from_code(code_content)
        vg_val = sum([func.complexity for func in v.functions]) if v.functions else 1.0
    except:
        vg_val = 1.0
        
    # 2. Thu hoạch các chỉ số cấu trúc Halstead tinh vi
    try:
        h = h_visit(code_content)
        halstead = h.total  # Quy ước mảng: [h1, h2, N1, N2, vocabulary, length, volume, difficulty, effort, time, bugs]
        n_val = float(halstead[5])
        v_val = float(halstead[6])
        d_val = float(halstead[7])
        e_val = float(halstead[8])
        t_val = float(halstead[9])
        b_val = float(halstead[10])
        l_val = float(1.0 / d_val) if d_val > 0 else 1.0
        i_val = float(v_val / d_val) if d_val > 0 else v_val
    except:
        n_val, v_val, l_val, d_val, i_val, e_val, b_val, t_val = 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 0.0, 0.0

    # 3. Đếm số dòng code thực tế có nội dung (LoC)
    loc_val = len([line for line in code_content.splitlines() if line.strip()])

    # Đóng gói cấu trúc mảng đặc trưng trùng khớp 100% với định dạng file .pkl đã học
    metrics = {
        'loc': float(loc_val), 'v(g)': float(vg_val), 'ev(g)': float(vg_val * 0.4), 'iv(g)': float(vg_val * 0.6),
        'n': n_val, 'v': v_val, 'l': l_val, 'd': d_val, 'i': i_val, 'e': e_val, 'b': b_val, 't': t_val,
        'locode': float(int(loc_val * 0.7)), 'locomment': 0.0, 'loblank': float(int(loc_val * 0.2)), 'loccodeandcomment': 0.0,
        'uniq_op': float(int(n_val * 0.3)), 'uniq_opnd': float(int(n_val * 0.3)), 
        'total_op': float(int(n_val * 0.5)), 'total_opnd': float(int(n_val * 0.5)), 'branchcount': float(vg_val * 2 - 1)
    }
    return metrics

def run_pipeline_validation():
    print("=== 🤖 AI DEVOPS SYSTEM: QUÉT BIẾN ĐỘNG FILE REAL-TIME CHỐT 1 ===")
    
    model_path = os.path.join(MODEL_DIR, "chot1_model.pkl")
    features_path = os.path.join(MODEL_DIR, "chot1_features.pkl")
    
    if not os.path.exists(model_path) or not os.path.exists(features_path):
        print("❌ Lỗi chí mạng: Thiếu file cấu trúc pkl trong thư mục saved_models/.")
        sys.exit(1)

    # Đánh dấu danh sách file python bị thay đổi trong commit
    changed_files = get_changed_files()
    
    if not changed_files:
        print("✅ Thống kê: Commit này hoàn toàn không chỉnh sửa file Python (.py) nào.")
        print("🚀 Trạng thái xử lý: AUTO APPROVED (Bỏ qua thẩm định AI).")
        sys.exit(0)

    print(f"📂 Phát hiện {len(changed_files)} file Python cần thẩm định: {changed_files}")
    
    # Nạp mô hình AI Stacking lên bộ nhớ
    model = joblib.load(model_path)
    feature_names = joblib.load(features_path)
    
    highest_risk = 0  # Biến lưu trữ mức độ rủi ro cao nhất phát hiện được
    risk_labels = {0: "THẤP (An toàn)", 1: "TRUNG BÌNH (Code Smell)", 2: "CAO (Nguy hiểm)"}
    
    # Vòng lặp quét xuyên qua từng file python bị biến động
    for file_path in changed_files:
        print("-" * 60)
        file_metrics = analyze_source_code(file_path)
        
        # Đồng bộ hóa cấu trúc cột DataFrame theo đúng thứ tự các thuộc tính đã train
        input_df = pd.DataFrame([file_metrics])
        input_df = input_df[feature_names]
        
        # Dự đoán nhãn rủi ro trực tiếp (Giải quyết triệt để lỗi AttributeError bất đồng bộ thư viện)
        prediction = int(model.predict(input_df)[0])
        print(f"🎯 Kết quả phân tích file [{file_path}]: MỨC RỦI RO ĐƯỢC CHẤM LÀ -> {risk_labels[prediction]}")
        
        if prediction > highest_risk:
            highest_risk = prediction

    print("\n" + "="*25 + " HỘI ĐỒNG AI QUYẾT ĐỊNH PIPELINE " + "="*25)
    if highest_risk == 2:
        print("❌ [CRITICAL REJECT] Phát hiện mã nguồn chứa rủi ro lỗi logic nghiêm trọng (Mức 2).")
        print("🛑 THÔNG BÁO: HỆ THỐNG TỰ ĐỘNG BẺ GÃY PIPELINE, TỪ CHỐI INTEGRATION!")
        sys.exit(1)  # Trả về code lỗi để GitHub Actions báo Đỏ
    elif highest_risk == 1:
        print("⚠️ [WARNING INTEGRATED] Phát hiện cấu trúc code loằng ngoằng vi phạm chuẩn (Mức 1).")
        print("⚠️ THÔNG BÁO: CHẤP NHẬN MERGE NHƯNG YÊU CẦU GẮN TAG CẦN REVIEW.")
        sys.exit(0)
    else:
        print("✅ [PERFECT PASSED] Tất cả các file sửa đổi đều đạt chuẩn an toàn tối ưu (Mức 0).")
        print("🚀 THÔNG BÁO: AUTO APPROVE - CHO PHÉP TÍCH HỢP HOÀN TOÀN.")
        sys.exit(0)  # Trả về code thành công để GitHub Actions báo Xanh

if __name__ == "__main__":
    run_pipeline_validation()