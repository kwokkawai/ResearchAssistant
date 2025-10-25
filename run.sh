#!/bin/bash
# 启动脚本 / Start script

echo "🔬 启动多智能体研究助手..."
echo "Starting Multi-Agent Research Assistant..."
echo ""

# 检查虚拟环境
if [ ! -d "venv" ]; then
    echo "创建虚拟环境..."
    python3 -m venv venv
fi

# 激活虚拟环境
source venv/bin/activate

# 安装依赖
echo "安装依赖..."
pip install -r requirements.txt

# 检查.env文件
if [ ! -f ".env" ]; then
    echo "⚠️  警告: .env文件不存在，使用默认配置"
    echo "请复制.env.example为.env并配置您的设置"
    cp .env.example .env
fi

# 启动应用
echo ""
echo "✅ 启动Flask应用..."
python app.py
