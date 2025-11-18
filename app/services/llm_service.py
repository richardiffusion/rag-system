from app.config.settings import settings
from typing import List
from app.models.document_models import Document
import logging

logger = logging.getLogger(__name__)

# 导入HTTP版本的Ollama服务
from app.services.ollama_http_service import ollama_http_service

class LLMService:
    def __init__(self):
        # 使用HTTP版本的Ollama服务
        self.llm_backend = ollama_http_service
    
    def is_available(self):
        """检查LLM服务是否可用"""
        return True  # HTTP服务总是尝试可用
    
    def generate_answer(self, question: str, context_docs: List[Document]) -> str:
        """基于检索到的文档生成答案"""
        return self.llm_backend.generate_answer(question, context_docs)
    
    def _build_context(self, documents: List[Document]) -> str:
        """构建上下文字符串"""
        return self.llm_backend._build_context(documents)
    
    def _build_prompt(self, question: str, context: str) -> str:
        """构建提示词"""
        return self.llm_backend._build_prompt(question, context)

# 全局LLM服务实例
llm_service = LLMService()