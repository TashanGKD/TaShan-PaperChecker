"""
引用映射工具
提供将引用与参考文献进行匹配和映射的功能
"""

import re
from difflib import SequenceMatcher
from typing import Dict, List, Optional, Tuple


def map_author_year_citation_to_reference(citation: str, references: List[Dict]) -> Optional[Dict]:
    """
    将作者年份格式的引用映射到参考文献条目
    
    Args:
        citation (str): 作者年份格式的引用，如 "张三（2024）"
        references (list): 参考文献条目列表
        
    Returns:
        dict: 匹配的参考文献条目，如果没有匹配则返回None
    """
    # 从引用中提取作者和年份
    citation_author, citation_year = extract_author_year_from_citation(citation)
    
    if not citation_author or not citation_year:
        return None
    
    best_match = None
    best_score = 0.0
    best_ref_year = None
    
    # 在参考文献中查找匹配项
    for ref in references:
        ref_text = ref['text']
        
        # 从参考文献条目中提取作者和年份
        ref_author, ref_year = extract_author_year_from_reference(ref_text)
        
        if not ref_author:
            continue
            
        # 新的匹配策略：直接在参考文献条目中搜索作者和年份
        # 计算作者匹配得分（使用更宽松的匹配）
        author_score = calculate_author_match_score(citation_author, ref_text, ref_author)
        
        # 计算年份匹配得分
        year_score = calculate_year_match_score(citation_year, ref_text, ref_year)
        
        # 综合得分 = 作者得分 * 0.6 + 年份得分 * 0.4
        total_score = author_score * 0.6 + year_score * 0.4
        
        # 更新最佳匹配
        if total_score > best_score:
            best_match = ref
            best_score = total_score
            best_ref_year = ref_year
    
    # 如果找到了较好的匹配（得分阈值）
    if best_match and best_score > 0.3:
        # 如果年份不一致，返回修正后的引用信息
        if best_ref_year and citation_year and best_ref_year != citation_year:
            # 创建一个包含修正年份的副本
            corrected_citation = f"{citation_author}（{best_ref_year}）"
            return {
                "reference": best_match,
                "corrected_citation": corrected_citation,
                "original_citation": citation
            }
        else:
            return {
                "reference": best_match,
                "corrected_citation": citation,  # 没有修正
                "original_citation": citation
            }
            
    return None


def is_ocr_error(year1: str, year2: str) -> bool:
    """
    判断两个年份是否可能是OCR错误
    
    Args:
        year1 (str): 第一个年份
        year2 (str): 第二个年份
        
    Returns:
        bool: 是否可能是OCR错误
    """
    # 必须都是4位
    if len(year1) != 4 or len(year2) != 4:
        return False
    
    # 将OCR错误字符转换为标准数字
    ocr_to_digit = {
        'O': '0', 'o': '0',
        'I': '1', 'i': '1', 'l': '1',
        'Z': '2', 'z': '2',
        'S': '5', 's': '5',
        'G': '6', 'g': '6',
        'B': '8', 'b': '8',
        'D': '0', 'd': '0'
    }
    
    # 转换year1中的OCR错误字符
    normalized_year1 = ""
    for char in year1:
        if char in ocr_to_digit:
            normalized_year1 += ocr_to_digit[char]
        else:
            normalized_year1 += char
    
    # 转换year2中的OCR错误字符
    normalized_year2 = ""
    for char in year2:
        if char in ocr_to_digit:
            normalized_year2 += ocr_to_digit[char]
        else:
            normalized_year2 += char
    
    # 如果转换后相等，则是OCR错误
    if normalized_year1 == normalized_year2:
        return True
    
    # 计算不同的字符数
    diff_count = 0
    for i in range(4):
        if normalized_year1[i] != normalized_year2[i]:
            diff_count += 1
    
    # 如果只有一个字符不同，则可能是OCR错误
    if diff_count == 1:
        return True
    
    # 如果有两个字符不同，检查是否是常见的OCR错误对
    if diff_count == 2:
        # 常见的OCR错误对
        ocr_errors = [
            ('0', 'O'), ('1', 'I'), ('1', 'l'), ('2', 'Z'), 
            ('5', 'S'), ('6', 'G'), ('8', 'B'), ('0', 'D'),
            ('1', '7'), ('2', '7'), ('2', '1'), ('0', '8')
        ]
        
        # 检查不同的位置是否符合常见的OCR错误对
        diff_positions = []
        for i in range(4):
            if normalized_year1[i] != normalized_year2[i]:
                diff_positions.append(i)
        
        if len(diff_positions) == 2:
            pos1, pos2 = diff_positions
            char1_1, char1_2 = normalized_year1[pos1], normalized_year1[pos2]
            char2_1, char2_2 = normalized_year2[pos1], normalized_year2[pos2]
            
            # 检查是否是OCR错误对
            for error1, error2 in ocr_errors:
                if (char1_1 == error1 and char2_1 == error2 and char1_2 == error2 and char2_2 == error1) or \
                   (char1_1 == error2 and char2_1 == error1 and char1_2 == error1 and char2_2 == error2):
                    return True
    
    return False


def calculate_author_match_score(citation_author: str, reference_text: str, ref_author: str) -> float:
    """
    计算作者在参考文献中的匹配得分
    
    Args:
        citation_author (str): 引用中的作者
        reference_text (str): 参考文献全文
        ref_author (str): 参考文献中提取的作者
        
    Returns:
        float: 匹配得分 (0.0 到 1.0)
    """
    # 转为小写进行比较
    citation_author = citation_author.strip().lower()
    reference_text = reference_text.lower()
    ref_author = ref_author.strip().lower()
    
    # 如果提取的作者完全匹配，给高分
    if citation_author == ref_author:
        return 1.0
    
    # 如果提取的作者包含引用作者或反之，给较高分
    if citation_author in ref_author or ref_author in citation_author:
        return 0.9
    
    # 在整个参考文献文本中搜索作者名
    if citation_author in reference_text:
        # 根据位置给分，越靠前得分越高
        position = reference_text.find(citation_author)
        # 假设参考文献前100个字符是作者信息区域
        if position < 100:
            return 0.8
        elif position < 200:
            return 0.6
        else:
            return 0.4
    
    # 使用difflib计算相似度作为备选方案
    similarity = SequenceMatcher(None, citation_author, ref_author).ratio()
    return similarity * 0.5


def calculate_year_match_score(citation_year: str, reference_text: str, ref_year: str) -> float:
    """
    计算年份在参考文献中的匹配得分
    
    Args:
        citation_year (str): 引用中的年份
        reference_text (str): 参考文献全文
        ref_year (str): 参考文献中提取的年份
        
    Returns:
        float: 匹配得分 (0.0 到 1.0)
    """
    # 如果提取的年份完全匹配，给高分
    if ref_year and citation_year == ref_year:
        return 1.0
    
    # 检查是否为OCR错误
    if ref_year and is_ocr_error(citation_year, ref_year):
        return 0.9
    
    # 在整个参考文献文本中搜索年份
    if citation_year in reference_text:
        return 0.8
    
    return 0.0


def extract_author_year_from_citation(citation: str) -> Tuple[Optional[str], Optional[str]]:
    """
    从作者年份格式的引用中提取作者和年份
    
    Args:
        citation (str): 作者年份格式的引用
        
    Returns:
        tuple: (作者, 年份)
    """
    # 匹配格式：作者（年份），允许年份中包含OCR错误字符
    match = re.search(r'^(.+?)（([0-9OoIiZzSsGgBbDd]{4})）', citation.strip())
    if match:
        author = match.group(1).strip()
        year = match.group(2)
        return author, year
    
    # 匹配英文格式：Author (Year)，允许年份中包含OCR错误字符
    match = re.search(r'^(.+?)\s*\(([0-9OoIiZzSsGgBbDd]{4})\)', citation.strip())
    if match:
        author = match.group(1).strip()
        year = match.group(2)
        return author, year
        
    return None, None


def extract_author_year_from_reference(reference_text: str) -> Tuple[Optional[str], Optional[str]]:
    """
    从参考文献条目中提取作者和年份
    
    Args:
        reference_text (str): 参考文献条目文本
        
    Returns:
        tuple: (作者, 年份)
    """
    # 匹配参考文献格式：作者. 文章标题. 期刊名, 年份, 卷(期): 页码.
    # 或者：作者. 文章标题[J]. 期刊名, 年份, 卷(期): 页码.
    # 或者：作者,作者. 文章标题. 期刊名, 年份, 卷(期): 页码.
    # 或者：作者. 书名[M]. 出版社: 年份.
    
    # 去除参考文献条目前的序号（如[1]、[71]等）
    clean_reference_text = re.sub(r'^\s*\[\d+\]\s*', '', reference_text)
    
    # 提取年份（4位数字）- 更全面的模式
    year_patterns = [
        r'\((\d{4})\)',         # 括号中的年份
        r'\((\d{4})\)\.',       # 括号中的年份后跟句点
        r',\s*(\d{4})[,)]',     # 逗号后跟年份和逗号或右括号
        r',\s*(\d{4})\.',       # 逗号后跟年份和句点
        r',\s*(\d{4})',         # 逗号后跟年份
        r':\s*(\d{4})\.',       # 冒号后跟年份和句点
        r':\s*(\d{4})',         # 冒号后跟年份
        r'\s(\d{4})\.',         # 空格后跟年份和句点
        r'\s(\d{4})',           # 空格后跟年份
    ]
    
    year = None
    for pattern in year_patterns:
        year_match = re.search(pattern, clean_reference_text)
        if year_match:
            year = year_match.group(1)
            break
    
    # 提取作者（第一个逗号或点之前的内容）
    author_match = re.search(r'^([^.,]+)', clean_reference_text)
    author = author_match.group(1).strip() if author_match else None
    
    # 处理多个作者的情况，只取第一个作者
    if author and ('，' in author or ',' in author):
        # 分割多个作者，取第一个
        separators = ['，', ',']
        for sep in separators:
            if sep in author:
                author = author.split(sep)[0].strip()
                break
    
    # 如果作者以"等"或"et al"结尾，去掉这些词
    if author:
        author = re.sub(r'等$', '', author).strip()
        author = re.sub(r'et al\.?$', '', author).strip()
    
    return author, year


def calculate_author_similarity(author1: str, author2: str) -> float:
    """
    计算两个作者名的相似度

    Args:
        author1 (str): 第一个作者名
        author2 (str): 第二个作者名

    Returns:
        float: 相似度分数 (0.0 到 1.0)
    """
    # 检查输入是否为None
    if author1 is None:
        author1 = ""
    if author2 is None:
        author2 = ""

    # 确保输入是字符串类型
    author1 = str(author1).strip().lower()
    author2 = str(author2).strip().lower()
    
    # 完全匹配
    if author1 == author2:
        return 1.0
        
    # 使用difflib计算相似度
    similarity = SequenceMatcher(None, author1, author2).ratio()
    
    # 特殊处理：如果一个作者名包含另一个，则给予较高的相似度
    if author1 in author2 or author2 in author1:
        similarity = max(similarity, 0.9)
        
    # 特殊处理：英文名的姓氏匹配
    if is_english_name(author1) and is_english_name(author2):
        surname1 = extract_surname(author1)
        surname2 = extract_surname(author2)
        if surname1 == surname2:
            similarity = max(similarity, 0.95)
        elif surname1 in surname2 or surname2 in surname1:
            similarity = max(similarity, 0.9)
    
    # 特殊处理：多作者引用与单作者参考文献的匹配
    # 如果引用中有多个作者（包含&或and），尝试匹配第一个作者
    if ('&' in author1 or 'and' in author1) and not ('&' in author2 or 'and' in author2):
        # 分割引用中的第一个作者
        first_author_in_citation = author1.split('&')[0].split('and')[0].strip()
        # 计算第一个作者与参考文献作者的相似度
        first_author_similarity = SequenceMatcher(None, first_author_in_citation, author2).ratio()
        # 如果第一个作者相似度更高，则使用这个相似度
        if first_author_similarity > similarity:
            similarity = first_author_similarity
            # 特殊处理：如果第一个作者包含参考文献作者或反之
            if first_author_in_citation in author2 or author2 in first_author_in_citation:
                similarity = max(similarity, 0.9)
            # 特殊处理：英文名的姓氏匹配
            if is_english_name(first_author_in_citation):
                first_surname = extract_surname(first_author_in_citation)
                second_surname = extract_surname(author2)
                if first_surname == second_surname:
                    similarity = max(similarity, 0.95)
                elif first_surname in second_surname or second_surname in first_surname:
                    similarity = max(similarity, 0.9)
    
    # 特殊处理：单作者引用与多作者参考文献的匹配
    # 如果参考文献中有多个作者（包含&或and），尝试匹配第一个作者
    if ('&' in author2 or 'and' in author2) and not ('&' in author1 or 'and' in author1):
        # 分割参考文献中的第一个作者
        first_author_in_reference = author2.split('&')[0].split('and')[0].strip()
        # 计算引用作者与第一个作者的相似度
        first_author_similarity = SequenceMatcher(None, author1, first_author_in_reference).ratio()
        # 如果第一个作者相似度更高，则使用这个相似度
        if first_author_similarity > similarity:
            similarity = first_author_similarity
            # 特殊处理：如果第一个作者包含引用作者或反之
            if first_author_in_reference in author1 or author1 in first_author_in_reference:
                similarity = max(similarity, 0.9)
            # 特殊处理：英文名的姓氏匹配
            if is_english_name(first_author_in_reference):
                first_surname = extract_surname(author1)
                second_surname = extract_surname(first_author_in_reference)
                if first_surname == second_surname:
                    similarity = max(similarity, 0.95)
                elif first_surname in second_surname or second_surname in first_surname:
                    similarity = max(similarity, 0.9)
    
    # 特殊处理：处理参考文献中带有名字缩写的情况（如Ohanian, R.）
    # 如果参考文献中的作者包含逗号和名字缩写，而引用中只有姓氏
    if ',' in author2 and '.' in author2:
        # 提取参考文献中的姓氏部分（逗号前的部分）
        ref_surname = author2.split(',')[0].strip().lower()
        if ref_surname == author1:
            similarity = max(similarity, 0.95)
        elif ref_surname in author1 or author1 in ref_surname:
            similarity = max(similarity, 0.9)
    
    # 特殊处理：处理引用中只有姓氏，参考文献中有完整姓名的情况
    if ',' in author1 and '.' in author1:
        # 提取引用中的姓氏部分（逗号前的部分）
        cit_surname = author1.split(',')[0].strip().lower()
        if cit_surname == author2:
            similarity = max(similarity, 0.95)
        elif cit_surname in author2 or author2 in cit_surname:
            similarity = max(similarity, 0.9)
            
    return similarity


def is_similar_author(author1: str, author2: str) -> bool:
    """
    判断两个作者名是否相似 (兼容旧接口)
    
    Args:
        author1 (str): 第一个作者名
        author2 (str): 第二个作者名
        
    Returns:
        bool: 是否相似
    """
    return calculate_author_similarity(author1, author2) > 0.7


def is_english_name(name: str) -> bool:
    """判断是否为英文名"""
    # 检查输入是否为None
    if name is None:
        return False

    # 确保输入是字符串类型
    name = str(name)

    return bool(re.match(r'^[A-Za-z\s.,]+$', name))


def extract_surname(name: str) -> str:
    """提取英文名的姓氏"""
    import re

    # 检查输入是否为None
    if name is None:
        return ""

    # 确保输入是字符串类型
    name = str(name)

    # 去除"et al."后缀
    name = re.sub(r'\s+et\s+al\.?', '', name, flags=re.IGNORECASE).strip()

    # 去除"等"后缀
    name = re.sub(r'\s+等', '', name).strip()

    # 分割名字部分
    parts = name.split()
    if parts:
        # 特殊处理：对于像"Van Den Heuvel Christopher"这样的复合姓氏
        # 如果倒数第二个部分是常见的荷兰姓氏前缀，将它们组合起来
        dutch_prefixes = {'van', 'den', 'de', 'der', 'ter', 'ten', 'vanden', 'vander'}
        
        if len(parts) >= 2:
            # 检查倒数第二个部分是否为荷兰姓氏前缀
            second_last = parts[-2].lower()
            if second_last in dutch_prefixes:
                # 组合倒数两个部分作为姓氏
                return f"{parts[-2]} {parts[-1]}"
            # 检查倒数第三个和第二个部分是否都是荷兰姓氏前缀
            elif len(parts) >= 3 and parts[-3].lower() in dutch_prefixes and second_last in dutch_prefixes:
                # 组合倒数三个部分作为姓氏
                return f"{parts[-3]} {parts[-2]} {parts[-1]}"
        
        # 如果最后一个部分是单个字母或缩写，取倒数第二个部分作为姓氏
        if len(parts[-1]) == 1 or (len(parts[-1]) == 2 and parts[-1][1] == '.'):
            return parts[-2] if len(parts) > 1 else parts[-1]
        else:
            return parts[-1]  # 姓氏是最后一个部分
    return name


def extract_authors_from_reference(reference_text: str) -> Tuple[List[str], bool]:
    """
    从参考文献条目中提取作者列表

    参数:
        reference_text: 参考文献文本

    返回:
        作者列表, 是否有et al.标记
    """
    # 首先检查是否是中文文献
    if contains_chinese(reference_text[:50]) or any(char in reference_text for char in ['，', '。', '期刊', '杂志']):
        authors = extract_chinese_authors(reference_text)
        return authors, False
    else:
        return extract_english_authors(reference_text)


def contains_chinese(text: str) -> bool:
    """检查文本是否包含中文字符"""
    return bool(re.search('[\u4e00-\u9fff]', text))


def extract_chinese_authors(reference_text: str) -> List[str]:
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


def extract_english_authors(reference_text: str) -> List[str]:
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


def format_citation_by_authors(authors: List[str], year: str, original_citation: str, has_et_al: bool = False) -> str:
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