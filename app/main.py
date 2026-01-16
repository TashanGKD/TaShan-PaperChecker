import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi import FastAPI, File, UploadFile, HTTPException, Query
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from typing import Dict, Any
import tempfile
import shutil
from datetime import datetime

from core.processors.citation_processor import CitationProcessor
from core.reports.api import ReportService
from utils.file_handler import save_upload_file, cleanup_file
from config.config import settings

# 最大上传文件大小
MAX_FILE_SIZE = settings.max_upload_size

app = FastAPI(
    title="PaperChecker API",
    description="学术论文引用合规性检查API - 重构版",
    version="2.0.0"
)

# 允许跨域请求
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 临时文件存储目录
TEMP_DIR = settings.temp_dir
os.makedirs(TEMP_DIR, exist_ok=True)

@app.get("/")
def read_root():
    return {
        "message": "PaperChecker API - 重构版",
        "version": "2.0.0",
        "modules": ["extractor", "checker", "processor", "reports"]
    }

# 挂载静态文件目录到 /frontend 路径
app.mount("/frontend", StaticFiles(directory="front/web", html=True), name="frontend")

@app.post("/api/full-report")
async def get_full_citation_report(file: UploadFile = File(...)):
    """
    生成完整的引文合规性报告，兼容原有standalone_mapping_test.py的输出格式
    """
    # 检查文件大小
    file.file.seek(0, 2)  # 移动到文件末尾
    file_size = file.file.tell()
    file.file.seek(0)  # 移回文件开头
    
    if file_size > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=413,
            detail=f"文件过大，最大支持 {MAX_FILE_SIZE // (1024*1024)}MB"
        )
    
    file_path = None
    try:
        # 保存上传的文件
        file_path = save_upload_file(file, TEMP_DIR)
        
        # 使用新的处理器执行分析
        processor = CitationProcessor()
        analysis_result = processor.process(file_path)
        
        # 返回分析结果（保持与原standalone_mapping_test.py输出格式兼容）
        return JSONResponse(content=analysis_result)
    
    except HTTPException:
        # 重新抛出HTTP异常
        raise
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"分析过程中出现错误: {str(e)}")
    
    finally:
        # 清理上传的文件
        if file_path:
            cleanup_file(file_path)

from core.checker.relevance_checker import RelevanceChecker
from models.document import Document, Citation
from core.extractor.word_extractor import WordExtractor


from fastapi import Request, Form

@app.post("/api/extract-citations")
async def extract_citations_form(file_path: str = Form(None)):
    """
    从文档中提取引用文献（通过表单数据）
    """
    try:
        # 验证文件是否存在
        if not file_path:
            raise HTTPException(status_code=400, detail="文件路径不能为空")

        # 获取项目根目录
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # 获取项目根目录

        # 验证路径安全性，防止路径遍历攻击
        allowed_base_dir = os.path.abspath(os.path.join(project_root, "temp_uploads"))

        # 处理路径，如果是绝对路径则直接使用，否则相对于项目根目录
        if os.path.isabs(file_path):
            abs_file_path = os.path.abspath(file_path)
        else:
            abs_file_path = os.path.abspath(os.path.join(project_root, file_path))

        # 检查规范化路径是否在允许的目录内
        if not abs_file_path.startswith(allowed_base_dir):
            raise HTTPException(status_code=400, detail="Invalid file path")

        if not os.path.exists(abs_file_path):
            raise HTTPException(status_code=404, detail="文件不存在")

        # 根据文件类型选择适当的提取器
        _, ext = os.path.splitext(abs_file_path)
        ext = ext.lower().lstrip('.')

        if ext in ['doc', 'docx']:
            extractor = WordExtractor()
        elif ext == 'pdf':
            # 使用改进的PDF提取器，进行本地处理，避免API调用
            from core.extractor.pdf_extractor import PDFExtractor
            extractor = PDFExtractor()
        else:
            raise HTTPException(status_code=400, detail=f"不支持的文件类型: {ext}")

        document = extractor.extract(abs_file_path)

        # 提取引用文献
        citations = []
        for citation in document.citations:
            citations.append({
                "text": citation.text,
                "format_type": citation.format_type,
                "context": citation.context,
                "author": citation.author,
                "year": citation.year
            })

        return JSONResponse(content={"citations": citations})

    except HTTPException:
        # 重新抛出HTTP异常
        raise

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"提取引用文献过程中出现错误: {str(e)}")


@app.post("/api/extract-citations-json")
async def extract_citations_json(request: Request):
    """
    从文档中提取引用文献（通过JSON数据）
    """
    try:
        body = await request.json()
        file_path = body.get("file_path")

        # 验证文件是否存在
        if not file_path or not os.path.exists(file_path):
            raise HTTPException(status_code=404, detail="文件不存在")

        # 根据文件类型选择适当的提取器
        _, ext = os.path.splitext(file_path)
        ext = ext.lower().lstrip('.')

        if ext in ['doc', 'docx']:
            extractor = WordExtractor()
        elif ext == 'pdf':
            # 使用改进的PDF提取器，进行本地处理，避免API调用
            from core.extractor.pdf_extractor import PDFExtractor
            extractor = PDFExtractor()
        else:
            raise HTTPException(status_code=400, detail=f"不支持的文件类型: {ext}")

        document = extractor.extract(file_path)

        # 提取引用文献
        citations = []
        for citation in document.citations:
            citations.append({
                "text": citation.text,
                "format_type": citation.format_type,
                "context": citation.context,
                "author": citation.author,
                "year": citation.year
            })

        return JSONResponse(content={"citations": citations})

    except HTTPException:
        # 重新抛出HTTP异常
        raise

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"提取引用文献过程中出现错误: {str(e)}")


@app.post("/api/relevance-check")
async def perform_relevance_check(
    file_path: str = Form(...),
    target_content: str = Form(...),
    task_type: str = Form("文章整体"),
    use_full_content: bool = Form(False)
):
    """
    执行文献相关性检查
    """
    try:
        # 获取项目根目录
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # 获取项目根目录

        # 验证路径安全性，防止路径遍历攻击
        allowed_base_dir = os.path.abspath(os.path.join(project_root, "temp_uploads"))

        # 处理路径，如果是绝对路径则直接使用，否则相对于项目根目录
        if os.path.isabs(file_path):
            abs_file_path = os.path.abspath(file_path)
        else:
            abs_file_path = os.path.abspath(os.path.join(project_root, file_path))

        # 检查规范化路径是否在允许的目录内
        if not abs_file_path.startswith(allowed_base_dir):
            raise HTTPException(status_code=400, detail="Invalid file path")

        # 验证文件是否存在
        if not os.path.exists(abs_file_path):
            raise HTTPException(status_code=404, detail="文件不存在")

        # 根据文件类型选择适当的提取器
        _, ext = os.path.splitext(abs_file_path)
        ext = ext.lower().lstrip('.')

        if ext in ['doc', 'docx']:
            extractor = WordExtractor()
        elif ext == 'pdf':
            # 使用改进的PDF提取器，进行本地处理，避免API调用
            from core.extractor.pdf_extractor import PDFExtractor
            extractor = PDFExtractor()
        else:
            raise HTTPException(status_code=400, detail=f"不支持的文件类型: {ext}")

        document = extractor.extract(abs_file_path)

        # 创建相关性检查器
        checker = RelevanceChecker(use_full_content=use_full_content)

        # 执行相关性检查
        result = checker.check(document, target_content, task_type)

        # 提取文件名而不是完整路径
        document_filename = os.path.basename(file_path)

        # 格式化时间为中文格式
        current_time = datetime.now()
        formatted_time = current_time.strftime("%Y年%m月%d日%H:%M:%S")

        # 构造响应数据
        response_data = {
            "文档": document_filename,
            "生成时间": formatted_time,
            "task_type": task_type,
            "check_method": "accurate_check" if use_full_content else "quick_check",
            "relevance_score": result.statistics.get("relevance_score", 0),
            "is_suitable_for_citation": result.is_compliant,
            "brief_basis": result.issues[0].get("brief_basis", "") if result.issues else "",
            "detailed_reasoning": result.issues[0].get("detailed_reasoning", "") if result.issues else "",
            "raw_result": result.metadata.get("ai_response", "")
        }

        return JSONResponse(content=response_data)

    except HTTPException:
        # 重新抛出HTTP异常
        raise

    except Exception as e:
        # 记录详细的错误信息，有助于调试
        import traceback
        error_details = traceback.format_exc()
        print(f"相关性检查过程中出现错误: {error_details}")

        # 确保错误信息不会包含敏感的内部数据
        error_msg = str(e)
        # 如果错误信息包含可能的JSON格式内容，进行清理
        if '"relevance_score"' in error_msg:
            error_msg = "AI响应解析错误，请检查AI服务配置"

        raise HTTPException(status_code=500, detail=f"相关性检查过程中出现错误: {error_msg}")


@app.get("/api/health")
def health_check():
    """健康检查端点"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "modules": {
            "extractor": "available",
            "checker": "available",
            "processor": "available",
            "reports": "available"
        }
    }


@app.post("/api/upload-only")
async def upload_only(file: UploadFile = File(...)):
    """
    仅上传文件，不进行处理
    """
    # 检查文件大小
    file.file.seek(0, 2)  # 移动到文件末尾
    file_size = file.file.tell()
    file.file.seek(0)  # 移回文件开头

    if file_size > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=413,
            detail=f"文件过大，最大支持 {MAX_FILE_SIZE // (1024*1024)}MB"
        )

    # 验证文件类型
    allowed_extensions = {'.doc', '.docx', '.pdf'}
    file_ext = os.path.splitext(file.filename)[1].lower()
    if file_ext not in allowed_extensions:
        raise HTTPException(
            status_code=400,
            detail=f"不支持的文件类型: {file_ext}. 支持的类型: .docx, .doc, .pdf"
        )

    try:
        # 保存上传的文件到临时目录
        file_path = save_upload_file(file, "temp_uploads")

        return JSONResponse(content={
            "status": "success",
            "message": "文件上传成功",
            "file_path": file_path,
            "filename": file.filename
        })

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"上传过程中出现错误: {str(e)}")


@app.get("/api/list-all-files")
async def list_all_files():
    """
    列出所有上传的文件
    """
    try:
        temp_dir = "temp_uploads"
        if not os.path.exists(temp_dir):
            os.makedirs(temp_dir, exist_ok=True)

        files = []
        for filename in os.listdir(temp_dir):
            file_path = os.path.join(temp_dir, filename)
            if os.path.isfile(file_path):
                # 获取文件扩展名并验证是否为支持的类型
                _, ext = os.path.splitext(filename)
                if ext.lower() in {'.doc', '.docx', '.pdf'}:
                    # 返回绝对路径，以便前端可以正确删除文件
                    abs_file_path = os.path.abspath(file_path)
                    files.append({
                        "name": filename,
                        "path": abs_file_path,
                        "size": os.path.getsize(file_path),
                        "modified": datetime.fromtimestamp(os.path.getmtime(file_path)).isoformat()
                    })

        return JSONResponse(content={"files": files})

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取文件列表时出现错误: {str(e)}")


@app.delete("/api/file")
async def delete_file(file_path: str = Query(..., alias="file_path")):
    """
    删除指定路径的文件
    """
    try:
        # 获取项目根目录
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # 获取项目根目录

        # 验证路径安全性，防止路径遍历攻击
        allowed_base_dir = os.path.abspath(os.path.join(project_root, "temp_uploads"))

        # 处理路径，如果是绝对路径则直接使用，否则相对于项目根目录
        if os.path.isabs(file_path):
            safe_path = os.path.abspath(file_path)
        else:
            safe_path = os.path.abspath(os.path.join(project_root, file_path))

        # 检查规范化路径是否在允许的目录内
        if not safe_path.startswith(allowed_base_dir):
            raise HTTPException(status_code=400, detail="Invalid file path")

        if os.path.exists(safe_path):
            os.remove(safe_path)
            return JSONResponse(content={"status": "success", "message": "文件删除成功"})
        else:
            raise HTTPException(status_code=404, detail="文件不存在")

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"删除文件时出现错误: {str(e)}")


@app.post("/api/full-report-from-path")
async def get_full_citation_report_from_path(
    file_path: str = Form(...),
    author_format: str = Form("full")
):
    """
    通过文件路径生成完整的引文合规性报告
    """
    try:
        # 获取项目根目录
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # 获取项目根目录

        # 验证路径安全性，防止路径遍历攻击
        allowed_base_dir = os.path.abspath(os.path.join(project_root, "temp_uploads"))

        # 处理路径，如果是绝对路径则直接使用，否则相对于项目根目录
        if os.path.isabs(file_path):
            abs_file_path = os.path.abspath(file_path)
        else:
            abs_file_path = os.path.abspath(os.path.join(project_root, file_path))

        # 检查规范化路径是否在允许的目录内
        if not abs_file_path.startswith(allowed_base_dir):
            raise HTTPException(status_code=400, detail="Invalid file path")

        if not os.path.exists(abs_file_path):
            raise HTTPException(status_code=404, detail="File not found")

        # 验证文件类型
        allowed_extensions = {'.doc', '.docx', '.pdf'}
        file_ext = os.path.splitext(abs_file_path)[1].lower()
        if file_ext not in allowed_extensions:
            raise HTTPException(
                status_code=400,
                detail=f"不支持的文件类型: {file_ext}. 支持的类型: .docx, .doc, .pdf"
            )

        # 使用新的处理器执行分析
        processor = CitationProcessor()
        analysis_result = processor.process(abs_file_path)

        # 返回分析结果（保持与原standalone_mapping_test.py输出格式兼容）
        return JSONResponse(content=analysis_result)

    except HTTPException:
        # 重新抛出HTTP异常
        raise

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"分析过程中出现错误: {str(e)}")