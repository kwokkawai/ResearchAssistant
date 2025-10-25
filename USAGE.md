# 使用指南 / Usage Guide

## 快速开始

### 1. 使用本地Ollama

这是最简单的方式，不需要API密钥：

```bash
# 1. 安装Ollama
# 访问 https://ollama.ai 下载安装

# 2. 拉取模型
ollama pull llama2

# 3. 配置环境变量
cat > .env << EOF
LLM_PROVIDER=ollama
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama2
EOF

# 4. 运行应用
python app.py
```

### 2. 使用OpenAI API

```bash
# 配置环境变量
cat > .env << EOF
LLM_PROVIDER=openai
OPENAI_API_KEY=sk-your-api-key-here
OPENAI_MODEL=gpt-3.5-turbo
EOF

# 运行应用
python app.py
```

### 3. 使用Google Gemini

```bash
# 配置环境变量
cat > .env << EOF
LLM_PROVIDER=gemini
GEMINI_API_KEY=your-gemini-api-key-here
GEMINI_MODEL=gemini-pro
EOF

# 运行应用
python app.py
```

## API使用示例

### Python示例

```python
import requests

BASE_URL = "http://localhost:5000"

# 创建会话
response = requests.post(f"{BASE_URL}/api/session/new")
session_id = response.json()['session_id']

# 发送消息
message = {
    "message": "什么是机器学习？",
    "session_id": session_id
}
response = requests.post(
    f"{BASE_URL}/api/chat",
    json=message
)
print(response.json()['response'])
```

### JavaScript/Node.js示例

```javascript
const axios = require('axios');

const BASE_URL = 'http://localhost:5000';

async function chat() {
    // 创建会话
    const sessionResp = await axios.post(`${BASE_URL}/api/session/new`);
    const sessionId = sessionResp.data.session_id;
    
    // 发送消息
    const chatResp = await axios.post(`${BASE_URL}/api/chat`, {
        message: '什么是机器学习？',
        session_id: sessionId
    });
    
    console.log(chatResp.data.response);
}

chat();
```

### cURL示例

```bash
# 创建会话
SESSION_ID=$(curl -s -X POST http://localhost:5000/api/session/new | jq -r '.session_id')

# 发送消息
curl -X POST http://localhost:5000/api/chat \
  -H "Content-Type: application/json" \
  -d "{
    \"message\": \"什么是机器学习？\",
    \"session_id\": \"$SESSION_ID\"
  }" | jq
```

## 智能体选择

系统会根据问题自动选择合适的智能体，也可以手动指定：

```python
# 自动选择（默认）
message = {
    "message": "如何进行文献综述？",
    "session_id": session_id
}

# 手动指定研究助手
message = {
    "message": "如何进行文献综述？",
    "session_id": session_id,
    "agent_type": "research"
}

# 手动指定数据分析专家
message = {
    "message": "如何选择统计方法？",
    "session_id": session_id,
    "agent_type": "data"
}

# 手动指定写作顾问
message = {
    "message": "如何改进论文摘要？",
    "session_id": session_id,
    "agent_type": "writing"
}

# 手动指定通用助手
message = {
    "message": "一般性问题",
    "session_id": session_id,
    "agent_type": "general"
}
```

## 部署建议

### 开发环境

```bash
python app.py
```

### 生产环境（使用Gunicorn）

```bash
# 安装Gunicorn
pip install gunicorn

# 运行
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

### Docker部署

创建 `Dockerfile`:

```dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 5000

CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "app:app"]
```

运行:

```bash
docker build -t research-assistant .
docker run -p 5000:5000 --env-file .env research-assistant
```

## 常见问题

### Q: 如何切换不同的LLM模型？

A: 编辑 `.env` 文件，修改 `LLM_PROVIDER` 和相应的模型配置，然后重启应用。

### Q: 可以同时使用多个模型吗？

A: 当前版本只支持同时使用一个提供商。如需支持多模型，需要修改代码实现动态切换。

### Q: 如何调整对话上下文长度？

A: 在 `session_manager.py` 的 `get_context()` 方法中修改 `max_messages` 参数。

### Q: 如何自定义智能体？

A: 在 `agents.py` 中创建新的Agent类，继承自 `Agent` 基类，并在 `AgentCoordinator` 中注册。

## 性能优化

1. **使用缓存**: 对于常见问题，可以实现响应缓存
2. **异步处理**: 使用异步库如 `aiohttp` 提高并发性能
3. **负载均衡**: 使用多个worker进程处理请求
4. **会话持久化**: 将会话存储到Redis或数据库中
