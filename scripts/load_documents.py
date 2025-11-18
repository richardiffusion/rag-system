#!/usr/bin/env python3
"""
文档批量加载脚本 - ChromaDB版本
"""

import sys
import os
import logging
from pathlib import Path

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.vector_store import vector_store
from app.services.embedding_service import embedding_service
from app.utils.text_processor import text_processor
from app.models.document_models import DocumentCreate
import time

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def load_text_file(file_path: str) -> str:
    """加载文本文件"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        logger.error(f"读取文件 {file_path} 失败: {e}")
        return ""

def load_pdf_file(file_path: str) -> str:
    """加载PDF文件"""
    try:
        import PyPDF2
        content = ""
        with open(file_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            for page in pdf_reader.pages:
                content += page.extract_text() + "\n"
        return content
    except Exception as e:
        logger.error(f"读取PDF文件 {file_path} 失败: {e}")
        return ""

def load_docx_file(file_path: str) -> str:
    """加载DOCX文件"""
    try:
        from docx import Document
        doc = Document(file_path)
        content = ""
        for paragraph in doc.paragraphs:
            content += paragraph.text + "\n"
        return content
    except Exception as e:
        logger.error(f"读取DOCX文件 {file_path} 失败: {e}")
        return ""

def load_documents_from_directory(directory: str):
    """从目录加载所有文档文件"""
    data_dir = Path(directory)
    
    if not data_dir.exists():
        logger.error(f"目录不存在: {directory}")
        return
    
    # 支持的文件格式
    text_files = list(data_dir.glob("*.txt"))
    pdf_files = list(data_dir.glob("*.pdf"))
    docx_files = list(data_dir.glob("*.docx"))
    
    all_files = text_files + pdf_files + docx_files
    
    if not all_files:
        logger.warning(f"在 {directory} 中没有找到支持的文档文件")
        return
    
    logger.info(f"支持的文件格式: .txt, .pdf, .docx")
    
    total_chunks = 0
    successful_chunks = 0
    
    for file_path in all_files:
        logger.info(f"处理文件: {file_path.name}")
        
        # 根据文件类型加载内容
        if file_path.suffix.lower() == '.pdf':
            content = load_pdf_file(str(file_path))
        elif file_path.suffix.lower() == '.docx':
            content = load_docx_file(str(file_path))
        else:
            content = load_text_file(str(file_path))
            
        if not content:
            logger.warning(f"文件内容为空: {file_path.name}")
            continue
        
        # 文本分块处理
        chunks = text_processor.process_document(content)
        
        # 将每个块作为独立文档存储
        for i, chunk in enumerate(chunks):
            if not chunk.strip():
                continue
                
            document = DocumentCreate(
                content=chunk,
                metadata={
                    "source_file": file_path.name,
                    "chunk_index": i,
                    "total_chunks": len(chunks),
                    "file_type": file_path.suffix.lower()
                }
            )
            
            try:
                # 生成嵌入并存储
                embedding = embedding_service.get_embedding(chunk)
                doc_id = vector_store.insert_document(document, embedding)
                
                total_chunks += 1
                successful_chunks += 1
                
                if total_chunks % 5 == 0:
                    logger.info(f"已处理 {total_chunks} 个文档块...")
                    
            except Exception as e:
                logger.error(f"处理文档块失败: {e}")
                total_chunks += 1
        
        logger.info(f"文件 {file_path.name} 处理完成，生成 {len(chunks)} 个文档块")
    
    logger.info(f"文档加载完成！共处理 {len(all_files)} 个文件，成功加载 {successful_chunks}/{total_chunks} 个文档块")

def main():
    """主函数"""
    # 默认数据目录
    data_directory = "data/raw"
    
    # 如果提供了命令行参数，使用参数作为目录
    if len(sys.argv) > 1:
        data_directory = sys.argv[1]
    
    logger.info(f"从目录加载文档: {data_directory}")
    
    # 检查嵌入服务状态
    if hasattr(embedding_service, 'use_simple') and embedding_service.use_simple:
        logger.warning("⚠️  使用简单嵌入服务，检索效果可能不如专业模型")
    
    start_time = time.time()
    load_documents_from_directory(data_directory)
    end_time = time.time()
    
    logger.info(f"总耗时: {end_time - start_time:.2f}秒")

if __name__ == "__main__":
    main()