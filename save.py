import csv
import os


def func_for_save(batches, to_file_name):
    # 文件路径
    file_path = to_file_name

    # 判断文件是否存在
    file_exists = os.path.isfile(file_path)

    # 打开文件，模式为 'a' 以实现追加写入
    with open(file_path, mode='a', newline='', encoding='utf-8') as file:
        fieldnames = list(batches[0].keys())
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        # 如果文件不存在，写入表头
        if not file_exists:
            # 写入首行：去掉冒号的字段名
            cleaned_header = [field.rstrip("：") for field in fieldnames]
            writer.writerow(dict(zip(fieldnames, cleaned_header)))        
  
        for save_dict in batches:
            if not isinstance(save_dict, dict):
                print("不对")
                raise ValueError("Expected save_dict to be a dictionary, but got {}".format(type(save_dict).__name__))
            writer.writerow(save_dict)


        

