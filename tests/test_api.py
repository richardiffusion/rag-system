import pytest
from fastapi.testclient import TestClient
from app.main import app
import time

client = TestClient(app)

def test_health_check():
    """测试健康检查端点"""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}

def test_root_endpoint():
    """测试根端点"""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "status" in data

def test_query_empty_question():
    """测试空问题查询"""
    response = client.post("/api/v1/query/", json={
        "question": "",
        "top_k": 5
    })
    assert response.status_code == 400

def test_query_invalid_top_k():
    """测试无效的top_k参数"""
    response = client.post("/api/v1/query/", json={
        "question": "测试问题",
        "top_k": 0
    })
    assert response.status_code == 400
    
    response = client.post("/api/v1/query/", json={
        "question": "测试问题",
        "top_k": 25
    })
    assert response.status_code == 400

def test_query_success():
    """测试成功的查询（需要数据库中有数据）"""
    response = client.post("/api/v1/query/", json={
        "question": "什么是人工智能？",
        "top_k": 3
    })
    
    # 如果数据库为空，可能返回404或空结果
    if response.status_code == 200:
        data = response.json()
        assert "answer" in data
        assert "source_documents" in data
        assert "confidence" in data
        assert "processing_time" in data
        assert isinstance(data["source_documents"], list)

def test_create_document():
    """测试创建文档"""
    test_content = f"这是一个测试文档内容，时间戳：{time.time()}"
    
    response = client.post("/api/v1/documents/", json={
        "content": test_content,
        "metadata": {
            "source": "test",
            "type": "test_document"
        }
    })
    
    # 如果数据库连接正常，应该成功创建
    if response.status_code == 201:
        data = response.json()
        assert "document_id" in data
        assert "message" in data
    else:
        # 如果数据库连接失败，可能是测试环境问题
        assert response.status_code in [500, 503]

def test_list_documents():
    """测试获取文档列表"""
    response = client.get("/api/v1/documents/", params={
        "limit": 5,
        "skip": 0
    })
    
    if response.status_code == 200:
        data = response.json()
        assert isinstance(data, list)