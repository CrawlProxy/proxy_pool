import requests
import csv
import os
from bs4 import BeautifulSoup
import time
import multiprocessing
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
import singleDownload
import save




class Downloader:
    def __init__(self, source_file_name, to_file_name):
        self.source_file_name = source_file_name
        self.to_file_name = to_file_name
        self.batches = []

        # 创建一个独立的会话对象
        self.session = requests.Session()

        # 设置重试机制
        retries = Retry(
            total=2,               # 最大重试次数
            backoff_factor=0.3,     # 退避因子
            status_forcelist=[500, 502, 503, 504],  # 服务器错误时重试，只有这几个才充实
            method_whitelist=["GET", "POST"],      # 重试的 HTTP 方法
        )

        # 为会话对象添加重试机制
        self.session.mount('http://', HTTPAdapter(max_retries=retries))
        self.session.mount('https://', HTTPAdapter(max_retries=retries))

        self.proxy = self.get_proxy("zhiwang")
        self.proxies = {
            "http": self.proxy,
            "https": self.proxy,
        }


    def read_csv_and_download(self):
        # 获取上次保存的行数
        row_count = 1
        file_exists = os.path.isfile(self.to_file_name)
        if not file_exists:
            row_count = 1
        else:
            with open(self.to_file_name, mode='r', newline='', encoding='utf-8') as file:
                reader = csv.reader(file)
                row_count = sum(1 for row in reader)

        
        # 读取 CSV 文件并处理
        with open(self.source_file_name, 'r', newline='', encoding='utf-8') as file:
            reader = csv.reader(file)
            # 跳过已经存储的行
            for i in range(row_count):
                next(reader)  

            count = 0
            for row in reader:
                url = row[3]
                headers = {
                    "Referer": url,
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36 Edg/129.0.0.0"
                }

                # 请求并处理响应
                while_count = 20
                while while_count > 0:
                    try:
                        response = self.session.get(url, headers=headers, timeout=1, proxies=self.proxies)
                        # 检查响应码是否为 200
                        if response.status_code != 200:
                            raise Exception(f"请求失败，响应码：{response.status_code}")                        
                        while_count = 20
                        break
                    except Exception as e:
                        
                        print(f"发生错误：{e}。将重新获取代理")
                        
                        self.proxy = self.get_proxy("zhiwang")
                        self.proxies = {
                            "http": self.proxy,
                            "https": self.proxy,
                        }
                        while_count = while_count - 1

                # 异常情况，需要终止循环        
                # 如果不为20，说明不是成功的
                if while_count != 20:
                    break
                html_content = response.text
                soup = BeautifulSoup(html_content, 'html.parser')
                wrong_tag = soup.find(class_="verify_wrap")
                if wrong_tag is not None:
                    print("需要使用验证码，停止下载")
                    break

                # 保存页面内容
                save_dict = singleDownload.scrapy_and_save(html_content, url)
                self.batches.append(save_dict)
                count = count + 1
                if(count >= 1):
                    save.func_for_save(self.batches, self.to_file_name)
                    self.batches = []
                    count = 0
            # 最后一批不满100，没有写入，现在要补上
            if  self.batches:
                    save.func_for_save(self.batches, self.to_file_name)
                    self.batches = []
                    count = 0

    def get_proxy(self, website):
        # 最多尝试20次
        count = 20
        while count > 0:
            try:
                response = self.session.get("http://127.0.0.1:5010/get/?table_name=" + website,  timeout=1)
                # 检查响应码
                if response.status_code == 200:
                    # 解析 JSON 内容
                    data = response.json()  # 直接使用 .json() 方法将响应内容转换为字典
                    # 获取 proxy 字段
                    return data.get('proxy', None)
            except Exception as e:
                print("没有获得代理，重新尝试")
                count = count -1




# 通用任务函数
def task(file_name, output_file):
    downloader = Downloader(file_name, output_file)
    downloader.read_csv_and_download()


if __name__ == "__main__":
    # 记录开始时间
    start_time = time.time()
    
    # 获取所有源文件名
    base_file_name = "papers"
    file_extension = ".csv"

    # 动态生成任务列表
    tasks = [(f"{base_file_name}_chunk_{i}{file_extension}", f"{base_file_name}_chunk_{i}-article.csv") for i in range(0, 16)]

    # 使用多进程来处理任务
    procs = []
    for task_params in tasks:
        # 使用 *task_params 来解包元组，将它们传递给任务函数
        p = multiprocessing.Process(target=task, args=task_params)
        procs.append(p)
        p.start()

    for p in procs:
        p.join()

    
    # 记录结束时间
    end_time = time.time()

    # 计算运行时间
    execution_time = end_time - start_time
    print(f"运行时间：{execution_time} 秒")
    print("所有任务完成。")
