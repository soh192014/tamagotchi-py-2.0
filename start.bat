@echo off
chcp 65001 >nul
title 宠物养成游戏启动器

echo ===================================================
echo       🌟 正在为您直接启动宠物养成游戏 🌟
echo ===================================================
echo.

:: 直接检查游戏文件是否存在
if not exist "main.py" (
    color 0C
    echo ❌ 错误：在当前目录下找不到游戏主程序 [main.py] ！
    echo 请确保这个 .bat 文件和您的 [main.py] 放在同一个文件夹内。
    echo.
    pause
    exit
)

echo 🔄 正在自动安装/检查游戏依赖，请稍候...
:: 使用 start /b 或者是直接调用 python 执行，如果 python 不行就尝试用 py 命令
py -m pip install requests inquirer colorama python-dotenv -i https://pypi.tuna.tsinghua.edu.cn/simple >nul 2>&1

cls
echo 🚀 正在启动游戏...
echo ---------------------------------------------------

:: 核心修改：Windows 很多时候“py”命令比“python”命令更管用！
py main.py

if %errorlevel% neq 0 (
    echo.
    echo ⚠️ 如果游戏没有启动成功，请尝试下面两步：
    echo 1. 双击运行一下 main.py 看看能否打开。
    echo 2. 在这里输入：python main.py
    echo.
    python main.py
)

pause