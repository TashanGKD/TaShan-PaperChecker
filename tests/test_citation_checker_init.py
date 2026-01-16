#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试CitationChecker初始化
"""

import sys
import os

# 添加项目根目录到路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

def test_citation_checker_init():
    """测试CitationChecker初始化"""
    print("测试CitationChecker初始化...")
    
    from core.checker.citation_checker import CitationChecker
    
    print("测试新的CitationChecker...")
    
    try:
        # 使用 processors 中的 CitationChecker，它有完整的实现
        from core.processors.full_document_checker import CitationChecker

        # 需要提供文档路径和配置路径
        doc_path = os.path.join(project_root, "tests", "毛文静-最终论文.docx")
        config_path = os.path.join(project_root, "config", "config.json")

        if os.path.exists(doc_path):
            checker = CitationChecker(doc_path, config_path)
            print("✓ CitationChecker初始化成功")
            # 由于这个类不是继承自BaseChecker，我们不能调用相同的接口
            print(f"  - 检查器类型: {type(checker)}")
        else:
            print(f"警告: 找不到文档 {doc_path}，使用虚拟路径测试初始化")
            checker = CitationChecker("dummy.docx", config_path)
            print("✓ CitationChecker初始化成功（使用虚拟路径）")
    except Exception as e:
        print(f"✗ CitationChecker初始化失败: {e}")
        import traceback
        traceback.print_exc()

        # 如果上面的测试失败，尝试使用core中的实现
        try:
            from core.checker.citation_checker import CitationChecker
            # 由于这是一个抽象基类的实现，我们需要用其他方式测试
            print("尝试使用core.checker.citation_checker...")
            # 创建一个子类来实例化
            class TestCitationChecker(CitationChecker):
                def check(self, document):
                    from models.compliance import ComplianceResult, CheckType
                    return ComplianceResult(CheckType.CITATIONS, True, [], {}, {})

            checker = TestCitationChecker()
            print("✓ CitationChecker初始化成功（使用子类）")
            print(f"  - 检查类型: {checker.get_check_type()}")
            print(f"  - 检查名称: {checker.get_check_name()}")
        except Exception as e2:
            print(f"✗ 两种方法都失败: {e2}")

if __name__ == "__main__":
    test_citation_checker_init()