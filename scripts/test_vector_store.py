#!/usr/bin/env python3
"""
测试向量存储功能
"""

import sys
import os

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.vector_store import vector_store
from app.models.document_models import DocumentCreate
from app.services.embedding_service import embedding_service

def test_vector_store():
    """测试向量存储功能"""
    try:
        print("测试向量存储...")
        
        # 测试插入
        test_doc = DocumentCreate(
            content="这是一个测试文档，用于验证向量存储功能。",
            metadata={"source": "test", "type": "test_document"}
        )
        
        # 生成嵌入
        embedding = embedding_service.get_embedding(test_doc.content)
        print(f"✅ 嵌入生成成功，维度: {len(embedding)}")
        
        # 插入文档
        doc_id = vector_store.insert_document(test_doc, embedding)
        print(f"✅ 文档插入成功: {doc_id}")
        
        # 测试搜索
        results = vector_store.similarity_search(embedding, top_k=3)
        print(f"✅ 搜索测试成功，找到 {len(results)} 个文档")
        
        if results:
            for i, doc in enumerate(results):
                print(f"  文档 {i+1}: {doc.content[:50]}...")
        
        print("✅ 向量存储测试完成！")
        
    except Exception as e:
        print(f"❌ 向量存储测试失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_vector_store()