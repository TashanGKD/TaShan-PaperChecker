#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
API功能测试脚本
"""

import requests
import json
import os
import sys

def test_api_endpoints():
    """测试API的各种端点"""
    base_url = "http://localhost:8000"
    
    print("测试API端点...")
    
    # 测试根端点
    print("\n1. 测试根端点...")
    try:
        response = requests.get(f"{base_url}/")
        data = response.json()
        print(f"   状态码: {response.status_code}")
        print(f"   响应: {data}")
        assert data["message"] == "PaperChecker API"
        print("   ✓ 根端点测试通过")
    except Exception as e:
        print(f"   ✗ 根端点测试失败: {e}")
    
    # 测试健康端点
    print("\n2. 测试健康端点...")
    try:
        response = requests.get(f"{base_url}/api/health")
        data = response.json()
        print(f"   状态码: {response.status_code}")
        print(f"   响应: {data}")
        assert data["status"] == "healthy"
        print("   ✓ 健康端点测试通过")
    except Exception as e:
        print(f"   ✗ 健康端点测试失败: {e}")
    
    # 测试API文档
    print("\n3. 测试API文档端点...")
    try:
        response = requests.get(f"{base_url}/docs")
        print(f"   状态码: {response.status_code}")
        assert "PaperChecker API" in response.text
        print("   ✓ API文档端点测试通过")
    except Exception as e:
        print(f"   ✗ API文档端点测试失败: {e}")
    
    # 测试OpenAPI规范
    print("\n4. 测试OpenAPI规范端点...")
    try:
        response = requests.get(f"{base_url}/openapi.json")
        data = response.json()
        print(f"   状态码: {response.status_code}")
        assert "PaperChecker API" == data["info"]["title"]
        print(f"   API标题: {data['info']['title']}")
        print(f"   API版本: {data['info']['version']}")
        print("   ✓ OpenAPI规范端点测试通过")
    except Exception as e:
        print(f"   ✗ OpenAPI规范端点测试失败: {e}")
    
    print("\nAPI端点测试完成！")

if __name__ == "__main__":
    test_api_endpoints()