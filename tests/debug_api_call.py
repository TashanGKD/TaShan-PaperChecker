#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
调试API调用
"""

import requests
import json
import os

def debug_api_call():
    """调试API调用"""
    base_url = "http://localhost:8000"
    
    print("调试API调用...")
    
    # 检查示例文档是否存在
    doc_path = os.path.join(os.path.dirname(__file__), "examples", "毛文静-最终论文.docx")
    if not os.path.exists(doc_path):
        print(f"错误: 找不到文档 {doc_path}")
        return
    
    print(f"准备上传文档: {doc_path}")
    
    try:
        # 上传文件
        with open(doc_path, 'rb') as f:
            files = {'file': (os.path.basename(doc_path), f, 'application/vnd.openxmlformats-officedocument.wordprocessingml.document')}
            response = requests.post(f"{base_url}/api/full-report", files=files)
        
        print(f"状态码: {response.status_code}")
        print(f"响应头: {response.headers}")
        print(f"响应内容: {response.text}")
        
    except Exception as e:
        print(f"请求失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_api_call()