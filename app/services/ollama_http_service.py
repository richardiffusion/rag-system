import requests
from app.config.settings import settings
from typing import List
from app.models.document_models import Document
import logging
import time
import json

logger = logging.getLogger(__name__)

class OllamaHTTPService:
    def __init__(self):
        self.base_url = settings.ollama_base_url
        self.model = settings.ollama_model
        self.is_connected = self._test_connection()
    
    def _test_connection(self):
        """测试连接"""
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=10)
            if response.status_code == 200:
                logger.info("Ollama HTTP服务连接成功")
                # 检查模型是否存在（支持短名称匹配）
                models = response.json().get('models', [])
                model_names = [model['name'] for model in models]
                
                # 检查完整匹配或前缀匹配
                model_found = self.model in model_names
                if not model_found:
                    # 检查是否可以使用短名称（去掉:latest后缀）
                    short_model = self.model.split(':')[0]  # 获取主名称
                    for model_name in model_names:
                        if model_name.startswith(short_model + ':'):
                            logger.info(f"找到匹配的模型: {model_name} (使用短名称 {self.model})")
                            model_found = True
                            break
                
                if not model_found:
                    logger.warning(f"模型 {self.model} 不在可用模型列表中: {model_names}")
                    logger.info("但将继续尝试使用该模型...")
                return True
            else:
                logger.error(f"连接测试失败: {response.status_code}")
                return False
        except Exception as e:
            logger.error(f"连接测试异常: {e}")
            return False
    
    def is_available(self):
        """服务是否可用"""
        return self.is_connected
    
    def generate_answer(self, question: str, context_docs: List[Document]) -> str:
        """基于检索到的文档生成答案"""
        
        if not self.is_available():
            return "Ollama服务不可用，请确保Ollama服务正在运行。"
        
        # 构建上下文
        context = self._build_context(context_docs)
        
        # 构建提示词
        prompt = self._build_prompt(question, context)
        
        try:
            start_time = time.time()
            
            payload = {
                "model": self.model,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": settings.temperature,
                    "top_p": settings.top_p,
                    "num_predict": settings.max_tokens,
                }
            }
            
            logger.info(f"发送请求到Ollama，模型: {self.model}")
            response = requests.post(
                f"{self.base_url}/api/generate",
                json=payload,
                timeout=120  # 增加超时时间
            )
            
            if response.status_code == 200:
                result = response.json()
                answer = result['response'].strip()
                
                end_time = time.time()
                logger.info(f"Ollama生成完成，耗时: {end_time - start_time:.2f}秒")
                
                return answer
            else:
                logger.error(f"生成失败，状态码: {response.status_code}, 响应: {response.text}")
                return f"生成失败，HTTP状态码: {response.status_code}, 错误: {response.text}"
            
        except requests.exceptions.Timeout:
            logger.error("请求超时")
            return "请求超时，请稍后重试或检查模型是否正在加载。"
        except Exception as e:
            logger.error(f"生成答案失败: {e}")
            return f"生成答案时出现错误: {str(e)}"
    
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

# 全局HTTP Ollama服务实例
ollama_http_service = OllamaHTTPService()