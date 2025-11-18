import numpy as np
from typing import List
import logging
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import hashlib
import re

logger = logging.getLogger(__name__)

class SimpleEmbeddingService:
    """
    简单的嵌入服务，作为sentence-transformers的备选方案
    使用TF-IDF和简单的文本哈希来生成向量
    """
    
    def __init__(self):
        self.vectorizer = TfidfVectorizer(max_features=768, stop_words=None)
        self.is_fitted = False
        self.vocabulary = None
        logger.info("简单嵌入服务初始化完成")
    
    def get_embedding(self, text: str) -> List[float]:
        """获取文本的简单向量表示"""
        if not text.strip():
            return [0.0] * 768
        
        try:
            # 方法1: 使用TF-IDF（如果已经拟合过）
            if self.is_fitted:
                vector = self.vectorizer.transform([text]).toarray()[0]
                if len(vector) < 768:
                    # 填充到768维
                    vector = np.pad(vector, (0, 768 - len(vector)))
                elif len(vector) > 768:
                    # 截断到768维
                    vector = vector[:768]
                return vector.tolist()
            else:
                # 方法2: 使用文本哈希作为简单向量
                return self._text_to_hash_vector(text)
                
        except Exception as e:
            logger.error(f"简单嵌入生成失败: {e}")
            return self._text_to_hash_vector(text)
    
    def _text_to_hash_vector(self, text: str) -> List[float]:
        """将文本转换为基于哈希的向量"""
        # 清理文本
        cleaned_text = re.sub(r'\s+', ' ', text.strip())
        
        # 使用SHA256哈希生成确定性向量
        hash_obj = hashlib.sha256(cleaned_text.encode('utf-8'))
        hash_hex = hash_obj.hexdigest()
        
        # 将哈希转换为768维向量
        vector = []
        for i in range(0, min(len(hash_hex), 768*6), 6):
            chunk = hash_hex[i:i+6]
            if len(chunk) == 6:
                # 将16进制转换为0-1之间的浮点数
                value = int(chunk, 16) / 0xFFFFFF
                vector.append(value)
        
        # 如果向量长度不足，用0填充
        while len(vector) < 768:
            vector.append(0.0)
        
        return vector[:768]
    
    def get_embeddings_batch(self, texts: List[str]) -> List[List[float]]:
        """批量获取向量嵌入"""
        return [self.get_embedding(text) for text in texts]
    
    def fit_vectorizer(self, texts: List[str]):
        """使用文本列表拟合TF-IDF向量化器"""
        try:
            self.vectorizer.fit(texts)
            self.is_fitted = True
            logger.info(f"TF-IDF向量化器拟合完成，词汇表大小: {len(self.vectorizer.vocabulary_)}")
        except Exception as e:
            logger.error(f"拟合TF-IDF向量化器失败: {e}")

# 全局简单嵌入服务实例
simple_embedding_service = SimpleEmbeddingService()