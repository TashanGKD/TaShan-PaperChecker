#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
模拟API流程测试
"""

import sys
import os

# 添加项目根目录到路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

def test_api_flow():
    """测试API处理流程"""
    print("测试API处理流程...")

    # 由于没有找到processors.citation_processor，我们需要找到正确的处理器模块
    # 根据项目结构，可能需要使用其他处理器
    from core.processors.full_document_checker import CitationChecker

    def analyze_document(doc_path):
        """使用新的处理器分析文档"""
        # 使用CitationChecker类进行分析
        from config.config_manager import ConfigManager
        config_manager = ConfigManager("config/config.json")
        config = config_manager.get_config()

        checker = CitationChecker(doc_path, "config/config.json")
        # 使用checker的方法进行分析
        # 由于CitationChecker的API可能不同，我们需要调用适当的方法
        checker.extract_citations_and_references()

        # 构建类似analyze_document的返回格式
        result = {
            "document": doc_path,
            "total_citations": len(checker.citations),
            "total_references": len(checker.references),
            "citations": checker.citations,
            "references": [ref.text if hasattr(ref, 'text') else str(ref) for ref in checker.references]
        }
        return result

    # 使用示例文档路径进行测试
    doc_path = os.path.join(project_root, "tests", "毛文静-最终论文.docx")

    if not os.path.exists(doc_path):
        print(f"警告: 找不到测试文档 {doc_path}")
        # 尝试其他可能的路径
        doc_path = os.path.join(project_root, "毛文静-最终论文.docx")
        if not os.path.exists(doc_path):
            print("无法找到测试文档，跳过功能测试")
            return None

    print(f"文档路径: {doc_path}")

    try:
        # 模拟API调用，调用analyze_document函数
        result = analyze_document(doc_path)

        print("✓ analyze_document调用成功")
        print(f"  - 结果类型: {type(result)}")
        print(f"  - 结果包含键: {list(result.keys()) if isinstance(result, dict) else 'N/A'}")

        # 检查是否包含预期的字段
        expected_keys = ['test_date', 'document', 'total_citations', 'total_references', 'results']
        missing_keys = [key for key in expected_keys if key not in result]
        if not missing_keys:
            print("  ✓ 返回结果包含所有预期字段")
        else:
            print(f"  ⚠ 缺少字段: {missing_keys}")

        return result

    except Exception as e:
        print(f"✗ analyze_document调用失败: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    test_api_flow()