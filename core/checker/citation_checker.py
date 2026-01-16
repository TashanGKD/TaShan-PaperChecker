from .base_checker import BaseChecker
from models.document import Document
from models.compliance import ComplianceResult, CheckType
from typing import List, Dict, Any

class CitationChecker(BaseChecker):
    """引用合规性检查器 - 实现BaseChecker接口"""
    
    def get_check_type(self) -> CheckType:
        return CheckType.CITATIONS
    
    def get_check_name(self) -> str:
        return "citation_compliance_checker"
    
    def check(self, document: Document) -> ComplianceResult:
        """
        执行引用合规性检查
        
        Args:
            document: 要检查的文档对象
            
        Returns:
            ComplianceResult: 检查结果
        """
        results: List[Dict[str, Any]] = []  # 使用results名称以符合输出格式
        statistics: Dict[str, Any] = {
            "total_citations": len(document.citations),
            "total_references": len(document.references),
            "matched_citations": 0,
            "unmatched_citations": 0,
            "year_inconsistencies": 0
        }
        
        # 这里集成现有的引用匹配逻辑
        # 使用utils/reference_mapper中的函数
        from core.checker.citation_checking.reference_mapper import map_author_year_citation_to_reference, extract_authors_from_reference, format_citation_by_authors
        
        # 转换参考文献为字典格式以兼容映射函数
        reference_dicts = []
        for ref in document.references:
            reference_dicts.append({
                'text': ref.text,
                'author': ref.author,
                'year': ref.year if ref.year is not None else ref.text  # 使用参考文献文本作为备用来源
            })
        
        matched_count = 0
        unmatched_count = 0
        corrected_count = 0
        formatted_count = 0
        corrections_needed = []
        formatting_needed = []
        
        # 存储所有映射结果
        all_mapping_results = []
        
        # 处理每个引用
        for i, citation in enumerate(document.citations, 1):
            report_entry = {
                "citation_index": i,
                "original_citation": citation.text,
                "matched": False,
                "needs_correction": False,
                "needs_formatting": False
            }
            
            if citation.format_type == 'author_year':
                # 使用现有的映射逻辑
                result = map_author_year_citation_to_reference(
                    citation.text,
                    reference_dicts
                )
                
                # 如果匹配成功，提取作者信息
                if result:
                    reference_text = result['reference']['text']
                    # 从映射结果中获取年份（优先使用映射结果中的年份）
                    ref_year = result['reference'].get('year', '')
                    
                    # 从参考文献文本中提取作者信息
                    authors, has_et_al = extract_authors_from_reference(reference_text)
                    
                    # 根据作者信息格式化引用
                    year = ref_year
                    if not year and 'corrected_citation' in result:
                        # 尝试从修正后的引用中提取年份
                        import re
                        year_match = re.search(r'（(\d{4})）', result['corrected_citation'])
                        if year_match:
                            year = year_match.group(1)
                    
                    if year and authors:
                        formatted_citation = format_citation_by_authors(authors, year, result['corrected_citation'], has_et_al)
                        result['formatted_citation'] = formatted_citation
                    else:
                        result['formatted_citation'] = result['corrected_citation']
                        
                    # 记录映射结果
                    all_mapping_results.append(result)
                    
                    # 更新报告记录
                    matched_count += 1
                    report_entry.update({
                        "matched": True,
                        "reference_text": reference_text,
                        "reference_year": ref_year if ref_year else "未知",
                        "matched_year": ref_year if ref_year else "未知",
                        "authors": authors,
                        "has_et_al": has_et_al
                    })
                    
                    # 检查是否需要修正
                    needs_correction = result['corrected_citation'] != result['original_citation']
                    needs_formatting = result.get('formatted_citation', result['corrected_citation']) != result['corrected_citation']
                    
                    if needs_correction or needs_formatting:
                        if needs_correction:
                            corrected_count += 1
                            report_entry.update({
                                "corrected_citation": result['corrected_citation'],
                                "needs_correction": True,
                                "correction_reason": "年份不一致"
                            })
                            corrections_needed.append({
                                "original": result['original_citation'],
                                "corrected": result['corrected_citation'],
                                "reference": (reference_text[:100] + "...") if len(reference_text) > 100 else reference_text
                            })
                        
                        if needs_formatting:
                            formatted_count += 1
                            report_entry.update({
                                "formatted_citation": result['formatted_citation'],
                                "needs_formatting": True,
                                "formatting_reason": "作者格式不一致"
                            })
                            formatting_needed.append({
                                "original": result['corrected_citation'] if needs_correction else result['original_citation'],
                                "formatted": result['formatted_citation'],
                                "reference": (reference_text[:100] + "...") if len(reference_text) > 100 else reference_text
                            })
                        
                        # 如果已经有修正，则使用修正后的引用作为基准
                        if needs_correction:
                            report_entry["corrected_citation"] = result['corrected_citation']
                        else:
                            report_entry["corrected_citation"] = result['corrected_citation']
                            
                    # 如果只需要格式化而不需要修正
                    if needs_formatting and not needs_correction:
                        report_entry.update({
                            "needs_formatting": True,
                            "formatted_citation": result['formatted_citation'],
                            "formatting_reason": "作者格式不一致"
                        })
                        # 在这种情况下，仍然需要保留corrected_citation字段
                        report_entry["corrected_citation"] = result['corrected_citation']
                else:
                    unmatched_count += 1
            else:
                # 对于数字格式的引用，暂时只记录未匹配状态
                unmatched_count += 1
            
            results.append(report_entry)
        
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
        
        # 更新统计信息
        statistics.update({
            "matched_citations": matched_count,
            "unmatched_citations": unmatched_count,
            "corrected_count": corrected_count,
            "formatted_count": formatted_count,
            "unused_references_count": len(unused_references)
        })
        
        # 创建兼容现有API格式的输出
        compatibility_output = {
            "test_date": __import__('datetime').datetime.now().isoformat(),
            "document": document.metadata.get('file_path', ''),
            "total_citations": len(document.citations),
            "total_references": len(document.references),
            "results": results,
            "matched_count": matched_count,
            "unmatched_count": unmatched_count,
            "corrected_count": corrected_count,
            "formatted_count": formatted_count,
            "unused_references_count": len(unused_references),
            "match_rate": f"{matched_count/len(document.citations)*100:.1f}%" if len(document.citations) > 0 else "0%",
            "corrections_needed": corrections_needed,
            "formatting_needed": formatting_needed,
            "unused_references": unused_references_dicts
        }
        
        # 创建结果对象，保留兼容输出作为metadata
        result = ComplianceResult(
            check_type=CheckType.CITATIONS,
            is_compliant=unmatched_count == 0,
            issues=results,  # 将结果以issues的形式存储
            statistics=statistics,
            metadata={
                "compatibility_output": compatibility_output,
                "checker_version": "1.0.0"
            }
        )
        
        return result