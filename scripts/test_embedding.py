#!/usr/bin/env python3
"""
测试嵌入模型是否正常工作的脚本
"""

import sys
import os
import logging

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.config.settings import settings
import numpy as np

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_embedding_model():
    """测试当前系统使用的嵌入模型"""
    print("测试当前系统嵌入服务...")
    
    try:
        # 使用系统当前的嵌入服务
        from app.services.embedding_service import embedding_service
        
        print(f"当前使用的嵌入服务: {'简单嵌入服务' if hasattr(embedding_service, 'use_simple') and embedding_service.use_simple else '专业嵌入模型'}")
        
        # 测试编码
        test_texts = [
            "这是一个测试句子",
            "人工智能是计算机科学的一个分支",
            "机器学习使计算机能够自主学习"
        ]
        
        print("测试文本编码...")
        embeddings = []
        for text in test_texts:
            embedding = embedding_service.get_embedding(text)
            embeddings.append(embedding)
            print(f"  '{text}' -> 维度: {len(embedding)}")
        
        print(f"✅ 编码成功，生成 {len(embeddings)} 个嵌入向量")
        print(f"向量维度: {len(embeddings[0])}")
        print(f"向量示例: {embeddings[0][:5]}...")  # 显示前5个值
        
        # 测试相似度
        similarity = np.dot(embeddings[0], embeddings[1]) / (np.linalg.norm(embeddings[0]) * np.linalg.norm(embeddings[1]))
        print(f"相似度测试: {similarity:.4f}")
        
        return True
        
    except Exception as e:
        print(f"❌ 嵌入服务测试失败: {e}")
        return False

def test_professional_model(model_name="paraphrase-albert-small-v2"):
    """测试专业嵌入模型"""
    print(f"\n测试专业嵌入模型: {model_name}")
    
    try:
        from sentence_transformers import SentenceTransformer
        
        # 尝试加载模型
        print("正在加载专业模型...")
        model = SentenceTransformer(model_name)
        print("✅ 专业模型加载成功")
        
        # 测试编码
        test_texts = [
            "这是一个测试句子",
            "人工智能是计算机科学的一个分支"
        ]
        
        embeddings = model.encode(test_texts)
        
        print(f"✅ 专业模型编码成功，维度: {embeddings[0].shape}")
        
        # 测试相似度
        similarity = np.dot(embeddings[0], embeddings[1]) / (np.linalg.norm(embeddings[0]) * np.linalg.norm(embeddings[1]))
        print(f"专业模型相似度: {similarity:.4f}")
        
        return True
        
    except Exception as e:
        print(f"❌ 专业模型测试失败: {e}")
        return False

if __name__ == "__main__":
    print("🧪 嵌入服务测试")
    print("=" * 50)
    
    # 测试当前系统使用的嵌入服务
    success = test_embedding_model()
    
    # 测试专业模型（可选）
    if success:
        print("\n" + "=" * 50)
        test_professional_model(settings.embedding_model)
    
    sys.exit(0 if success else 1)