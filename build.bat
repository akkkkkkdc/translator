@echo off
chcp 65001 >nul
echo =====================================
echo   小欧翻译 - Windows 一键打包工具
echo =====================================
echo.

echo [1/3] 检查 Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo 错误：未找到 Python，请先安装 Python 3.9+
    echo 下载地址：https://www.python.org/downloads/
    pause
    exit /b 1
)

echo [2/3] 安装依赖（PyQt6 约 100MB，请耐心等待）...
pip install PyQt6 pyinstaller -q
if errorlevel 1 (
    echo 错误：依赖安装失败，请重试
    pause
    exit /b 1
)

echo [3/3] 打包 exe...
pyinstaller --onefile --windowed --icon=icon.ico --add-data "icon.ico;." --name="xiaoou_translator" main.py

echo.
echo =====================================
if exist "dist\xiaoou_translator.exe" (
    echo 打包成功！exe 文件在：
    echo   dist\xiaoou_translator.exe
) else (
    echo 打包失败，请检查错误信息
)
echo =====================================
pause
