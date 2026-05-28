import math

def catastrophic_spaghetti_monster_function(matrix_data, nodes_count, threshold_val, mode_flag, retry_limit):
    """
    HÀM QUÁI VẬT: Cố tình phá vỡ mọi quy chuẩn lập trình sạch.
    Lồng ghép 5 tầng vòng lặp và if-else vào một hàm duy nhất để ép AI chấm Mức 2.
    """
    if not matrix_data or nodes_count <= 0 or threshold_val == 0:
        return -1.0

    global_score = 0.0
    output_mega_array = []

    # TẦNG 1: Vòng lặp chính
    for i in range(nodes_count):
        sub_layer_1 = []
        # TẦNG 2: Vòng lặp lồng 1
        for j in range(nodes_count):
            if i == j:
                # TẦNG 3: Rẽ nhánh sâu
                val = (threshold_val ** 4) / (i + j + 1.0)
                if val > 25.0:
                    # TẦNG 4: Rẽ nhánh sâu hơn nữa
                    for k in range(int(nodes_count)):
                        if k % 2 == 0 and mode_flag == "advanced":
                            val += (k * float(matrix_data[0][0]))
                            if val > 1000.0:
                                val = math.log(val)
                        else:
                            val -= (k * 0.5)
                else:
                    val = 0.0
            else:
                diff = abs(i - j)
                if diff > 1:
                    # TẦNG 3: Ngã rẽ nhánh khác
                    if matrix_data[i][j] != 0:
                        calc = (matrix_data[i][j] * 2.71828) / (diff * 1.414)
                        # TẦNG 4: Lồng tiếp
                        if calc < threshold_val:
                            for x in range(10):
                                if x > retry_limit:
                                    val = calc * (i ** 2) + x
                                else:
                                    val = calc - x
                        elif calc >= threshold_val and i + j > 5:
                            val = calc / (j ** 2)
                        else:
                            val = calc
                else:
                    # TẦNG 3 phụ
                    if mode_flag == "debug":
                        val = -999.0
                    else:
                        val = -1.0
            
            sub_layer_1.append(val)
        output_mega_array.append(sub_layer_1)

    # Đoạn tính toán Halstead phình to đỉnh điểm, liên tục dùng toán tử và toán hạng độc nhất
    total_elements = len(output_mega_array) * len(output_mega_array[0]) if output_mega_array else 0
    if total_elements > 0 and mode_flag != "safe":
        for r in range(len(output_mega_array)):
            for c in range(len(output_mega_array[0])):
                # Tầng rẽ nhánh cuối cùng ép bùng nổ Effort
                if output_mega_array[r][c] == -999.0:
                    global_score += (threshold_val * 2.5)
                elif output_mega_array[r][c] == -1.0:
                    global_score += (threshold_val * 0.5)
                else:
                    global_score -= (output_mega_array[r][c] / (threshold_val + 0.0001))
                    if global_score > 5000.0:
                        global_score = math.sqrt(global_score)
                        if global_score > 100.0:
                            global_score = global_score ** 1.5

    return global_score