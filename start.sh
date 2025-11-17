#!/bin/bash

# CataBot Startup Script with Error Handling
# This script provides better error messages than systemd

set -e

APP_DIR="/opt/catabot"
cd "$APP_DIR"

# Activate virtual environment
if [ ! -f "venv/bin/activate" ]; then
    echo "ERROR: Virtual environment not found at $APP_DIR/venv"
    exit 1
fi

source venv/bin/activate

# Check if .env exists
if [ ! -f ".env" ]; then
    echo "WARNING: .env file not found, using defaults"
fi

# Check Python version
PYTHON_VERSION=$(python3 --version 2>&1)
echo "Using Python: $PYTHON_VERSION"

# Check if app.py exists
if [ ! -f "app.py" ]; then
    echo "ERROR: app.py not found in $APP_DIR"
    exit 1
fi

# Test imports before starting
echo "Testing Python imports..."
python3 -c "
import sys
try:
    import flask
    print('✓ Flask imported successfully')
except ImportError as e:
    print(f'✗ Failed to import Flask: {e}')
    sys.exit(1)

try:
    import requests
    print('✓ Requests imported successfully')
except ImportError as e:
    print(f'✗ Failed to import Requests: {e}')
    sys.exit(1)

try:
    from dotenv import load_dotenv
    print('✓ python-dotenv imported successfully')
except ImportError:
    print('⚠ python-dotenv not available (optional)')

print('All critical imports successful')
" || exit 1

# Start the application
echo "Starting CataBot..."
exec python3 app.py
