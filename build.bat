@echo off
chcp 65001 >nul
echo =====================================
echo   程序翻译器 - Windows 打包工具
echo =====================================
echo.

echo [1/3] 检查 Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo 错误：未找到 Python，请先安装 Python 3.9+
    pause
    exit /b 1
)

echo [2/3] 安装依赖...
pip install PyQt6 pyinstaller -q
if errorlevel 1 (
    echo 错误：依赖安装失败
    pause
    exit /b 1
)

echo [3/3] 打包 exe...
python -m PyInstaller --onefile --windowed --icon=icon.ico --add-data "icon.ico;." --name="translator_build" main.py

echo.
echo 重命名为中文名...
python -c "
import os, glob, shutil
dist = 'dist'
# 找到所有 exe
files = glob.glob(os.path.join(dist, '*.exe'))
print('找到文件:', files)
for f in files:
    target = os.path.join(dist, '程序翻译器.exe')
    if os.path.exists(target):
        os.remove(target)
    print(f'重命名: {f} -> {target}')
    shutil.move(f, target)
print('最终文件:', os.listdir(dist))
"

echo.
echo =====================================
if exist "dist\程序翻译器.exe" (
    echo 打包成功！
    echo   dist\程序翻译器.exe
) else (
    echo 打包失败
)
echo =====================================
pause
