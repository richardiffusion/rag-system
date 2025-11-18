#!/usr/bin/env python3
"""
测试嵌入模型是否正常工作的脚本
"""

import sys
import os
import logging

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sentence_transformers import SentenceTransformer
import numpy as np

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_embedding_model(model_name="all-MiniLM-L6-v2"):
    """测试嵌入模型"""
    print(f"测试嵌入模型: {model_name}")
    
    try:
        # 尝试加载模型
        print("正在加载模型...")
        model = SentenceTransformer(model_name)
        print("✅ 模型加载成功")
        
        # 测试编码
        test_texts = [
            "这是一个测试句子",
            "人工智能是计算机科学的一个分支",
            "机器学习使计算机能够自主学习"
        ]
        
        print("测试文本编码...")
        embeddings = model.encode(test_texts)
        
        print(f"✅ 编码成功，生成 {len(embeddings)} 个嵌入向量")
        print(f"每个向量的维度: {embeddings[0].shape}")
        print(f"向量示例: {embeddings[0][:5]}...")  # 显示前5个值
        
        # 测试相似度
        similarity = np.dot(embeddings[0], embeddings[1]) / (np.linalg.norm(embeddings[0]) * np.linalg.norm(embeddings[1]))
        print(f"相似度测试: {similarity:.4f}")
        
        return True
        
    except Exception as e:
        print(f"❌ 模型测试失败: {e}")
        return False

def list_available_models():
    """列出可用的嵌入模型"""
    print("可用的嵌入模型:")
    models = [
        "all-MiniLM-L6-v2",
        "paraphrase-albert-small-v2", 
        "all-distilroberta-v1",
        "multi-qa-MiniLM-L6-cos-v1",
        "all-MiniLM-L12-v2"
    ]
    
    for model in models:
        print(f"  - {model}")

if __name__ == "__main__":
    print("🧪 嵌入模型测试")
    list_available_models()
    print("-" * 50)
    
    # 测试默认模型
    success = test_embedding_model("all-MiniLM-L6-v2")
    
    if not success:
        print("\n尝试备用模型...")
        backup_models = [
            "paraphrase-albert-small-v2",
            "all-distilroberta-v1"
        ]
        
        for model in backup_models:
            print(f"\n尝试模型: {model}")
            if test_embedding_model(model):
                print(f"💡 建议在 .env 文件中使用: EMBEDDING_MODEL={model}")
                break
    
    sys.exit(0 if success else 1)