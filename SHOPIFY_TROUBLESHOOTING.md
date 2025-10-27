# 🔧 Shopify助手故障排除

## 问题：查询订单时返回通用说明而不是真实数据

### 症状

提问："what is the last order in shopify"

**错误返回：**
> 在 Shopify 后台，**"最近的订单"**即指时间上最新的一笔已完成或待处理的订单。你可以在商店管理面板的「Orders」页面看到，页面默认按下单时间倒序排列...

**期望返回：**
```
📦 订单详情
━━━━━━━━━━━━━━━━━━━━━━
订单号: #1234
总金额: 99.99 USD
订单状态: paid
...
```

---

## 🔍 诊断步骤

### 步骤 1: 验证意图识别

运行测试脚本：
```bash
python3 test_intent_detection.py
```

**期望输出：**
```
Query: what is the last order in shopify
  ✅ Intent: orders
  📋 Params: {'limit': 1}
```

✅ 如果输出正确，意图识别没有问题，继续下一步。

### 步骤 2: 检查环境变量配置

运行配置检查：
```bash
python3 check_shopify_config.py
```

**如果显示：**
```
❌ No shop URL configured
```

**原因：** `.env` 文件未配置或配置不正确。

### 步骤 3: 验证代码版本

检查 `agents/shopify_agent.py` 中是否有自动认证代码。

在 `process_query` 方法开头应该有：
```python
# 🔧 自动检测并使用环境变量中的凭证
if not self.is_authenticated(session_id):
    import os
    env_shop_url = os.environ.get('SHOPIFY_SHOP_URL', '').strip() or \
                  os.environ.get('SHOPIFY_SHOP_DOMAIN', '').strip()
    ...
```

✅ 如果有这段代码，说明版本正确。  
❌ 如果没有，需要更新代码。

---

## ✅ 解决方案

### 方案 1: 配置环境变量（推荐）

1. **创建或编辑 `.env` 文件**

在项目根目录创建 `.env` 文件：
```bash
# Shopify Configuration
SHOPIFY_SHOP_DOMAIN=uon9.myshopify.com
SHOPIFY_ACCESS_TOKEN=shpat_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

2. **获取访问令牌**（如果还没有）

   a. 登录 Shopify 管理后台：https://uon9.myshopify.com/admin
   
   b. 进入「设置」>「应用和销售渠道」>「开发应用」
   
   c. 点击「创建应用」（如果还没有自定义应用）
   
   d. 配置 API 权限：
      - ✅ `read_orders` - 查询订单
      - ✅ `read_products` - 查询产品
      - ✅ `read_customers` - 查询客户
      - ✅ `read_fulfillments` - 查询发货
   
   e. 点击「安装应用」
   
   f. 复制「Admin API 访问令牌」

3. **重启应用**
```bash
# 如果应用正在运行，先停止（Ctrl+C）
python3 app.py
```

4. **测试查询**

在应用中提问："what is the last order?"

**应该看到日志：**
```
🔑 [Shopify] 检测到环境变量配置，自动连接...
   Shop URL: uon9.myshopify.com
✅ [Shopify] 连接成功！
```

**然后返回真实订单数据。**

### 方案 2: 通过对话配置（临时）

如果不想使用环境变量，可以在对话中配置：

```
您: 配置商店 uon9.myshopify.com shpat_xxxxx
助手: ✅ 成功连接到Shopify商店！
```

然后再提问："what is the last order?"

---

## 🧪 完整测试流程

### 1. 验证配置
```bash
python3 check_shopify_config.py
```

**期望输出：**
```
✅ Using shop URL: uon9.myshopify.com
```

### 2. 测试连接
```bash
python3 test_shopify_connection.py
```

**期望输出：**
```
✅ Connection successful!
📋 Shop Information:
   Shop Name: Your Shop Name
   Shop Domain: uon9.myshopify.com
```

### 3. 测试查询
启动应用后，提问："what is the last order?"

**应该看到日志：**
```
============================================================
🛍️ [Shopify Agent] 处理查询请求
============================================================
查询内容: what is the last order?
🔑 [Shopify] 检测到环境变量配置，自动连接...
✅ [Shopify] 连接成功！
识别意图: orders
提取参数: {'limit': 1}
🔍 [Shopify] 查询订单列表:
   返回数量: 1
✅ [Shopify] 订单列表查询成功:
   返回订单数: 1
```

**返回结果：**
```
📦 订单详情
━━━━━━━━━━━━━━━━━━━━━━
订单号: #1234
创建时间: 2025-10-27
订单状态: paid
履行状态: fulfilled
总金额: 99.99 USD

👤 客户信息:
  姓名: John Doe
  邮箱: john@example.com

📋 订单商品:
  • Product A x1 - 99.99 USD
```

---

## ❌ 常见错误

### 错误 1: 仍然返回通用说明

**可能原因：**
1. `.env` 文件不在项目根目录
2. 环境变量名拼写错误
3. 应用没有重启以加载新配置
4. 使用了旧版本代码

**解决：**
```bash
# 1. 确认 .env 文件位置
ls -la .env

# 2. 确认内容
cat .env | grep SHOPIFY

# 3. 重启应用
# Ctrl+C 停止，然后：
python3 app.py

# 4. 查看启动日志中是否有自动认证提示
```

### 错误 2: 连接失败

**日志显示：**
```
⚠️ [Shopify] 环境变量认证失败: Unauthorized
```

**解决：**
1. 验证访问令牌是否正确复制（完整的 `shpat_...`）
2. 确认令牌没有过期
3. 检查自定义应用是否已安装
4. 验证API权限是否配置正确

### 错误 3: 意图识别错误

**如果测试显示意图不是 `orders`：**

更新代码（已修复）：
- 支持 "last", "latest", "recent", "newest"
- 支持 "最后", "最新", "最近"
- 自动设置 `limit=1`

---

## 📊 工作流程图

```
用户提问："what is the last order?"
         ↓
    意图识别
         ↓
    [orders, limit=1] ✅
         ↓
    检查认证状态？
         ↓ [未认证]
    检测环境变量？
         ↓ [已配置]
    自动连接商店
         ↓ [成功]
    调用 Shopify API
         ↓
    获取订单数据
         ↓
    格式化输出
         ↓
    返回真实订单信息 ✅
```

---

## 🎯 关键检查点

使用以下命令逐一检查：

```bash
# 1. 检查配置
python3 check_shopify_config.py

# 2. 测试意图识别
python3 test_intent_detection.py

# 3. 测试连接
python3 test_shopify_connection.py

# 4. 查看应用日志（启动后查询时）
# 应该看到自动认证的日志
```

---

## 📞 获取帮助

如果按照以上步骤仍然无法解决：

1. **检查日志输出**
   - 启动应用时的日志
   - 查询时的详细日志
   - 是否看到"🔑 检测到环境变量"

2. **验证文件位置**
   ```bash
   pwd  # 确认当前目录
   ls -la .env  # 确认.env存在
   ```

3. **运行完整测试**
   ```bash
   python3 test_shopify_connection.py
   ```

4. **查看相关文档**
   - [SHOPIFY_AUTO_AUTH.md](SHOPIFY_AUTO_AUTH.md) - 自动认证功能
   - [SHOPIFY_ENV_FIX.md](SHOPIFY_ENV_FIX.md) - 环境变量修复
   - [TEST_SHOPIFY_README.md](TEST_SHOPIFY_README.md) - 测试指南

---

## ✅ 成功标志

配置成功后，您应该能够：

1. ✅ 提问"what is the last order?" 
2. ✅ 看到自动认证日志
3. ✅ 获得真实订单数据
4. ✅ 不再看到通用说明

**不需要任何手动认证步骤！**

---

**最后更新：** 2025-10-27  
**版本：** 0.4  
**状态：** ✅ 意图识别已修复，支持"last/latest/recent"关键词

