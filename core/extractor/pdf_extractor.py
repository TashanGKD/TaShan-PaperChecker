import os
from .base_extractor import BaseExtractor
from models.document import Document, Citation, Reference
import re

class PDFExtractor(BaseExtractor):
    """PDF文档提取器"""
    
    def validate_file(self, file_path: str) -> bool:
        return file_path.lower().endswith('.pdf')
    
    def extract(self, file_path: str) -> Document:
        """提取PDF文档内容"""
        # 尝试使用MinerU API进行转换
        md_content = None
        try:
            from utils.mineru_pdf_converter import convert_pdf_to_markdown

            # 调用PDF转换功能
            project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            config_path = os.path.join(project_root, "config", "config.json")
            md_file_path = convert_pdf_to_markdown(file_path, config_path=config_path)

            # 从Markdown内容提取信息
            with open(md_file_path, 'r', encoding='utf-8') as f:
                md_content = f.read()

        except Exception as e:
            print(f"MinerU API转换失败: {e}")
            print("切换到本地PDF提取方法...")
            # 使用本地方法提取PDF内容
            md_content = self._extract_pdf_locally(file_path)

        # 提取正文内容（按行分割）
        paragraphs = md_content.split('\n') if md_content else []

        # 提取表格内容（从Markdown表格中）
        # 简单的表格识别
        tables_content = []
        lines = md_content.split('\n') if md_content else []
        for line in lines:
            if '|' in line and line.strip().startswith('|'):
                tables_content.append(line.strip())

        # 提取引文和参考文献，这里需要实现PDF的提取逻辑
        citations = self._extract_citations(paragraphs, md_content or "", file_path)
        references = self._extract_references(paragraphs)

        # 构建文档对象
        return Document(
            content=paragraphs,
            tables=tables_content,
            citations=citations,
            references=references,
            metadata={'file_type': 'pdf', 'file_path': file_path}
        )

    def _extract_pdf_locally(self, file_path: str) -> str:
        """使用本地库提取PDF内容"""
        import fitz  # PyMuPDF

        # 打开PDF文档
        doc = fitz.open(file_path)
        text_content = []

        # 提取每一页的文本
        for page_num in range(len(doc)):
            page = doc.load_page(page_num)
            text = page.get_text()
            text_content.append(text)

        doc.close()

        # 将所有页面的文本合并
        full_text = "\n".join(text_content)

        # 将PDF文本转换为类似markdown的格式
        # 这里可以进一步处理格式，但现在先返回纯文本
        return full_text
    
    def _extract_citations(self, paragraphs: list, md_content: str, file_path: str) -> list:
        """提取引文"""
        all_citations = []
        processed_citations = set()  # 用于去重
        
        # 从extractor模块导入AI增强的引用提取功能
        try:
            from .ai_extractor import extract_citations_from_text
            AI_EXTRACTION_AVAILABLE = True
        except ImportError:
            AI_EXTRACTION_AVAILABLE = False
        
        # 如果AI提取功能可用，使用AI从Markdown内容中提取作者年份格式的引用
        if AI_EXTRACTION_AVAILABLE:
            try:
                # 准备AI优化的配置（这里可以使用从配置文件传入的配置参数）
                ai_config = {
                    "api_key": "your-api-key",  # 可以从配置文件传入
                    "model_name": "qwen-plus"   # 可以从配置文件传入
                }
                
                # 从Markdown内容提取作者年份格式的引用
                text_citations = extract_citations_from_text(md_content, ai_config)
                
                # 将AI提取的引用添加到列表中
                for citation_text in text_citations:
                    formatted_citation = f"[AUTH:{citation_text}]"  
                    if formatted_citation not in processed_citations:
                        # 创建引用对象，格式化为AI提取的格式
                        citation_obj = Citation(
                            text=formatted_citation,
                            format_type='author_year',
                            context="AI提取"
                        )
                        all_citations.append(citation_obj)
                        processed_citations.add(formatted_citation)
            except Exception as e:
                print(f"AI增强引用提取失败: {e}")
        
        # 提取数字格式引用 [1], [2-5] 等（作为补充）
        full_text_str = '\n'.join(paragraphs)
        # 提取文中的引用（包括单个引用和范围引用，例如[1], [2-5]等格式）
        citation_pattern = r'\[\d+(?:-\d+)?\]'
        raw_citations = re.findall(citation_pattern, full_text_str)
        
        # 展开范围引用为单个引用
        expanded_citations = set()
        for citation in raw_citations:
            if '-' in citation:
                # 处理范围引用，如[1-3]
                match = re.match(r'\[(\d+)-(\d+)\]', citation)
                if match:
                    start = int(match.group(1))
                    end = int(match.group(2))
                    # 展开范围引用为单个引用
                    for i in range(start, end + 1):
                        expanded_citations.add(f'[{i}]')
            else:
                # 单个引用，直接添加
                expanded_citations.add(citation)
        
        for citation in expanded_citations:
            if citation not in processed_citations:
                all_citations.append(Citation(text=citation, format_type='number', context="PDF提取"))
                processed_citations.add(citation)
        
        # 提取作者年份格式引用作为补充（以防AI提取遗漏）
        for paragraph in paragraphs:
            author_year_citations = self._extract_author_year_citations(paragraph)
            for citation in author_year_citations:
                if citation.text not in processed_citations:
                    all_citations.append(citation)
                    processed_citations.add(citation.text)
        
        return all_citations
    
    def _extract_author_year_citations(self, paragraph: str) -> list:
        """提取作者年份格式引用"""
        citations = []
        # 中文格式：张三（2024）
        chinese_pattern = r'([\u4e00-\u9fa5\w\s]+)（(\d{4})）'
        chinese_matches = re.findall(chinese_pattern, paragraph)
        for author, year in chinese_matches:
            citations.append(Citation(text=f"{author}（{year}）", 
                                    format_type='author_year', 
                                    author=author.strip(), 
                                    year=year, 
                                    context=paragraph))
        
        # 英文格式：Smith (2020) 或 Smith（2020）
        english_pattern = r'([A-Za-z\s\.\-&]+)\s*[（\(](\d{4})[）\)]'
        english_matches = re.findall(english_pattern, paragraph)
        for author, year in english_matches:
            citations.append(Citation(text=f"{author.strip()} ({year})", 
                                    format_type='author_year', 
                                    author=author.strip(), 
                                    year=year, 
                                    context=paragraph))
        
        return citations
    
    def _extract_references(self, paragraphs: list) -> list:
        """提取参考文献"""
        references = []

        # 方法1: 查找"参考文献"标题后的传统方式
        traditional_refs = self._extract_references_traditional(paragraphs)

        # 方法2: 基于模式匹配的全文搜索方式
        pattern_based_refs = self._extract_references_pattern_based(paragraphs)

        # 方法3: 专门搜索文档后半部分的学术引用
        academic_refs = self._extract_references_academic_style(paragraphs)

        # 合并所有方法的结果
        all_refs = traditional_refs + pattern_based_refs + academic_refs

        # 去重并返回
        return self._remove_duplicates_and_validate(all_refs)

    def _extract_references_traditional(self, paragraphs: list) -> list:
        """传统的参考文献提取方法（保留向后兼容）"""
        references = []
        references_start = -1

        # 查找参考文献部分
        for i, paragraph in enumerate(paragraphs):
            if any(keyword in paragraph for keyword in ['参考文献', 'References', 'REFERENCES']):
                references_start = i
                break

        if references_start != -1:
            # 提取参考文献条目（从标题之后开始）
            for i in range(references_start + 1, len(paragraphs)):
                text = paragraphs[i].strip()
                if text:
                    # 检查是否为参考文献条目
                    if self._is_reference_entry(text):
                        # 提取DOI、URL等信息
                        doi = self._extract_doi(text)
                        url = self._extract_url(text)

                        # 从参考文献文本中提取作者和年份
                        from core.checker.citation_checking.reference_mapper import extract_author_year_from_reference
                        extracted_author, extracted_year = extract_author_year_from_reference(text)

                        references.append(Reference(
                            text=text,
                            author=extracted_author,
                            year=extracted_year
                        ))
                    # 如果遇到结束标记则停止
                    elif self._is_end_marker(text):
                        break
        else:
            # 如果没有找到"参考文献"标题，尝试在文档的后半部分查找可能的参考文献条目
            start_search = max(0, len(paragraphs) - 100)
            for i in range(start_search, len(paragraphs)):
                text = paragraphs[i].strip()
                if text and self._is_reference_entry(text):
                    doi = self._extract_doi(text)
                    url = self._extract_url(text)

                    references.append(Reference(
                        text=text,
                        author=None,  # 从参考文献文本中提取作者和年份
                        year=None
                    ))

        return references

    def _extract_references_pattern_based(self, paragraphs: list) -> list:
        """基于正则表达式模式的参考文献提取"""
        references = []

        # 定义多种参考文献模式
        patterns = [
            # [J] 期刊文章模式: 作者, 年份, 期刊名, [J], 卷(期): 页码.
            r'.*?[，,].*?\d{4}.*?\[J\].*?',
            # [M] 书籍模式: 作者. 书名[M]. 出版社, 年份.
            r'.*?[，,].*?\d{4}.*?\[M\].*?',
            # [C] 会议论文模式
            r'.*?[，,].*?\d{4}.*?\[C\].*?',
            # [D] 学位论文模式
            r'.*?[，,].*?\d{4}.*?\[D\].*?',
            # 简单年份模式（作者，年份，期刊）
            r'.*?[，,].*?\d{4}.*?[，,].*?[。\.]',
            # 序号模式 [数字]或(数字)
            r'[\[\(]\d+[\]\)].*?\d{4}.*?[。\.]',
            # 作者等年份模式：作者等，年份
            r'.*?等[，,]?\s*\d{4}.*?[。\.]',
            # 英文作者年份模式：Author (Year)
            r'[A-Z][a-z]+.*?\(\d{4}\)',
            # 英文作者年份模式：Author [Year]
            r'[A-Z][a-z]+.*?\[\d{4}\]',
            # 英文作者年份模式：Author, Year
            r'[A-Z][a-z]+.*?[,，]\s*\d{4}.*?[。\.]',
        ]

        for i, paragraph in enumerate(paragraphs):
            text = paragraph.strip()
            if len(text) > 20:  # 基本长度要求
                # 检查是否包含年份（基本要求）
                has_year = bool(re.search(r'\d{4}', text))
                if has_year:
                    # 检查是否符合任一模式
                    matches_pattern = any(re.search(pattern, text) for pattern in patterns)

                    # 额外检查：包含学术特征词汇
                    has_academic_indicators = any(indicator in text for indicator in
                                                 ['学报', '期刊', '研究', '出版', '出版社', '大学',
                                                  '论文', '文献', '杂志', '科学', '经济', '管理',
                                                  'Journal', 'Research', 'Studies', 'Review',
                                                  'University', 'Press', 'Academic'])

                    # 检查是否有引用格式特征
                    has_citation_indicators = any(indicator in text for indicator in
                                                 ['[J]', '[M]', '[C]', '[D]', '[S]', '[R]',
                                                  'Vol.', 'No.', 'pp.', 'p.', 'Vol',
                                                  '等.', '著', '编', '译'])

                    if matches_pattern or has_academic_indicators or has_citation_indicators:
                        # 验证是否为有效的参考文献（避免误判）
                        if self._is_valid_reference(text):
                            from core.checker.citation_checking.reference_mapper import extract_author_year_from_reference
                            extracted_author, extracted_year = extract_author_year_from_reference(text)

                            references.append(Reference(
                                text=text,
                                author=extracted_author,
                                year=extracted_year
                            ))

        return references

    def _extract_references_academic_style(self, paragraphs: list) -> list:
        """专门针对学术论文风格的参考文献提取"""
        references = []

        # 从配置文件加载参数
        config = self._load_config()
        start_percentage = config.get('academic_references_start_percentage', 0.7)

        # 重点关注文档后半部分（通常参考文献在此）
        # 使用文档长度的百分比来确定搜索起始位置
        doc_length = len(paragraphs)

        if doc_length == 0:
            return references

        # 计算基于百分比的起始位置
        start_idx = int(doc_length * start_percentage)

        for i in range(start_idx, len(paragraphs)):
            text = paragraphs[i].strip()
            if len(text) > 10 and text:  # 有效文本
                # 检查是否符合学术参考文献的特征
                if self._has_academic_reference_characteristics(text):
                    from core.checker.citation_checking.reference_mapper import extract_author_year_from_reference
                    extracted_author, extracted_year = extract_author_year_from_reference(text)

                    references.append(Reference(
                        text=text,
                        author=extracted_author,
                        year=extracted_year
                    ))

        return references

    def _load_config(self) -> dict:
        """加载配置文件"""
        import json

        config_path = "config.json"
        if not os.path.exists(config_path):
            # 如果当前目录没有配置文件，尝试在项目根目录查找
            import pathlib
            project_root = pathlib.Path(__file__).parent.parent
            config_path = project_root / "config.json"

        if os.path.exists(config_path):
            with open(config_path, 'r', encoding='utf-8') as f:
                full_config = json.load(f)
            # 返回PDF提取器配置部分
            return full_config.get('pdf_extractor_config', {})
        else:
            # 如果配置文件不存在，返回默认值
            return {
                'academic_references_start_percentage': 0.7
            }

    def _has_academic_reference_characteristics(self, text: str) -> bool:
        """检查文本是否具有学术参考文献的特征"""
        # 包含年份
        has_year = bool(re.search(r'\b(19|20)\d{2}\b', text))
        if not has_year:
            return False

        # 包含学术关键词或格式
        academic_indicators = [
            '[J]', '[M]', '[C]', '[D]', '[S]', '[R]',  # 文献类型标识
            '学报', '期刊', '研究', '出版', '出版社', '大学',
            '论文', '文献', '杂志', '科学', '经济', '管理',
            'Vol.', 'No.', 'pp.', 'p.',  # 英文学术标识
            '等.', '著', '编', '译',  # 中文学术标识
            'University', 'Press', 'Academic', 'Journal',
            'Research', 'Studies', 'Review',
            # 序号格式
            r'^\s*\d+\.', r'^\s*\[\d+\]', r'^\s*[A-Z]\d+\s+'
        ]

        for indicator in academic_indicators[:-2]:  # 前面的直接字符串检查
            if indicator in text:
                return True

        # 检查序号格式
        for pattern in academic_indicators[-2:]:  # 最后两个是正则表达式
            if re.search(pattern, text):
                return True

        # 检查长度和结构
        if len(text) > 30:  # 足够长以包含完整信息
            # 检查是否包含逗号、句号等分隔符，表明有多个信息段
            punctuation_count = text.count('，') + text.count(',') + text.count('。') + text.count('.')
            if punctuation_count >= 2:
                return True

        return False

    def _is_valid_reference(self, text: str) -> bool:
        """验证是否为有效的参考文献条目"""
        # 基本长度要求
        if len(text) < 10:
            return False

        # 检查是否包含必要的学术元素
        has_year = bool(re.search(r'\b(19|20)\d{2}\b', text))
        if not has_year:
            return False

        # 检查是否不是其他类型的文本（如正文段落）
        # 排除包含这些关键词的文本（可能是正文而非参考文献）
        exclude_keywords = ['图', '表', '章节', '本章', '该', '此', '这些', '这种', '因此', '所以', '但是']
        for keyword in exclude_keywords:
            if keyword in text[:50]:  # 检查前50个字符
                return False

        return True

    def _remove_duplicates_and_validate(self, references: list) -> list:
        """移除重复并验证参考文献"""
        seen_texts = set()
        unique_refs = []

        for ref in references:
            # 标准化文本以进行比较（移除多余的空白字符）
            normalized_text = ' '.join(ref.text.split())

            if normalized_text not in seen_texts:
                seen_texts.add(normalized_text)
                # 验证参考文献是否有效
                if self._is_valid_reference(ref.text):
                    unique_refs.append(ref)

        return unique_refs
    
    def _is_reference_entry(self, text: str) -> bool:
        """判断是否为参考文献条目"""
        # 检查是否包含年份和基本结构
        has_year = bool(re.search(r'\d{4}', text))
        has_basic_structure = len(text) > 10 and ('.' in text or '[' in text)
        
        # 排除非参考文献的条目
        exclude_keywords = ['附录', '致谢', '作者简历', '图', '表', '目录']
        has_exclude_keyword = any(keyword in text for keyword in exclude_keywords)
        
        return has_year and has_basic_structure and not has_exclude_keyword
    
    def _is_end_marker(self, text: str) -> bool:
        """判断是否为参考文献部分结束标记"""
        end_keywords = ['附录', '致谢', '作者简历', 'Appendix', 'Acknowledgements']
        return any(keyword in text for keyword in end_keywords) and len(text) < 20
    
    def _extract_doi(self, text: str) -> str:
        """提取DOI"""
        doi_pattern = r'doi:\s*([^\s,.;\)]+)|DOI:\s*([^\s,.;\)]+)'
        match = re.search(doi_pattern, text, re.IGNORECASE)
        if match:
            return match.group(1) or match.group(2)
        return None
    
    def _extract_url(self, text: str) -> str:
        """提取URL"""
        url_pattern = r'https?://[^\s,.;\)]+'
        match = re.search(url_pattern, text)
        return match.group(0) if match else None