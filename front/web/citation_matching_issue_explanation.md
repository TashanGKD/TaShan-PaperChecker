# 引用匹配问题分析与解决方案

## 问题描述
当前系统在处理同作者同年度的不同文献时存在以下问题：

1. 原文中有两处分别引用了李三希教授2023年的两篇文章，但在原文中两处都标的是（李三希等，2023）
2. 系统无法准确对应下面参考文献列表中的相应条目
3. 尝试使用（李三希等，2023a）、（李三希等，2023b）来区分时，系统仍无法正确识别

## 问题根源分析
引用匹配算法可能存在以下缺陷：

1. **简单的模式匹配**：当前算法可能只是简单地按"作者+年份"进行匹配，对于"李三希等，2023"这种形式的引用，无法区分具体对应哪一篇文献。

2. **扩展字符支持不足**：当前算法在处理"李三希等，2023a"、"李三希等，2023b"等带有扩展字符的引用时，可能未能正确识别a、b等字母标识。

3. **上下文匹配缺失**：高级的引用系统通常会结合上下文信息（如引用位置、内容关联度等）来精确匹配引用与参考文献。

## 解决方案

### 1. 增强引用识别正则表达式
修改引用识别的正则表达式，使其支持带字母扩展的年份引用格式：
- 当前格式：`(作者等，年份)`
- 扩展格式：`(作者等，年份[字母])` 如 (李三希等，2023a)

### 2. 改进匹配算法
- 在"年份"字段基础上增加"副键"字段，用于处理同年度多篇文献的情况
- 将"年份+扩展字符"作为复合键进行匹配

### 3. 实现步骤建议

#### 后端引用解析模块修改：
```python
import re

def parse_citation(citation_text):
    """
    解析引用文本，支持标准格式和带扩展字符的格式
    """
    # 支持 (李三希等, 2023) 和 (李三希等, 2023a) 等格式
    patterns = [
        r'([^(]*)\(([^)]+?)等[，,]\s*(\d{4})([a-z]?)\)',  # 中文格式
        r'\(?([^(]+?)\s+et\s+al\.?,?\s+(\d{4})([a-z]?)\)'   # 英文格式
    ]
    
    for pattern in patterns:
        match = re.search(pattern, citation_text)
        if match:
            # 提取作者、年份和扩展字符
            authors = match.group(1).strip() if len(match.groups()) > 1 else match.group(2).strip()
            year = match.group(2).strip() if len(match.groups()) > 2 else match.group(3).strip()
            extension = match.group(3).strip() if len(match.groups()) > 3 else (match.group(4) if len(match.groups()) > 3 else '')
            
            return {
                'authors': authors,
                'year': year,
                'extension': extension,
                'full_key': f"{authors}_{year}{extension}"
            }
    
    return None

def match_citations_to_references(citations, references):
    """
    匹配引用与参考文献，使用复合键提高准确性
    """
    matched_results = []
    unmatched_citations = []
    
    # 构建参考文献索引，使用复合键
    ref_index = {}
    for ref in references:
        # 从参考文献中提取元数据构建键
        ref_data = extract_reference_metadata(ref)
        key = ref_data.get('full_key', f"{ref_data.get('authors', '')}_{ref_data.get('year', '')}{ref_data.get('extension', '')}")
        
        if key not in ref_index:
            ref_index[key] = []
        ref_index[key].append(ref)
    
    # 匹配引用
    for citation in citations:
        citation_parsed = parse_citation(citation)
        if citation_parsed:
            # 尝试精确匹配（包括扩展字符）
            full_key = citation_parsed['full_key']
            
            if full_key in ref_index and ref_index[full_key]:
                matched_ref = ref_index[full_key].pop(0)  # 取第一个匹配项
                matched_results.append({
                    'original_citation': citation,
                    'matched_reference': matched_ref,
                    'matched': True
                })
            else:
                # 尝试模糊匹配（只有年份，忽略扩展字符）
                base_key = f"{citation_parsed['authors']}_{citation_parsed['year']}"
                similar_keys = [k for k in ref_index.keys() if k.startswith(base_key)]
                
                if similar_keys and ref_index[similar_keys[0]]:
                    matched_ref = ref_index[similar_keys[0]].pop(0)
                    matched_results.append({
                        'original_citation': citation,
                        'matched_reference': matched_ref,
                        'matched': True,
                        'warning': f'引用使用了扩展字符但参考文献中未找到精确匹配: {full_key}'
                    })
                else:
                    unmatched_citations.append(citation)
        else:
            unmatched_citations.append(citation)
    
    return matched_results, unmatched_citations
```

### 4. 额外考虑
- **顺序匹配**：如果文档中引用了多个相同作者年份的文献，可根据出现顺序进行匹配
- **内容相似性**：对引用内容和参考文献进行文本相似性分析，辅助匹配决策
- **引用计数**：记录同作者同年度文献的引用次数，帮助进行匹配

## 注意事项
要修复此问题，需要访问和修改后端服务的引用解析模块。前端代码无需修改，因为问题在于后端的引用匹配逻辑。