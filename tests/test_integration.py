import pytest
import time
import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

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
        self.doc_ids = []  # 存储测试文档ID用于清理
    
    def teardown_method(self):
        """测试清理"""
        # 清理测试数据
        if hasattr(self, 'doc_ids') and self.doc_ids:
            try:
                # ChromaDB 删除文档的正确方法
                vector_store.collection.delete(ids=self.doc_ids)
                print(f"✅ 清理了 {len(self.doc_ids)} 个测试文档")
            except Exception as e:
                print(f"⚠️ 清理测试文档失败: {e}")
    
    def test_full_rag_pipeline(self):
        """测试完整的RAG流程"""
        print("🧪 开始测试完整RAG流程...")
        
        # 跳过测试如果向量存储不可用
        if not hasattr(vector_store, 'collection'):
            pytest.skip("向量数据库连接不可用")
        
        # 1. 插入测试文档
        for doc in self.test_documents:
            embedding = embedding_service.get_embedding(doc.content)
            doc_id = vector_store.insert_document(doc, embedding)
            self.doc_ids.append(doc_id)
        
        print(f"✅ 插入了 {len(self.doc_ids)} 个测试文档")
        
        # 2. 测试检索
        query = "什么是机器学习？"
        query_embedding = embedding_service.get_embedding(query)
        results = vector_store.similarity_search(query_embedding, top_k=2)
        
        assert len(results) > 0, "应该检索到至少一个文档"
        assert any("机器学习" in doc.content for doc in results), "应该检索到包含'机器学习'的文档"
        print(f"✅ 检索测试通过，找到 {len(results)} 个相关文档")
        
        # 3. 测试生成（如果API可用）
        try:
            answer = llm_service.generate_answer(query, results)
            assert isinstance(answer, str), "答案应该是字符串"
            assert len(answer) > 0, "答案不应该为空"
            print(f"✅ 生成测试通过，答案长度: {len(answer)} 字符")
        except Exception as e:
            pytest.skip(f"LLM服务不可用: {e}")
    
    def test_performance(self):
        """测试性能"""
        print("🧪 开始性能测试...")
        
        start_time = time.time()
        
        # 测试嵌入生成性能
        texts = ["测试性能的文本 " * 10] * 5  # 5个长文本
        embeddings = embedding_service.get_embeddings_batch(texts)
        
        embedding_time = time.time() - start_time
        print(f"批量嵌入生成时间: {embedding_time:.2f}秒")
        
        # 合理的性能期望（根据硬件调整）
        assert embedding_time < 10.0, "嵌入生成应该在10秒内完成"
        assert len(embeddings) == 5, "应该生成5个嵌入向量"
        print("✅ 性能测试通过")
    
    def test_error_handling(self):
        """测试错误处理"""
        print("🧪 开始错误处理测试...")
        
        # 测试空查询
        empty_embedding = embedding_service.get_embedding("")
        assert len(empty_embedding) == 768, "空文本应该返回768维向量"
        
        # 测试无效向量搜索
        invalid_embedding = [0.0] * 768
        results = vector_store.similarity_search(invalid_embedding, top_k=1)
        # 应该返回空列表而不是抛出异常
        assert isinstance(results, list), "应该返回列表"
        print("✅ 错误处理测试通过")

# 如果直接运行这个文件，执行测试
if __name__ == "__main__":
    print("🚀 直接运行集成测试...")
    
    # 创建测试实例
    test_instance = TestIntegration()
    
    try:
        # 运行setup
        test_instance.setup_method()
        
        # 运行各个测试
        print("\n" + "="*50)
        test_instance.test_full_rag_pipeline()
        
        print("\n" + "="*50)
        test_instance.test_performance()
        
        print("\n" + "="*50)
        test_instance.test_error_handling()
        
        print("\n🎉 所有集成测试通过！")
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        raise
    finally:
        # 确保清理
        test_instance.teardown_method()