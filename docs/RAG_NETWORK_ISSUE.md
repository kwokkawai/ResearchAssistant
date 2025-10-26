# RAG功能网络问题解决方案

## 问题描述

RAG（Retrieval-Augmented Generation）功能在首次运行时需要从 HuggingFace 下载AI模型（约400MB），如果没有网络连接会导致RAG功能不可用。

## 当前状态

✅ **应用已优化，即使RAG不可用也能正常启动**
- 应用会尝试初始化RAG系统
- 如果失败（如无网络），会显示警告但不会崩溃
- 其他功能（网络搜索、普通对话）仍然可用

## 解决方案

### 方案1: 首次联网初始化（推荐）

1. **确保网络连接**
   ```bash
   # 测试网络连接
   ping www.google.com
   ```

2. **运行模型下载脚本**
   ```bash
   cd /Users/pkwok/Projects/46. ResearchAssistant/Release/ResearchAssistant_0.3/ResearchAssistant
   source venv/bin/activate
   python3 init_rag_models.py
   ```

3. **模型下载完成后重启应用**
   ```bash
   # 停止应用
   pkill -f 'python3 app.py'
   
   # 重新启动
   python3 app.py
   ```

4. **验证RAG功能**
   - 打开浏览器: http://localhost:5050
   - 不应该看到"RAG功能不可用"的警告
   - 可以在模板配置中启用并测试RAG

### 方案2: 使用已缓存的模型

如果之前在其他项目中使用过 `sentence-transformers`，模型可能已经被缓存：

**检查缓存目录：**
```bash
ls -la ~/.cache/huggingface/hub/
```

如果存在以下目录之一，说明模型已缓存：
- `models--sentence-transformers--paraphrase-multilingual-MiniLM-L12-v2`
- `models--sentence-transformers--all-MiniLM-L6-v2`

**直接启动应用即可，系统会自动使用缓存的模型。**

### 方案3: 手动下载模型（高级用户）

1. **在有网络的机器上下载模型**
   ```bash
   pip install sentence-transformers
   python3 -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('all-MiniLM-L6-v2')"
   ```

2. **复制模型文件到目标机器**
   ```bash
   # 源机器
   tar -czf models.tar.gz ~/.cache/huggingface/hub/
   
   # 传输到目标机器
   scp models.tar.gz user@target:/tmp/
   
   # 目标机器
   cd ~
   tar -xzf /tmp/models.tar.gz
   ```

3. **重启应用**

### 方案4: 在离线模式下运行（RAG功能将不可用）

如果暂时无法解决网络问题：

1. **应用仍然可以正常运行**
   - 启动后会显示警告，10秒后自动消失
   - 所有非RAG功能都可以使用

2. **模板配置中的本地文档RAG选项将不可用**
   - 可以继续使用"网络搜索"模式
   - 其他功能不受影响

## 当前应用启动流程

```
1. 启动 Flask 应用
   ↓
2. 初始化 RAG Manager
   ↓
3. 尝试加载 Sentence Transformer 模型
   ├─ 首先尝试从缓存加载 ✅ (离线可用)
   ├─ 如果缓存不存在，尝试下载 🌐 (需要网络)
   └─ 如果下载失败，RAG设为不可用 ⚠️
   ↓
4. 应用继续启动 (无论RAG是否成功)
   ↓
5. 前端检测RAG状态
   ├─ 可用 → 显示正常 ✅
   └─ 不可用 → 显示警告 (10秒后消失) ⚠️
```

## 验证RAG状态

### 通过API检查
```bash
curl http://localhost:5050/api/rag/status
```

**成功响应：**
```json
{
  "available": true,
  "message": "RAG系统运行正常"
}
```

**失败响应：**
```json
{
  "available": false,
  "error": "无法加载任何嵌入模型...",
  "message": "RAG系统初始化失败。可能原因：..."
}
```

### 通过前端检查
1. 打开浏览器开发者工具 (F12)
2. 查看Console日志
   - ✅ `RAG系统运行正常` - 功能可用
   - ⚠️ `RAG系统不可用` - 功能不可用

## 常见问题

### Q1: 为什么需要下载这么大的模型？
**A:** Sentence Transformer 模型用于将文本转换为向量表示，是实现语义搜索的核心。虽然文件较大，但首次下载后会永久缓存，后续无需网络。

### Q2: 可以使用更小的模型吗？
**A:** 可以。系统已配置备用方案：
- 主模型: `paraphrase-multilingual-MiniLM-L12-v2` (支持中文)
- 备用模型: `all-MiniLM-L6-v2` (更小，但中文支持较差)

### Q3: RAG功能是必需的吗？
**A:** 不是。RAG功能是可选的高级特性，用于基于本地文档回答问题。如果您主要使用网络搜索功能，可以不启用RAG。

### Q4: 如何临时禁用RAG初始化以加快启动速度？
**A:** 修改 `app.py`：
```python
# 在 app.py 中找到以下行并注释掉
# rag_manager = RAGManager()
rag_manager = None
```

## 技术细节

**模型信息：**
- **paraphrase-multilingual-MiniLM-L12-v2**
  - 大小: ~420MB
  - 支持: 50+种语言（包括中文）
  - 用途: 文本嵌入和语义搜索

- **all-MiniLM-L6-v2**
  - 大小: ~80MB
  - 支持: 英语为主
  - 用途: 备用轻量级模型

**缓存位置：**
- macOS/Linux: `~/.cache/huggingface/hub/`
- Windows: `C:\Users\<username>\.cache\huggingface\hub\`

**网络要求：**
- 仅首次运行需要网络
- 后续运行完全离线
- 如果缓存存在，启动速度: <5秒

## 下一步

1. **立即行动**: 运行 `python3 init_rag_models.py` 下载模型
2. **验证**: 检查 RAG 状态 API
3. **测试**: 在模板配置中测试文档加载
4. **反馈**: 如有问题，提供控制台日志

---

**更新时间**: 2025-10-26  
**相关文档**: `docs/rag_troubleshooting.md`
