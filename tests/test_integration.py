import pytest
import time
from app.services.vector_store import vector_store
from app.services.embedding_service import embedding_service
from app.services.llm_service import llm_service
from app.models.document_models import DocumentCreate

class TestIntegration:
    """集成测试"""
    
    def setup_method(self):
        """测试准备"""
        self.test_documents = [
            DocumentCreate(
                content="机器学习是人工智能的一个分支，专注于让计算机从数据中学习。",
                metadata={"topic": "AI", "type": "definition"}
            ),
            DocumentCreate(
                content="深度学习是机器学习的一个子领域，使用神经网络模拟人脑工作。",
                metadata={"topic": "AI", "type": "definition"} 
            ),
            DocumentCreate(
                content="自然语言处理是人工智能领域，专注于计算机与人类语言交互。",
                metadata={"topic": "NLP", "type": "definition"}
            )
        ]
    
    def test_full_rag_pipeline(self):
        """测试完整的RAG流程"""
        # 跳过测试如果数据库不可用
        if not vector_store.client:
            pytest.skip("MongoDB连接不可用")
        
        # 1. 插入测试文档
        doc_ids = []
        for doc in self.test_documents:
            embedding = embedding_service.get_embedding(doc.content)
            doc_id = vector_store.insert_document(doc, embedding)
            doc_ids.append(doc_id)
        
        try:
            # 2. 测试检索
            query = "什么是机器学习？"
            query_embedding = embedding_service.get_embedding(query)
            results = vector_store.similarity_search(query_embedding, top_k=2)
            
            assert len(results) > 0
            assert any("机器学习" in doc.content for doc in results)
            
            # 3. 测试生成（如果API可用）
            try:
                answer = llm_service.generate_answer(query, results)
                assert isinstance(answer, str)
                assert len(answer) > 0
            except Exception as e:
                pytest.skip(f"LLM服务不可用: {e}")
                
        finally:
            # 清理测试数据
            from bson import ObjectId
            for doc_id in doc_ids:
                vector_store.collection.delete_one({"_id": ObjectId(doc_id)})
    
    def test_performance(self):
        """测试性能"""
        start_time = time.time()
        
        # 测试嵌入生成性能
        texts = ["测试性能的文本 " * 10] * 5  # 5个长文本
        embeddings = embedding_service.get_embeddings_batch(texts)
        
        embedding_time = time.time() - start_time
        print(f"批量嵌入生成时间: {embedding_time:.2f}秒")
        
        # 合理的性能期望（根据硬件调整）
        assert embedding_time < 10.0  # 应该能在10秒内完成
    
    def test_error_handling(self):
        """测试错误处理"""
        # 测试空查询
        empty_embedding = embedding_service.get_embedding("")
        assert len(empty_embedding) == 384
        
        # 测试无效向量搜索
        invalid_embedding = [0.0] * 384
        results = vector_store.similarity_search(invalid_embedding, top_k=1)
        # 应该返回空列表而不是抛出异常
        assert isinstance(results, list)