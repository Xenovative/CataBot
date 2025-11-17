@echo off
chcp 65001 >nul
echo.
echo ╔════════════════════════════════════════════════════════════════╗
echo ║              CataBot Web Application Launcher                  ║
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

REM Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python not found
    pause
    exit /b 1
)

REM Check Flask
python -c "import flask" >nul 2>&1
if errorlevel 1 (
    echo Installing Flask...
    pip install flask flask-cors werkzeug
)

echo 🚀 Starting CataBot Web Application...
echo.
echo 📍 Access at: http://localhost:5000
echo 🛑 Press Ctrl+C to stop
echo.

python app.py

pause
