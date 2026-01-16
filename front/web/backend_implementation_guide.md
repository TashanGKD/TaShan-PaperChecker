# 后端功能扩展说明：添加通过路径直接分析文件的功能

## 概述

当前系统允许用户上传Word文档进行引用分析，但不支持直接从服务器上的文件路径分析已上传的文件。此文档说明如何扩展后端API以支持`/api/full-report-from-path`端点。

## API 端点定义

### `POST /api/full-report-from-path`

通过文件路径直接分析已上传的文档。

**请求参数：**
- `file_path` (form): 要分析的文件路径 (必填)
- `author_format` (form): 作者格式规则 ('full' 或 'abbrev'，可选，默认为 'full')

**响应：**
与 `/api/full-report` 相同的格式（完整的引用分析报告）

## 实现步骤

### 1. 创建新的API路由

将以下代码添加到您的FastAPI应用中（通常是 `main.py` 或 `api.py` 文件）：

```python
from fastapi import APIRouter, HTTPException, Form
from fastapi.responses import JSONResponse
import os
from pathlib import Path

@router.post("/api/full-report-from-path")
async def full_report_from_path(
    file_path: str = Form(...),
    author_format: str = Form("full")
):
    """
    通过文件路径直接分析文档
    """
    try:
        # 验证文件路径的安全性，防止路径遍历攻击
        safe_path = Path(file_path).resolve()
        base_dir = Path("temp_uploads").resolve()
        
        # 验证路径是否在temp_uploads目录下
        if not str(safe_path).startswith(str(base_dir)):
            raise HTTPException(status_code=400, detail="Invalid file path")
        
        # 检查文件是否存在
        if not safe_path.exists():
            raise HTTPException(status_code=404, detail="File not found")
        
        # 验证文件类型
        allowed_extensions = {'.doc', '.docx', '.docm', '.dot', '.dotx', '.dotm'}
        if safe_path.suffix.lower() not in allowed_extensions:
            raise HTTPException(status_code=400, detail="Invalid file type")
        
        # 调用现有的文档分析逻辑
        # 以下是关键部分 - 您需要将这里替换为实际的分析调用
        # 请参考您现有的 /api/full-report 实现
        
        # 示例（需要根据您的实际实现调整）：
        # 1. 导入您现有的分析函数
        # from your_analysis_module import analyze_document, format_report
        
        # 2. 调用分析函数
        # result = analyze_document(file_path, author_format=author_format)
        
        # 3. 格式化结果并返回
        # return JSONResponse(content=format_report(result))
        
        # 临时返回 - 替换为实际分析逻辑
        file_path_str = str(safe_path)
        result = perform_file_analysis(file_path_str, author_format)
        return JSONResponse(content=result)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis error: {str(e)}")
```

### 2. 实现分析函数

您需要将以下伪代码替换为实际的分析逻辑，参考您现有的 `/api/full-report` 实现：

```python
def perform_file_analysis(file_path: str, author_format: str):
    """
    实际的文件分析逻辑
    此函数需要根据您现有的分析代码进行实现
    """
    # 1. 读取文件
    # 2. 调用文档解析和引用分析逻辑
    # 3. 根据author_format参数应用格式规则
    # 4. 返回与现有API相同的格式结果
    
    # 示例框架（需要根据您的代码进行调整）：
    """
    from your_document_processor import process_document
    from your_citation_analyzer import analyze_citations
    
    # 处理文档
    doc_content = process_document(file_path)
    
    # 分析引用
    analysis_result = analyze_citations(
        doc_content,
        author_format=author_format
    )
    
    # 格式化为API响应格式
    return format_analysis_result(analysis_result)
    """
    
    # 临时返回值 - 需替换为实际实现
    import json
    return {
        "document": os.path.basename(file_path),
        "test_date": "2024-01-01T00:00:00",  # 确保包括实际的测试日期
        "total_citations": 0,
        "total_references": 0,
        "matched_count": 0,
        "unmatched_count": 0,
        "corrected_count": 0,
        "formatted_count": 0,
        "match_rate": "0%",
        "results": [],
        "corrections_needed": [],
        "formatting_needed": [],
        "unused_references": []
    }
```

### 3. 修改前端API调用

在完成上述后端修改后，您需要重新更新前端代码，将之前创建的临时解决方法替换为直接调用新API：

```javascript
// 修改后的 analyzeFileFromList 函数
function analyzeFileFromList(filePath) {
    const serverUrl = defaultBase.trim().replace(/\/$/, '');
    const analyzeUrl = serverUrl + '/api/full-report-from-path';

    // 获取当前选中的作者格式
    const selectedAuthorFormat = document.querySelector('input[name="author-format"]:checked').value;

    const params = new URLSearchParams({
        file_path: filePath,
        author_format: selectedAuthorFormat
    });

    setBar(uploadProgress, 0);
    setBar(analysisProgress, 0);
    resultBox.hidden = true;
    log('准备分析文件：' + filePath.split('/').pop() + '，作者格式规则：' + (selectedAuthorFormat === 'full' ? '完整显示' : '简略显示'));

    startBtn.disabled = true;

    // 更新开始按钮的状态
    const originalButtonText = startBtn.textContent;
    startBtn.textContent = '分析中...';

    const xhr = new XMLHttpRequest();

    // 模拟分析进度，因为后端不提供进度API
    const progressInterval = setInterval(() => {
        if (xhr.readyState < 4) {
            // 模拟分析进度，当上传完成后的阶段
            if (xhr.readyState === 2) { // HEADERS_RECEIVED
                const currentProgress = parseFloat(analysisProgress.style.width || '0');
                if (currentProgress < 90) { // 不到100%，因为我们要等待实际响应
                    setBar(analysisProgress, currentProgress + 2);
                }
            }
        }
    }, 500);

    xhr.onreadystatechange = () => {
        if (xhr.readyState !== XMLHttpRequest.DONE) return;

        clearInterval(progressInterval); // 停止模拟进度
        
        // 恢复开始按钮的原始状态
        startBtn.disabled = false;
        startBtn.textContent = originalButtonText;

        if (xhr.status === 200) {
            setBar(uploadProgress, 100);
            setBar(analysisProgress, 100);
            log('分析完成。');
            try {
                const payload = JSON.parse(xhr.responseText);
                renderResult(payload);
            } catch (err) {
                log('响应解析失败：' + err.message);
            }
        } else {
            log('请求失败：' + (xhr.responseText || ('状态码 ' + xhr.status)));
        }
    };

    xhr.onerror = () => {
        clearInterval(progressInterval); // 停止模拟进度
        startBtn.disabled = false;
        startBtn.textContent = originalButtonText;
        log('网络异常，请确认后端服务可访问。');
    };

    xhr.open('POST', analyzeUrl + '?' + params.toString(), true);
    xhr.send();
}
```

## 安全考虑

1. **路径验证**：确保文件路径在允许的目录内，防止路径遍历攻击
2. **文件类型验证**：验证文件扩展名，只允许Word文档类型
3. **权限控制**：根据需要实现适当的认证和授权

## 部署说明

1. 将上述代码集成到后端项目中
2. 确保在启动时正确注册了新端点
3. 重新启动后端服务
4. 验证新API端点是否正常工作
5. 如需要，更新前端代码以使用新功能

## 故障排除

如果API不可用，请检查：
1. 后端服务是否已重新启动
2. API端点是否正确注册
3. 防火墙或代理设置是否阻止了请求