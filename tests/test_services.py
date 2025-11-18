import pytest
import numpy as np
from app.services.embedding_service import embedding_service
from app.services.llm_service import llm_service
from app.models.document_models import Document

class TestEmbeddingService:
    """嵌入服务测试"""
    
    def test_embedding_creation(self):
        """测试向量嵌入生成"""
        text = "这是一个测试句子"
        embedding = embedding_service.get_embedding(text)
        
        assert isinstance(embedding, list)
        assert len(embedding) == 384  # 模型维度
        assert all(isinstance(x, float) for x in embedding)
    
    def test_empty_text_embedding(self):
        """测试空文本的向量嵌入"""
        embedding = embedding_service.get_embedding("")
        assert isinstance(embedding, list)
        assert len(embedding) == 384
    
    def test_batch_embeddings(self):
        """测试批量向量嵌入生成"""
        texts = ["第一个句子", "第二个句子", "第三个句子"]
        embeddings = embedding_service.get_embeddings_batch(texts)
        
        assert isinstance(embeddings, list)
        assert len(embeddings) == len(texts)
        assert all(len(emb) == 384 for emb in embeddings)

class TestLLMService:
    """LLM服务测试"""
    
    def test_prompt_building(self):
        """测试提示词构建"""
        question = "测试问题"
        documents = [
            Document(
                _id="1",
                content="这是第一个文档内容",
                metadata={"source": "test"}
            ),
            Document(
                _id="2", 
                content="这是第二个文档内容",
                metadata={"source": "test"}
            )
        ]
        
        # 测试上下文构建
        context = llm_service._build_context(documents)
        assert "文档 1:" in context
        assert "文档 2:" in context
        assert documents[0].content in context
        
        # 测试提示词构建
        prompt = llm_service._build_prompt(question, context)
        assert question in prompt
        assert context in prompt
        assert "基于以下上下文信息" in prompt
    
    def test_answer_generation(self):
        """测试答案生成（需要Groq API可用）"""
        question = "请简单介绍一下你自己"
        documents = [
            Document(
                _id="1",
                content="这是一个测试文档，用于验证LLM服务功能",
                metadata={"source": "test"}
            )
        ]
        
        try:
            answer = llm_service.generate_answer(question, documents)
            assert isinstance(answer, str)
            assert len(answer) > 0
        except Exception as e:
            # 如果API调用失败，跳过测试
            pytest.skip(f"Groq API不可用: {e}")