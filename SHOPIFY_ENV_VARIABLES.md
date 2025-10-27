# 📋 Shopify环境变量说明

## ✅ 标准变量（推荐使用）

### SHOPIFY_SHOP_URL
**描述：** 您的Shopify商店域名

**格式：** `your-shop.myshopify.com`

**示例：**
```bash
SHOPIFY_SHOP_URL=uon9.myshopify.com
```

**注意：**
- 不要包含 `https://` 前缀
- 必须使用 `.myshopify.com` 域名
- 不要使用自定义域名（如 `www.yourstore.com`）

---

### SHOPIFY_ACCESS_TOKEN
**描述：** Shopify Admin API访问令牌

**格式：** `shpat_` 开头的32位字符串

**示例：**
```bash
SHOPIFY_ACCESS_TOKEN=shpat_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

**如何获取：**
1. 登录 Shopify 管理后台
2. 进入「设置」>「应用和销售渠道」>「开发应用」
3. 创建或选择自定义应用
4. 配置 API 权限（read_orders, read_products等）
5. 安装应用并复制访问令牌

---

## ⚠️ 已弃用的变量

### SHOPIFY_SHOP_DOMAIN
**状态：** ⚠️ 已弃用，请使用 `SHOPIFY_SHOP_URL` 代替

**说明：**
- 功能与 `SHOPIFY_SHOP_URL` 完全相同
- 为了向后兼容，代码仍支持此变量
- 但所有文档和示例已统一使用 `SHOPIFY_SHOP_URL`

**迁移：**
如果您的 `.env` 文件中使用了 `SHOPIFY_SHOP_DOMAIN`：

```bash
# 旧的配置（仍然可以工作）
SHOPIFY_SHOP_DOMAIN=uon9.myshopify.com

# 请改为（推荐）
SHOPIFY_SHOP_URL=uon9.myshopify.com
```

---

## 📝 完整的 `.env` 配置示例

```bash
# Shopify Configuration
SHOPIFY_SHOP_URL=uon9.myshopify.com
SHOPIFY_ACCESS_TOKEN=shpat_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

# Flask Configuration
SECRET_KEY=your-secret-key
DEBUG=True
PORT=5050

# OpenAI (如果使用)
OPENAI_API_KEY=sk-xxxxxxxxxxxxxxxx

# Google Gemini (如果使用)
GOOGLE_API_KEY=AIxxxxxxxxxxxxxxxx

# Ollama (本地LLM)
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=deepseek-r1:latest
```

---

## ✅ 验证配置

运行检查脚本：
```bash
python3 check_shopify_config.py
```

**正确的输出：**
```
✅ .env file loaded
Environment Variables:
  SHOPIFY_SHOP_URL: uon9.myshopify.com
  SHOPIFY_ACCESS_TOKEN: ✅ Set (shpat_xxxxx...xxxxx)

✅ Will use: uon9.myshopify.com
```

**如果使用了已弃用的变量：**
```
⚠️ Note: Using deprecated SHOPIFY_SHOP_DOMAIN (uon9.myshopify.com)
   Please rename it to SHOPIFY_SHOP_URL in your .env file
```

---

## 🔧 代码中的使用

虽然我们推荐使用 `SHOPIFY_SHOP_URL`，但代码仍然支持两个变量名：

```python
# integrations/shopify_api.py
self.shop_url = (shop_url or 
                os.environ.get('SHOPIFY_SHOP_URL', '').strip() or 
                os.environ.get('SHOPIFY_SHOP_DOMAIN', '').strip())
```

**优先级：**
1. 传入的参数 `shop_url`
2. 环境变量 `SHOPIFY_SHOP_URL`
3. 环境变量 `SHOPIFY_SHOP_DOMAIN`（向后兼容）

---

## 📊 变量对比

| 特性 | SHOPIFY_SHOP_URL | SHOPIFY_SHOP_DOMAIN |
|------|------------------|---------------------|
| **状态** | ✅ 推荐使用 | ⚠️ 已弃用 |
| **功能** | 商店域名 | 商店域名（相同） |
| **文档** | ✅ 所有文档使用 | ❌ 不再推荐 |
| **代码支持** | ✅ 完全支持 | ✅ 向后兼容 |
| **示例** | ✅ 所有示例使用 | ❌ 不再出现 |

---

## 🎯 最佳实践

1. **使用标准变量**
   ```bash
   SHOPIFY_SHOP_URL=uon9.myshopify.com  ✅
   ```

2. **不要混用**
   ```bash
   # ❌ 不要同时设置两个
   SHOPIFY_SHOP_URL=shop-a.myshopify.com
   SHOPIFY_SHOP_DOMAIN=shop-b.myshopify.com
   
   # ✅ 只使用一个
   SHOPIFY_SHOP_URL=uon9.myshopify.com
   ```

3. **迁移旧配置**
   如果您已经有 `SHOPIFY_SHOP_DOMAIN`，只需重命名：
   ```bash
   # 在 .env 文件中
   # 找到：SHOPIFY_SHOP_DOMAIN=xxx
   # 改为：SHOPIFY_SHOP_URL=xxx
   ```

---

## ❓ 常见问题

### Q: 为什么改名？
**A:** 统一命名规范，避免混淆。`SHOPIFY_SHOP_URL` 更符合Shopify官方术语。

### Q: 我的旧配置还能用吗？
**A:** 可以！代码仍然支持 `SHOPIFY_SHOP_DOMAIN`，但建议改为 `SHOPIFY_SHOP_URL`。

### Q: 两个都设置会怎样？
**A:** `SHOPIFY_SHOP_URL` 优先。建议只设置一个。

### Q: 需要重启应用吗？
**A:** 是的，修改 `.env` 后需要重启应用才能生效。

---

## 📚 相关文档

- [快速设置指南](SETUP_SHOPIFY_ENV.md)
- [完整集成说明](SHOPIFY_INTEGRATION_SUMMARY.md)
- [故障排除](SHOPIFY_TROUBLESHOOTING.md)
- [快速测试](QUICK_TEST_SHOPIFY.md)

---

**最后更新：** 2025-10-27  
**变量标准化：** ✅ 完成  
**推荐使用：** `SHOPIFY_SHOP_URL`

