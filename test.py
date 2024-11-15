import requests
import json

# 发送请求
response = requests.get("http://127.0.0.1:5010/get/?table_name=zhiwang")

# 检查响应码
if response.status_code == 200:
    # 解析 JSON 内容
    data = response.json()  # 直接使用 .json() 方法将响应内容转换为字典
    # 获取 proxy 字段
    proxy = data.get('proxy', None)
    if proxy:
        print(f"{proxy}")
    else:
        print("No proxy found.")
else:
    print(f"Error: {response.status_code}")