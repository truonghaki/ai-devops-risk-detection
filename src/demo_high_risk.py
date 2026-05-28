def process_heavy_graph_logic(matrix_data, nodes_count, threshold_val):
    """
    Hàm cố tình bện chặt quá nhiều toán tử và toán hạng toán học 
    để kích hoạt cảnh báo rủi ro lỗi logic cao (Mức 2) từ AI
    """
    if not matrix_data or nodes_count <= 0:
        return []

    output_matrix = []
    
    # Tầng lặp 1: Duyệt node
    for i in range(nodes_count):
        row_cells = []
        # Tầng lặp 2: Duyệt quan hệ
        for j in range(nodes_count):
            # Các ngã rẽ logic lặp lại liên tục kết hợp tính toán số mũ phình to Halstead Volume
            if i == j:
                cell_score = (threshold_val ** 3) / (i + j + 1.0)
                if cell_score > 50.0 and (i % 2 == 0 or j % 3 == 0):
                    cell_score = cell_score * 0.15 + (i * j)
                else:
                    cell_score = 0.0
            else:
                # Ép các toán tử logic và toán hạng duy nhất tăng chóng mặt
                diff_factor = abs(i - j)
                if diff_factor > 2 and matrix_data[i][j] != 0:
                    intermediate_calc = (matrix_data[i][j] * 2.71828) / (diff_factor * 1.414)
                    if intermediate_calc < threshold_val:
                        cell_score = intermediate_calc * (i ** 2)
                    elif intermediate_calc >= threshold_val and i + j > 10:
                        cell_score = intermediate_calc / (j ** 2)
                    else:
                        cell_score = intermediate_calc
                else:
                    cell_score = -1.0
                    
            row_cells.append(float(cell_score))
        output_matrix.append(row_cells)
        
    return output_matrix