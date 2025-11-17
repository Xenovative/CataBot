@echo off
chcp 65001 >nul
echo.
echo ╔════════════════════════════════════════════════════════════════╗
echo ║           Create Virtual Environment for CataBot              ║
echo ╚════════════════════════════════════════════════════════════════╝
echo.

REM Check if virtual environment already exists
if exist "venv" (
    echo ⚠️  Virtual environment already exists at 'venv'
    echo.
    choice /C YN /M "Do you want to recreate it? (Y/N)"
    if errorlevel 2 goto :end
    echo.
    echo Removing existing virtual environment...
    rmdir /s /q venv
)

REM Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python not found
    echo Please install Python 3.8 or higher
    pause
    exit /b 1
)

echo [1/3] Creating virtual environment...
python -m venv venv
if errorlevel 1 (
    echo ❌ Failed to create virtual environment
    pause
    exit /b 1
)
echo ✓ Virtual environment created
echo.

echo [2/3] Activating virtual environment...
call venv\Scripts\activate.bat
echo ✓ Virtual environment activated
echo.

echo [3/3] Installing dependencies...
python -m pip install --upgrade pip
pip install -r requirements.txt
if errorlevel 1 (
    echo ❌ Failed to install dependencies
    pause
    exit /b 1
)
echo ✓ Dependencies installed
echo.

echo ╔════════════════════════════════════════════════════════════════╗
echo ║                    ✅ Setup Complete!                          ║
echo ╚════════════════════════════════════════════════════════════════╝
echo.
echo Virtual environment created at: venv\
echo.
echo To activate manually:
echo   venv\Scripts\activate.bat
echo.
echo To deactivate:
echo   deactivate
echo.
echo All batch files will now automatically use this virtual environment!
echo.
echo Next steps:
echo   1. run_demo.bat       - Run demo
echo   2. run_webapp.bat     - Launch web interface
echo   3. python main.py     - Use command line
echo.

:end
pause
