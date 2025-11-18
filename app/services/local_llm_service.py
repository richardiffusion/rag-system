import torch
from transformers import AutoTokenizer, AutoModelForCausalLM
from app.config.settings import settings
from typing import List
from app.models.document_models import Document
import logging
import time

logger = logging.getLogger(__name__)

class LocalLLMService:
    def __init__(self):
        self.tokenizer = None
        self.model = None
        self.device = None
        self._load_model()
    
    def _load_model(self):
        """加载本地Llama3.1模型"""
        try:
            logger.info(f"开始加载本地模型: {settings.local_model_path}")
            
            # 自动检测设备 (GPU/CPU)
            if torch.cuda.is_available():
                self.device = "cuda"
                logger.info("使用CUDA (GPU) 进行推理")
            else:
                self.device = "cpu" 
                logger.info("使用CPU进行推理")
            
            # 加载tokenizer
            self.tokenizer = AutoTokenizer.from_pretrained(
                settings.local_model_path,
                trust_remote_code=True
            )
            
            # 加载模型
            self.model = AutoModelForCausalLM.from_pretrained(
                settings.local_model_path,
                torch_dtype=torch.float16 if self.device == "cuda" else torch.float32,
                device_map="auto" if self.device == "cuda" else None,
                trust_remote_code=True,
                low_cpu_mem_usage=True
            )
            
            # 如果使用CPU，将模型移动到设备
            if self.device == "cpu":
                self.model = self.model.to(self.device)
            
            logger.info("本地Llama3.1模型加载成功")
            
        except Exception as e:
            logger.error(f"加载本地模型失败: {e}")
            raise
    
    def generate_answer(self, question: str, context_docs: List[Document]) -> str:
        """基于检索到的文档生成答案"""
        
        # 构建上下文
        context = self._build_context(context_docs)
        
        # 构建提示词
        prompt = self._build_prompt(question, context)
        
        try:
            start_time = time.time()
            
            # 编码输入
            inputs = self.tokenizer.encode(prompt, return_tensors="pt").to(self.device)
            
            # 生成参数
            generation_config = {
                "max_new_tokens": settings.max_new_tokens,
                "temperature": settings.temperature,
                "top_p": settings.top_p,
                "do_sample": True,
                "pad_token_id": self.tokenizer.eos_token_id,
                "eos_token_id": self.tokenizer.eos_token_id,
            }
            
            # 生成回答
            with torch.no_grad():
                outputs = self.model.generate(
                    inputs,
                    **generation_config
                )
            
            # 解码输出
            response = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
            
            # 提取生成的答案（去掉提示部分）
            answer = response[len(prompt):].strip()
            
            end_time = time.time()
            logger.info(f"本地模型推理完成，耗时: {end_time - start_time:.2f}秒")
            
            return answer
            
        except Exception as e:
            logger.error(f"本地模型生成答案失败: {e}")
            return f"抱歉，生成答案时出现错误: {str(e)}"
    
    def _build_context(self, documents: List[Document]) -> str:
        """构建上下文字符串"""
        context_parts = []
        for i, doc in enumerate(documents, 1):
            context_parts.append(f"文档 {i}:\n{doc.content}")
        
        return "\n\n".join(context_parts)
    
    def _build_prompt(self, question: str, context: str) -> str:
        """构建Llama3.1的提示词格式"""
        # Llama3.1的聊天格式
        system_message = """你是一个专业的AI助手，基于提供的上下文信息回答问题。
请严格基于上下文内容回答，不要编造信息。
如果上下文没有提供足够的信息，请如实说明你不知道。"""

        prompt = f"""<|start_header_id|>system<|end_header_id|>

{system_message}<|eot_id|>
<|start_header_id|>user<|end_header_id|>

基于以下上下文信息，请回答问题：

上下文：
{context}

问题：{question}<|eot_id|>
<|start_header_id|>assistant<|end_header_id|>

"""
        return prompt

# 全局本地LLM服务实例
local_llm_service = LocalLLMService()