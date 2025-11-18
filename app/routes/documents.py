from fastapi import APIRouter, HTTPException, status
from app.models.document_models import Document, DocumentCreate
from app.services.vector_store import vector_store
from app.services.embedding_service import embedding_service
from typing import List
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

@router.post("/documents/", response_model=dict, status_code=status.HTTP_201_CREATED)
async def create_document(document: DocumentCreate):
    """
    添加新文档到知识库
    """
    try:
        # 生成文档的向量嵌入
        embedding = embedding_service.get_embedding(document.content)
        
        # 存储到向量数据库
        document_id = vector_store.insert_document(document, embedding)
        
        return {
            "message": "文档添加成功",
            "document_id": document_id,
            "content_length": len(document.content)
        }
    except Exception as e:
        logger.error(f"添加文档失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"文档添加失败: {str(e)}"
        )

@router.get("/documents/", response_model=List[Document])
async def list_documents(limit: int = 10, skip: int = 0):
    """
    获取文档列表（主要用于调试）
    """
    try:
        # 注意：这里只是简单查询，不涉及向量搜索
        cursor = vector_store.collection.find().skip(skip).limit(limit)
        documents = []
        
        for doc in cursor:
            documents.append(Document(
                _id=str(doc["_id"]),
                content=doc["content"],
                metadata=doc.get("metadata", {}),
                embedding=doc.get("embedding")
            ))
        
        return documents
    except Exception as e:
        logger.error(f"获取文档列表失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取文档列表失败: {str(e)}"
        )

@router.get("/documents/{document_id}", response_model=Document)
async def get_document(document_id: str):
    """
    根据ID获取特定文档
    """
    try:
        from bson import ObjectId
        doc = vector_store.collection.find_one({"_id": ObjectId(document_id)})
        
        if not doc:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="文档不存在"
            )
        
        return Document(
            _id=str(doc["_id"]),
            content=doc["content"],
            metadata=doc.get("metadata", {}),
            embedding=doc.get("embedding")
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取文档失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取文档失败: {str(e)}"
        )