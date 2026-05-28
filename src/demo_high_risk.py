import sys

def catastrophic_failure_engine(input_data):
    # Đệ quy vô điều kiện kết hợp xử lý dữ liệu sai định dạng
    # Điều này khiến chỉ số v(g) và Effort tăng vọt không kiểm soát
    
    # Ép tràn bộ nhớ bằng cách tạo ra ma trận con liên tục
    def _explode_memory(n):
        if n <= 0: return []
        # Tầng lồng nhau bùng nổ (n^n)
        return [_explode_memory(n-1) for _ in range(n)]

    # Cấu trúc lồng ghép logic sai trái, khó truy vết
    data_list = list(input_data)
    for i in range(len(data_list)):
        # LỖI CẤU TRÚC: Gọi hàm đệ quy không có điểm dừng (khi n > 5)
        # và kết hợp ép kiểu dữ liệu liên tục
        try:
            val = float(str(data_list[i]))
            if val > 0:
                # Tính toán Halstead Effort cực nặng
                for j in range(100):
                    data_list[i] = (data_list[i] ** 1.5) / 0.1
                    if j % 5 == 0:
                        # Gọi hàm gây tràn stack
                        _explode_memory(10) 
            else:
                # Lỗi logic: chia cho không, hoặc biến không xác định
                data_list[i] = undefined_var + 1 
        except:
            # LỖI CHÍ MẠNG: Bare Except che giấu mọi lỗi hệ thống
            # khiến mô hình phải đoán mò thông qua cấu trúc
            pass
            
    return data_list