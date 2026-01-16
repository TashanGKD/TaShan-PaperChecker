#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试示例文档的引文分析功能
"""

import os
import sys
import json
from datetime import datetime

# 添加项目根目录到路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from core.processors.citation_processor import CitationProcessor

def analyze_document(doc_path):
    """使用新的处理器分析文档"""
    processor = CitationProcessor()
    return processor.process(doc_path)

def test_example_document():
    """测试示例文档的引文分析功能"""
    print("=== 开始测试示例文档引文分析功能 ===")
    
    # 设置文档路径
    doc_path = os.path.join(project_root, "tests", "examples", "毛文静-最终论文.docx")
    
    # 检查文档是否存在
    if not os.path.exists(doc_path):
        print(f"错误: 找不到文档 {doc_path}")
        return None
    
    print(f"正在分析文档: {doc_path}")
    
    try:
        # 分析文档
        start_time = datetime.now()
        result = analyze_document(doc_path)
        end_time = datetime.now()
        
        print(f"\n分析完成，耗时: {end_time - start_time}")
        
        # 输出统计信息
        print(f"\n=== 分析结果统计 ===")
        print(f"总引用数: {result['total_citations']}")
        print(f"总参考文献数: {result['total_references']}")
        print(f"成功匹配数: {result['matched_count']}")
        print(f"未匹配数: {result['unmatched_count']}")
        print(f"需要修正数: {result['corrected_count']}")
        print(f"需要格式化数: {result['formatted_count']}")
        print(f"未使用参考文献数: {result['unused_references_count']}")
        print(f"匹配率: {result['match_rate']}")
        
        # 输出部分结果
        print(f"\n=== 部分分析结果示例 ===")
        if result['corrections_needed']:
            print("需要修正的引用示例 (前3个):")
            for i, correction in enumerate(result['corrections_needed'][:3]):
                print(f"  {i+1}. 原始: {correction['original']} -> 修正: {correction['corrected']}")
        
        if result['formatting_needed']:
            print("\n需要格式化的引用示例 (前3个):")
            for i, formatting in enumerate(result['formatting_needed'][:3]):
                print(f"  {i+1}. 原始: {formatting['original']} -> 格式化: {formatting['formatted']}")
        
        if result['unused_references']:
            print("\n未使用的参考文献示例 (前3个):")
            for i, ref in enumerate(result['unused_references'][:3]):
                print(f"  {i+1}. {ref['text'][:100]}...")
        
        print(f"\n=== 分析完成 ===")
        return result
        
    except Exception as e:
        print(f"分析过程中出现错误: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    test_example_document()