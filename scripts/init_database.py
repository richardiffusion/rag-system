#!/usr/bin/env python3
"""
数据库初始化脚本 - 现在用于初始化ChromaDB
"""

import sys
import os
import logging

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.vector_store import vector_store
from app.services.embedding_service import embedding_service

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def init_database():
    """
    初始化向量数据库
    """
    try:
        logger.info("开始初始化向量数据库...")
        
        # 测试向量存储连接
        test_text = "测试连接"
        test_embedding = embedding_service.get_embedding(test_text)
        results = vector_store.similarity_search(test_embedding, top_k=1)
        
        logger.info(f"向量数据库测试成功")
        logger.info(f"当前文档数量: {len(results)}")
        
        # 如果有文档，显示一些统计信息
        if results:
            logger.info(f"示例文档内容长度: {len(results[0].content)}")
        
        logger.info("向量数据库初始化完成！")
        
    except Exception as e:
        logger.error(f"向量数据库初始化失败: {e}")
        sys.exit(1)

if __name__ == "__main__":
    init_database()