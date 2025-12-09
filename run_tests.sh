#!/bin/bash
# 运行测试脚本

set -e

echo "🔍 检查依赖..."
if ! python3 -c "import rapidfuzz" 2>/dev/null; then
    echo "❌ rapidfuzz 未安装，正在安装..."
    pip3 install rapidfuzz>=3.0.0,<4.0.0
fi

if ! python3 -c "import pytest" 2>/dev/null; then
    echo "❌ pytest 未安装，正在安装..."
    pip3 install pytest>=7.0.0,<8.0.0
fi

echo "✅ 依赖检查完成"
echo ""
echo "🧪 运行测试..."
python3 -m pytest tests/ -v --tb=short

echo ""
echo "✅ 测试完成！"
