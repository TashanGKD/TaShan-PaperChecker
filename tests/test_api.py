import requests
import os

# 测试服务器是否运行
def test_api():
    # 测试根端点
    response = requests.get("http://localhost:8000/")
    print("Root endpoint:", response.json())
    
    # 测试健康端点
    response = requests.get("http://localhost:8000/api/health")
    print("Health endpoint:", response.json())
    
    # 获取API文档
    response = requests.get("http://localhost:8000/docs")
    print("Docs status:", response.status_code)

if __name__ == "__main__":
    test_api()