#!/usr/bin/env python3
"""
检查系统支持的文件格式
"""

import sys
import os

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.utils.document_parser import document_parser

def main():
    print("RAG系统支持的文件格式:")
    print("=" * 40)
    
    formats = document_parser.get_supported_formats()
    for fmt in formats:
        if fmt == '.txt':
            print(f"✅ {fmt} - 文本文件")
        elif fmt == '.pdf':
            print(f"✅ {fmt} - PDF文档 (需要pdfplumber)")
        elif fmt == '.docx':
            print(f"✅ {fmt} - Word文档 (需要python-docx)")
        else:
            print(f"✅ {fmt}")
    
    print("\n使用说明:")
    print("1. 将文档放入 data/raw/ 目录")
    print("2. 运行: python scripts/load_documents.py")
    print("3. 系统会自动解析并加载支持的文档格式")

if __name__ == "__main__":
    main()