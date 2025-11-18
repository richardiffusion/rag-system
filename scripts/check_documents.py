#!/usr/bin/env python3
"""
检查已加载的文档 - ChromaDB版本
"""

import sys
import os

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.vector_store import vector_store

def check_documents():
    """检查数据库中的文档"""
    try:
        # 获取文档数量
        doc_count = vector_store.get_document_count()
        print(f"📊 ChromaDB中的文档总数: {doc_count}")
        
        # 获取文档示例
        sample_docs = vector_store.get_all_documents(limit=3)
        
        print("\n📄 文档示例:")
        for i, doc in enumerate(sample_docs):
            print(f"\n文档 {i+1}:")
            print(f"  ID: {doc.id}")
            content_preview = doc.content[:100] + "..." if len(doc.content) > 100 else doc.content
            print(f"  内容预览: {content_preview}")
            print(f"  元数据: {doc.metadata}")
        
        return True
        
    except Exception as e:
        print(f"❌ 检查文档失败: {e}")
        return False

if __name__ == "__main__":
    success = check_documents()
    sys.exit(0 if success else 1)