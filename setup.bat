@echo off
chcp 65001 >nul
echo.
echo ╔════════════════════════════════════════════════════════════════╗
echo ║                    CataBot 安裝程式                            ║
echo ║                  CataBot Setup Script                          ║
echo ╚════════════════════════════════════════════════════════════════╝
echo.

REM Activate virtual environment if present
if exist "venv\Scripts\activate.bat" (
    echo 🔵 Activating virtual environment...
    call venv\Scripts\activate.bat
    echo ✓ Virtual environment activated
    echo.
) else if exist ".venv\Scripts\activate.bat" (
    echo 🔵 Activating virtual environment...
    call .venv\Scripts\activate.bat
    echo ✓ Virtual environment activated
    echo.
)

REM Check Python installation
echo [1/4] 檢查 Python 安裝...
echo       Checking Python installation...
python --version >nul 2>&1
if errorlevel 1 (
    echo.
    echo ❌ 錯誤: 未找到 Python
    echo    Error: Python not found
    echo.
    echo 請先安裝 Python 3.8 或更高版本
    echo Please install Python 3.8 or higher
    echo 下載地址: https://www.python.org/downloads/
    echo.
    pause
    exit /b 1
)

python --version
echo ✓ Python 已安裝
echo.

REM Check pip
echo [2/4] 檢查 pip...
echo       Checking pip...
pip --version >nul 2>&1
if errorlevel 1 (
    echo ❌ pip 未找到，正在安裝...
    python -m ensurepip --default-pip
)
echo ✓ pip 已就緒
echo.

REM Install dependencies
echo [3/4] 安裝依賴套件...
echo       Installing dependencies...
echo.
pip install -r requirements.txt
if errorlevel 1 (
    echo.
    echo ❌ 安裝失敗
    echo    Installation failed
    echo.
    pause
    exit /b 1
)
echo.
echo ✓ 依賴套件安裝完成
echo.

REM Setup environment
echo [4/4] 設定環境...
echo       Setting up environment...
if not exist ".env" (
    copy .env.example .env >nul
    echo ✓ 已創建 .env 文件
    echo   Created .env file
    echo.
    echo ⚠️  請編輯 .env 文件添加你的 OpenAI API 金鑰（可選）
    echo    Please edit .env file to add your OpenAI API key (optional)
) else (
    echo ✓ .env 文件已存在
    echo   .env file already exists
)
echo.

REM Create output directories
if not exist "output" mkdir output
if not exist "pdfs" mkdir pdfs
echo ✓ 已創建輸出目錄
echo   Created output directories
echo.

REM Installation complete
echo ╔════════════════════════════════════════════════════════════════╗
echo ║                    ✅ 安裝完成！                               ║
echo ║                  Installation Complete!                        ║
echo ╚════════════════════════════════════════════════════════════════╝
echo.
echo 下一步 Next Steps:
echo.
echo 1. 運行演示程式 Run demo:
echo    run_demo.bat
echo    或 or: python test_demo.py
echo.
echo 2. 處理真實 PDF Process real PDFs:
echo    python main.py --directory ./your_papers
echo.
echo 3. 查看文檔 Read documentation:
echo    - README.md
echo    - QUICKSTART.md
echo    - PROJECT_OVERVIEW.md
echo.
echo 4. (可選) 配置 API 金鑰 (Optional) Configure API key:
echo    編輯 .env 文件
echo    Edit .env file
echo.
pause
