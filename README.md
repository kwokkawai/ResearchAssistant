# 🔬 多智能体研究助手 / Multi-Agent Research Assistant

一个基于Flask的现代化多智能体研究助手系统，支持本地Ollama LLM和云端OpenAI、Google Gemini模型，提供专业化的研究分析和连续对话功能。

A modern multi-agent research assistant system based on Flask, supporting local Ollama LLM and cloud-based OpenAI and Google Gemini models, providing professional research analysis and continuous conversation capabilities.

## ✨ 特性 / Features

- 🤖 **多智能体系统**: 四个专业化智能体（研究、数据分析、写作、通用）
- 🔄 **连续对话**: 支持多轮对话，保持上下文
- 🌐 **多模型支持**: 
  - 本地部署：Ollama（支持Llama2、Mistral等开源模型）
  - 云端服务：OpenAI GPT系列、Google Gemini
- 💬 **现代化Web界面**: 响应式设计，支持实时对话
- 📊 **会话管理**: 创建、清空、删除会话，管理对话历史
- 🎯 **智能路由**: 自动根据问题类型选择最合适的智能体

## 📋 系统要求 / Requirements

- Python 3.8+
- Flask 3.0+
- （可选）本地Ollama服务
- （可选）OpenAI API密钥
- （可选）Google Gemini API密钥

## 🚀 快速开始 / Quick Start

### 1. 克隆项目 / Clone the repository

```bash
git clone https://github.com/kwokkawai/ResearchAssistant.git
cd ResearchAssistant
```

### 2. 安装依赖 / Install dependencies

```bash
pip install -r requirements.txt
```

### 3. 配置环境变量 / Configure environment variables

复制示例配置文件并编辑：

```bash
cp .env.example .env
```

编辑 `.env` 文件，根据你的需求配置：

```env
# 选择LLM提供商: ollama, openai, 或 gemini
LLM_PROVIDER=ollama

# Ollama配置（使用本地模型时）
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama2

# OpenAI配置（使用OpenAI时）
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_MODEL=gpt-3.5-turbo

# Gemini配置（使用Google Gemini时）
GEMINI_API_KEY=your_gemini_api_key_here
GEMINI_MODEL=gemini-pro
```

### 4. 运行应用 / Run the application

```bash
python app.py
```

访问 http://localhost:5000 开始使用！

## 🎯 智能体说明 / Agents Description

### 📚 研究助手 (Research Agent)
- 学术研究和文献分析
- 研究方法建议
- 理论框架构建
- 学术概念解释

### 📊 数据分析专家 (Data Analysis Agent)
- 统计分析方法
- 数据可视化建议
- 数据收集策略
- 分析结果解读

### ✍️ 写作顾问 (Writing Agent)
- 学术写作指导
- 论文结构优化
- 语言表达改进
- 引用格式建议

### 💡 通用助手 (General Agent)
- 一般性研究问题
- 综合性任务处理
- 创意头脑风暴
- 跨领域咨询

## 🔧 API端点 / API Endpoints

### 聊天接口
```
POST /api/chat
Content-Type: application/json

{
  "message": "你的问题",
  "session_id": "会话ID（可选）",
  "agent_type": "智能体类型（可选，默认自动选择）"
}
```

### 获取智能体列表
```
GET /api/agents
```

### 会话管理
```
POST /api/session/new                    # 创建新会话
GET /api/session/{session_id}/history    # 获取会话历史
POST /api/session/{session_id}/clear     # 清空会话
DELETE /api/session/{session_id}/delete  # 删除会话
```

### 系统状态
```
GET /api/status
```

## 🛠️ 本地Ollama部署 / Local Ollama Deployment

如果选择使用本地Ollama：

1. 安装Ollama: https://ollama.ai
2. 拉取模型：
```bash
ollama pull llama2
# 或其他模型：mistral, codellama, neural-chat等
```
3. 确保Ollama服务运行在 `http://localhost:11434`

## 📁 项目结构 / Project Structure

```
ResearchAssistant/
├── app.py                 # Flask应用主文件
├── config.py             # 配置管理
├── llm_client.py         # LLM客户端实现
├── agents.py             # 多智能体系统
├── session_manager.py    # 会话管理
├── requirements.txt      # Python依赖
├── .env.example         # 环境变量示例
├── templates/           # HTML模板
│   └── index.html
└── static/             # 静态文件
    ├── css/
    │   └── style.css
    └── js/
        └── app.js
```

## 🎨 界面预览 / UI Preview

- 现代化响应式设计
- 实时对话界面
- 智能体选择面板
- 会话管理控制

## 🔐 安全建议 / Security Recommendations

- 不要将包含真实API密钥的 `.env` 文件提交到版本控制
- 在生产环境中使用强随机密钥作为 `SECRET_KEY`
- 考虑实现用户认证和授权
- 定期更新依赖包以修复安全漏洞

## 📝 开发建议 / Development Tips

1. 使用虚拟环境隔离依赖
2. 根据需求调整智能体的系统提示
3. 可以扩展添加更多专业智能体
4. 调整会话超时时间以适应使用场景

## 🤝 贡献 / Contributing

欢迎提交Issue和Pull Request！

## 📄 许可证 / License

MIT License

## 📧 联系方式 / Contact

如有问题或建议，请通过GitHub Issues联系。

---

Made with ❤️ using Flask and AI