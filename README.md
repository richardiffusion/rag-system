# 此为自用学习系统，此项目非稳定版本，慎用！


# RAG智能问答系统

基于检索增强生成技术的智能问答系统，能够理解用户问题、从私有知识库中检索相关信息，并基于检索到的内容生成准确答案。

## 🚀 功能特性

- **📚 智能检索**: 基于向量相似度从知识库中精准检索相关信息
- **🤖 本地模型**: 使用本地Llama3.1模型，无需云API，保护数据隐私
- **🔍 多格式支持**: 支持PDF、DOCX、TXT等多种文档格式
- **⚡ 高性能**: ChromaDB向量数据库，毫秒级检索速度
- **🛡️ 健壮性**: 多层错误处理和自动回退机制
- **📊 生产就绪**: 完整的RESTful API接口和监控工具

## 🛠️ 技术架构

### 核心技术栈
- **后端框架**: FastAPI (Python)
- **向量数据库**: ChromaDB
- **大语言模型**: Llama3.1 (通过Ollama)
- **嵌入模型**: paraphrase-albert-small-v2
- **文档处理**: PyPDF2, python-docx

### 系统架构
用户提问 → API接收 → 向量化查询 → 向量数据库检索 → 上下文构建 → LLM生成 → 返回答案


## 📥 安装部署

### 环境要求
- Python 3.9+
- 至少8GB内存（运行Llama3.1模型）
- 网络连接（用于下载嵌入模型）

### 1. 克隆项目
```bash
git clone <www.github.com/richardiffusion/rag-system>
cd rag-system
```

### 2. 创建虚拟环境
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. 安装依赖
```bash
pip install -r requirements.txt
```

### 4. 配置环境变量
```bash
cp .env.example .env
# 编辑 .env 文件，配置您的设置
```

### 5. 启动Ollama服务
```bash
# 在一个终端中启动Ollama服务
ollama serve

# 在另一个终端中下载模型
ollama pull llama3.1
```

### 6. 加载文档到知识库
```bash
# 将您的文档放入 data/raw/ 目录
# 支持格式: .txt, .pdf, .docx
python scripts/load_documents.py
```

### 7. 启动系统
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## 🎯 快速开始

### 访问Web界面
启动服务后，访问: http://localhost:8000/chat

### 使用API接口
```bash
# 健康检查
curl http://localhost:8000/health

# 智能问答
curl -X POST "http://localhost:8000/api/v1/query/" \
  -H "Content-Type: application/json" \
  -d '{
    "question": "技术栈有哪些？",
    "top_k": 3
  }'

# 添加文档
curl -X POST "http://localhost:8000/api/v1/documents/" \
  -H "Content-Type: application/json" \
  -d '{
    "content": "文档内容...",
    "metadata": {"source": "manual"}
  }'
```

## 📚 API文档

启动服务后访问: http://localhost:8000/docs

### 主要端点
- `POST /api/v1/query/` - 核心问答接口
- `POST /api/v1/documents/` - 添加文档到知识库
- `GET /api/v1/documents/` - 获取文档列表
- `GET /health` - 健康检查

### 请求示例
```python
import requests

response = requests.post(
    "http://localhost:8000/api/v1/query/",
    json={
        "question": "您的问题",
        "top_k": 5
    }
)

print(response.json())
```

## 🗂️ 项目结构

```txt
rag-system/
├── app/                    # 应用代码
│   ├── main.py            # FastAPI应用入口
│   ├── config/            # 配置管理
│   ├── models/            # 数据模型
│   ├── services/          # 核心服务
│   ├── routes/            # API路由
│   └── utils/             # 工具函数
├── scripts/               # 实用脚本
│   ├── clear_cache.py              # 清除缓存
│   ├── show_ollama_models.py       # 查看Ollama模型列表
│   ├── verify_ollama.py            # Ollama模型检查
│   ├── check_supported_formats.py  # 文档格式检查
│   ├── init_database.py            # 初始化数据库
│   ├── load_documents.py           # 文档加载
│   ├── verify_chromadb.py          # ChromaDB验证
│   ├── warmup_model.py             # 模型预热
│   ├── performance_test.py         # 性能测试
│   ├── check_documents.py          # 文档检查
│   └── test_full_system.py         # 完整测试
├── data/                  # 数据目录
│   └── raw/              # 原始文档存储
├── chroma_db/            # ChromaDB向量数据库
├── requirements.txt       # Python依赖
└── README.md             # 项目说明
```

## 🔧 配置说明

### 环境变量 (.env)
```env
# ChromaDB配置
CHROMA_DB_PATH=./chroma_db

# Ollama配置
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3.1

# 嵌入模型配置
EMBEDDING_MODEL=paraphrase-albert-small-v2

# 生成参数
MAX_TOKENS=1024
TEMPERATURE=0.1
TOP_P=0.9
```

### 参数调优
- **top_k**: 检索文档数量 (默认: 5)
- **chunk_size**: 文本分块大小 (默认: 300字符)
- **temperature**: 生成创造性 (默认: 0.1)

## 📊 系统监控

### 检查系统状态
```bash
python scripts/check_system.py
```

### 性能监控
```bash
python scripts/monitor_system.py
```

### 文档统计
```bash
python scripts/check_documents.py
```

## 🐛 故障排除

### 常见问题

**1. Ollama连接失败**
```bash
# 确保Ollama服务运行
ollama serve
# 检查服务状态
curl http://localhost:11434/api/tags
```

**2. 嵌入模型加载失败**
- 系统会自动回退到简单嵌入服务
- 检查网络连接，重新下载模型

**3. 文档检索为空**
```bash
# 检查文档是否加载成功
python scripts/check_documents.py
# 重新加载文档
python scripts/load_documents.py
```

**4. 服务启动失败**
```bash
# 检查端口占用
netstat -ano | findstr :8000
# 清除Python缓存
find . -name "__pycache__" -type d -exec rm -rf {} +
```

### 日志查看
服务启动时会显示详细日志，关注以下信息：
- ChromaDB连接状态
- 嵌入模型加载状态
- Ollama服务连接状态

## 🚀 生产部署

### 系统要求
- **内存**: 至少8GB (运行Llama3.1)
- **存储**: 至少10GB可用空间
- **网络**: 稳定的网络连接

## 🔮 扩展开发

### 添加新功能
1. 在 `app/routes/` 中添加新的API端点
2. 在 `app/services/` 中实现业务逻辑
3. 在 `app/models/` 中定义数据模型
4. 在 `scripts/` 中添加测试脚本

### 集成其他模型
修改 `app/services/llm_service.py` 来支持其他LLM提供商。


**💡 提示**: 要充分发挥RAG系统的威力，请加载您的私有文档（公司文档、个人笔记、专业资料等），然后询问只有这些文档中才有的具体信息！

```
