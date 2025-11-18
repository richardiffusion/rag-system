import ollama
from app.config.settings import settings
from typing import List
from app.models.document_models import Document
import logging
import time
import requests
import json

logger = logging.getLogger(__name__)

class OllamaService:
    def __init__(self):
        self.client = None
        self._setup_client()
    
    def _setup_client(self):
        """设置Ollama客户端"""
        try:
            # 首先检查Ollama服务是否可用
            if not self._check_ollama_health():
                logger.error("Ollama服务健康检查失败")
                return
            
            # 使用自定义基础URL（如果提供）
            if settings.ollama_base_url:
                self.client = ollama.Client(host=settings.ollama_base_url)
            else:
                self.client = ollama.Client()
                
            logger.info(f"Ollama客户端初始化成功，使用模型: {settings.ollama_model}")
            
            # 直接测试模型是否可用，而不是验证列表
            if not self._test_model_simple():
                logger.error(f"模型 {settings.ollama_model} 测试失败")
                self.client = None
            else:
                logger.info(f"模型 {settings.ollama_model} 测试成功")
                
        except Exception as e:
            logger.error(f"初始化Ollama客户端失败: {e}")
            self.client = None
    
    def _check_ollama_health(self):
        """检查Ollama服务健康状态"""
        try:
            response = requests.get(f"{settings.ollama_base_url}/api/tags", timeout=10)
            if response.status_code == 200:
                logger.info("Ollama服务连接成功")
                return True
            else:
                logger.error(f"Ollama服务返回状态码: {response.status_code}")
                return False
        except requests.exceptions.ConnectionError:
            logger.error(f"无法连接到Ollama服务: {settings.ollama_base_url}")
            return False
        except Exception as e:
            logger.error(f"检查Ollama服务时出错: {e}")
            return False
    
    def _test_model_simple(self):
        """简单测试模型是否可用"""
        try:
            # 使用更简单的测试方法
            test_response = requests.post(
                f"{settings.ollama_base_url}/api/generate",
                json={
                    "model": settings.ollama_model,
                    "prompt": "Say OK",
                    "stream": False
                },
                timeout=30
            )
            
            if test_response.status_code == 200:
                return True
            else:
                logger.error(f"模型测试返回状态码: {test_response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"模型测试失败: {e}")
            return False
    
    def is_available(self):
        """检查服务是否可用"""
        return self.client is not None
    
    def generate_answer(self, question: str, context_docs: List[Document]) -> str:
        """基于检索到的文档生成答案"""
        
        if not self.is_available():
            return "Ollama服务不可用，请确保Ollama服务正在运行且模型已加载。"
        
        # 构建上下文
        context = self._build_context(context_docs)
        
        # 构建提示词
        prompt = self._build_prompt(question, context)
        
        try:
            start_time = time.time()
            
            # 调用Ollama生成回答
            response = self.client.generate(
                model=settings.ollama_model,
                prompt=prompt,
                options={
                    "temperature": settings.temperature,
                    "top_p": settings.top_p,
                    "num_predict": settings.max_tokens,
                }
            )
            
            answer = response['response'].strip()
            
            end_time = time.time()
            logger.info(f"Ollama生成完成，耗时: {end_time - start_time:.2f}秒")
            
            return answer
            
        except Exception as e:
            logger.error(f"Ollama生成答案失败: {e}")
            # 尝试使用直接HTTP请求作为备选
            return self._generate_with_http_fallback(question, context_docs)
    
    def _generate_with_http_fallback(self, question: str, context_docs: List[Document]) -> str:
        """使用直接HTTP请求作为备选生成方法"""
        try:
            context = self._build_context(context_docs)
            prompt = self._build_prompt(question, context)
            
            response = requests.post(
                f"{settings.ollama_base_url}/api/generate",
                json={
                    "model": settings.ollama_model,
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "temperature": settings.temperature,
                        "top_p": settings.top_p,
                        "num_predict": settings.max_tokens,
                    }
                },
                timeout=60
            )
            
            if response.status_code == 200:
                result = response.json()
                return result['response'].strip()
            else:
                return f"HTTP备选方法也失败，状态码: {response.status_code}"
                
        except Exception as e:
            return f"所有生成方法都失败: {str(e)}"
    
    def _build_context(self, documents: List[Document]) -> str:
        """构建上下文字符串"""
        if not documents:
            return "没有找到相关文档。"
            
        context_parts = []
        for i, doc in enumerate(documents, 1):
            context_parts.append(f"文档 {i}:\n{doc.content}")
        
        return "\n\n".join(context_parts)
    
    def _build_prompt(self, question: str, context: str) -> str:
        """构建Ollama的提示词"""
        system_prompt = """你是一个专业的AI助手，基于提供的上下文信息回答问题。
请严格基于上下文内容回答，不要编造信息。
如果上下文没有提供足够的信息，请如实说明你不知道。"""

        prompt = f"""系统提示: {system_prompt}

上下文信息:
{context}

用户问题: {question}

请基于上述上下文信息回答用户问题。如果上下文信息不足以回答问题，请说明这一点。"""
        
        return prompt

# 全局Ollama服务实例
ollama_service = OllamaService()