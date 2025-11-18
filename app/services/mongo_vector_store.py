import pymongo
from pymongo import MongoClient
from app.config.settings import settings
from app.models.document_models import Document, DocumentCreate
from typing import List, Optional
import logging


logger = logging.getLogger(__name__)

class VectorStore:
    def __init__(self):
        self.client = None
        self.db = None
        self.collection = None
        self._connect()
    
    def _connect(self):
        """连接到MongoDB Atlas"""
        try:
            self.client = MongoClient(settings.mongodb_uri)
            self.db = self.client[settings.database_name]
            self.collection = self.db["documents"]
            logger.info("成功连接到MongoDB")
        except Exception as e:
            logger.error(f"连接MongoDB失败: {e}")
            raise
    
    def create_vector_index(self):
        """创建向量搜索索引"""
        index_definition = {
            "fields": [
                {
                    "type": "vector",
                    "path": "embedding",
                    "numDimensions": settings.vector_dimension,
                    "similarity": "cosine"
                }
            ]
        }
        
        try:
            self.db.command({
                "createIndexes": "documents",
                "indexes": [{
                    "name": "vector_index",
                    "key": {"embedding": "vector"},
                    "vectorOptions": index_definition
                }]
            })
            logger.info("向量索引创建成功")
        except Exception as e:
            logger.warning(f"向量索引可能已存在: {e}")
    
    def insert_document(self, document: DocumentCreate, embedding: List[float]) -> str:
        """插入文档和向量"""
        doc_data = {
            "content": document.content,
            "metadata": document.metadata or {},
            "embedding": embedding
        }
        
        result = self.collection.insert_one(doc_data)
        return str(result.inserted_id)
    
    def similarity_search(self, query_embedding: List[float], top_k: int = 5) -> List[Document]:
        """向量相似度搜索"""
        pipeline = [
            {
                "$vectorSearch": {
                    "index": "vector_index",
                    "path": "embedding",
                    "queryVector": query_embedding,
                    "numCandidates": top_k * 10,
                    "limit": top_k
                }
            },
            {
                "$project": {
                    "_id": 1,
                    "content": 1,
                    "metadata": 1,
                    "embedding": 1,
                    "score": {"$meta": "vectorSearchScore"}
                }
            }
        ]
        
        results = list(self.collection.aggregate(pipeline))
        documents = []
        
        for result in results:
            doc = Document(
                _id=str(result["_id"]),
                content=result["content"],
                metadata=result.get("metadata", {}),
                embedding=result.get("embedding")
            )
            documents.append(doc)
        
        return documents

# 全局向量存储实例
vector_store = VectorStore()