# Google Gemini 模型说明

## 当前可用的Gemini模型

### 1. Gemini 1.5 Pro (`gemini-1.5-pro`)
- **描述**: 最新的高级模型，具有强大的推理和理解能力
- **特点**: 
  - 支持多达100万个token的上下文窗口
  - 多模态理解（文本、图像、音频、视频）
  - 高级推理和规划能力
- **适用场景**: 复杂任务、深度分析、多模态内容处理

### 2. Gemini 1.5 Flash (`gemini-1.5-flash`)
- **描述**: 快速响应的轻量级模型
- **特点**:
  - 更快的响应速度
  - 较低的成本
  - 保持良好的性能
- **适用场景**: 实时应用、高频查询、成本敏感的应用

### 3. Gemini Pro Vision (`gemini-pro-vision`)
- **描述**: 专门用于图像理解和分析的模型
- **特点**:
  - 强大的图像分析能力
  - 图像描述和解释
  - 多模态内容理解
- **适用场景**: 图像分析、视觉内容处理、多模态研究

### 4. Gemini Pro (`gemini-pro`)
- **描述**: 经典的中等规模模型
- **特点**:
  - 平衡性能和效率
  - 广泛的任务支持
  - 稳定的性能
- **适用场景**: 通用任务、标准应用

## 配置示例

### 环境变量配置
```bash
# 使用Gemini 1.5 Pro（推荐）
GEMINI_MODEL=gemini-1.5-pro

# 使用Gemini 1.5 Flash（快速响应）
GEMINI_MODEL=gemini-1.5-flash

# 使用Gemini Pro Vision（图像处理）
GEMINI_MODEL=gemini-pro-vision

# 使用经典Gemini Pro
GEMINI_MODEL=gemini-pro
```

### API调用示例
```python
# 在代码中动态选择模型
def get_gemini_model(task_type):
    if task_type == "image_analysis":
        return "gemini-pro-vision"
    elif task_type == "fast_response":
        return "gemini-1.5-flash"
    elif task_type == "complex_analysis":
        return "gemini-1.5-pro"
    else:
        return "gemini-pro"
```

## 模型选择建议

| 任务类型 | 推荐模型 | 原因 |
|---------|---------|------|
| 复杂研究分析 | `gemini-1.5-pro` | 最强推理能力，长上下文支持 |
| 实时交互 | `gemini-1.5-flash` | 快速响应，成本效益高 |
| 图像分析 | `gemini-pro-vision` | 专业图像理解能力 |
| 通用任务 | `gemini-pro` | 稳定可靠，广泛适用 |

## 注意事项

1. **API密钥**: 需要有效的Google API密钥
2. **配额限制**: 不同模型有不同的使用配额
3. **成本考虑**: Gemini 1.5 Pro成本较高，Flash成本较低
4. **功能差异**: 不是所有模型都支持相同的功能

## 更新历史

- **2024年2月**: Gemini 1.5系列发布
- **2023年12月**: Gemini Pro首次发布
- **2023年**: Gemini Ultra、Pro、Nano系列发布
