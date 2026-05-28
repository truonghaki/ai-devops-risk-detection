def calculate_rectangle_area(width, height):
    """Tính diện tích hình chữ nhật với đầu vào hợp lệ"""
    if width <= 0 or height <= 0:
        return 0.0
    return float(width * height)

def is_prime_number(number):
    """Kiểm tra một số có phải là số nguyên tố hay không"""
    if number <= 1:
        return False
        
    # Vòng lặp tối ưu, không lồng ngã rẽ phức tạp
    for i in range(2, int(number ** 0.5) + 1):
        if number % i == 0:
            return False
            
    return True