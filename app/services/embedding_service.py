from app.config.settings import settings
import numpy as np
from typing import List
import logging
import os
import shutil

logger = logging.getLogger(__name__)

# 尝试导入sentence-transformers，失败时使用简单版本
try:
    from sentence_transformers import SentenceTransformer
    SENTENCE_TRANSFORMERS_AVAILABLE = True
except ImportError:
    SENTENCE_TRANSFORMERS_AVAILABLE = False
    logger.warning("sentence-transformers 不可用，将使用简单嵌入服务")

# 导入简单嵌入服务作为备选
from app.services.simple_embedding_service import simple_embedding_service

class EmbeddingService:
    def __init__(self):
        self.model = None
        self.use_simple = False
        self._load_model_with_fallback()
    
    def _load_model_with_fallback(self):
        """加载嵌入模型，支持多种回退方案"""
        # 如果sentence-transformers不可用，直接使用简单版本
        if not SENTENCE_TRANSFORMERS_AVAILABLE:
            logger.warning("sentence-transformers 不可用，使用简单嵌入服务")
            self.use_simple = True
            return
        
        # 尝试加载指定模型
        if self._try_load_model(settings.embedding_model):
            return
        
        # 如果指定模型失败，尝试其他备选模型
        backup_models = [
            "paraphrase-albert-small-v2",
            "all-distilroberta-v1", 
            "multi-qa-MiniLM-L6-cos-v1"
        ]
        
        for model_name in backup_models:
            if model_name != settings.embedding_model:  # 跳过已经尝试的模型
                logger.info(f"尝试备选模型: {model_name}")
                if self._try_load_model(model_name):
                    # 更新设置以使用成功的模型
                    import app.config.settings as settings_module
                    settings_module.settings.embedding_model = model_name
                    logger.info(f"已切换到备选模型: {model_name}")
                    return
        
        # 所有模型都失败，使用简单版本
        logger.error("所有嵌入模型加载失败，使用简单嵌入服务")
        self.use_simple = True
    
    def _try_load_model(self, model_name: str) -> bool:
        """尝试加载特定模型"""
        max_retries = 2
        for attempt in range(max_retries):
            try:
                logger.info(f"尝试加载嵌入模型: {model_name} (尝试 {attempt + 1}/{max_retries})")
                
                # 清除可能损坏的缓存
                if attempt > 0:
                    self._clear_model_cache()
                
                self.model = SentenceTransformer(model_name)
                logger.info(f"嵌入模型 {model_name} 加载成功")
                return True
                
            except Exception as e:
                logger.error(f"加载嵌入模型 {model_name} 失败 (尝试 {attempt + 1}): {e}")
                
                if attempt == max_retries - 1:
                    return False
    
    def _clear_model_cache(self):
        """清除模型缓存"""
        try:
            cache_paths = [
                os.path.expanduser('~/.cache/torch/sentence_transformers'),
                os.path.expanduser('~/.cache/huggingface/hub'),
                os.path.expanduser('~/.cache/torch/transformers'),
            ]
            
            for cache_path in cache_paths:
                if os.path.exists(cache_path):
                    shutil.rmtree(cache_path, ignore_errors=True)
                    logger.info(f"已清除缓存: {cache_path}")
        except Exception as e:
            logger.warning(f"清除缓存时出错: {e}")
    
    def get_embedding(self, text: str) -> List[float]:
        """获取文本的向量嵌入"""
        if self.use_simple or self.model is None:
            return simple_embedding_service.get_embedding(text)
        else:
            try:
                embedding = self.model.encode(text)
                embedding = embedding / np.linalg.norm(embedding)
                return embedding.tolist()
            except Exception as e:
                logger.error(f"sentence-transformers 嵌入失败，回退到简单版本: {e}")
                return simple_embedding_service.get_embedding(text)
    
    def get_embeddings_batch(self, texts: List[str]) -> List[List[float]]:
        if self.use_simple or self.model is None:
            return simple_embedding_service.get_embeddings_batch(texts)
        else:
            try:
                embeddings = self.model.encode(texts)
                # 修复：embeddings 已经是列表，不需要调用 tolist()
                normalized_embeddings = []
                for emb in embeddings:
                    normalized_emb = emb / np.linalg.norm(emb)
                    normalized_embeddings.append(normalized_emb.tolist())
                return normalized_embeddings
            except Exception as e:
                logger.error(f"sentence-transformers 批量嵌入失败，回退到简单版本: {e}")
                return simple_embedding_service.get_embeddings_batch(texts)

# 临时解决方案：强制使用简单嵌入服务
embedding_service = EmbeddingService()

# from app.services.simple_embedding_service import simple_embedding_service
# embedding_service = simple_embedding_service
# logger.warning("使用简单嵌入服务（临时解决方案）")