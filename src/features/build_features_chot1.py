import pandas as pd
import numpy as np
import os
import sys

# Khắc phục vấn đề import cấu hình từ thư mục gốc
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from config import JM1_RAW, JM1_PROCESSED

def process_chot1():
    print("--- 🚀 TIỀN XỬ LÝ CHỐT 1 [PHƯƠNG ÁN B]: LỌC TRIỆT ĐỂ DỮ LIỆU NHIỄU ---")
    
    if not os.path.exists(JM1_RAW):
        print(f"❌ Lỗi: Thiếu file CSV thô tại {JM1_RAW}")
        return

    # Đọc dữ liệu gốc
    df = pd.read_csv(JM1_RAW, encoding='utf-8-sig')
    total_raw = df.shape[0]
    print(f"📊 Tổng số lượng mẫu thô ban đầu: {total_raw} dòng.")

    # Đưa toàn bộ tên cột về chữ thường và xóa khoảng trắng
    df.columns = df.columns.str.strip().str.lower()

    # Ép kiểu số cho toàn bộ các cột đặc trưng toán học
    for col in df.columns:
        if col != 'defects':
            df[col] = pd.to_numeric(df[col], errors='coerce')

    # === 🎯 BỘ LỌC KHỬ NHIỄU TRIỆT ĐỂ (PHƯƠNG ÁN B) ===
    # 1. Loại bỏ các dòng dummy có chỉ số quá nhỏ/bằng phẳng (Ví dụ dòng 1.1, dòng 1.0)
    condition_dummy = (df['loc'] <= 1.1) & (df['v(g)'] <= 1.4)
    
    # 2. Loại bỏ các dòng lỗi hệ thống (Có dòng code nhưng các chỉ số Halstead phụ bị bằng 0 hoàn toàn)
    # Đây là nguyên nhân chính khiến mô hình đoán sai lớp Cao thành lớp Thấp khi che cột v(g) và loc.
    condition_zero_halstead = (df['loc'] > 5) & (df['v'] == 0.0) & (df['e'] == 0.0)
    
    # Áp dụng bộ lọc loại bỏ nhiễu mâu thuẫn nhãn
    df_clean = df[~(condition_dummy | condition_zero_halstead)].copy()
    print(f"🧹 Đã quét sạch {total_raw - df_clean.shape[0]} dòng dữ liệu mâu thuẫn hệ thống.")

    # Điền các giá trị trống phát sinh còn lại (nếu có) bằng Median
    df_clean = df_clean.fillna(df_clean.median(numeric_only=True))

    # Chuẩn hóa giá trị cột defects về dạng Số (1 và 0) thay vì Boolean chữ
    if 'defects' in df_clean.columns:
        df_clean['defects'] = df_clean['defects'].astype(str).str.strip().str.lower()
        df_clean['defects'] = df_clean['defects'].isin(['true', '1', 't', '1.0']).astype(int)

    # === LOGIC GÁN NHÃN 3 MỨC CHUẨN ===
    def assign_risk_level(row):
        is_defective = int(row.get('defects', 0))
        loc_val = row.get('loc', 0)
        vg_val = row.get('v(g)', 0)
        
        # MỨC 2: CAO - Code dính lỗi thật (defects = 1)
        if is_defective == 1:
            return 2
        # MỨC 1: TRUNG BÌNH - Chưa lỗi nhưng cấu trúc loằng ngoằng theo chuẩn NIST (v(g) > 10 hoặc loc > 50)
        elif vg_val > 10 or loc_val > 50:
            return 1
        # MỨC 0: THẤP - Code sạch, an toàn
        else:
            return 0

    print("-> Đang gán lại nhãn rủi ro thực chất...")
    df_clean['risk_level'] = df_clean.apply(assign_risk_level, axis=1)

    # Danh sách đặc trưng chuẩn xuất ra
    features_to_keep = [
        'loc', 'v(g)', 'ev(g)', 'iv(g)', 'n', 'v', 'l', 'd', 'i', 'e', 'b', 't',
        'locode', 'locomment', 'loblank', 'loccodeandcomment', 
        'uniq_op', 'uniq_opnd', 'total_op', 'total_opnd', 'branchcount', 'defects', 'risk_level'
    ]
    
    df_final = df_clean[[col for col in features_to_keep if col in df_clean.columns]]

    # Lưu file processed sạch bóng nhiễu
    os.makedirs(os.path.dirname(JM1_PROCESSED), exist_ok=True)
    df_final.to_csv(JM1_PROCESSED, index=False)
    
    print(f"✔ Thành công! File dữ liệu siêu sạch đã lưu tại: {JM1_PROCESSED}")
    print("📊 Phân bổ số lượng mẫu sau khi loại bỏ mâu thuẫn nhãn:")
    print(df_final['risk_level'].value_counts())

if __name__ == "__main__":
    process_chot1()