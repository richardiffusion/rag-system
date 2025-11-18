from fastapi import APIRouter, HTTPException
from app.models.document_models import QueryRequest, QueryResponse, SearchResult, Document
from app.services.embedding_service import embedding_service
from app.services.vector_store import vector_store
from app.services.llm_service import llm_service
import logging
import time

logger = logging.getLogger(__name__)

router = APIRouter()

@router.post("/query/", response_model=QueryResponse)
async def query_knowledge_base(request: QueryRequest):
    """
    核心问答接口 - 基于知识库回答问题
    """
    try:
        start_time = time.time()
        
        # 输入验证
        if not request.question.strip():
            raise HTTPException(
                status_code=400, 
                detail="问题不能为空"
            )
        
        if request.top_k <= 0 or request.top_k > 20:
            raise HTTPException(
                status_code=400,
                detail="top_k 参数必须在 1-20 之间"
            )
        
        logger.info(f"处理问题: {request.question}")
        
        # 1. 将问题转换为向量
        query_embedding = embedding_service.get_embedding(request.question)
        
        # 2. 向量相似度搜索
        relevant_docs = vector_store.similarity_search(
            query_embedding, 
            top_k=request.top_k
        )
        
        logger.info(f"检索到 {len(relevant_docs)} 个相关文档")
        
        # 3. 如果没有找到相关文档
        if not relevant_docs:
            end_time = time.time()
            return QueryResponse(
                answer="抱歉，在知识库中没有找到与您问题相关的信息。",
                question=request.question,
                source_documents=[],
                confidence=0.0,
                processing_time=end_time - start_time,
                total_documents_retrieved=0
            )
        
        # 4. 使用LLM基于检索到的文档生成答案
        answer = llm_service.generate_answer(request.question, relevant_docs)
        
        # 5. 计算简单的置信度（基于检索到的文档数量）
        confidence = min(len(relevant_docs) / request.top_k, 1.0)
        
        end_time = time.time()
        
        # 转换文档格式为SearchResult
        search_results = []
        for i, doc in enumerate(relevant_docs):
            search_results.append(SearchResult(
                document_id=doc.id,
                content=doc.content,
                metadata=doc.metadata or {},
                score=1.0 - (i * 0.1),  # 简单模拟分数
                rank=i + 1
            ))
        
        return QueryResponse(
            answer=answer,
            question=request.question,
            source_documents=search_results,
            confidence=round(confidence, 2),
            processing_time=end_time - start_time,
            total_documents_retrieved=len(relevant_docs)
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"处理查询失败: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"处理查询时发生错误: {str(e)}"
        )