#!/bin/bash

# CataBot Diagnostic Script
# Run this to diagnose deployment issues

set +e  # Don't exit on error

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

APP_DIR="/opt/catabot"
APP_USER="catabot"
SERVICE_NAME="catabot"

echo -e "${GREEN}=== CataBot Diagnostic Tool ===${NC}"
echo ""

# Check if running as root
if [ "$EUID" -ne 0 ]; then 
    echo -e "${YELLOW}Note: Some checks require root. Run with sudo for complete diagnostics.${NC}"
    echo ""
fi

# 1. Check if application directory exists
echo -e "${YELLOW}[1] Checking application directory...${NC}"
if [ -d "$APP_DIR" ]; then
    echo -e "${GREEN}✓${NC} Directory exists: $APP_DIR"
    ls -la $APP_DIR | head -10
else
    echo -e "${RED}✗${NC} Directory not found: $APP_DIR"
fi
echo ""

# 2. Check if user exists
echo -e "${YELLOW}[2] Checking application user...${NC}"
if id "$APP_USER" &>/dev/null; then
    echo -e "${GREEN}✓${NC} User exists: $APP_USER"
    id $APP_USER
else
    echo -e "${RED}✗${NC} User not found: $APP_USER"
fi
echo ""

# 3. Check Python virtual environment
echo -e "${YELLOW}[3] Checking Python virtual environment...${NC}"
if [ -f "$APP_DIR/venv/bin/python3" ]; then
    echo -e "${GREEN}✓${NC} Virtual environment exists"
    $APP_DIR/venv/bin/python3 --version
    
    # Check key dependencies
    echo "Checking dependencies..."
    $APP_DIR/venv/bin/python3 -c "import flask; print('  Flask:', flask.__version__)" 2>&1
    $APP_DIR/venv/bin/python3 -c "import requests; print('  Requests:', requests.__version__)" 2>&1
    $APP_DIR/venv/bin/python3 -c "import openai; print('  OpenAI:', openai.__version__)" 2>&1
else
    echo -e "${RED}✗${NC} Virtual environment not found"
fi
echo ""

# 4. Check .env file
echo -e "${YELLOW}[4] Checking environment configuration...${NC}"
if [ -f "$APP_DIR/.env" ]; then
    echo -e "${GREEN}✓${NC} .env file exists"
    ls -la $APP_DIR/.env
    echo "Environment variables (keys only):"
    grep -v '^#' $APP_DIR/.env | grep '=' | cut -d'=' -f1 | sed 's/^/  /'
else
    echo -e "${RED}✗${NC} .env file not found"
fi
echo ""

# 5. Check systemd service
echo -e "${YELLOW}[5] Checking systemd service...${NC}"
if [ -f "/etc/systemd/system/${SERVICE_NAME}.service" ]; then
    echo -e "${GREEN}✓${NC} Service file exists"
    
    # Check service status
    if systemctl is-active --quiet $SERVICE_NAME; then
        echo -e "${GREEN}✓${NC} Service is running"
    else
        echo -e "${RED}✗${NC} Service is not running"
    fi
    
    if systemctl is-enabled --quiet $SERVICE_NAME; then
        echo -e "${GREEN}✓${NC} Service is enabled"
    else
        echo -e "${YELLOW}!${NC} Service is not enabled (won't start on boot)"
    fi
    
    echo ""
    echo "Service status:"
    systemctl status $SERVICE_NAME --no-pager -l | head -20
else
    echo -e "${RED}✗${NC} Service file not found"
fi
echo ""

# 6. Check logs
echo -e "${YELLOW}[6] Checking application logs...${NC}"
if [ -d "$APP_DIR/logs" ]; then
    echo -e "${GREEN}✓${NC} Logs directory exists"
    ls -lh $APP_DIR/logs/
    
    if [ -f "$APP_DIR/logs/error.log" ]; then
        echo ""
        echo "Recent errors (last 10 lines):"
        tail -10 $APP_DIR/logs/error.log
    fi
else
    echo -e "${RED}✗${NC} Logs directory not found"
fi
echo ""

# 7. Check recent journal logs
echo -e "${YELLOW}[7] Checking systemd journal logs...${NC}"
echo "Last 20 lines from service:"
journalctl -u $SERVICE_NAME -n 20 --no-pager 2>/dev/null || echo "Cannot access journal (need root)"
echo ""

# 8. Check port availability
echo -e "${YELLOW}[8] Checking port availability...${NC}"
PORT=$(grep '^PORT=' $APP_DIR/.env 2>/dev/null | cut -d'=' -f2 || echo "5000")
if lsof -i :$PORT &>/dev/null; then
    echo -e "${YELLOW}!${NC} Port $PORT is in use"
    lsof -i :$PORT
else
    echo -e "${GREEN}✓${NC} Port $PORT is available"
fi
echo ""

# 9. Check Nginx
echo -e "${YELLOW}[9] Checking Nginx configuration...${NC}"
if [ -f "/etc/nginx/sites-available/${SERVICE_NAME}" ]; then
    echo -e "${GREEN}✓${NC} Nginx config exists"
    
    if [ -L "/etc/nginx/sites-enabled/${SERVICE_NAME}" ]; then
        echo -e "${GREEN}✓${NC} Nginx site is enabled"
    else
        echo -e "${YELLOW}!${NC} Nginx site is not enabled"
    fi
    
    # Test Nginx config
    nginx -t 2>&1 | head -5
else
    echo -e "${RED}✗${NC} Nginx config not found"
fi
echo ""

# 10. Check permissions
echo -e "${YELLOW}[10] Checking file permissions...${NC}"
if [ -d "$APP_DIR" ]; then
    echo "Application directory:"
    ls -ld $APP_DIR
    
    echo "Key directories:"
    for dir in pdfs uploads job_history logs; do
        if [ -d "$APP_DIR/$dir" ]; then
            ls -ld $APP_DIR/$dir
        else
            echo -e "${RED}✗${NC} Missing: $APP_DIR/$dir"
        fi
    done
fi
echo ""

# Summary
echo -e "${GREEN}=== Diagnostic Complete ===${NC}"
echo ""
echo "Common fixes:"
echo "  1. If service won't start: sudo systemctl restart catabot"
echo "  2. If .env missing: Create it with required variables"
echo "  3. If permissions wrong: sudo chown -R catabot:catabot /opt/catabot"
echo "  4. If dependencies missing: cd /opt/catabot && source venv/bin/activate && pip install -r requirements.txt"
echo "  5. View live logs: sudo journalctl -u catabot -f"
echo ""
