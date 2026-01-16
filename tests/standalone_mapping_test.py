#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
独立的引用与参考文献映射功能测试程序（重构版）
使用新的模块结构，实现端到端测试
"""

import sys
import os
import json
import re
from datetime import datetime

# 添加项目根目录到路径
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)  # Go up one level to project root
sys.path.insert(0, project_root)

from core.extractor.extractor_factory import ExtractorFactory
from core.checker.checker_factory import CheckerFactory
from core.checker.citation_checking.reference_mapper import map_author_year_citation_to_reference, extract_authors_from_reference, format_citation_by_authors


def contains_chinese(text):
    """检查文本是否包含中文字符"""
    return bool(re.search('[\u4e00-\u9fff]', text))


def extract_chinese_authors(reference_text):
    """
    从中文参考文献条目中提取作者列表
    """
    authors = []
    
    # 中文文献模式: 作者1,作者2.文章名...
    chinese_pattern = r'^([^\.]+?)\.'  # 匹配第一个句号之前的内容
    
    match = re.search(chinese_pattern, reference_text)
    if match:
        authors_str = match.group(1)
        # 分割作者 (中文使用逗号或顿号分隔)
        if '，' in authors_str:
            authors = [author.strip() for author in authors_str.split('，') if author.strip()]
        elif ',' in authors_str:
            authors = [author.strip() for author in authors_str.split(',') if author.strip()]
        else:
            authors = [authors_str.strip()]
        
        # 处理"等"字
        authors = [author for author in authors if author != '等']
    
    return authors


def extract_english_authors(reference_text):
    """
    从英文参考文献条目中提取作者列表
    
    返回:
        作者列表, 是否有et al.标记
    """
    authors = []
    has_et_al = False
    
    # 检查是否有et al.
    if re.search(r'et al\.?', reference_text, re.IGNORECASE):
        has_et_al = True
    
    # 提取作者部分 (通常在第一个句号或括号之前)
    match = re.search(r'^([^\(]+?)\(\d{4}\)', reference_text)
    if match:
        authors_str = match.group(1)
    else:
        match = re.search(r'^([^\.]+?)\.\s*\(\d{4}\)', reference_text)
        if match:
            authors_str = match.group(1)
        else:
            match = re.search(r'^([^\.]+?)\.', reference_text)
            if match:
                authors_str = match.group(1)
            else:
                # 如果以上模式都不匹配，尝试提取第一个逗号或句号之前的内容
                first_comma = reference_text.find(',')
                first_period = reference_text.find('.')
                
                if first_comma != -1 and (first_period == -1 or first_comma < first_period):
                    authors_str = reference_text[:first_comma]
                elif first_period != -1:
                    authors_str = reference_text[:first_period]
                else:
                    return authors, has_et_al
    
    # 处理"and"和"&"连接符
    authors_str = re.sub(r'\s+and\s+', ', ', authors_str)
    authors_str = re.sub(r'\s*&\s*', ', ', authors_str)
    
    # 移除"et al."等缩写
    authors_str = re.sub(r',?\s*et al\.?', '', authors_str, flags=re.IGNORECASE)
    
    # 改进的作者分割逻辑
    # 使用更智能的方法分割作者，考虑名字缩写中的逗号
    author_list = []
    current_author = ""
    in_abbreviation = False
    
    for char in authors_str:
        if char == ',' and not in_abbreviation:
            if current_author.strip():
                author_list.append(current_author.strip())
            current_author = ""
        else:
            current_author += char
            if char == '.':
                in_abbreviation = True
            elif char == ' ' and in_abbreviation:
                in_abbreviation = False
    
    if current_author.strip():
        author_list.append(current_author.strip())
    
    # 处理每个作者
    for author in author_list:
        # 处理名字缩写 (如 "A." 或 "A. B.")
        if re.match(r'^[A-Z]\.(?:\s*[A-Z]\.)?$', author):
            if authors:
                # 将缩写合并到前一个作者
                authors[-1] = authors[-1] + ' ' + author
            else:
                # 第一个就是缩写，可能是单字母作者名
                authors.append(author)
        else:
            authors.append(author)
    
    return authors, has_et_al


def extract_surname(author):
    """
    从作者字符串中提取姓氏
    
    参数:
        author: 作者字符串
        
    返回:
        姓氏
    """
    # 去除可能的前后空格
    author = author.strip()
    
    # 如果包含逗号，则逗号前的是姓 (如 "Ohanian, R.")
    if ',' in author:
        return author.split(',')[0].strip()
    
    # 处理英文名字，提取姓
    parts = author.split()
    if len(parts) == 0:
        return author
    elif len(parts) == 1:
        return parts[0]
    else:
        # 对于英文名字，通常第一个部分是姓
        return parts[0]


def format_citation_by_authors(authors, year, original_citation, has_et_al=False):
    """
    根据作者数量和类型格式化引用
    
    参数:
        authors: 作者列表
        year: 年份
        original_citation: 原始引用
        has_et_al: 是否有et al.标记
        
    返回:
        格式化后的引用
    """
    if not authors:
        return original_citation
    
    # 判断是否是中文作者
    is_chinese = contains_chinese(authors[0]) if authors else False
    
    if is_chinese:
        # 中文作者
        if len(authors) > 1 or has_et_al:
            return f"{authors[0]} 等（{year}）"
        else:
            return f"{authors[0]}（{year}）"
    else:
        # 欧美作者
        # 提取作者的姓
        surnames = [extract_surname(author) for author in authors]
        
        # 处理机构或团体作者
        if len(surnames) == 1 and (len(surnames[0].split()) > 2 or surnames[0].isupper()):
            return f"{surnames[0]}（{year}）"
        
        # 如果有et al.标记，或者作者数量大于2，使用et al.
        if has_et_al or len(surnames) > 2:
            return f"{surnames[0]} et al.（{year}）"
        elif len(surnames) == 2:
            return f"{surnames[0]} & {surnames[1]}（{year}）"
        else:
            return f"{surnames[0]}（{year}）"


def test_real_document_mapping():
    """使用真实文档测试引用映射功能"""
    
    # 使用真实文档 - 首先尝试当前目录的文档
    doc_path = os.path.join(current_dir, '毛文静-最终论文.docx')
    
    # 检查文档是否存在
    if not os.path.exists(doc_path):
        print(f"错误: 找不到文档 {doc_path}")
        # 尝试在上层目录找到文档
        parent_doc_path = os.path.join(current_dir, '../../毛文静-最终论文.docx')
        if os.path.exists(parent_doc_path):
            doc_path = parent_doc_path
        else:
            # 尝试在tests/examples目录中查找
            examples_doc_path = os.path.join(current_dir, 'examples/毛文静-最终论文.docx')
            if os.path.exists(examples_doc_path):
                doc_path = examples_doc_path
            else:
                print(f"错误: 找不到文档 {doc_path}")
                return
    
    print("=== 使用真实文档测试引用映射功能 ===")
    
    # 创建提取器实例
    extractor = ExtractorFactory.get_extractor(doc_path)
    
    # 提取文档内容
    print("开始提取文档内容...")
    document = extractor.extract(doc_path)
    
    print(f"\n提取到 {len(document.citations)} 个引用和 {len(document.references)} 个参考文献条目")
    
    # 筛选出作者年份格式的引用
    author_year_citations = [c for c in document.citations if c.format_type == 'author_year']
    
    print(f"其中作者年份格式引用 {len(author_year_citations)} 个")
    
    # 同时也处理数字格式的引用
    numeric_citations = [c for c in document.citations if c.format_type == 'number']
    print(f"数字格式引用 {len(numeric_citations)} 个")
    
    # 统计匹配结果
    matched_count = 0
    unmatched_count = 0
    corrected_count = 0
    formatted_count = 0
    corrections_needed = []
    formatting_needed = []
    
    print("\n=== 映射结果 ===")
    
    # 准备详细报告数据
    detailed_report = {
        "test_date": datetime.now().isoformat(),
        "document": doc_path,
        "total_citations": len(document.citations),
        "total_references": len(document.references),
        "results": []
    }
    
    # 存储所有映射结果
    all_mapping_results = []
    
    # 测试所有引用 (作者年份格式和数字格式)
    for i, citation in enumerate(document.citations, 1):
        actual_citation = citation.text
        
        if citation.format_type == 'author_year':
            # 将Reference对象转换为字典格式以兼容映射逻辑
            reference_dicts = []
            for ref in document.references:
                reference_dicts.append({
                    'text': ref.text,
                    'author': ref.author,
                    'year': ref.year
                })
            
            # 执行映射
            result = map_author_year_citation_to_reference(actual_citation, reference_dicts)
            
            # 如果匹配成功，提取作者信息
            if result:
                reference_text = result['reference']['text']
                authors, has_et_al = extract_authors_from_reference(reference_text)
                result['authors'] = authors
                result['has_et_al'] = has_et_al
                
                # 根据作者信息格式化引用
                year = result['reference'].get('year', '')
                if not year and 'corrected_citation' in result:
                    # 尝试从修正后的引用中提取年份
                    year_match = re.search(r'（(\d{4})）', result['corrected_citation'])
                    if year_match:
                        year = year_match.group(1)
                
                if year and authors:
                    formatted_citation = format_citation_by_authors(authors, year, result['corrected_citation'], has_et_al)
                    result['formatted_citation'] = formatted_citation
                else:
                    result['formatted_citation'] = result['corrected_citation']
        
            # 存储映射结果
            if result:
                all_mapping_results.append(result)
            
            print(f"\n{i}. 测试引用: {actual_citation}")
            
            # 记录结果到详细报告
            report_entry = {
                "citation_index": i,
                "original_citation": actual_citation,
                "matched": result is not None,
                "needs_correction": False,
                "needs_formatting": False
            }
            
            if result:
                matched_count += 1
                print("  匹配成功!")
                print(f"  匹配的参考文献: {result['reference']['text'][:100]}...")
                
                # 打印作者信息
                if 'authors' in result and result['authors']:
                    print(f"  提取的作者: {', '.join(result['authors'])}")
                    if result.get('has_et_al', False):
                        print(f"  有et al.标记: 是")
                else:
                    print("  未能提取作者信息")
                
                report_entry.update({
                    "reference_text": result['reference']['text'],
                    "reference_year": result['reference'].get('year', '未知'),
                    "matched_year": result['reference'].get('year', '未知'),
                    "authors": result.get('authors', []),
                    "has_et_al": result.get('has_et_al', False)
                })
                
                # 检查是否需要修正
                needs_correction = result['corrected_citation'] != result['original_citation']
                needs_formatting = result.get('formatted_citation', result['corrected_citation']) != result['corrected_citation']
                
                if needs_correction or needs_formatting:
                    if needs_correction:
                        corrected_count += 1
                        print(f"  修正后的引用: {result['corrected_citation']}")
                        report_entry.update({
                            "corrected_citation": result['corrected_citation'],
                            "needs_correction": True,
                            "correction_reason": "年份不一致"
                        })
                        corrections_needed.append({
                            "original": result['original_citation'],
                            "corrected": result['corrected_citation'],
                            "reference": result['reference']['text'][:100] + "..."
                        })
                    
                    if needs_formatting:
                        formatted_count += 1
                        print(f"  格式化后的引用: {result['formatted_citation']}")
                        report_entry.update({
                            "formatted_citation": result['formatted_citation'],
                            "needs_formatting": True,
                            "formatting_reason": "作者格式不一致"
                        })
                        formatting_needed.append({
                            "original": result['corrected_citation'] if needs_correction else result['original_citation'],
                            "formatted": result['formatted_citation'],
                            "reference": result['reference']['text'][:100] + "..."
                        })
                    
                    print(f"  原始引用: {result['original_citation']}")
                else:
                    print(f"  引用无须修正: {result['corrected_citation']}")
                    report_entry["corrected_citation"] = result['corrected_citation']
            else:
                unmatched_count += 1
                print("  未找到匹配的参考文献")
        else:
            # 对于数字格式的引用，暂时跳过映射处理
            print(f"\n{i}. 测试引用: {actual_citation}")
            print("  [数字格式 - 暂不处理映射]")
            
            report_entry = {
                "citation_index": i,
                "original_citation": actual_citation,
                "matched": False,
                "needs_correction": False,
                "needs_formatting": False
            }
        
        detailed_report["results"].append(report_entry)
    
    # 识别未被引用的参考文献
    used_references = {result['reference']['text'] for result in all_mapping_results if result}
    unused_references = [ref for ref in document.references if ref.text not in used_references]
    
    # 将unused_references转换为字典格式以兼容输出
    unused_references_dicts = []
    for ref in unused_references:
        unused_references_dicts.append({
            'text': ref.text,
            'author': ref.author,
            'year': ref.year
        })
    
    # 添加统计信息到报告
    detailed_report.update({
        "matched_count": matched_count,
        "unmatched_count": unmatched_count,
        "corrected_count": corrected_count,
        "formatted_count": formatted_count,
        "unused_references_count": len(unused_references),
        "match_rate": f"{matched_count/len(document.citations)*100:.1f}%" if len(document.citations) > 0 else "0.0%",
        "corrections_needed": corrections_needed,
        "formatting_needed": formatting_needed,
        "unused_references": unused_references_dicts
    })
    
    # 保存详细报告
    report_path = os.path.join(current_dir, "standalone_citation_mapping_detailed_report.json")
    with open(report_path, 'w', encoding='utf-8') as f:
        json.dump(detailed_report, f, ensure_ascii=False, indent=2)
    
    print(f"\n=== 测试总结 ===")
    print(f"测试引用数量: {len(document.citations)}")
    print(f"成功匹配: {matched_count}")
    print(f"未匹配: {unmatched_count}")
    print(f"需要修正: {corrected_count}")
    print(f"未使用参考文献: {len(unused_references)}")
    print(f"需要格式化: {formatted_count}")
    print(f"匹配率: {matched_count/len(document.citations)*100:.1f}%" if len(document.citations) > 0 else "匹配率: 0.0%")
    
    # 打印需要修正的引用
    if corrections_needed:
        print(f"\n需要修正的引用 ({corrected_count} 个):")
        for correction in corrections_needed:
            print(f"  - 原始: {correction['original']}")
            print(f"    修正: {correction['corrected']}")
            print(f"    参考文献: {correction['reference']}")
    
    # 打印需要格式化的引用
    if formatting_needed:
        print(f"\n需要格式化的引用 ({formatted_count} 个):")
        for formatting in formatting_needed:
            print(f"  - 原始: {formatting['original']}")
            print(f"    格式化: {formatting['formatted']}")
            print(f"    参考文献: {formatting['reference']}")
            print("--------------------------------------------------")
    
    if unused_references:
        print(f"\n未被引用的参考文献 ({len(unused_references)} 个):")
        for i, ref in enumerate(unused_references, 1):
            print(f"  {i}. {ref.text}")
            print("--------------------------------------------------")

    print(f"\n详细报告已保存到 {report_path}")


if __name__ == "__main__":
    test_real_document_mapping()