# Three-Damo Backend

基于 FastAPI + LangChain + FAISS 的 RAG 智能对话系统后端。

## 🚀 快速开始

### 环境要求

- Python 3.10+
- UV (推荐) 或 pip

### 安装依赖

```bash
# 使用 UV (推荐)
uv pip install -r requirements.txt

# 或使用 pip
pip install -r requirements.txt
```

### 配置环境变量

复制 `.env.example` 并重命名为 `.env`，填入你的 API Keys：

```bash
cp .env.example .env
```

编辑 `.env` 文件：

```env
# LLM API Configuration
OPENAI_API_KEY=your-api-key-here
OPENAI_API_BASE=https://cc-vibe.com
OPENAI_MODEL=claude-haiku-4-5-20251001

# Embedding Configuration
EMBEDDING_MODEL=nvidia/llama-nemotron-embed-vl-1b-v2:free
EMBEDDING_API_BASE=https://openrouter.ai/api/v1
EMBEDDING_API_KEY=your-embedding-api-key-here

# Chat Configuration
MAX_HISTORY_LENGTH=10
```

### 启动服务

```bash
# 开发模式
uvicorn app.main:app --reload --port 8000

# 或使用 UV
uv run uvicorn app.main:app --reload --port 8000
```

访问 http://localhost:8000/docs 查看 API 文档。

## 📁 项目结构

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py          # FastAPI 应用入口
│   ├── chat.py          # 对话管理
│   ├── rag.py           # RAG 检索管线
│   └── config.py        # 配置管理
├── requirements.txt     # Python 依赖
├── .env.example         # 环境变量模板
└── README.md
```

## 🔧 API 端点

| 端点 | 方法 | 功能 |
|------|------|------|
| `/` | GET | 健康检查 |
| `/health` | GET | 服务状态 |
| `/chat` | POST | 对话接口（流式响应） |
| `/rebuild-index` | POST | 重建向量索引 |

## 📚 知识库管理

将 `.txt` 文件放入 `../data/documents/` 目录，然后调用：

```bash
curl -X POST http://localhost:8000/rebuild-index
```

## 🚀 部署

### Railway

```bash
railway login
railway init
railway up
```

### Render

连接 GitHub 仓库，Render 会自动检测并部署。

### Fly.io

```bash
fly launch
fly deploy
```

## 📝 环境变量说明

- `OPENAI_API_KEY`: LLM API 密钥
- `OPENAI_API_BASE`: LLM API 基础 URL
- `OPENAI_MODEL`: 使用的模型名称
- `EMBEDDING_MODEL`: Embedding 模型名称
- `EMBEDDING_API_BASE`: Embedding API 基础 URL
- `EMBEDDING_API_KEY`: Embedding API 密钥（可选，默认使用 OPENAI_API_KEY）
- `MAX_HISTORY_LENGTH`: 对话历史保留轮数

## 📄 License

MIT
