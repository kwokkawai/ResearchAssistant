# GitHub 版本管理指南

## 🚀 新版本开发Git工作流程

### 1. 确保当前工作区干净
```bash
# 检查当前状态
git status

# 如果有未提交的更改，先提交或暂存
git add .
git commit -m "完成v0.3版本开发"
```

### 2. 创建新版本分支
```bash
# 从当前分支创建新版本分支
git checkout -b version-0.4

# 或者从main/master分支创建（推荐）
git checkout main  # 或 master
git pull origin main  # 确保是最新版本
git checkout -b version-0.4
```

### 3. 推送新分支到远程仓库
```bash
# 推送新分支到GitHub
git push -u origin version-0.4
```

### 4. 为新版本打标签（可选但推荐）
```bash
# 为当前v0.3版本打标签
git checkout version-0.3
git tag -a v0.3.0 -m "Release version 0.3.0"
git push origin v0.3.0

# 切换回新版本分支继续开发
git checkout version-0.4
```

### 5. 日常开发工作流程
```bash
# 创建功能分支
git checkout -b feature/new-feature-name

# 开发完成后合并到版本分支
git checkout version-0.4
git merge feature/new-feature-name

# 删除功能分支
git branch -d feature/new-feature-name
```

### 6. 版本发布流程
```bash
# 完成开发后，合并到主分支
git checkout main
git merge version-0.4

# 打版本标签
git tag -a v0.4.0 -m "Release version 0.4.0"

# 推送所有更改
git push origin main
git push origin v0.4.0
```

## 📋 推荐的版本管理策略

### 分支命名规范
- `main/master`: 主分支，稳定版本
- `version-X.Y`: 版本开发分支
- `feature/功能名`: 功能开发分支
- `hotfix/修复名`: 紧急修复分支

### 版本号规范
- **主版本号**: 重大架构变更
- **次版本号**: 新功能添加
- **修订号**: 错误修复和小改进

### 提交信息规范
```bash
# 功能添加
git commit -m "feat: 添加新的智能体类型"

# 错误修复
git commit -m "fix: 修复Ollama连接超时问题"

# 文档更新
git commit -m "docs: 更新API使用说明"

# 性能优化
git commit -m "perf: 优化LLM响应速度"
```

## 🔧 针对ResearchAssistant项目的具体建议

基于你的ResearchAssistant项目，我建议：

1. **保持v0.3分支稳定**: 用于bug修复和紧急更新
2. **在v0.4分支开发新功能**: 如用户认证、性能分析等
3. **使用功能分支**: 每个新功能独立开发
4. **定期合并**: 避免分支差异过大

## 📚 常用Git命令速查

### 分支操作
```bash
# 查看所有分支
git branch -a

# 切换分支
git checkout branch-name

# 创建并切换分支
git checkout -b new-branch

# 删除本地分支
git branch -d branch-name

# 删除远程分支
git push origin --delete branch-name
```

### 标签操作
```bash
# 查看所有标签
git tag

# 创建标签
git tag -a v1.0.0 -m "Release version 1.0.0"

# 推送标签
git push origin v1.0.0

# 推送所有标签
git push origin --tags
```

### 合并和变基
```bash
# 合并分支
git merge feature-branch

# 变基（保持线性历史）
git rebase main

# 交互式变基
git rebase -i HEAD~3
```

### 撤销操作
```bash
# 撤销最后一次提交
git reset --soft HEAD~1

# 撤销工作区更改
git checkout -- filename

# 撤销暂存区更改
git reset HEAD filename
```

## 🚨 注意事项

1. **永远不要强制推送主分支**: `git push --force` 会覆盖历史
2. **合并前先拉取**: `git pull origin main` 确保最新
3. **使用有意义的分支名**: 便于团队协作
4. **定期备份**: 重要更改前先备份
5. **测试后再合并**: 确保代码质量

---

**提示**: 这个指南适用于ResearchAssistant项目的版本管理，可以根据项目需要调整分支命名和版本号规范。
