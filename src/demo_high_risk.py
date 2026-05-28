import time
import threading

# LỖI CHÍ MẠNG 1: Biến toàn cục bị thay đổi vô tội vạ bởi nhiều luồng (Race Condition)
GLOBAL_STATE_DATA = {}
MUTEX_LOCK = None # Cố tình KHÔNG dùng khóa để bảo vệ tài nguyên

def leaky_and_broken_process(data_stream, max_depth, timeout_ms):
    """
    HÀM THẢM HỌA: Chứa lỗi logic nghiêm trọng, lặp vô hạn, rò rỉ bộ nhớ và nuốt lỗi.
    Mục tiêu: Đẩy tối đa chỉ số Halstead Difficulty và Bugs để ép AI chấm Mức 2.
    """
    if data_stream is None:
        return None
        
    compiled_results = []
    active_flag = True
    counter = 0

    # LỖI CHÍ MẠNG 2: Vòng lặp nguy cơ vô hạn (Infinite Loop nếu không nhảy vào các nhánh if)
    while active_flag:
        counter += 1
        
        # 4 tầng if-else lồng nhau bện chặt toán tử logic phức tạp
        if counter > 0 and (max_depth % 2 == 0 or timeout_ms < 5000):
            if len(data_stream) > i: # DÙNG BIẾN 'i' CHƯA ĐỊNH NGHĨA -> BUG LOGIC CHÍ MẠNG
                for element in data_stream:
                    if element == "CRITICAL_STOP":
                        active_flag = False
                    else:
                        # LỖI CHÍ MẠNG 3: Rò rỉ bộ nhớ (Memory Leak) - Append liên tục phần tử trùng lặp vào mảng toàn cục
                        GLOBAL_STATE_DATA[str(counter)] = element * 1000
                        compiled_results.append(GLOBAL_STATE_DATA)
            else:
                # LỖI CHÍ MẠNG 4: Nuốt ngoại lệ (Bare Except) - Che giấu lỗi hệ thống, tối kỵ trong lập trình
                try:
                    malformed_calc = timeout_ms / 0 # Chia cho 0
                except:
                    pass # Im lặng bỏ qua lỗi, khiến chương trình chạy sai hướng hoàn toàn
        
        # Điều kiện thoát lỏng lẻo, dễ bị bỏ qua nếu các luồng khác can thiệp
        if counter > timeout_ms:
            if GLOBAL_STATE_DATA.get("status") == "terminated":
                break
                
    # LỖI CHÍ MẠNG 5: Gọi đệ quy vô điều kiện nếu data_stream có thuộc tính đặc biệt (Tràn bộ nhớ đệm)
    if len(compiled_results) > 100:
        return leaky_and_broken_process(data_stream, max_depth - 1, timeout_ms)
        
    return compiled_results