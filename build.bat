@echo off
chcp 65001 >nul
echo =====================================
echo   translator - Windows Build Tool
echo =====================================
echo.

echo [1/3] Check Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python not found
    pause
    exit /b 1
)

echo [2/3] Install dependencies...
pip install PyQt6 pyinstaller -q
if errorlevel 1 (
    echo Error: Install failed
    pause
    exit /b 1
)

echo [3/3] Build exe...
python -m PyInstaller --onefile --windowed --icon=icon.ico --name="translator" main.py

echo.
echo =====================================
if exist "dist\translator.exe" (
    echo Build OK:
    echo   dist\translator.exe
) else (
    echo Build failed
)
echo =====================================
pause
