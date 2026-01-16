#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
逐一测试 papers 目录中的 PDF 文件
"""

import sys
import os
from pathlib import Path

# 添加项目根目录到路径
current_dir = Path(__file__).parent
project_root = current_dir.parent  # 上一级目录是项目根目录
sys.path.insert(0, str(project_root))

from core.extractor.extractor_factory import ExtractorFactory


def test_pdf_files():
    """测试 papers 目录中的所有 PDF 文件"""
    papers_dir = current_dir / "papers"

    if not papers_dir.exists():
        print(f"错误: 找不到目录 {papers_dir}")
        return

    pdf_files = list(papers_dir.glob("*.pdf"))
    
    if not pdf_files:
        print(f"在 {papers_dir} 中没有找到 PDF 文件")
        return
    
    print(f"找到 {len(pdf_files)} 个 PDF 文件:")
    for i, pdf_file in enumerate(pdf_files, 1):
        print(f"  {i}. {pdf_file.name}")
    
    print("\n开始逐一测试 PDF 文件...")
    
    success_count = 0
    error_count = 0
    
    for i, pdf_file in enumerate(pdf_files, 1):
        print(f"\n{'='*60}")
        print(f"正在测试 ({i}/{len(pdf_files)}): {pdf_file.name}")
        print(f"{'='*60}")
        
        try:
            # 创建提取器实例
            extractor = ExtractorFactory.get_extractor(str(pdf_file))
            
            # 提取文档内容
            print("开始提取文档内容...")
            document = extractor.extract(str(pdf_file))
            
            print(f"提取成功!")
            print(f"  - 正文段落数: {len(document.content)}")
            print(f"  - 表格数: {len(document.tables)}")
            print(f"  - 引用数: {len(document.citations)}")
            print(f"  - 参考文献数: {len(document.references)}")
            
            # 统计引用类型
            author_year_citations = [c for c in document.citations if c.format_type == 'author_year']
            number_citations = [c for c in document.citations if c.format_type == 'number']
            
            print(f"  - 作者年份格式引用: {len(author_year_citations)}")
            print(f"  - 数字格式引用: {len(number_citations)}")
            
            success_count += 1
            
        except Exception as e:
            print(f"提取失败: {str(e)}")
            error_count += 1
    
    print(f"\n{'='*60}")
    print("测试总结:")
    print(f"  总文件数: {len(pdf_files)}")
    print(f"  成功: {success_count}")
    print(f"  失败: {error_count}")
    print(f"  成功率: {success_count/len(pdf_files)*100:.1f}%")
    print(f"{'='*60}")


if __name__ == "__main__":
    test_pdf_files()