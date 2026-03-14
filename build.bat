@echo off
echo ====================================
echo   🦘 袋鼠沙漠大冒险 - 打包工具
echo ====================================
echo.

REM 检查 Python 是否安装
python --version >nul 2>&1
if errorlevel 1 (
    echo [错误] 未检测到 Python，请先安装 Python 3.8+
    echo 下载地址：https://www.python.org/downloads/
    pause
    exit /b 1
)

echo [1/4] 检查 Python 环境...
python --version

echo.
echo [2/4] 安装依赖包...
pip install -r requirements.txt
if errorlevel 1 (
    echo [错误] 安装依赖失败
    pause
    exit /b 1
)

echo.
echo [3/4] 开始打包成 EXE...
echo 这可能需要 1-3 分钟，请耐心等待...
pyinstaller kangaroo_game.spec --noconfirm

if errorlevel 1 (
    echo [错误] 打包失败
    pause
    exit /b 1
)

echo.
echo [4/4] 打包完成！
echo.
echo ====================================
echo   ✅ 可执行文件已生成：
echo   dist\KangarooAdventure.exe
echo ====================================
echo.
echo 你可以：
echo 1. 直接双击 dist\KangarooAdventure.exe 运行游戏
echo 2. 将整个 dist 文件夹发给朋友
echo 3. 把 KangarooAdventure.exe 复制到任意位置运行
echo.
echo 按任意键退出...
pause >nul
