import chromadb
from app.config.settings import settings
from app.models.document_models import Document, DocumentCreate
from typing import List, Optional
import logging
import uuid

logger = logging.getLogger(__name__)

class ChromaVectorStore:
    def __init__(self):
        self.client = None
        self.collection = None
        self._setup_client()
    
    def _setup_client(self):
        """设置ChromaDB客户端和集合"""
        try:
            # 创建持久化客户端
            self.client = chromadb.PersistentClient(path=settings.chroma_db_path)
            logger.info(f"ChromaDB客户端初始化成功，存储路径: {settings.chroma_db_path}")
            
            # 获取或创建集合
            try:
                self.collection = self.client.get_collection("documents")
                logger.info("找到现有的文档集合")
            except Exception:
                self.collection = self.client.create_collection(
                    name="documents",
                    metadata={"description": "文档向量存储"}
                )
                logger.info("创建新的文档集合")
                
        except Exception as e:
            logger.error(f"初始化ChromaDB失败: {e}")
            raise
    
    def insert_document(self, document: DocumentCreate, embedding: List[float]) -> str:
        """插入文档和向量到ChromaDB"""
        try:
            doc_id = str(uuid.uuid4())
            
            self.collection.add(
                ids=[doc_id],
                embeddings=[embedding],
                documents=[document.content],
                metadatas=[document.metadata]
            )
            
            logger.debug(f"文档插入成功: {doc_id}")
            return doc_id
            
        except Exception as e:
            logger.error(f"插入文档失败: {e}")
            raise
    
    def similarity_search(self, query_embedding: List[float], top_k: int = 5) -> List[Document]:
        """向量相似度搜索"""
        try:
            # 确保向量维度正确
            if len(query_embedding) != settings.vector_dimension:
                logger.warning(f"查询向量维度不匹配: 期望{settings.vector_dimension}, 实际{len(query_embedding)}")
                # 调整维度
                if len(query_embedding) > settings.vector_dimension:
                    query_embedding = query_embedding[:settings.vector_dimension]
                else:
                    query_embedding = query_embedding + [0.0] * (settings.vector_dimension - len(query_embedding))
            
            # 执行搜索
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=top_k,
                include=["documents", "metadatas", "distances"]
            )
            
            documents = []
            if results['ids'] and len(results['ids'][0]) > 0:
                for i in range(len(results['ids'][0])):
                    doc_id = results['ids'][0][i]
                    content = results['documents'][0][i]
                    metadata = results['metadatas'][0][i] if results['metadatas'] else {}
                    distance = results['distances'][0][i] if results['distances'] else 0.0
                    
                    # 将距离转换为相似度分数 (1 - 标准化距离)
                    score = 1.0 - (distance / 2.0)  # 假设最大距离为2.0
                    
                    doc = Document(
                        id=doc_id,
                        content=content,
                        metadata=metadata,
                        embedding=None  # 不返回嵌入向量以节省带宽
                    )
                    documents.append(doc)
                    
                    logger.debug(f"检索到文档: {doc_id}, 分数: {score:.4f}")
            
            logger.info(f"相似度搜索完成，找到 {len(documents)} 个文档")
            return documents
            
        except Exception as e:
            logger.error(f"相似度搜索失败: {e}")
            return []
    
    def get_document_count(self) -> int:
        """获取文档数量"""
        try:
            # ChromaDB没有直接的count方法，我们可以通过查询空字符串来获取数量
            results = self.collection.get()
            return len(results['ids']) if results['ids'] else 0
        except Exception as e:
            logger.error(f"获取文档数量失败: {e}")
            return 0
    
    def get_all_documents(self, limit: int = 10) -> List[Document]:
        """获取所有文档（用于调试）"""
        try:
            results = self.collection.get(limit=limit)
            documents = []
            
            if results['ids']:
                for i in range(len(results['ids'])):
                    doc = Document(
                        id=results['ids'][i],
                        content=results['documents'][i],
                        metadata=results['metadatas'][i] if results['metadatas'] else {},
                        embedding=None
                    )
                    documents.append(doc)
            
            return documents
        except Exception as e:
            logger.error(f"获取所有文档失败: {e}")
            return []

# 全局ChromaDB向量存储实例
chroma_vector_store = ChromaVectorStore()