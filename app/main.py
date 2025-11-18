from fastapi import FastAPI
from app.routes import documents, query
import logging

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 创建FastAPI应用
app = FastAPI(
    title="RAG系统API",
    description="基于检索增强生成的智能问答系统",
    version="1.0.0"
)

# 启动时初始化（ChromaDB自动初始化，无需手动操作）
@app.on_event("startup")
async def startup_event():
    try:
        logger.info("应用启动完成，ChromaDB已就绪")
    except Exception as e:
        logger.error(f"启动时初始化失败: {e}")

# 健康检查端点
@app.get("/")
async def root():
    return {"message": "RAG系统API服务运行正常", "status": "healthy"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

# 注册路由
app.include_router(documents.router, prefix="/api/v1", tags=["文档管理"])
app.include_router(query.router, prefix="/api/v1", tags=["问答"])

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)