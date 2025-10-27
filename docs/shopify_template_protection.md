# Shopify模板配置保护机制

## 🛡️ 概述

Shopify API专用模板（`shopify_focus`）采用**多层强制保护**，确保该模板**只能使用Shopify API**查询数据，严格禁止：
- ❌ 网络搜索
- ❌ 文档RAG查询
- ❌ 深度研究模式

**即使用户尝试在UI中修改配置，系统也会自动重置为纯API模式。**

---

## 🔒 保护层级

### 1️⃣ 配置文件层（`data/agent_definitions.json`）

模板默认配置已锁定为纯API模式：

```json
{
  "template_id": "shopify_focus",
  "config": {
    "deep_research_enabled": false,
    "web_search_enabled": false,
    "search_results_count": 0,
    "rag_enabled": false,
    "rag_top_k": 0,
    "rag_context_window": 0,
    "document_links": [],
    "force_api_only": true,
    "locked": true
  }
}
```

### 2️⃣ API层保护（`app.py`）

在模板更新API端点中，强制重置Shopify模板配置：

```python
@app.route('/api/templates/<template_id>', methods=['PUT'])
def update_template(template_id):
    # 🛡️ 强制保护Shopify模板配置
    if template_id == 'shopify_focus' and 'config' in data:
        config['web_search_enabled'] = False
        config['rag_enabled'] = False
        config['deep_research_enabled'] = False
        config['search_results_count'] = 0
        config['rag_top_k'] = 0
        config['rag_context_window'] = 0
        config['document_links'] = []
        config['force_api_only'] = True
        config['locked'] = True
```

### 3️⃣ 管理层保护（`management/agent_manager.py`）

在模板配置更新方法中，再次强制重置：

```python
def update_template_config(self, template_id: str, config: Dict[str, Any]) -> bool:
    # 🛡️ 强制保护Shopify模板配置
    if template_id == 'shopify_focus':
        config['web_search_enabled'] = False
        config['rag_enabled'] = False
        config['deep_research_enabled'] = False
        # ... 其他强制设置
```

### 4️⃣ 智能体执行层保护（`agents/agent_manager.py`）

在研究执行方法中，检测到Shopify智能体时强制禁用：

```python
def execute_research(...):
    if 'shopify' in selected_agents:
        deep_research_options['enableWebSearch'] = False
        deep_research_options['enableDeepResearch'] = False
        rag_manager = None  # 禁用RAG管理器
```

### 5️⃣ 智能体处理层保护（`agents/shopify_agent.py`）

在智能体查询处理中，强制清除上下文中的搜索结果：

```python
def process_query(self, query: str, context: Dict[str, Any] = None):
    if context:
        context['web_search_enabled'] = False
        context['rag_enabled'] = False
        context['deep_research_enabled'] = False
        if 'web_search_results' in context:
            del context['web_search_results']
        if 'rag_results' in context:
            del context['rag_results']
```

---

## 🧪 测试场景

### 场景1：用户在UI中尝试启用网络搜索

1. 用户选择"Shopify API专用模板"
2. 在UI中打开"网络搜索"开关
3. 点击"保存"

**结果：** 
- ✅ 系统自动将配置重置为`web_search_enabled: false`
- ✅ 控制台输出：`🛡️ 检测到Shopify模板更新请求，强制锁定API专用配置`
- ✅ 配置文件保持纯API模式

### 场景2：用户尝试启用文档RAG

1. 用户在UI中启用"RAG文档查询"
2. 设置`rag_top_k: 5`
3. 保存配置

**结果：**
- ✅ 系统自动重置为`rag_enabled: false`, `rag_top_k: 0`
- ✅ 即使保存成功，配置仍为纯API模式

### 场景3：直接修改JSON配置文件

1. 用户手动编辑`agent_definitions.json`
2. 修改`"web_search_enabled": true`
3. 重启应用

**结果：**
- ✅ 应用启动时加载配置
- ✅ 首次API调用时，保护机制会重新锁定配置
- ✅ 查询时不会使用网络搜索

---

## ✅ 配置字段说明

| 字段 | 锁定值 | 说明 |
|------|--------|------|
| `web_search_enabled` | `false` | 禁用网络搜索 |
| `rag_enabled` | `false` | 禁用文档RAG |
| `deep_research_enabled` | `false` | 禁用深度研究 |
| `search_results_count` | `0` | 搜索结果数量为0 |
| `rag_top_k` | `0` | RAG检索数量为0 |
| `rag_context_window` | `0` | RAG上下文窗口为0 |
| `document_links` | `[]` | 无文档链接 |
| `force_api_only` | `true` | 强制纯API模式标志 |
| `locked` | `true` | 配置锁定标志 |

---

## 🔍 日志输出示例

当保护机制触发时，控制台会输出：

```
🛡️ 检测到Shopify模板更新请求，强制锁定API专用配置
✅ 已强制锁定Shopify配置为纯API模式
🛡️ Shopify模板配置被保护，强制重置为纯API模式
🛡️ 检测到Shopify助手，强制禁用网络搜索和RAG功能（仅使用Shopify API）
```

---

## 🎯 设计理念

**为什么需要多层保护？**

1. **配置文件层**：防止手动修改配置文件
2. **API层**：防止通过前端UI修改配置
3. **管理层**：防止通过管理接口修改配置
4. **执行层**：防止运行时绕过配置
5. **智能体层**：防止智能体内部使用其他数据源

**冗余设计的优势：**
- ✅ 多重保障，确保配置不被绕过
- ✅ 即使某一层失效，其他层仍然生效
- ✅ 清晰的日志输出，便于调试
- ✅ 无需修改前端UI代码即可实现保护

---

## 🚀 使用建议

对于Shopify智能体的使用：

1. **选择模板**：始终使用"Shopify API专用模板"
2. **配置凭证**：通过对话或`.env`文件配置Shopify凭证
3. **开始查询**：直接提问，无需担心配置被修改
4. **数据来源**：所有数据保证来自Shopify API

**注意事项：**
- ⚠️ 不要尝试在UI中启用网络搜索或RAG（会被自动重置）
- ⚠️ 不要手动修改配置文件（保护机制会自动恢复）
- ✅ 专注于使用Shopify API功能即可

---

## 📋 总结

Shopify API专用模板通过**五层保护机制**，确保智能体只能使用Shopify API查询数据：

```
配置文件 → API层 → 管理层 → 执行层 → 智能体层
   ↓         ↓        ↓        ↓         ↓
  锁定 →  强制重置 → 再次锁定 → 禁用RAG → 清除搜索结果
```

**这种设计确保了：**
- ✅ 配置不可被修改
- ✅ 数据来源唯一（Shopify API）
- ✅ 用户体验一致
- ✅ 安全可控

