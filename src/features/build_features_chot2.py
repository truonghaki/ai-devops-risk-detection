import pandas as pd
import numpy as np
import os
import sys

# Khắc phục vấn đề import cấu hình từ thư mục gốc
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from config import K8S_PERFORMANCE, K8S_ALLOCATION, K8S_PROCESSED

def process_chot2():
    print("--- 🚀 TIỀN XỬ LÝ TOÀN DIỆN & TỐI ƯU HÓA 100% DATASET 2 (K8S) ---")
    
    if not os.path.exists(K8S_PERFORMANCE) or not os.path.exists(K8S_ALLOCATION):
        print("❌ Lỗi: Thiếu file CSV thô của Dataset 2 trong data/raw/")
        return

    # Đọc dữ liệu gốc
    df_perf = pd.read_csv(K8S_PERFORMANCE, encoding='utf-8-sig')
    df_alloc = pd.read_csv(K8S_ALLOCATION, encoding='utf-8-sig')
    
    # Chuẩn hóa tên cột về chữ thường và loại bỏ khoảng trắng thừa
    df_perf.columns = df_perf.columns.str.strip().str.lower()
    df_alloc.columns = df_alloc.columns.str.strip().str.lower()

    # GỘP TOÀN DIỆN (Outer Join): Giữ lại tất cả dữ liệu từ cả 2 file, thu về đầy đủ 26291 dòng
    df_merged = pd.merge(df_perf, df_alloc, on=['pod_name', 'namespace'], how='outer')
    print(f"📊 Tổng số lượng mẫu thu được sau khi gộp toàn phần: {df_merged.shape[0]} dòng.")

    # Chuyển đổi các cột số và xử lý dữ liệu khuyết thiếu bằng Median
    numeric_cols = [
        'cpu_allocation_efficiency', 'memory_allocation_efficiency', 'disk_io',
        'network_latency', 'node_temperature', 'node_cpu_usage', 'node_memory_usage',
        'pod_lifetime_seconds', 'cpu_request', 'cpu_limit', 'memory_request',
        'memory_limit', 'cpu_usage', 'memory_usage', 'restart_count',
        'uptime_seconds', 'network_bandwidth_usage'
    ]
    for col in numeric_cols:
        if col in df_merged.columns:
            df_merged[col] = pd.to_numeric(df_merged[col], errors='coerce')
            df_merged[col] = df_merged[col].fillna(df_merged[col].median())

    # Xử lý triệt để cột dữ liệu chữ bị khuyết (NaN) - Thay thế bằng chuỗi 'normal' hoặc 'unknown'
    categorical_cols = [
        'namespace', 'event_type', 'event_message', 
        'pod_status', 'deployment_strategy', 'scaling_policy'
    ]
    for col in categorical_cols:
        if col in df_merged.columns:
            # Điền khuyết dữ liệu dạng text thành chuỗi rỗng/mặc định trước khi ép kiểu string
            df_merged[col] = df_merged[col].fillna('normal').astype(str).str.strip().str.lower()

    if 'scaling_event' in df_merged.columns:
        df_merged['scaling_event'] = df_merged['scaling_event'].fillna('false').astype(str).str.strip().str.lower()
        df_merged['scaling_event'] = df_merged['scaling_event'].isin(['true', '1', 't']).astype(int)

    # === CHIẾN LƯỢC GÁN NHÃN 3 MỨC ĐÃ ĐƯỢC VÁ LỖI ÉP KIỂU SỐ THỰC ===
    def label_chot2_balanced(row):
        # Đảm bảo dữ liệu lấy ra chắc chắn là chuỗi ký tự bằng hàm str() để chặn lỗi float không thể lặp
        status = str(row.get('pod_status', 'normal'))
        msg = str(row.get('event_message', 'normal'))
        evt_type = str(row.get('event_type', 'normal'))
        restarts = row.get('restart_count', 0)
        
        node_cpu = row.get('node_cpu_usage', 50)
        node_mem = row.get('node_memory_usage', 50)
        latency = row.get('network_latency', 20)
        cpu_eff = row.get('cpu_allocation_efficiency', 0.5)

        # MỨC 2: CAO (Nguy kịch - Pod chết thực sự hoặc Node cạn kiệt tài nguyên nghiêm trọng)
        if (status == 'failed' or 
            'oomkilled' in msg or 
            restarts > 4 or 
            node_cpu > 92 or 
            node_mem > 92):
            return 2
            
        # MỨC 1: TRUNG BÌNH (Cảnh báo - Có dấu hiệu quá tải, lỗi log hoặc cấu hình không hiệu quả)
        elif (evt_type == 'error' or 
              evt_type == 'warning' or 
              'killed' in msg or
              status == 'unknown' or
              restarts > 0 or
              node_cpu > 70 or 
              node_mem > 70 or
              latency > 100 or
              cpu_eff < 0.1):
            return 1
            
        # MỨC 0: THẤP (An toàn)
        else:
            return 0

    print("-> Đang thực hiện gán nhãn phân phối lại hệ thống cân bằng...")
    df_merged['risk_level'] = df_merged.apply(label_chot2_balanced, axis=1)

    # Mã hóa các trường dạng chữ sang dạng số để mô hình Cây xử lý
    cols_to_encode = ['namespace', 'deployment_strategy', 'scaling_policy']
    for col in cols_to_encode:
        if col in df_merged.columns:
            df_merged[col] = df_merged[col].astype('category').cat.codes

    # Giữ lại danh sách các đặc trưng số học thuần túy
    features_to_keep = [
        'namespace', 'cpu_allocation_efficiency', 'memory_allocation_efficiency',
        'disk_io', 'network_latency', 'node_temperature', 'node_cpu_usage', 'node_memory_usage',
        'pod_lifetime_seconds', 'cpu_request', 'cpu_limit', 'memory_request', 'memory_limit',
        'cpu_usage', 'memory_usage', 'restart_count', 'uptime_seconds', 'network_bandwidth_usage',
        'scaling_event', 'risk_level'
    ]
    
    final_features = [col for col in features_to_keep if col in df_merged.columns]
    df_final = df_merged[final_features].fillna(0)

    # Tiến hành lưu trữ file sạch
    os.makedirs(os.path.dirname(K8S_PROCESSED), exist_ok=True)
    df_final.to_csv(K8S_PROCESSED, index=False)
    
    print(f"✔ Thành công! Đã xử lý trọn vẹn dữ liệu sạch tại: {K8S_PROCESSED}")
    print(f"📊 Tổng số lượng bản ghi thực tế xuất ra: {df_final.shape[0]} dòng.")
    print("📊 Phân bổ số lượng mẫu theo từng mức rủi ro sau khi tối ưu:")
    print(df_final['risk_level'].value_counts())

if __name__ == "__main__":
    process_chot2()