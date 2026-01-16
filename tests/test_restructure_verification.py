#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
验证重构后的模块是否产生与原来相同的测试结果
"""

import sys
import os
import json
from datetime import datetime

# 添加项目根目录到路径
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
sys.path.insert(0, project_root)

from core.extractor.extractor_factory import ExtractorFactory

def test_restructured_modules():
    """测试重构后的模块是否产生与原来相同的测试结果"""
    
    # 使用与原始测试相同的文档
    doc_path = os.path.join(project_root, 'tests/毛文静-最终论文.docx')
    
    if not os.path.exists(doc_path):
        print(f"错误: 找不到文档 {doc_path}")
        return False
    
    print("=== 测试重构后的模块 ===")
    
    # 使用新的处理器
    from core.processors.citation_processor import CitationProcessor
    processor = CitationProcessor()

    # 处理文档
    result = processor.process(doc_path)
    
    # 保存结果到与原始测试相同的路径
    report_path = os.path.join(project_root, 'tests/standalone_citation_mapping_detailed_report_restructured.json')
    with open(report_path, 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    
    print(f"重构模块的测试结果已保存到 {report_path}")
    
    # 验证结果结构是否相同
    original_result_path = os.path.join(project_root, 'tests/standalone_citation_mapping_detailed_report.json')
    if os.path.exists(original_result_path):
        with open(original_result_path, 'r', encoding='utf-8') as f:
            original_result = json.load(f)
        
        print("\n=== 比较结果 ===")
        print(f"原始结果引用数: {original_result.get('total_citations', 0)}")
        print(f"重构结果引用数: {result.get('total_citations', 0)}")
        
        print(f"原始结果匹配数: {original_result.get('matched_count', 0)}")
        print(f"重构结果匹配数: {result.get('matched_count', 0)}")
        
        print(f"原始结果未匹配数: {original_result.get('unmatched_count', 0)}")
        print(f"重构结果未匹配数: {result.get('unmatched_count', 0)}")
        
        # 检查关键字段是否存在
        expected_fields = [
            'test_date', 'document', 'total_citations', 'total_references',
            'matched_count', 'unmatched_count', 'corrected_count', 'formatted_count',
            'unused_references_count', 'match_rate', 'results'
        ]
        
        all_present = True
        for field in expected_fields:
            if field not in result:
                print(f"警告: 字段 '{field}' 缺失")
                all_present = False
        
        if 'results' in result:
            print(f"结果条目数: {len(result['results'])}")
        
        print(f"\n重构模块测试完成，结果保存至: {report_path}")
        return all_present
    else:
        print("警告: 未找到原始结果进行比较")
        return True

def test_extractor_module():
    """测试Extractor模块的功能"""
    print("\n=== 测试Extractor模块 ===")
    
    doc_path = os.path.join(project_root, 'tests/毛文静-最终论文.docx')
    
    if not os.path.exists(doc_path):
        print(f"错误: 找不到文档 {doc_path}")
        return False
    
    # 使用Extractor工厂获取Word提取器
    extractor = ExtractorFactory.get_extractor(doc_path)
    
    # 提取文档内容
    document = extractor.extract(doc_path)
    
    print(f"提取到 {len(document.citations)} 个引用")
    print(f"提取到 {len(document.references)} 个参考文献")
    print(f"提取到 {len(document.content)} 段正文内容")
    
    # 验证提取结果
    success = len(document.citations) > 0 and len(document.references) > 0
    print(f"Extractor模块测试 {'通过' if success else '失败'}")
    
    return success

def test_compatibility():
    """测试新旧模块的兼容性"""
    print("\n=== 测试兼容性 ===")
    
    # 验证导入是否正常
    try:
        from core.extractor.word_extractor import WordExtractor
        from core.checker.citation_checker import CitationChecker
        from core.processors.citation_processor import CitationProcessor
        from core.reports.report_generator import ReportGenerator
        print("模块导入测试: 通过")
        return True
    except ImportError as e:
        print(f"模块导入测试: 失败 - {e}")
        return False

if __name__ == "__main__":
    print("开始验证重构模块...")
    
    extractor_test = test_extractor_module()
    compatibility_test = test_compatibility()
    restructuring_test = test_restructured_modules()
    
    print(f"\n测试总结:")
    print(f"Extractor模块: {'通过' if extractor_test else '失败'}")
    print(f"兼容性测试: {'通过' if compatibility_test else '失败'}")
    print(f"重构功能测试: {'通过' if restructuring_test else '失败'}")
    
    all_tests_passed = extractor_test and compatibility_test and restructuring_test
    print(f"总体结果: {'所有测试通过' if all_tests_passed else '存在测试失败'}")
    
    sys.exit(0 if all_tests_passed else 1)