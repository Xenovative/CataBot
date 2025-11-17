@echo off
chcp 65001 >nul
echo ========================================
echo CataBot 演示程式 Demo Script
echo ========================================
echo.

REM Activate virtual environment if present
if exist "venv\Scripts\activate.bat" (
    echo 🔵 Activating virtual environment...
    call venv\Scripts\activate.bat
    echo.
) else if exist ".venv\Scripts\activate.bat" (
    echo 🔵 Activating virtual environment...
    call .venv\Scripts\activate.bat
    echo.
)

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ 錯誤: 未找到 Python
    echo Error: Python not found
    echo 請先安裝 Python 3.8 或更高版本
    echo Please install Python 3.8 or higher
    pause
    exit /b 1
)

echo ✓ Python 已安裝
echo.

REM Check if dependencies are installed
echo 檢查依賴套件...
echo Checking dependencies...
python -c "import pandas" >nul 2>&1
if errorlevel 1 (
    echo.
    echo 正在安裝依賴套件...
    echo Installing dependencies...
    pip install -r requirements.txt
    if errorlevel 1 (
        echo.
        echo ❌ 安裝失敗
        echo Installation failed
        pause
        exit /b 1
    )
)

echo ✓ 依賴套件已就緒
echo.

REM Run demo
echo 開始運行演示...
echo Running demo...
echo.
python test_demo.py

echo.
echo ========================================
echo 演示完成！Demo Complete!
echo ========================================
echo.
echo 查看 demo_output 目錄中的輸出文件
echo Check output files in demo_output directory
echo.
pause
