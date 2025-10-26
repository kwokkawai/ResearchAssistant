# 迷途小書僮 - 多智能体研究助手系统

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://python.org)
[![Flask](https://img.shields.io/badge/Flask-3.0+-green.svg)](https://flask.palletsprojects.com)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

一个基于Flask的现代化多智能体研究助手系统，支持本地Ollama LLM和云端OpenAI、Google Gemini模型，集成本地文档RAG功能，提供专业化的研究分析和连续对话功能。

## 🌟 核心特性

### 🤖 多智能体系统（专业级Prompt）
- **研究助手** 🔍: 系统性思维、批判性分析，提供6大板块的全面研究框架
- **技术专家** 💻: 技术问题分析和解决方案，专注于编程、架构和工程实践
- **学术专家** 🎓: 完整学术指导，包含论文结构、文献综述、研究方法、期刊投稿建议
- **商业分析师** 📊: PEST分析、波特五力、商业模式画布、风险矩阵、实施路线图
- **创意专家** 💡: SCAMPER创意技法、设计思维、原型测试、情感体验设计
- **法律顾问** ⚖️: 法律分析、风险评估、合规建议、证据清单、法律文书框架

### 🔗 多模型支持
- **OpenAI GPT**: GPT-4o, GPT-4-turbo, GPT-3.5-turbo
- **Google Gemini**: Gemini-1.5-pro, Gemini-1.5-flash, Gemini-pro-vision
- **Ollama (本地)**: deepseek-r1, llama2, codellama等本地模型

### 🌐 高级功能
- **模板配置系统**: 灵活的智能体模板配置，支持独立的模型、RAG和搜索设置
- **本地文档RAG**: 支持PDF、Word、Markdown、JSON等多格式文档的语义检索
- **向量数据库**: 基于ChromaDB的本地向量存储，100%私有数据保护
- **连续对话**: 基于之前研究结果进行进一步研究
- **上下文保持**: 自动使用之前的研究结果作为上下文
- **Web搜索集成**: 支持DuckDuckGo和Google搜索API，卡片式结果展示
- **深度研究**: 可配置的深度研究选项
- **会话管理**: 支持多个独立的对话会话
- **对话导出**: 导出完整的对话记录为JSON格式

## 🏗️ 系统架构

```
迷途小書僮研究助手系统
├── 🌐 Web层
│   ├── Flask应用 (app.py)
│   ├── 模板系统 (templates/)
│   └── REST API接口
│
├── 🤖 智能体层
│   ├── 智能体执行器 (agents/agent_manager.py)
│   ├── 模板配置管理 (management/agent_manager.py)
│   └── 智能体定义 (data/agent_definitions.json)
│
├── 🧠 LLM层
│   ├── LLM管理器 (llm/llm_manager.py)
│   ├── OpenAI提供者
│   ├── Gemini提供者
│   └── Ollama提供者（本地）
│
├── 📚 RAG层
│   ├── RAG管理器 (rag/rag_manager.py)
│   ├── 文档处理器 (rag/document_processor.py)
│   ├── 向量存储 (rag/vector_store.py)
│   └── ChromaDB数据库 (data/vector_store/)
│
├── 🔍 搜索层
│   ├── Web搜索模块 (search/web_search.py)
│   ├── DuckDuckGo搜索
│   └── Google搜索API
│
├── 💬 对话层
│   ├── 对话管理器 (conversation/conversation_manager.py)
│   ├── 会话管理
│   └── 上下文保持
│
└── ⚙️ 工具层
    ├── 配置管理 (utils/config.py)
    ├── 环境变量
    └── 日志系统
```

## 📦 安装和配置

### 1. 环境要求

- **Python**: 3.8+ （推荐3.10+，已在Python 3.13.3测试通过）
- **内存**: 至少4GB RAM（RAG功能需要8GB+）
- **存储**: 至少2GB可用空间（包含模型缓存）
- **Ollama**: 可选，用于本地LLM（推荐用于隐私保护）
- **API密钥**: OpenAI API密钥（可选，用于GPT模型）
- **API密钥**: Google API密钥（可选，用于Gemini模型）

### 2. 快速开始

```bash
# 克隆项目
git clone <repository-url>
cd ResearchAssistant

# 创建虚拟环境
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# 或
venv\Scripts\activate     # Windows

# 安装依赖
pip install -r requirements.txt

# 配置环境变量
cp env.example .env
# 编辑 .env 文件，填入您的API密钥

# 启动应用
python run.py
# 或
python app.py
```

访问: `http://localhost:5000`（端口可能是5000、5050或5051）

### 3. 详细配置

#### 环境变量配置

复制 `env.example` 到 `.env` 并配置以下变量：

```bash
# Flask配置
SECRET_KEY=your-secret-key-here
DEBUG=True
HOST=0.0.0.0
PORT=5050

# OpenAI配置
OPENAI_API_KEY=your-openai-api-key-here
OPENAI_MODEL=gpt-4o
OPENAI_TEMPERATURE=0.7
OPENAI_MAX_TOKENS=2000

# Google Gemini配置
GOOGLE_API_KEY=your-google-api-key-here
GEMINI_MODEL=gemini-1.5-pro
GEMINI_TEMPERATURE=0.7
GEMINI_MAX_TOKENS=2000

# Ollama配置 (本地LLM)
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=deepseek-r1:latest

# 智能体配置
MAX_AGENTS_PER_QUERY=5
AGENT_TIMEOUT=300

# Google搜索API配置 (可选)
GOOGLE_SEARCH_API_KEY=your-google-search-api-key-here
GOOGLE_SEARCH_ENGINE_ID=your-google-search-engine-id-here

# 研究配置
MAX_RESEARCH_DEPTH=3
ENABLE_WEB_SEARCH=True
```

#### Ollama本地模型设置

```bash
# 安装Ollama
curl -fsSL https://ollama.ai/install.sh | sh

# 下载推荐模型
ollama pull deepseek-r1:latest
ollama pull llama2
ollama pull codellama

# 启动Ollama服务
ollama serve
```

## 🚀 使用方法

### 1. 启动应用

```bash
# 开发模式
python run.py

# 或直接运行Flask
python app.py

# 生产模式（使用gunicorn）
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

访问: `http://localhost:5000`（或5050/5051，取决于端口配置）

### 2. Web界面使用

#### 选择智能体
系统提供6个专业级智能体，每个都配备了行业最佳实践的Prompt模板：
- **研究助手** 🔍: 系统性思维框架、知识图谱、研究方向建议
- **技术专家** 💻: 技术问题分析和解决方案
- **学术专家** 🎓: 论文结构、文献综述、研究方法、期刊投稿
- **商业分析师** 📊: PEST分析、波特五力、商业模式画布
- **创意专家** 💡: SCAMPER技法、设计思维、原型测试
- **法律顾问** ⚖️: 法律分析、风险评估、合规建议

#### 配置智能体模板
在"配置管理"中，您可以为每个智能体配置：
- **默认模型**: OpenAI/Gemini/Ollama（本地）
- **具体模型选择**: 
  - OpenAI: 自定义模型名（如 gpt-4o, gpt-3.5-turbo）
  - Gemini: 自定义模型名（如 gemini-1.5-pro）
  - Ollama: 从本地可用模型中选择（如 deepseek-r1:latest, gpt-oss:20b）
- **网络搜索**: 启用/禁用，选择搜索引擎（DuckDuckGo/Google）
- **本地文档RAG**: 启用/禁用，配置文档路径
- **注意**: 网络搜索和本地RAG只能二选一

#### 输入研究问题
示例问题：
- "人工智能在医疗领域的应用前景如何？"
- "如何撰写一篇关于机器学习的综述论文？"
- "分析共享办公空间的商业模式和市场机会"
- "为一个环保品牌设计创意营销活动"
- "分析电商平台的用户协议法律风险"

### 3. 连续对话功能

1. **开始研究**: 输入问题并选择智能体和模型
2. **查看结果**: 系统显示综合总结和各智能体分析
3. **继续研究**: 点击"继续研究"按钮
4. **输入新问题**: 基于之前结果提出新问题
5. **选择配置**: 可以选择不同的智能体和模型
6. **重复过程**: 可以无限次重复此过程

### 4. 对话管理

- **新建会话**: 开始全新的对话
- **会话历史**: 查看所有历史会话
- **导出对话**: 下载JSON格式的完整对话记录
- **上下文保持**: 自动使用之前的研究结果作为上下文

### 5. 本地文档RAG功能 🔥

基于本地文档的检索增强生成（Retrieval Augmented Generation），让AI回答完全基于您的私有文档：

**核心特性**:
- **多格式支持**: PDF、Word文档、Markdown、JSON、HTML、纯文本
- **语义检索**: 基于Sentence Transformers的语义搜索，非关键词匹配
- **100%私有**: 回答完全基于本地文档，不使用LLM的预训练知识
- **本地向量数据库**: 使用ChromaDB本地存储，数据不离开本地
- **批量加载**: 支持文件夹批量加载文档
- **实时测试**: 配置前可测试文档加载状态

#### 配置方法：
1. 进入"配置管理"标签页
2. 选择要配置的模板，点击"编辑配置"
3. 在"数据源配置"中选择"本地文档RAG"
4. RAG配置区域会自动展开：
   - **Top K结果数**: 检索时返回的最相关文档片段数（默认5）
   - **上下文窗口**: 每个片段的字符数（默认1000）
   - **文档链接**: 每行一个路径，支持：
     - 单个文件：`/path/to/document.pdf`
     - 整个文件夹：`/path/to/documents/`（会自动加载所有支持文件）
   - **强制重新加载**: 勾选后会清除现有文档重新加载
5. 点击"测试文档加载"验证配置
6. 点击"保存配置"

#### 支持的文档格式：
- `.pdf` - PDF文档
- `.docx`/`.doc` - Word文档  
- `.md`/`.markdown` - Markdown文件
- `.txt` - 纯文本文件
- `.json` - JSON文件
- `.html`/`.htm` - HTML文件

#### 文档管理功能：
- **测试文档加载**: 在保存前测试文档是否能成功加载
- **强制重新加载**: 清除现有文档并重新加载
- **清除所有文档**: 重置整个RAG向量数据库

#### 重要提示：
- ⚠️ 网络搜索和本地文档RAG **只能二选一**，不能同时启用
- ⚠️ 启用RAG后，查询结果将**100%基于您提供的文档**
- ⚠️ 首次加载文档可能需要较长时间（取决于文档数量和大小）
- ⚠️ 向量数据库存储在 `data/vector_store/` 目录

#### 故障排除：
如果遇到文档加载问题，请参考：
- [`docs/rag_troubleshooting.md`](docs/rag_troubleshooting.md) - RAG故障排除指南
- [`docs/RAG_DIAGNOSTIC_GUIDE.md`](docs/RAG_DIAGNOSTIC_GUIDE.md) - RAG诊断指南
- [`docs/RAG_NETWORK_ISSUE.md`](docs/RAG_NETWORK_ISSUE.md) - 网络问题说明

## 🔌 API接口

### 研究接口

```http
POST /api/research
Content-Type: application/json

{
    "query": "您的研究问题",
    "agents": ["research", "technical", "academic", "business"],
    "model": "openai",
    "openaiModel": "gpt-4o",
    "geminiModel": "gemini-1.5-pro",
    "ollamaModel": "deepseek-r1:latest",
    "isContinuation": false,
    "sessionId": "session-uuid",
    "deepResearch": {
        "enabled": true,
        "searchEngine": "duckduckgo",
        "searchResultsCount": 10,
        "includeImages": true
    }
}
```

### 对话管理接口

```http
# 创建新会话
POST /api/conversation/new

# 获取会话信息
GET /api/conversation/<session_id>

# 导出会话
GET /api/conversation/<session_id>/export

# 获取所有会话
GET /api/conversations
```

### 智能体和模板管理接口

```http
# 获取所有智能体
GET /api/agents

# 获取单个智能体
GET /api/agents/<agent_id>

# 更新智能体
PUT /api/agents/<agent_id>

# 获取所有模板
GET /api/templates

# 获取单个模板
GET /api/templates/<template_id>

# 更新模板配置
PUT /api/templates/<template_id>

# 获取Ollama模型列表
GET /api/ollama-models

# RAG系统状态
GET /api/rag/status

# 健康检查
GET /api/health
```

### RAG文档管理接口

```http
# 获取已加载文档列表
GET /api/rag/documents

# 添加文档（支持文件路径或文件夹路径）
POST /api/rag/documents
Content-Type: application/json

{
    "file_path": "/path/to/document.pdf",
    "force_reload": false
}

# 文件上传
POST /api/rag/documents/upload
Content-Type: multipart/form-data

# 删除文档
DELETE /api/rag/documents/{document_id}

# 清除所有文档
DELETE /api/rag/documents

# 获取文档详情
GET /api/rag/documents/{document_id}

# 直接查询文档
POST /api/rag/query
Content-Type: application/json

{
    "query": "您的查询",
    "document_ids": ["可选的文档ID列表"],
    "top_k": 5
}

# 生成RAG回答
POST /api/rag/generate
Content-Type: application/json

{
    "query": "您的查询",
    "document_ids": ["可选的文档ID列表"],
    "top_k": 5,
    "model": "openai"
}
```

## 📁 项目结构

```
ResearchAssistant/
├── 📱 应用核心
│   ├── app.py                    # Flask主应用（API路由）
│   ├── run.py                    # 启动脚本
│   ├── requirements.txt          # 完整依赖
│   └── requirements-minimal.txt  # 最小RAG依赖
│
├── 🤖 智能体模块
│   ├── agents/
│   │   ├── __init__.py
│   │   └── agent_manager.py      # 智能体执行器
│   └── management/
│       ├── __init__.py
│       └── agent_manager.py      # 模板配置管理
│
├── 🧠 LLM模块
│   └── llm/
│       ├── __init__.py
│       └── llm_manager.py        # 多LLM提供商管理
│
├── 📚 RAG模块
│   └── rag/
│       ├── __init__.py
│       ├── rag_manager.py        # RAG核心管理
│       ├── document_processor.py  # 文档处理
│       └── vector_store.py       # 向量数据库
│
├── 🔍 搜索模块
│   └── search/
│       ├── __init__.py
│       └── web_search.py         # 多搜索引擎集成
│
├── 💬 对话模块
│   └── conversation/
│       ├── __init__.py
│       └── conversation_manager.py # 对话和会话管理
│
├── ⚙️ 工具模块
│   └── utils/
│       ├── __init__.py
│       └── config.py             # 配置管理
│
├── 📊 数据和配置
│   └── data/
│       ├── __init__.py
│       ├── agent_definitions.json # 智能体和模板定义
│       └── vector_store/         # ChromaDB向量数据库
│           └── chroma.sqlite3
│
├── 🎨 前端资源
│   └── templates/
│       └── index.html            # 主页面（单页应用）
│
├── 📚 文档
│   ├── README.md                 # 项目说明（本文件）
│   ├── CLEANUP_COMPLETED.md      # 清理完成报告
│   ├── Github.md                 # Git版本管理指南
│   ├── LICENSE                   # MIT许可证
│   ├── env.example               # 环境变量示例
│   └── docs/                     # 详细文档
│       ├── usage_guide.md        # 使用指南
│       ├── openai_models.md      # OpenAI模型说明
│       ├── gemini_models.md      # Gemini模型说明
│       ├── rag_troubleshooting.md # RAG故障排除
│       ├── RAG_DIAGNOSTIC_GUIDE.md # RAG诊断指南
│       └── RAG_NETWORK_ISSUE.md  # RAG网络问题
│
└── 🐍 虚拟环境
    └── venv/                     # Python虚拟环境
```

## 🔧 配置选项

### 模板配置架构

每个智能体通过`template_id`关联到一个模板，模板包含完整的配置：

```json
{
  "templates": {
    "research_focus": {
      "template_id": "research_focus",
      "name": "研究助手模板",
      "description": "专注于综合研究分析的模板",
      "enabled": true,
      "config": {
        "default_model": "ollama",
        "preferred_openai_model": "gpt-4o",
        "preferred_gemini_model": "gemini-1.5-pro",
        "preferred_ollama_model": "deepseek-r1:latest",
        "temperature": 0.8,
        "max_tokens": 2500,
        "timeout": 400,
        "deep_research_enabled": true,
        "web_search_enabled": true,
        "search_engine": "google",
        "search_results_count": 30,
        "include_images": false,
        "rag_enabled": false,
        "rag_top_k": 5,
        "rag_context_window": 1000,
        "rag_document_links": []
      }
    }
  }
}
```

### 智能体定义

智能体定义简化为引用模板：

```json
{
  "agents": {
    "research": {
      "agent_id": "research",
      "name": "研究助手",
      "description": "通用研究分析智能体",
      "icon": "search",
      "color": "primary",
      "prompt_template": "专业级prompt...",
      "enabled": true,
      "template_id": "research_focus"
    }
  }
}
```

### 模型配置

| 提供商 | 模型 | 特点 | 推荐用途 |
|--------|------|------|----------|
| OpenAI | GPT-4o | 多模态，最新 | 综合研究 |
| OpenAI | GPT-4-turbo | 快速响应 | 快速分析 |
| OpenAI | GPT-3.5-turbo | 经济实惠 | 简单查询 |
| Gemini | Gemini-1.5-pro | 大上下文 | 深度研究 |
| Gemini | Gemini-1.5-flash | 快速响应 | 实时分析 |
| Ollama | deepseek-r1 | 本地推理 | 隐私保护 |
| Ollama | llama2 | 通用模型 | 基础研究 |

## 🛠️ 扩展开发

### 添加新的智能体

1. **创建智能体类**:
```python
from agents.agent_manager import Agent

class CustomAgent(Agent):
    def __init__(self, llm_manager):
        super().__init__("自定义智能体", "智能体描述", llm_manager)
    
    def get_specialization(self) -> str:
        return "您的专业领域"
    
    async def process_query(self, query: str, context: str = "") -> str:
        # 实现您的处理逻辑
        pass
```

2. **注册智能体**:
```python
# 在 agents/agent_manager.py 中注册
agent_manager.register_agent("custom", CustomAgent)
```

3. **更新配置**:
```json
// 在 data/agent_definitions.json 中添加
{
  "custom": {
    "agent_id": "custom",
    "name": "自定义智能体",
    "description": "智能体描述",
    "enabled": true
  }
}
```

### 添加新的LLM提供者

1. **创建提供者类**:
```python
from llm.llm_manager import LLMProvider

class CustomProvider(LLMProvider):
    def __init__(self, config):
        self.config = config
    
    def generate_response(self, prompt: str, **kwargs) -> str:
        # 实现您的LLM调用逻辑
        pass
    
    def is_available(self) -> bool:
        # 检查提供者是否可用
        pass
```

2. **注册提供者**:
```python
# 在 llm/llm_manager.py 中注册
llm_manager.register_provider("custom", CustomProvider)
```

## 🐛 故障排除

### 常见问题

#### 1. Ollama连接失败
```bash
# 检查Ollama服务状态
curl http://localhost:11434/api/tags

# 重启Ollama服务
ollama serve
```

#### 2. API密钥错误
- 检查环境变量中的API密钥
- 确认API密钥有效且有足够额度
- 验证API密钥格式正确

#### 3. 模型响应超时
- deepseek-r1等大型模型响应较慢（30-60秒）
- 系统已设置300秒超时
- 建议使用较短的查询以获得更快响应

#### 4. Web搜索失败
- 检查网络连接
- 验证Google搜索API配置（如果使用）
- DuckDuckGo搜索无需API密钥

### 日志和调试

```bash
# 查看应用日志
tail -f logs/app.log

# 查看错误日志
tail -f logs/error.log

# 调试模式运行
DEBUG=True python run.py
```

### 性能优化

1. **减少并发智能体数量**: 修改 `MAX_AGENTS_PER_QUERY`
2. **调整超时时间**: 修改 `AGENT_TIMEOUT`
3. **使用本地模型**: 减少网络延迟
4. **优化搜索参数**: 减少搜索结果数量

## 📊 性能指标

- **响应时间**: 通常5-30秒（取决于模型和查询复杂度）
- **并发支持**: 支持多用户同时使用
- **内存使用**: 约100-500MB（取决于模型）
- **存储需求**: 约1GB（包含虚拟环境）

## 🔒 安全考虑

- **API密钥**: 不要在代码中硬编码API密钥
- **环境变量**: 使用 `.env` 文件管理敏感信息
- **网络安全**: 生产环境建议使用HTTPS
- **访问控制**: 可以添加用户认证和授权

## 📈 路线图

### v0.3 已实现功能 ✅
- [x] 6个专业级智能体（最佳实践Prompt）
- [x] 智能体-模板分离架构
- [x] 灵活的模板配置系统
- [x] 多LLM支持（OpenAI/Gemini/Ollama）
- [x] 动态Ollama模型加载
- [x] 本地文档RAG功能
- [x] 多格式文档支持（PDF/Word/MD/JSON/HTML/TXT）
- [x] ChromaDB向量数据库
- [x] 语义检索和RAG生成
- [x] 网络搜索集成（DuckDuckGo/Google）
- [x] 搜索结果卡片式展示
- [x] 连续对话和会话管理
- [x] 对话导出功能
- [x] 网络搜索和RAG互斥控制

### v0.4 计划功能 🚧
- [ ] 用户认证和授权系统
- [ ] 多用户会话隔离
- [ ] 智能体性能监控和分析
- [ ] RAG文档版本管理
- [ ] 更多搜索提供商（Bing, Brave）
- [ ] 文档摘要预览
- [ ] 批量文档上传界面
- [ ] 移动端响应式优化

### v1.0 长期规划 🌟
- [ ] 插件系统架构
- [ ] 自定义智能体创建向导
- [ ] 多语言支持（英文/日文）
- [ ] Docker容器化部署
- [ ] 云端同步功能
- [ ] 团队协作功能

## 🤝 贡献指南

欢迎贡献代码！请遵循以下步骤：

1. **Fork项目**
2. **创建功能分支**: `git checkout -b feature/AmazingFeature`
3. **提交更改**: `git commit -m 'Add some AmazingFeature'`
4. **推送分支**: `git push origin feature/AmazingFeature`
5. **提交Pull Request**

### 代码规范

- 使用Python 3.8+语法
- 遵循PEP 8代码风格
- 添加适当的注释和文档字符串
- 编写单元测试（如果可能）

## 📄 许可证

本项目采用MIT许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 📞 联系方式

- **项目维护者**: Paul Kwok
- **邮箱**: pkwok@hotmail.com
- **GitHub**: https://github.com/kwokkawai

## 🙏 致谢

感谢以下开源项目和服务：

- [Flask](https://flask.palletsprojects.com/) - Web框架
- [OpenAI](https://openai.com/) - GPT模型API
- [Google AI](https://ai.google.dev/) - Gemini模型API
- [Ollama](https://ollama.ai/) - 本地LLM运行时
- [ChromaDB](https://www.trychroma.com/) - 向量数据库
- [Sentence Transformers](https://www.sbert.net/) - 语义嵌入模型
- [DuckDuckGo](https://duckduckgo.com/) - 隐私搜索服务
- [Bootstrap](https://getbootstrap.com/) - UI框架
- [PyMuPDF](https://pymupdf.readthedocs.io/) - PDF处理
- [python-docx](https://python-docx.readthedocs.io/) - Word文档处理

---

## 📝 更新日志

### v0.3 (2025-10-26)
- ✨ 新增6个专业级智能体Prompt模板
- ✨ 实现智能体-模板分离架构
- ✨ 集成本地文档RAG功能
- ✨ 添加ChromaDB向量数据库
- ✨ 支持多格式文档处理
- ✨ 实现动态Ollama模型加载
- ✨ 添加搜索结果卡片式展示
- ✨ 实现网络搜索和RAG互斥控制
- 🐛 修复模板配置保存问题
- 🐛 修复Ollama模型配置丢失问题
- 🧹 清理测试文件和临时文档
- 📚 完善文档和使用指南

### v0.2 (2025-10)
- ✨ 多智能体系统基础架构
- ✨ 多LLM支持（OpenAI/Gemini/Ollama）
- ✨ 连续对话功能
- ✨ Web搜索集成
- ✨ 会话管理

---

**迷途小書僮 v0.3** - 让研究更智能，让思考更深入 🧠✨

专业级智能体 | 本地RAG | 多LLM支持 | 100%隐私保护