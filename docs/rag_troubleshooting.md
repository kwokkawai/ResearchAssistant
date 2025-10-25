# RAG文档加载故障排除指南

## 🚨 常见问题

### 问题：文件夹中文档无法加载，但单个文件可以

**症状**: 测试显示"0/1 个文档加载成功"

**可能原因**:
1. 文件夹路径格式不正确
2. 文件夹权限问题
3. 文件夹为空或不包含支持的文件格式
4. 相对路径解析问题

## 🔍 诊断步骤

### 1. 使用路径测试工具

运行提供的诊断脚本：

```bash
# 测试单个文件
python test_rag_paths.py /path/to/your/document.pdf

# 测试文件夹
python test_rag_paths.py /path/to/your/documents/

# 测试多个路径
python test_rag_paths.py /path/to/file.pdf /path/to/folder/
```

### 2. 检查路径格式

#### ✅ 正确的路径格式
```
/Users/username/Documents/myfile.pdf          # 绝对路径
/Users/username/Documents/                     # 文件夹路径
./documents/myfile.pdf                         # 相对路径
~/Documents/myfile.pdf                         # 用户主目录
```

#### ❌ 错误的路径格式
```
~/Documents/myfile.pdf                          # 在Web界面中~可能无法正确解析
C:\Users\username\Documents\myfile.pdf          # Windows路径在macOS上无效
documents/myfile.pdf                           # 相对路径可能无法解析
```

### 3. 检查文件权限

```bash
# 检查文件权限
ls -la /path/to/your/file.pdf

# 检查文件夹权限
ls -la /path/to/your/folder/

# 检查上级目录权限
ls -la /path/to/your/
```

### 4. 检查支持的文件格式

**支持的格式**:
- `.pdf` - PDF文档
- `.docx` - Word文档
- `.doc` - Word文档（旧格式）
- `.md` - Markdown文件
- `.markdown` - Markdown文件
- `.txt` - 文本文件
- `.json` - JSON文件
- `.html` - HTML文件
- `.htm` - HTML文件

```bash
# 查看文件夹中的文件格式
ls -la /path/to/your/folder/
```

### 5. 检查Flask应用日志

启动应用时查看控制台输出：

```bash
python run.py
```

查找类似信息：
```
RAG API: Attempting to add document from path: '/path/to/folder'
Loading documents from directory: /absolute/path/to/folder
Found X total files/directories in /absolute/path/to/folder
Processing supported file: /path/to/folder/document.pdf
```

## 🛠️ 解决方案

### 方案1：使用绝对路径

```bash
# 获取绝对路径
pwd
# 或者
realpath /path/to/your/folder
```

然后在Web界面中使用完整的绝对路径。

### 方案2：检查文件夹内容

```bash
# 确认文件夹存在并可访问
ls -la /path/to/your/folder/

# 确认包含支持的文件
find /path/to/your/folder/ -type f \( -name "*.pdf" -o -name "*.docx" -o -name "*.md" -o -name "*.txt" \)
```

### 方案3：权限修复

```bash
# 修复文件夹权限
chmod 755 /path/to/your/folder/

# 修复文件权限
chmod 644 /path/to/your/folder/*.pdf
```

### 方案4：使用文件上传功能

如果文件夹访问有问题，可以：
1. 使用Web界面的文件上传功能
2. 或者将文件复制到应用可访问的位置

## 🔧 高级诊断

### 检查Python环境

```bash
# 确认虚拟环境已激活
which python
# 应该显示: /path/to/venv/bin/python

# 检查RAG模块导入
python -c "from rag.rag_manager import RAGManager; print('OK')"
```

### 检查系统依赖

某些文档格式需要额外的系统库：

```bash
# PDF处理 (PyPDF2)
pip install PyPDF2

# Word文档处理 (python-docx)
pip install python-docx

# 高级PDF处理 (可选)
pip install PyMuPDF
```

### 网络问题诊断

如果前端测试显示网络错误，检查：
1. Flask应用是否正常运行
2. API端点是否可访问
3. 防火墙设置

## 📝 配置示例

### 智能体RAG配置

在智能体模板配置中：

```
启用本地文档RAG: ✅
检索文档数量: 5
上下文窗口: 2
文档链接:
  /Users/username/Documents/research/
  /Users/username/Documents/papers/
  /Users/username/Desktop/manual.pdf
```

### 文件夹结构建议

```
research_project/
├── documents/           # RAG文档文件夹
│   ├── papers/         # 论文文件夹
│   ├── manuals/        # 手册文件夹
│   └── notes/          # 笔记文件夹
└── app.py              # Flask应用
```

## 🚨 如果问题持续存在

1. **检查Flask应用日志** - 寻找详细的错误信息
2. **使用路径测试脚本** - 验证路径访问
3. **尝试单个文件** - 确认基本功能正常
4. **检查文件权限** - 确保应用可以读取文件
5. **验证文件格式** - 确认文件扩展名正确

如果以上步骤都无法解决问题，请提供：
- 完整的错误信息
- 文件夹路径
- 文件夹内容列表 (`ls -la`)
- Flask应用日志输出
