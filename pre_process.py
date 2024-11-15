import os
import csv
from multiprocessing import Pool
import time

def write_chunk(data, chunk_id, output_dir, first_row):
    with open(f"{output_dir}/papers_chunk_{chunk_id}.csv", mode='w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(first_row)
        writer.writerows(data)

def split_file(input_file, num_chunks, output_dir):
    # 创建输出目录
    os.makedirs(output_dir, exist_ok=True)



    # 读取输入文件，并按行分割
    with open(input_file, 'r', newline='', encoding='utf-8') as file:
        reader = csv.reader(file)
        first_row = next(reader) 
        lines = list(reader)    # lines也是根据读指针来的，读指针已经过了第一行了
        
        print(len(lines))
    
    # 计算每个文件分配的行数
    chunk_size = len(lines) // num_chunks

    # 分割文件并使用多进程写入小文件
    chunks = [lines[i:i + chunk_size+2] for i in range(0, len(lines), chunk_size+2)]    #+2，以免有的进程跑的数量太少
    with Pool(processes=num_chunks) as pool:
        pool.starmap(write_chunk, [(chunk, i, output_dir, first_row) for i, chunk in enumerate(chunks)])

if __name__=="__main__":

    # 记录开始时间
    start_time = time.time()
    # 使用示例
    input_file = 'papers.csv'
    output_dir = '.'
    num_chunks = 16  # 将文件分成16份
    split_file(input_file, num_chunks, output_dir)
    # 记录结束时间
    end_time = time.time()

    # 计算运行时间
    execution_time = end_time - start_time
    print(f"运行时间：{execution_time} 秒")
    print("所有任务完成。")