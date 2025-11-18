from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # ChromaDB配置
    chroma_db_path: str = "./chroma_db"  # ChromaDB存储路径
    
    # Ollama配置
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "llama3.1"
    
    # 嵌入模型配置
    embedding_model: str = "paraphrase-albert-small-v2"
    
    # 应用配置
    max_documents: int = 5
    vector_dimension: int = 768
    
    # 生成参数
    max_tokens: int = 1024
    temperature: float = 0.1
    top_p: float = 0.9
    
    class Config:
        env_file = ".env"

settings = Settings()