# 迷途小書僮 - 多智能体研究助手系统

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://python.org)
[![Flask](https://img.shields.io/badge/Flask-2.3.3-green.svg)](https://flask.palletsprojects.com)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

一个基于Flask的现代化多智能体研究助手系统，支持本地Ollama LLM和云端OpenAI、Google Gemini模型，提供专业化的研究分析和连续对话功能。

## 🌟 核心特性

### 🤖 多智能体系统
- **研究助手** 🔍: 通用研究分析，擅长综合分析和多角度思考
- **技术专家** 💻: 技术问题分析，专注于编程、架构和工程实践
- **学术专家** 🎓: 学术研究分析，擅长文献综述和学术写作
- **商业分析师** 📊: 商业策略分析，专注于市场分析和商业洞察

### 🔗 多模型支持
- **OpenAI GPT**: GPT-4o, GPT-4-turbo, GPT-3.5-turbo
- **Google Gemini**: Gemini-1.5-pro, Gemini-1.5-flash, Gemini-pro-vision
- **Ollama (本地)**: deepseek-r1, llama2, codellama等本地模型

### 🌐 高级功能
- **连续对话**: 基于之前研究结果进行进一步研究
- **上下文保持**: 自动使用之前的研究结果作为上下文
- **Web搜索集成**: 支持DuckDuckGo和Google搜索API
- **深度研究**: 可配置的深度研究选项
- **会话管理**: 支持多个独立的对话会话
- **对话导出**: 导出完整的对话记录为JSON格式

## 🏗️ 系统架构

```
迷途小書僮研究助手系统
├── 🌐 Web层
│   ├── Flask应用 (app.py)
│   ├── 模板系统 (templates/)
│   └── 静态资源
│
├── 🤖 智能体层
│   ├── 智能体管理器 (agents/agent_manager.py)
│   ├── 动态智能体管理 (management/agent_manager.py)
│   └── 智能体配置 (data/agent_definitions.json)
│
├── 🧠 LLM层
│   ├── LLM管理器 (llm/llm_manager.py)
│   ├── OpenAI提供者
│   ├── Gemini提供者
│   └── Ollama提供者
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

- **Python**: 3.8+
- **Ollama**: 可选，用于本地LLM
- **API密钥**: OpenAI API密钥 (可选)
- **API密钥**: Google API密钥 (可选)

### 2. 快速开始

```bash
# 克隆项目
git clone <repository-url>
cd ResearchAssistant_0.2

# 创建虚拟环境
python -m venv venv
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
```

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

# 生产模式
gunicorn -w 4 -b 0.0.0.0:5050 app:app
```

访问: `http://localhost:5050`

### 2. Web界面使用

#### 选择智能体
- **研究助手** 🔍: 通用研究分析
- **技术专家** 💻: 技术问题分析  
- **学术专家** 🎓: 学术研究分析
- **商业分析师** 📊: 商业策略分析

#### 选择LLM模型
- **OpenAI GPT**: GPT-4o, GPT-4-turbo, GPT-3.5-turbo
- **Google Gemini**: Gemini-1.5-pro, Gemini-1.5-flash
- **Ollama (本地)**: 选择后可以进一步选择具体的本地模型

#### 输入研究问题
示例问题：
- "人工智能在医疗领域的应用前景如何？"
- "如何优化React应用的性能？"
- "区块链技术在供应链管理中的应用"
- "机器学习模型的可解释性研究现状"

#### 深度研究选项
- **启用Web搜索**: 自动搜索相关网络信息
- **搜索引擎**: DuckDuckGo或Google搜索API
- **搜索结果数量**: 5-20个结果
- **包含图片**: 是否在搜索中包含图片结果

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

### 5. 本地文档RAG功能

基于本地文档的检索增强生成，让AI回答完全基于您的私有文档：

- **多格式支持**: PDF、Word文档、Markdown、JSON、HTML、纯文本
- **智能检索**: 语义搜索而非关键词匹配
- **100%私有**: 回答完全基于本地文档，不使用外部知识
- **批量加载**: 支持文件夹批量加载文档
- **实时测试**: 配置前可测试文档加载状态

#### 配置方法：
1. 进入"智能体管理" → 选择智能体 → "配置模板"
2. 启用"本地文档RAG"
3. 在"文档链接"中输入文档路径（每行一个）
   - 支持单个文件：`/path/to/document.pdf`
   - 支持整个文件夹：`/path/to/documents/` （会自动加载文件夹中的所有支持文件）
4. 设置检索参数并测试加载

#### 支持的文档格式：
- `.pdf` - PDF文档
- `.docx`/`.doc` - Word文档
- `.md`/`.markdown` - Markdown文件
- `.txt` - 纯文本文件
- `.json` - JSON文件
- `.html`/`.htm` - HTML文件

#### 故障排除：
如果遇到文档加载问题，请参考 [`docs/rag_troubleshooting.md`](docs/rag_troubleshooting.md)

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

### 智能体和模型接口

```http
# 获取可用智能体
GET /api/agents

# 获取模型状态
GET /api/models

# 获取Ollama模型列表
GET /api/models/ollama

# 健康检查
GET /api/health
```

### 智能体模板配置接口

```http
# 获取智能体模板配置
GET /api/agents/template-config

# 更新智能体模板配置
POST /api/agents/template-config
```

### RAG文档管理接口

```http
# 获取已加载文档列表
GET /api/rag/documents

# 添加文档（支持文件路径或文件夹路径）
POST /api/rag/documents
Content-Type: application/json

{
    "file_path": "/path/to/document.pdf"
}

# 文件上传
POST /api/rag/documents/upload
Content-Type: multipart/form-data

# 删除文档
DELETE /api/rag/documents/{document_id}

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
ResearchAssistant_0.2/
├── 📱 应用核心
│   ├── app.py                    # Flask主应用
│   ├── run.py                    # 启动脚本
│   └── requirements.txt          # 依赖管理
│
├── 🤖 智能体模块
│   ├── agents/
│   │   ├── __init__.py
│   │   └── agent_manager.py      # 智能体管理器
│   └── management/
│       ├── __init__.py
│       └── agent_manager.py      # 动态智能体管理
│
├── 🧠 LLM模块
│   └── llm/
│       ├── __init__.py
│       └── llm_manager.py        # LLM管理器
│
├── 🔍 搜索模块
│   └── search/
│       ├── __init__.py
│       └── web_search.py         # Web搜索功能
│
├── 💬 对话模块
│   └── conversation/
│       ├── __init__.py
│       └── conversation_manager.py # 对话管理器
│
├── ⚙️ 工具模块
│   └── utils/
│       ├── __init__.py
│       └── config.py             # 配置管理
│
├── 📊 数据配置
│   └── data/
│       ├── __init__.py
│       └── agent_definitions.json # 智能体定义
│
├── 🎨 前端资源
│   └── templates/
│       └── index.html            # 主页面模板
│
├── 📚 文档
│   ├── README.md                 # 项目说明
│   ├── env.example               # 环境变量示例
│   └── docs/                     # 用户文档
│       ├── usage_guide.md        # 使用指南
│       ├── gemini_models.md      # Gemini模型说明
│       └── openai_models.md      # OpenAI模型说明
│
└── 🐍 虚拟环境
    └── venv/                     # Python虚拟环境
```

## 🔧 配置选项

### 智能体配置

每个智能体都有独立的配置选项：

```json
{
  "template_config": {
    "default_model": "gemini",
    "preferred_ollama_model": "deepseek-r1:latest",
    "preferred_openai_model": "gpt-4o",
    "preferred_gemini_model": "gemini-1.5-pro",
    "deep_research_enabled": true,
    "web_search_enabled": true,
    "search_engine": "duckduckgo",
    "search_results_count": 15,
    "include_images": true,
    "temperature": 0.8,
    "max_tokens": 2500,
    "timeout": 400
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

### 已实现功能 ✅
- [x] 多智能体系统
- [x] 多LLM支持
- [x] 连续对话
- [x] Web搜索集成
- [x] 会话管理
- [x] 对话导出
- [x] 智能体模板配置

### 已实现功能 ✅
- [x] 本地文档RAG功能
- [x] 多格式文档支持 (PDF, Word, MD, JSON, HTML, TXT)
- [x] 向量数据库和语义搜索
- [x] 智能体RAG配置
- [x] 文档上传和管理

### 计划功能 🚧
- [ ] 用户认证系统
- [ ] 智能体性能分析
- [ ] 更多搜索提供商
- [ ] 移动端适配
- [ ] 插件系统
- [ ] 多语言支持

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

- **项目维护者**: [您的姓名]
- **邮箱**: [您的邮箱]
- **GitHub**: [您的GitHub链接]

## 🙏 致谢

感谢以下开源项目和服务：

- [Flask](https://flask.palletsprojects.com/) - Web框架
- [OpenAI](https://openai.com/) - GPT模型
- [Google](https://ai.google.dev/) - Gemini模型
- [Ollama](https://ollama.ai/) - 本地LLM
- [DuckDuckGo](https://duckduckgo.com/) - 搜索服务
- [Bootstrap](https://getbootstrap.com/) - UI框架

---

**迷途小書僮** - 让研究更智能，让思考更深入 🧠✨