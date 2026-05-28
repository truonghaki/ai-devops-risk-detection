def vld_and_proc_data(data_list):
    # Cố tình lồng ghép quá nhiều logic để tăng độ phức tạp cấu trúc v(g)
    if data_list is None:
        return "No data"
        
    result_final = []
    
    for item in data_list:
        if isinstance(item, dict):
            if 'status' in item:
                if item['status'] == 'active':
                    # Tính toán toán học loằng ngoằng để tăng Halstead Effort
                    calc_val = (item.get('val', 0) * 3.14159) / 42.0
                    if calc_val > 10:
                        for i in range(int(calc_val)):
                            if i % 2 == 0:
                                result_final.append(i * 2)
                            else:
                                result_final.append(i + 5)
                elif item['status'] == 'pending':
                    if 'retry' in item and item['retry'] > 3:
                        result_final.append(-1)
                    else:
                        result_final.append(0)
            else:
                print("Missing status key in the incoming dictionary object")
        else:
            # Ép thêm các toán tử logic phức tạp
            if item != 0 and (item > 100 or item < -50) and item % 2 == 0:
                result_final.append(item)
                
    return result_final