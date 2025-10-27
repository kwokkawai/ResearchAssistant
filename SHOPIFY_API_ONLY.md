# Shopify助手 - 纯API模式说明

## ⚠️ 重要特性

Shopify助手被配置为**纯API模式**，这意味着：

### ✅ 只能做什么
- ✅ **仅使用Shopify Admin API**查询商店数据
- ✅ 查询订单、发货、账单、客户、产品信息
- ✅ 分析Shopify商店内的销售数据
- ✅ 实时获取商店最新信息

### ❌ 不能做什么
- ❌ **禁用网络搜索** - 不会使用Google、DuckDuckGo等搜索引擎
- ❌ **禁用RAG文档查询** - 不会访问本地文档库
- ❌ **禁用深度研究** - 不会进行多轮研究分析
- ❌ 不能查询Shopify API范围之外的信息

## 🛡️ 强制执行机制

系统在**多个层面**强制执行这些限制：

### 1. 配置层（agent_definitions.json）
```json
{
  "shopify_focus": {
    "config": {
      "web_search_enabled": false,
      "rag_enabled": false,
      "deep_research_enabled": false,
      "search_results_count": 0,
      "rag_top_k": 0,
      "document_links": [],
      "force_api_only": true
    }
  }
}
```

### 2. 智能体层（agents/shopify_agent.py）
```python
def process_query(self, query: str, context: Dict[str, Any] = None):
    # 强制禁用网络搜索和RAG
    if context:
        context['web_search_enabled'] = False
        context['rag_enabled'] = False
        context['deep_research_enabled'] = False
```

### 3. API层（app.py）
```python
# 强制禁用Shopify助手的网络搜索和RAG功能
if 'shopify' in selected_agents:
    deep_research_options['enableWebSearch'] = False
    deep_research_options['enableDeepResearch'] = False
```

### 4. 执行层（agents/agent_manager.py）
```python
# 强制禁用Shopify助手的网络搜索和RAG功能
if 'shopify' in selected_agents:
    deep_research_options['enableWebSearch'] = False
    deep_research_options['enableDeepResearch'] = False
    rag_manager = None  # 禁用RAG管理器
```

## 💡 为什么这样设计？

### 1. 数据准确性
- Shopify API提供的是**实时、准确**的商店数据
- 网络搜索可能包含过时或不相关的信息
- 文档可能与实际商店状态不一致

### 2. 数据安全
- 所有数据来自用户自己的Shopify商店
- 不会泄露商店数据到外部搜索引擎
- 不会在文档中存储敏感商业信息

### 3. 功能专注
- Shopify助手专注于**商店数据查询和分析**
- 避免混淆来自不同来源的信息
- 提供清晰、一致的用户体验

### 4. 性能优化
- 直接API调用比搜索+分析更快
- 减少不必要的网络请求
- 降低token消耗

## 📊 实际效果

### 场景1：用户查询订单
```
用户: 显示最近10个订单
✅ 助手通过Shopify API获取订单数据
❌ 不会搜索"shopify 订单"相关网页
❌ 不会查询本地文档中的订单信息
```

### 场景2：用户查询销售分析
```
用户: 分析最近30天的销售数据
✅ 助手调用Shopify API获取订单
✅ 助手计算销售额、订单量、热销产品
❌ 不会搜索行业销售报告
❌ 不会参考文档中的分析模板
```

### 场景3：用户查询产品信息
```
用户: 显示库存最多的产品
✅ 助手通过API查询产品列表
✅ 助手按库存量排序
❌ 不会搜索"库存管理最佳实践"
❌ 不会查阅文档中的库存指南
```

## 🎯 UI显示

当选择Shopify助手时，UI应显示：

### 模板配置禁用项
- 🚫 网络搜索（已禁用）
- 🚫 文档RAG（已禁用）
- 🚫 深度研究（已禁用）

### 提示信息
```
ℹ️ Shopify助手仅使用Shopify API查询数据
    不使用网络搜索或文档资料
```

## 🔍 验证方法

### 检查配置
```bash
# 查看agent_definitions.json中的shopify_focus配置
cat data/agent_definitions.json | grep -A 20 "shopify_focus"
```

应该看到：
```json
"web_search_enabled": false,
"rag_enabled": false,
"document_links": []
```

### 查看运行日志
启动应用后，选择Shopify助手查询时应看到：
```
🛡️ 检测到Shopify助手，强制禁用网络搜索和RAG功能（仅使用Shopify API）
```

### 测试查询
```
用户: 显示订单
预期: 返回Shopify商店的实际订单数据
不应: 包含网络搜索结果或文档引用
```

## 📝 文档更新

已更新以下文档：
- ✅ `agent_definitions.json` - 配置强制禁用
- ✅ `agents/shopify_agent.py` - 智能体层强制禁用
- ✅ `agents/agent_manager.py` - 执行层强制禁用
- ✅ `app.py` - API层强制禁用

## 🆘 常见问题

### Q: 可以临时启用网络搜索吗？
**A**: 不可以。这是硬编码的限制，无法通过UI或API临时启用。

### Q: 为什么我在UI中看不到搜索选项？
**A**: 这是预期行为。Shopify助手的模板配置已禁用这些功能。

### Q: 如果我需要查询Shopify之外的信息怎么办？
**A**: 请使用其他智能体（如研究助手、技术专家等）。

### Q: 这会影响其他智能体吗？
**A**: 不会。这些限制只适用于Shopify助手（agent_id: "shopify"）。

### Q: 可以同时使用Shopify助手和其他智能体吗？
**A**: 可以，但Shopify助手仍然只会使用API。其他智能体不受影响。

## 🎉 总结

Shopify助手是一个**纯API模式**的专用智能体：
- ✅ 专注于Shopify商店数据
- ✅ 保证数据准确性和实时性
- ✅ 保护商业数据安全
- ✅ 提供一致的用户体验
- ❌ 不使用网络搜索
- ❌ 不使用文档RAG
- ❌ 不进行深度研究

这种设计确保了Shopify助手提供的是**最准确、最安全、最相关**的商店数据。

---

**配置日期**: 2025-01-09  
**强制执行**: 配置层 + 智能体层 + API层 + 执行层  
**状态**: ✅ 已实施并验证

