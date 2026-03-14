#!/bin/bash
echo "===================================="
echo "  🦘 袋鼠沙漠大冒险 - 打包工具"
echo "===================================="
echo ""

# 检查 Python 是否安装
if ! command -v python3 &> /dev/null; then
    echo "[错误] 未检测到 Python3，请先安装 Python 3.8+"
    exit 1
fi

echo "[1/4] 检查 Python 环境..."
python3 --version

echo ""
echo "[2/4] 安装依赖包..."
pip3 install -r requirements.txt
if [ $? -ne 0 ]; then
    echo "[错误] 安装依赖失败"
    exit 1
fi

echo ""
echo "[3/4] 开始打包..."
echo "这可能需要 1-3 分钟，请耐心等待..."
pyinstaller kangaroo_game.spec --noconfirm

if [ $? -ne 0 ]; then
    echo "[错误] 打包失败"
    exit 1
fi

echo ""
echo "[4/4] 打包完成！"
echo ""
echo "===================================="
echo "  ✅ 可执行文件已生成："
if [ "$(uname)" == "Darwin" ]; then
    echo "  dist/KangarooAdventure.app"
else
    echo "  dist/KangarooAdventure"
fi
echo "===================================="
echo ""
