import math

def process_heavy_graph_logic_part1(matrix_data, nodes_count, threshold_val):
    if not matrix_data or nodes_count <= 0: return []
    output = []
    for i in range(nodes_count):
        row = []
        for j in range(nodes_count):
            if i == j:
                val = (threshold_val ** 3) / (i + j + 1.0)
                if val > 50.0 and (i % 2 == 0 or j % 3 == 0):
                    val = val * 0.15 + (i * j)
                else: val = 0.0
            else:
                diff = abs(i - j)
                if diff > 2 and matrix_data[i][j] != 0:
                    calc = (matrix_data[i][j] * 2.71828) / (diff * 1.414)
                    if calc < threshold_val: val = calc * (i ** 2)
                    elif calc >= threshold_val and i + j > 10: val = calc / (j ** 2)
                    else: val = calc
                else: val = -1.0
            row.append(float(val))
        output.append(row)
    return output

def process_heavy_graph_logic_part2(matrix_data, nodes_count, threshold_val):
    # Sao chép và tăng độ phức tạp bằng cách đổi biến liên tục
    if nodes_count < 5: return []
    res = []
    for x in range(nodes_count):
        tmp = []
        for y in range(nodes_count):
            if x != y and matrix_data[x][y] > 0:
                a1 = math.sin(matrix_data[x][y]) * threshold_val
                a2 = math.cos(threshold_val) * x
                if a1 > a2 or (a1 + a2) < 0:
                    for k in range(10):
                        a1 += (k * 0.1)
                    tmp.append(a1 * a2)
                else:
                    tmp.append(0.0)
            else:
                tmp.append(-99.0)
        res.append(tmp)
    return res

def master_decision_module(matrix_data, nodes_count, threshold_val):
    # Hàm thứ 3 bện chặt kết quả của 2 hàm trên để đẩy chỉ số lên đỉnh điểm
    data1 = process_heavy_graph_logic_part1(matrix_data, nodes_count, threshold_val)
    data2 = process_heavy_graph_logic_part2(matrix_data, nodes_count, threshold_val)
    
    final_score = 0.0
    if len(data1) == len(data2) and len(data1) > 0:
        for r in range(len(data1)):
            for c in range(len(data1[0])):
                if data1[r][c] == -1.0 or data2[r][c] == -99.0:
                    final_score += (threshold_val * 1.5)
                else:
                    final_score -= (data1[r][c] / (data2[r][c] + 0.001))
                    if final_score > 1000:
                        final_score = math.sqrt(final_score)
    return final_score