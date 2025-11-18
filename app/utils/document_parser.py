import os
import logging
from typing import List, Optional, Dict, Any
from pathlib import Path

# 条件导入，避免在没有安装依赖时报错
try:
    import pdfplumber
    PDF_SUPPORT = True
except ImportError:
    PDF_SUPPORT = False
    logging.warning("PDF支持未安装，请安装: pip install pdfplumber")

try:
    from docx import Document as DocxDocument
    DOCX_SUPPORT = True
except ImportError:
    DOCX_SUPPORT = False
    logging.warning("DOCX支持未安装，请安装: pip install python-docx")

logger = logging.getLogger(__name__)

class DocumentParser:
    def __init__(self):
        self.supported_formats = ['.txt']
        if PDF_SUPPORT:
            self.supported_formats.append('.pdf')
        if DOCX_SUPPORT:
            self.supported_formats.append('.docx')
    
    def parse_file(self, file_path: str) -> Optional[Dict[str, Any]]:
        """
        解析文件并返回内容
        
        Returns:
            Dict with keys: 'content', 'metadata', 'success', 'error_message'
        """
        file_path = Path(file_path)
        if not file_path.exists():
            return {
                'content': '',
                'metadata': {'error': '文件不存在'},
                'success': False,
                'error_message': f'文件不存在: {file_path}'
            }
        
        file_extension = file_path.suffix.lower()
        
        try:
            if file_extension == '.txt':
                return self._parse_txt(file_path)
            elif file_extension == '.pdf' and PDF_SUPPORT:
                return self._parse_pdf(file_path)
            elif file_extension == '.docx' and DOCX_SUPPORT:
                return self._parse_docx(file_path)
            else:
                return {
                    'content': '',
                    'metadata': {'error': '不支持的文件格式'},
                    'success': False,
                    'error_message': f'不支持的文件格式: {file_extension}'
                }
        except Exception as e:
            logger.error(f"解析文件 {file_path} 失败: {e}")
            return {
                'content': '',
                'metadata': {'error': '解析失败'},
                'success': False,
                'error_message': str(e)
            }
    
    def _parse_txt(self, file_path: Path) -> Dict[str, Any]:
        """解析文本文件"""
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        return {
            'content': content,
            'metadata': {
                'file_type': 'txt',
                'file_name': file_path.name,
                'file_size': os.path.getsize(file_path)
            },
            'success': True,
            'error_message': None
        }
    
    def _parse_pdf(self, file_path: Path) -> Dict[str, Any]:
        """解析PDF文件"""
        content_parts = []
        total_pages = 0
        
        with pdfplumber.open(file_path) as pdf:
            total_pages = len(pdf.pages)
            for page_num, page in enumerate(pdf.pages):
                try:
                    text = page.extract_text()
                    if text and text.strip():
                        content_parts.append(f"第{page_num + 1}页:\n{text}")
                except Exception as e:
                    logger.warning(f"提取PDF第{page_num + 1}页失败: {e}")
                    continue
        
        content = "\n\n".join(content_parts)
        
        return {
            'content': content,
            'metadata': {
                'file_type': 'pdf',
                'file_name': file_path.name,
                'file_size': os.path.getsize(file_path),
                'total_pages': total_pages,
                'extracted_pages': len(content_parts)
            },
            'success': True,
            'error_message': None
        }
    
    def _parse_docx(self, file_path: Path) -> Dict[str, Any]:
        """解析Word文档"""
        doc = DocxDocument(file_path)
        content_parts = []
        
        for paragraph in doc.paragraphs:
            if paragraph.text.strip():
                content_parts.append(paragraph.text)
        
        content = "\n".join(content_parts)
        
        return {
            'content': content,
            'metadata': {
                'file_type': 'docx',
                'file_name': file_path.name,
                'file_size': os.path.getsize(file_path),
                'paragraphs_count': len(content_parts)
            },
            'success': True,
            'error_message': None
        }
    
    def get_supported_formats(self) -> List[str]:
        """获取支持的文件格式"""
        return self.supported_formats

# 全局文档解析器实例
document_parser = DocumentParser()