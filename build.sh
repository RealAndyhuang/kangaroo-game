#!/bin/bash

echo "========================================"
echo "🦘 袋鼠沙漠大冒险 3.0 - 打包工具"
echo "========================================"
echo ""

echo "[1/4] 检查 Python 环境..."
if ! command -v python3 &> /dev/null; then
    echo "❌ 错误：未找到 Python3，请先安装 Python 3.8+"
    exit 1
fi
echo "✓ Python 环境正常 ($(python3 --version))"

echo ""
echo "[2/4] 安装依赖..."
pip3 install -r requirements.txt -q
if [ $? -ne 0 ]; then
    echo "❌ 错误：安装依赖失败"
    exit 1
fi
echo "✓ 依赖安装完成"

echo ""
echo "[3/4] 清理旧文件..."
rm -rf build dist
echo "✓ 清理完成"

echo ""
echo "[4/4] 开始打包 (这可能需要 2-5 分钟)..."
echo ""
pyinstaller --clean kangaroo_game_3.spec

if [ $? -ne 0 ]; then
    echo ""
    echo "❌ 打包失败！请检查错误信息。"
    exit 1
fi

echo ""
echo "========================================"
echo "✅ 打包成功！"
echo "========================================"
echo ""
echo "游戏位置：dist/KangarooAdventure3/KangarooAdventure3"
echo ""
echo "你可以："
echo "  1. 直接运行 dist/KangarooAdventure3/KangarooAdventure3"
echo "  2. 将整个 dist/KangarooAdventure3 文件夹复制给其他电脑"
echo ""
