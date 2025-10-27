# 📄 Shopify Invoice 查询功能

## ✅ 已添加功能

现在Shopify助手支持通过API查询发票（Draft Orders）信息了！

## 🎯 功能概述

Shopify API中的发票功能主要通过**Draft Orders**（草稿订单）实现。Draft Orders可以：
- 创建待支付的发票
- 发送发票邮件给客户
- 转换为正式订单

## 🔧 新增API方法

### ShopifyAPIClient 新增方法

1. **`get_draft_orders(limit, since_id, status, fields)`**
   - 获取草稿订单列表
   - 支持状态筛选：`open`, `invoice_sent`, `completed`
   
2. **`get_draft_order(draft_order_id)`**
   - 获取特定草稿订单详情
   
3. **`get_draft_order_count(status)`**
   - 统计草稿订单数量
   
4. **`send_invoice(draft_order_id, custom_message)`**
   - 向客户发送发票邮件
   
5. **`complete_draft_order(draft_order_id, payment_pending)`**
   - 完成草稿订单并转换为正式订单

## 📝 查询示例

### 查询所有发票
```
show me all invoices
显示所有发票
查询发票
```

### 查询最近的发票
```
show me last 5 invoices
最近5张发票
最近10个草稿订单
```

### 按状态筛选
```
show me open invoices
查询未发送的发票
显示已发送的发票
查询已完成的草稿订单
```

### 查询特定发票
```
show me invoice 1234567890
查询发票1234567890
发票号123456的详情
```

## 🎨 返回信息格式

### 发票列表
```
📄 发票列表 (共5个)
━━━━━━━━━━━━━━━━━━━━━━
📝 #D1001: 99.99 USD | open | John Doe
✉️ #D1002: 149.99 USD | invoice_sent | jane@example.com
✅ #D1003: 89.99 USD | completed | Guest
```

状态图标说明：
- 📝 `open` - 未发送的草稿
- ✉️ `invoice_sent` - 已发送发票
- ✅ `completed` - 已完成/转换为订单

### 发票详情
```
📄 发票详情
━━━━━━━━━━━━━━━━━━━━━━
发票号: #D1001
创建时间: 2025-10-27
状态: open
总金额: 99.99 USD
税费: 10.00 USD
发票状态: 未发送

👤 客户信息:
  姓名: John Doe
  邮箱: john@example.com

📋 订单商品:
  • Product A x2 - 49.99 USD
  • Product B x1 - 49.99 USD
```

## 🔍 状态说明

### Draft Order状态类型

1. **`open`（未发送）**
   - 草稿订单已创建但尚未发送发票给客户
   - 可以继续编辑
   
2. **`invoice_sent`（已发送）**
   - 发票邮件已发送给客户
   - 等待客户支付
   
3. **`completed`（已完成）**
   - 草稿订单已转换为正式订单
   - 包含关联的订单ID

## 💡 使用场景

### 1. 查询待发送的发票
```
显示未发送的发票
```
用途：查看哪些发票还没有发送给客户

### 2. 查询已发送但未支付的发票
```
显示已发送的发票
```
用途：跟踪待支付的发票

### 3. 查询特定客户的发票
```
查询包含customer@example.com的发票
```
用途：查看特定客户的所有发票

### 4. 分析发票总金额
```
显示所有发票并分析总金额
```
用途：了解待收款金额

## 🔒 需要的API权限

要查询Draft Orders，您的Shopify Admin API访问令牌需要以下权限：

- `read_draft_orders` - 查询草稿订单
- `write_draft_orders` - 发送发票和完成草稿订单（如需要）

### 配置API权限步骤

1. 登录Shopify管理后台
2. 进入「应用」>「应用和销售渠道」>「开发应用」
3. 选择您的自定义应用
4. 配置API范围（Scopes）
5. 勾选 `read_draft_orders` 和 `write_draft_orders`
6. 保存并重新生成访问令牌

## 📊 完整API响应示例

查询发票时，控制台会显示详细的API响应日志：

```
============================================================
🛍️ [Shopify Agent] 处理查询请求
============================================================
查询内容: show me last 5 invoices
Session ID: abc123...
认证状态: ✅ 已连接
当前商店: My Shop (myshop.myshopify.com)
识别意图: invoices
提取参数: {'limit': 5}

🔍 [Shopify] 查询发票列表:
   状态筛选: 全部
   返回数量: 5
✅ [Shopify] 发票列表查询成功:
   返回发票数: 5
   总金额: 499.95 USD

📦 [Shopify API Response] 发票数据:
   Invoice 1:
      ID: 1234567890
      Name: #D1001
      Total: 99.99 USD
      Status: open
      Customer: john@example.com
      Created: 2025-10-27
   ...
```

## 🆚 Draft Orders vs Orders 对比

| 特性 | Draft Orders (发票) | Orders (订单) |
|------|---------------------|---------------|
| **状态** | open, invoice_sent, completed | pending, paid, cancelled |
| **用途** | 创建待支付发票 | 已确认的订单 |
| **发送** | 可发送发票邮件 | 发送订单确认邮件 |
| **支付** | 等待支付 | 已支付或待支付 |
| **转换** | 可转换为订单 | 已经是订单 |

## 🔄 工作流程

典型的发票工作流程：

1. **创建草稿订单**（通过Shopify后台或API）
   ```
   Draft Order创建 → status: open
   ```

2. **发送发票给客户**
   ```
   发送发票邮件 → status: invoice_sent
   ```

3. **客户支付**
   ```
   完成支付 → status: completed
   转换为正式订单 → Order创建
   ```

## 🧪 测试查询

### 快速测试
打开Shopify助手，尝试以下查询：

```bash
# 查询所有发票
show me all invoices

# 查询未发送的发票
show me open invoices

# 查询最近3张发票
show me last 3 invoices

# 查询特定发票详情
show me invoice [ID]
```

## 📚 相关资源

- **Shopify Admin API文档**: [Draft Orders API](https://shopify.dev/docs/api/admin-rest/2024-01/resources/draftorder)
- **API范围**: `read_draft_orders`, `write_draft_orders`
- **相关文件**:
  - `integrations/shopify_api.py` - API客户端实现
  - `agents/shopify_agent.py` - 代理处理逻辑

## ⚡ 性能优化

- 默认返回10条发票（可通过`limit`参数调整，最大250）
- 支持分页查询（通过`since_id`参数）
- 支持字段筛选（通过`fields`参数减少数据传输）

## 🎉 总结

现在您可以通过Shopify助手：

✅ 查询所有草稿订单/发票  
✅ 按状态筛选（未发送/已发送/已完成）  
✅ 查看发票详情（金额、客户、商品等）  
✅ 追踪待支付的发票  
✅ 分析发票总金额  
✅ 查询特定发票详情  

所有查询都通过Shopify Admin API实时获取数据，确保信息准确及时！

