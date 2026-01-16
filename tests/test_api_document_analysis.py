#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试API文档分析功能
模拟前端上传文档，后端返回JSON报告
"""

import requests
import json
import os

def test_api_document_analysis():
    """测试API文档分析功能"""
    base_url = "http://localhost:8000"
    
    print("测试API文档分析功能...")
    
    # 检查示例文档是否存在
    doc_path = os.path.join(os.path.dirname(__file__), "examples", "毛文静-最终论文.docx")
    if not os.path.exists(doc_path):
        print(f"错误: 找不到文档 {doc_path}")
        return
    
    print(f"准备上传文档: {doc_path}")
    
    # 测试文件上传接口
    print("\n1. 测试 /api/full-report 端点...")
    try:
        with open(doc_path, 'rb') as f:
            files = {'file': f}
            response = requests.post(f"{base_url}/api/full-report", files=files)
        
        print(f"   状态码: {response.status_code}")
        
        if response.status_code == 200:
            # 检查响应是否为JSON格式
            try:
                result = response.json()
                print("   响应格式: JSON (成功)")
                
                # 检查返回的JSON是否包含预期的字段
                expected_fields = ['test_date', 'document', 'total_citations', 
                                 'total_references', 'results', 'matched_count', 
                                 'unmatched_count', 'match_rate']
                
                missing_fields = [field for field in expected_fields if field not in result]
                if not missing_fields:
                    print("   ✓ 返回的JSON包含所有预期字段")
                else:
                    print(f"   ⚠ 缺少字段: {missing_fields}")
                
                # 显示一些关键统计信息
                print(f"   - 文档: {result.get('document', 'N/A')}")
                print(f"   - 总引用数: {result.get('total_citations', 'N/A')}")
                print(f"   - 总参考文献数: {result.get('total_references', 'N/A')}")
                print(f"   - 成功匹配数: {result.get('matched_count', 'N/A')}")
                print(f"   - 未匹配数: {result.get('unmatched_count', 'N/A')}")
                print(f"   - 匹配率: {result.get('match_rate', 'N/A')}")
                
                # 保存返回的JSON到文件（模拟前端接收）
                with open('/tmp/test_api_result.json', 'w', encoding='utf-8') as output_file:
                    json.dump(result, output_file, ensure_ascii=False, indent=2)
                print(f"   - 结果已保存到 /tmp/test_api_result.json")
                
                print("   ✓ API文档分析功能测试通过")
                return result
                
            except json.JSONDecodeError:
                print("   ✗ 响应不是有效的JSON格式")
                print(f"   响应内容: {response.text[:200]}...")
                return None
        else:
            print(f"   ✗ 请求失败，状态码: {response.status_code}")
            print(f"   响应内容: {response.text}")
            return None
            
    except Exception as e:
        print(f"   ✗ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    test_api_document_analysis()