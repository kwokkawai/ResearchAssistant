# 🚀 Git推送指南 - ResearchAssistant v0.3

## 📊 当前状态

**分支**: `version-0.3`  
**主要更新**: 
- ✅ 6个专业级智能体Prompt
- ✅ 智能体-模板分离架构
- ✅ 本地文档RAG功能
- ✅ 项目清理（删除84个测试文件）
- ✅ README.md完整更新

---

## 🔍 当前Git状态分析

### 已修改的核心文件
```
modified:   README.md                      # 完整更新
modified:   agents/agent_manager.py        # RAG集成、模板配置
modified:   app.py                         # 新增API、RAG路由
modified:   data/agent_definitions.json    # 6个智能体Prompt更新
modified:   management/agent_manager.py    # 模板管理重构
modified:   rag/rag_manager.py            # RAG核心逻辑
modified:   rag/vector_store.py           # 向量数据库
modified:   templates/index.html          # UI重构、RAG配置
```

### 已删除的文件
```
deleted:    data/templates.json           # 已合并到agent_definitions.json
deleted:    test_*.py (84个测试文件)      # 项目清理
```

### 新增的文件
```
docs/RAG_DIAGNOSTIC_GUIDE.md             # RAG诊断指南
docs/RAG_NETWORK_ISSUE.md                # RAG网络问题说明
```

### 不建议提交的文件
```
data/vector_store/*                       # 向量数据库（用户数据）
documents/.document_tracking.json         # 文档追踪（运行时数据）
```

---

## 📝 推荐的Git操作流程

### 步骤1: 查看并确认更改

```bash
# 进入项目目录
cd /Users/pkwok/Projects/46.\ ResearchAssistant/Release/ResearchAssistant_0.3/ResearchAssistant

# 查看详细的文件变更
git status

# 查看具体的代码变更（可选）
git diff README.md
git diff data/agent_definitions.json
```

### 步骤2: 添加核心文件到暂存区

```bash
# 添加核心应用文件
git add README.md
git add agents/agent_manager.py
git add app.py
git add data/agent_definitions.json
git add management/agent_manager.py
git add rag/rag_manager.py
git add rag/vector_store.py
git add templates/index.html

# 添加新文档
git add docs/RAG_DIAGNOSTIC_GUIDE.md
git add docs/RAG_NETWORK_ISSUE.md

# 确认删除的文件
git rm data/templates.json
git rm test_force_reload.py
git rm test_rag_integration.py
git rm test_rag_paths.py
git rm test_rag_query.py
```

### 步骤3: 忽略不需要提交的文件

创建或更新`.gitignore`文件：

```bash
# 检查.gitignore是否存在
cat .gitignore

# 如果需要，添加以下内容到.gitignore
cat >> .gitignore << 'EOF'

# 向量数据库（用户数据）
data/vector_store/*
!data/vector_store/.gitkeep

# 文档追踪
documents/.document_tracking.json
documents/*
!documents/.gitkeep

# Python缓存
__pycache__/
*.pyc
*.pyo
*.pyd
.Python
*.so

# 虚拟环境
venv/
env/
ENV/

# 环境变量
.env
.env.local

# IDE
.vscode/
.idea/
*.swp
*.swo
*~

# 日志
*.log
logs/

# 临时文件
*.tmp
*.bak
*.backup
.DS_Store
EOF
```

### 步骤4: 提交更改

```bash
# 提交所有已添加的文件
git commit -m "feat: ResearchAssistant v0.3 - 专业级智能体与RAG功能

主要更新:
- ✨ 6个专业级智能体（行业最佳实践Prompt）
  - 研究助手: 系统性思维框架
  - 学术专家: 完整学术指导
  - 商业分析师: PEST分析、波特五力
  - 创意专家: SCAMPER技法、设计思维
  - 法律顾问: 法律分析、风险评估
  - 技术专家: 技术解决方案

- 🏗️ 架构重构
  - 智能体-模板分离架构
  - 模板配置系统
  - 动态Ollama模型加载

- 📚 本地文档RAG功能
  - ChromaDB向量数据库
  - Sentence Transformers语义检索
  - 多格式文档支持（PDF/Word/MD/JSON/HTML/TXT）
  - 100%私有数据保护

- 🌐 功能增强
  - 网络搜索和RAG互斥控制
  - 搜索结果卡片式展示
  - 模板配置UI重构
  - 详细的配置管理

- 🧹 项目优化
  - 清理84个测试和临时文件
  - 完整更新README.md（786行）
  - 新增RAG诊断文档

- 🐛 Bug修复
  - 修复模板配置保存问题
  - 修复Ollama模型配置丢失
  - 修复JSON解析错误
  - 修复网络搜索结果显示

Breaking Changes:
- data/templates.json 已合并到 data/agent_definitions.json
- 智能体配置从直接配置改为模板引用

Migration Guide:
- 旧版智能体配置会自动迁移到新架构
- 无需手动操作"
```

### 步骤5: 推送到GitHub

```bash
# 推送到远程仓库的version-0.3分支
git push origin version-0.3

# 如果是首次推送该分支
git push -u origin version-0.3
```

---

## 🔀 可选：创建Pull Request合并到主分支

如果您想将v0.3合并到主分支：

### 方法1: 通过GitHub Web界面

1. 访问您的GitHub仓库
2. 点击 "Pull requests" 标签
3. 点击 "New pull request"
4. Base: `main` (或 `master`) ← Compare: `version-0.3`
5. 填写PR标题和描述：

**标题**: `Release v0.3: 专业级智能体与RAG功能`

**描述**:
```markdown
## 🚀 ResearchAssistant v0.3 发布

### 主要特性
- 6个专业级智能体（最佳实践Prompt）
- 本地文档RAG功能（ChromaDB + Sentence Transformers）
- 智能体-模板分离架构
- 动态Ollama模型加载
- 网络搜索和RAG互斥控制

### 重大变更
- 架构重构：智能体-模板分离
- 清理84个测试文件
- README.md完整更新

### 文档
- [x] README.md已更新
- [x] RAG诊断指南已添加
- [x] 使用指南已完善

### 测试
- [x] 所有核心功能已测试
- [x] JSON配置验证通过
- [x] Flask应用正常运行

### Breaking Changes
⚠️ `data/templates.json` 已移除，配置已合并到 `data/agent_definitions.json`

### Migration
无需手动迁移，系统会自动处理。
```

6. 点击 "Create pull request"
7. 等待审核（或自己审核）
8. 点击 "Merge pull request"

### 方法2: 通过命令行合并

```bash
# 切换到主分支
git checkout main  # 或 master

# 合并version-0.3分支
git merge version-0.3

# 推送到远程主分支
git push origin main
```

---

## 🏷️ 可选：创建版本标签

创建v0.3标签以标记这个重要版本：

```bash
# 创建带注释的标签
git tag -a v0.3 -m "Release v0.3: 专业级智能体与RAG功能

主要特性:
- 6个专业级智能体
- 本地文档RAG功能
- 智能体-模板分离架构
- 动态Ollama模型加载

发布日期: 2025-10-26"

# 推送标签到远程
git push origin v0.3

# 或推送所有标签
git push origin --tags
```

在GitHub上，这会自动创建一个Release，您可以：
1. 访问仓库的 "Releases" 页面
2. 点击标签旁的 "Create release from tag"
3. 填写Release说明
4. 可选：上传编译后的文件或安装包

---

## 📋 完整的推送命令（一键复制）

```bash
# 1. 进入项目目录
cd /Users/pkwok/Projects/46.\ ResearchAssistant/Release/ResearchAssistant_0.3/ResearchAssistant

# 2. 查看状态
git status

# 3. 添加所有核心文件
git add README.md agents/agent_manager.py app.py data/agent_definitions.json management/agent_manager.py rag/rag_manager.py rag/vector_store.py templates/index.html docs/RAG_DIAGNOSTIC_GUIDE.md docs/RAG_NETWORK_ISSUE.md

# 4. 确认删除文件
git rm data/templates.json test_force_reload.py test_rag_integration.py test_rag_paths.py test_rag_query.py

# 5. 提交
git commit -m "feat: ResearchAssistant v0.3 - 专业级智能体与RAG功能

主要更新:
- ✨ 6个专业级智能体（行业最佳实践Prompt）
- 🏗️ 智能体-模板分离架构
- 📚 本地文档RAG功能（ChromaDB + Sentence Transformers）
- 🌐 网络搜索和RAG互斥控制
- 🧹 清理84个测试文件，完整更新README
- 🐛 多项Bug修复和性能优化

Breaking Changes:
- data/templates.json 已合并到 data/agent_definitions.json"

# 6. 推送
git push origin version-0.3

# 7. 可选：创建标签
git tag -a v0.3 -m "Release v0.3: 专业级智能体与RAG功能"
git push origin v0.3
```

---

## ⚠️ 推送前检查清单

在执行推送前，请确认：

- [ ] 所有测试文件已清理（84个文件）
- [ ] README.md已更新且准确
- [ ] 核心功能正常工作（已验证Flask应用运行）
- [ ] JSON配置文件格式正确
- [ ] .gitignore已配置（排除向量数据库和用户数据）
- [ ] 提交信息清晰描述了所有主要更改
- [ ] 没有敏感信息（API密钥、密码等）

---

## 🔒 安全提示

### 确保不要提交敏感信息：

```bash
# 检查是否有.env文件被跟踪
git ls-files | grep .env

# 如果有，立即取消跟踪
git rm --cached .env
echo ".env" >> .gitignore

# 检查data/agent_definitions.json中是否有API密钥
grep -i "api.*key" data/agent_definitions.json

# 确保向量数据库不被提交
git rm -r --cached data/vector_store/
echo "data/vector_store/*" >> .gitignore
```

---

## 🚨 如果推送失败

### 错误1: 远程有更新
```bash
error: failed to push some refs to 'origin'
hint: Updates were rejected because the remote contains work that you do not have locally
```

**解决方案**:
```bash
# 先拉取远程更改
git pull origin version-0.3 --rebase

# 解决冲突（如果有）
# 编辑冲突文件，然后：
git add <冲突文件>
git rebase --continue

# 重新推送
git push origin version-0.3
```

### 错误2: 没有权限
```bash
ERROR: Permission to user/repo.git denied to user
```

**解决方案**:
```bash
# 检查远程仓库URL
git remote -v

# 如果需要，更新为SSH URL
git remote set-url origin git@github.com:用户名/仓库名.git

# 或使用HTTPS（需要token）
git remote set-url origin https://github.com/用户名/仓库名.git
```

### 错误3: 文件过大
```bash
remote: error: File is too large
```

**解决方案**:
```bash
# 检查大文件
git ls-files | xargs ls -lh | sort -k5 -rh | head -10

# 取消大文件的跟踪
git rm --cached <大文件>
echo "<大文件>" >> .gitignore

# 修改提交
git commit --amend
```

---

## 📊 推送后验证

推送成功后，验证：

1. **GitHub上查看**:
   - 访问 `https://github.com/用户名/ResearchAssistant`
   - 切换到 `version-0.3` 分支
   - 确认所有文件已更新
   - 查看提交历史

2. **本地验证**:
```bash
# 查看提交历史
git log --oneline -5

# 查看远程分支状态
git remote show origin

# 确认标签（如果创建了）
git tag -l
```

3. **克隆测试**（可选）:
```bash
# 在另一个目录克隆仓库
cd /tmp
git clone https://github.com/用户名/ResearchAssistant.git test-clone
cd test-clone
git checkout version-0.3

# 验证文件完整性
ls -la
cat README.md | head -20
```

---

## 🎉 推送完成后

恭喜！您的ResearchAssistant v0.3已成功推送到GitHub！

### 下一步建议：

1. **创建Release** (推荐)
   - 在GitHub上创建v0.3 Release
   - 添加更新日志
   - 可选：附加安装包或文档

2. **更新文档**
   - 在GitHub Wiki中添加详细文档
   - 更新项目主页链接

3. **通知用户**
   - 发布更新公告
   - 提供升级指南

4. **持续开发**
   - 创建v0.4开发分支
   - 规划下一阶段功能

---

**准备好推送了吗？** 🚀

按照上面的步骤执行，或使用"完整的推送命令"一键复制执行！

