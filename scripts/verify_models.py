#!/usr/bin/env python3
"""
验证本地模型是否正常工作的脚本
"""

import sys
import os
import logging

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.local_llm_service import LocalLLMService
from app.models.document_models import Document

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_local_model():
    """测试本地模型功能"""
    try:
        logger.info("开始测试本地Llama3.1模型...")
        
        # 创建LLM服务实例
        llm_service = LocalLLMService()
        
        # 创建测试文档
        test_documents = [
            Document(
                _id="test1",
                content="人工智能是计算机科学的一个分支，旨在创造能够执行通常需要人类智能的任务的机器。",
                metadata={"source": "test"}
            ),
            Document(
                _id="test2", 
                content="机器学习是人工智能的一个子集，它使计算机能够在没有明确编程的情况下学习和改进。",
                metadata={"source": "test"}
            )
        ]
        
        # 测试生成
        test_question = "什么是人工智能？"
        answer = llm_service.generate_answer(test_question, test_documents)
        
        print(f"问题: {test_question}")
        print(f"回答: {answer}")
        print("✅ 本地模型测试成功！")
        
    except Exception as e:
        logger.error(f"本地模型测试失败: {e}")
        print("❌ 本地模型测试失败！")
        sys.exit(1)

if __name__ == "__main__":
    test_local_model()