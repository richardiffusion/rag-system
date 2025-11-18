
# RAG系统 - 检索增强生成系统

基于FastAPI + MongoDB Atlas + Llama-3构建的智能问答系统。

## 功能特性

- 📚 文档向量化存储和管理
- 🔍 语义相似度检索
- 🤖 基于上下文的智能问答
- 🐳 Docker容器化部署
- 📊 生产级API设计

## 快速开始

### 环境要求

- Python 3.9+
- MongoDB Atlas账户
- Groq Cloud API密钥

### 安装步骤

1. 克隆项目并安装依赖：
```bash
git clone <repository-url>
cd rag-system
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
配置环境变量：

bash
cp .env.example .env
# 编辑 .env 文件，填入您的MongoDB和Groq API配置
初始化数据库：

bash
python scripts/init_database.py
加载示例文档：

bash
# 将您的文档文件放入 data/raw/ 目录
python scripts/load_documents.py
启动服务：

bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
API使用
添加文档
bash
curl -X POST "http://localhost:8000/api/v1/documents/" \
  -H "Content-Type: application/json" \
  -d '{
    "content": "您的文档内容...",
    "metadata": {"source": "manual"}
  }'
提问
bash
curl -X POST "http://localhost:8000/api/v1/query/" \
  -H "Content-Type: application/json" \
  -d '{
    "question": "您的问题是什么？",
    "top_k": 5
  }'
Docker部署
bash
# 构建镜像
docker build -t rag-system .

# 运行容器
docker run -p 8000:8000 --env-file .env rag-system
API文档
启动服务后访问：http://localhost:8000/docs

项目结构
参见项目根目录的详细结构说明。

text

这些文件完成了整个RAG系统的主要功能。现在您可以：

1. 按照README的步骤配置环境
2. 运行数据库初始化脚本
3. 加载您的文档数据
4. 启动服务并测试API

系统现在已经具备了完整的文档管理、向量检索和智能问答功能。