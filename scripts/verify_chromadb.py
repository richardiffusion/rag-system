#!/usr/bin/env python3
"""
验证ChromaDB是否正常工作
"""

import sys
import os
import logging

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.vector_store import vector_store
from app.services.embedding_service import embedding_service
from app.models.document_models import DocumentCreate

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def verify_chromadb():
    """验证ChromaDB功能"""
    try:
        print("验证ChromaDB功能...")
        
        # 测试插入文档
        test_doc = DocumentCreate(
            content="这是一个测试文档，用于验证ChromaDB向量搜索功能。人工智能是计算机科学的重要分支。",
            metadata={"source": "test", "type": "verification"}
        )
        
        # 生成嵌入
        embedding = embedding_service.get_embedding(test_doc.content)
        
        # 插入文档
        doc_id = vector_store.insert_document(test_doc, embedding)
        print(f"✅ 文档插入成功，ID: {doc_id}")
        
        # 测试搜索
        query_text = "人工智能"
        query_embedding = embedding_service.get_embedding(query_text)
        results = vector_store.similarity_search(query_embedding, top_k=2)
        
        print(f"✅ 向量搜索成功")
        print(f"搜索查询: '{query_text}'")
        print(f"找到文档数量: {len(results)}")
        
        for i, doc in enumerate(results):
            print(f"文档 {i+1}: {doc.content[:50]}...")
        
        # 清理测试数据
        print("✅ ChromaDB验证完成！")
        
    except Exception as e:
        print(f"❌ ChromaDB验证失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    verify_chromadb()