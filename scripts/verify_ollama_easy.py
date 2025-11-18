#!/usr/bin/env python3
"""
验证Ollama是否正常工作的脚本 - 简化版
"""

import sys
import os
import logging

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.ollama_service import OllamaService
from app.models.document_models import Document

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_ollama():
    """测试Ollama功能"""
    print("开始测试Ollama...")
    
    # 创建Ollama服务实例
    ollama_service = OllamaService()
    
    if not ollama_service.is_available():
        print("❌ Ollama服务不可用")
        return False
    
    print("✅ Ollama服务可用")
    
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
    print(f"问题: {test_question}")
    
    try:
        answer = ollama_service.generate_answer(test_question, test_documents)
        print(f"回答: {answer}")
        
        if answer and len(answer) > 10:  # 简单检查回答是否合理
            print("✅ Ollama测试成功！")
            return True
        else:
            print("❌ 回答太短或为空")
            return False
            
    except Exception as e:
        print(f"❌ 生成答案时出错: {e}")
        return False

if __name__ == "__main__":
    success = test_ollama()
    sys.exit(0 if success else 1)