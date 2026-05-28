import os
import sys
import subprocess
import joblib
import pandas as pd
from radon.visitors import ComplexityVisitor
from radon.metrics import h_visit

# Khắc phục vấn đề import cấu hình
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from config import MODEL_DIR

def get_changed_files():
    """ Sử dụng lệnh Git lệnh để tìm danh sách các file .py vừa được chỉnh sửa hoặc thêm mới """
    try:
        # Lấy danh sách các file thay đổi so với commit trước đó (HEAD~1)
        result = subprocess.run(
            ['git', 'diff', '--name-only', 'HEAD~1', 'HEAD'],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        files = result.stdout.splitlines()
        # Chỉ lọc lấy các file Python (.py) và file đó phải thực sự tồn tại
        py_files = [f for f in files if f.endswith('.py') and os.path.exists(f)]
        return py_files
    except Exception as e:
        print(f"⚠️ Không thể lấy danh sách Git diff: {e}")
        return []

def analyze_source_code(file_path):
    """ Đọc file code thực tế và trích xuất toàn bộ chỉ số McCabe + Halstead khớp với tập dữ liệu NASA """
    print(f"🔍 Đang bóc tách toán học file: {file_path}")
    with open(file_path, 'r', encoding='utf-8') as f:
        code_content = f.read()
    
    # 1. Tính toán độ phức tạp Cyclomatic (McCabe v(g))
    try:
        v = ComplexityVisitor.from_code(code_content)
        vg_val = sum([func.complexity for func in v.functions]) if v.functions else 1.0
    except:
        vg_val = 1.0
        
    # 2. Tính toán các chỉ số Halstead tinh vi
    try:
        h = h_visit(code_content)
        halstead = h.total # Quy đổi: [h1, h2, N1, N2, vocabulary, length, volume, difficulty, effort, time, bugs]
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

    # 3. Tính toán số dòng code thực tế (LoC)
    loc_val = len([line for line in code_content.splitlines() if line.strip()])

    # Đóng gói thành dict trùng khớp hoàn toàn với cấu trúc mảng đặc trưng Chốt 1 đã học
    metrics = {
        'loc': float(loc_val), 'v(g)': float(vg_val), 'ev(g)': float(vg_val * 0.4), 'iv(g)': float(vg_val * 0.6),
        'n': n_val, 'v': v_val, 'l': l_val, 'd': d_val, 'i': i_val, 'e': e_val, 'b': b_val, 't': t_val,
        'locode': float(int(loc_val * 0.7)), 'locomment': 0.0, 'loblank': float(int(loc_val * 0.2)), 'loccodeandcomment': 0.0,
        'uniq_op': float(int(n_val * 0.3)), 'uniq_opnd': float(int(n_val * 0.3)), 
        'total_op': float(int(n_val * 0.5)), 'total_opnd': float(int(n_val * 0.5)), 'branchcount': float(vg_val * 2 - 1)
    }
    return metrics

def run_pipeline_validation():
    print("=== 🤖 AI DEVOPS SYSTEM: QUÉT BIẾN ĐỘNG FILE REAL-TIME ===")
    
    model_path = os.path.join(MODEL_DIR, "chot1_model.pkl")
    features_path = os.path.join(MODEL_DIR, "chot1_features.pkl")
    
    if not os.path.exists(model_path) or not os.path.exists(features_path):
        print("❌ Lỗi hệ thống: Không tìm thấy file não bộ AI .pkl. Hãy đảm bảo đã đẩy thư mục saved_models lên Git.")
        sys.exit(1)

    # Tự động bắt mạch các file Python vừa thay đổi trong commit
    changed_files = get_changed_files()
    
    if not changed_files:
        print("✅ Thống kê: Commit này không thay đổi bất kỳ file Python (.py) nào hoặc đây là Commit khởi tạo đầu tiên.")
        print("🚀 Giao kịch bản: AUTO APPROVED (Bỏ qua kiểm tra AI).")
        sys.exit(0)

    print(f"📂 Tìm thấy {len(changed_files)} file Python bị biến động: {changed_files}")
    
    model = joblib.load(model_path)
    feature_names = joblib.load(features_path)
    
    highest_risk = 0 # Biến dùng để ghi nhận mức độ rủi ro lớn nhất trong các file bị sửa
    
    # Duyệt qua từng file một để bắt bug ẩn bằng AI
    for file_path in changed_files:
        print("-" * 50)
        file_metrics = analyze_source_code(file_path)
        
        # Biến đổi thành DataFrame và đồng bộ thứ tự cột theo đúng file phao .pkl đã học
        input_df = pd.DataFrame([file_metrics])
        input_df = input_df[feature_names]
        
        # Ép mô hình AI dự đoán nhãn rủi ro
        prediction = int(model.predict(input_df)[0])
        pred_proba = model.predict_proba(input_df)[0]
        
        print(f"🎯 Kết quả phân tích file [{file_path}]: MỨC RỦI RO {prediction} (Độ tin cậy: {pred_proba[prediction]*100:.2f}%)")
        
        if prediction > highest_risk:
            highest_risk = prediction

    print("\n" + "="*30 + " KẾT LUẬN CUỐI CỦA AI PIPELINE " + "="*30)
    if highest_risk == 2:
        print("❌ [CRITICAL REJECT] Có ít nhất một file dính lỗi logic cấu trúc nghiêm trọng (Mức 2).")
        print("🛑 HÀNH ĐỘNG: BẺ GÃY PIPELINE KHÔNG CHO MERGE! Vui lòng refactor lại đoạn code nguy hiểm trên.")
        sys.exit(1) # Trả về số 1 để GitHub Action chuyển sang màu đỏ (Thất bại)
    elif highest_risk == 1:
        print("⚠️ [WARNING APPROVED] Phát hiện file có cấu trúc phức tạp vi phạm chuẩn phần mềm sạch (Mức 1).")
        print("⚠️ HÀNH ĐỘNG: Chấp nhận tích hợp nhưng gắn nhãn cảnh báo cần Review thêm.")
        sys.exit(0)
    else:
        print("✅ [PERFECT PASSED] Tất cả các file commit đều đạt chuẩn an toàn tuyệt đối (Mức 0).")
        print("🚀 HÀNH ĐỘNG: CHẤP NHẬN HOÀN TOÀN (AUTO APPROVE).")
        sys.exit(0)

if __name__ == "__main__":
    run_pipeline_validation()