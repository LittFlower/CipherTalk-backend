#!/bin/bash

# 聊天后端启动脚本

echo "=== 聊天后端启动脚本 ==="

# 检查Python环境
if ! command -v python3 &> /dev/null; then
    echo "错误: 未找到Python3，请先安装Python3"
    exit 1
fi

# 检查pip
if ! command -v pip3 &> /dev/null; then
    echo "错误: 未找到pip3，请先安装pip3"
    exit 1
fi

# 创建虚拟环境（可选）
if [ ! -d "venv" ]; then
    echo "创建虚拟环境..."
    python3 -m venv venv
fi

# 激活虚拟环境
echo "激活虚拟环境..."
source venv/bin/activate

# 安装依赖
echo "安装依赖包..."
pip install -r requirements.txt

# 检查环境变量文件
if [ ! -f ".env" ]; then
    echo "警告: 未找到.env文件，请复制.env.example并配置数据库连接信息"
    echo "cp .env.example .env"
    echo "然后编辑.env文件设置数据库配置"
    exit 1
fi

# 启动应用
echo "启动聊天后端应用..."
python app.py
