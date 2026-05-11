#!/bin/bash

echo ""
echo "==============================================="
echo "  道路裂缝检测 Web应用启动脚本"
echo "==============================================="
echo ""

# 检查Python
if ! command -v python3 &> /dev/null; then
    echo "✗ 未找到Python 3，请先安装Python 3.8+"
    exit 1
fi

echo "✓ Python已安装"

# 检查requirements.txt
if [ ! -f "requirements.txt" ]; then
    echo "✗ requirements.txt 不存在"
    exit 1
fi

echo ""
echo "正在检查/安装依赖..."
pip3 install -r requirements.txt -q

if [ $? -ne 0 ]; then
    echo "✗ 安装依赖失败"
    exit 1
fi

echo "✓ 依赖已就绪"

# 验证配置
echo ""
echo "正在验证模型配置..."
python3 config_matcher.py

# 启动应用
echo ""
echo "==============================================="
echo "  启动Web服务器..."
echo "==============================================="
echo ""
echo "访问地址: http://localhost:5000"
echo "按 Ctrl+C 停止服务器"
echo ""
echo "==============================================="

python3 app.py
