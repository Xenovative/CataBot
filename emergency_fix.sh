#!/bin/bash

# Emergency Fix Script for CataBot Service Failures
# Run this when the service won't start

set +e  # Don't exit on error

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${RED}╔════════════════════════════════════════════════════════╗${NC}"
echo -e "${RED}║        CataBot Emergency Fix Script                   ║${NC}"
echo -e "${RED}╚════════════════════════════════════════════════════════╝${NC}"
echo ""

if [ "$EUID" -ne 0 ]; then 
    echo -e "${RED}Please run as root (use sudo)${NC}"
    exit 1
fi

APP_DIR="/opt/catabot"

echo -e "${YELLOW}[1/8] Stopping service...${NC}"
systemctl stop catabot
echo "✓ Service stopped"
echo ""

echo -e "${YELLOW}[2/8] Checking Python dependencies...${NC}"
if [ -f "$APP_DIR/venv/bin/python3" ]; then
    cd $APP_DIR
    sudo -u catabot bash -c "source venv/bin/activate && pip install -q -r requirements.txt"
    echo "✓ Python dependencies checked/installed"
    
    # Install Playwright browsers
    sudo -u catabot bash -c "source venv/bin/activate && python3 -m playwright install chromium" 2>/dev/null
    echo "✓ Playwright browsers checked"
else
    echo -e "${RED}✗ Virtual environment not found!${NC}"
    echo "Creating new virtual environment..."
    cd $APP_DIR
    sudo -u catabot python3 -m venv venv
    sudo -u catabot bash -c "source venv/bin/activate && pip install -r requirements.txt"
    sudo -u catabot bash -c "source venv/bin/activate && python3 -m playwright install chromium"
    echo "✓ Virtual environment recreated"
fi
echo ""

echo -e "${YELLOW}[3/8] Checking .env file...${NC}"
if [ ! -f "$APP_DIR/.env" ]; then
    echo "Creating .env file..."
    
    # Copy from .env.example if available
    if [ -f "$APP_DIR/.env.example" ]; then
        cp $APP_DIR/.env.example $APP_DIR/.env
        sed -i "s/change-this-to-a-random-secret-key/$(openssl rand -hex 32)/" $APP_DIR/.env
        echo "✓ .env file created from .env.example"
    else
        # Create from scratch
        cat > $APP_DIR/.env << EOF
FLASK_ENV=production
FLASK_DEBUG=0
SECRET_KEY=$(openssl rand -hex 32)
HOST=0.0.0.0
PORT=5000
OPENAI_API_KEY=
ANTHROPIC_API_KEY=
EOF
        echo "✓ .env file created"
    fi
    
    chown catabot:catabot $APP_DIR/.env
    chmod 600 $APP_DIR/.env
else
    echo "✓ .env file exists"
fi
echo ""

echo -e "${YELLOW}[4/8] Fixing permissions and directories...${NC}"

# Ensure all required directories exist
for dir in pdfs uploads job_history logs output templates static; do
    mkdir -p $APP_DIR/$dir
done

chown -R catabot:catabot $APP_DIR
chmod -R 755 $APP_DIR
chmod -R 775 $APP_DIR/pdfs
chmod -R 775 $APP_DIR/uploads
chmod -R 775 $APP_DIR/job_history
chmod -R 775 $APP_DIR/logs
chmod -R 775 $APP_DIR/output
chmod 600 $APP_DIR/.env 2>/dev/null
echo "✓ Permissions and directories fixed"
echo ""

echo -e "${YELLOW}[5/8] Checking for port conflicts...${NC}"
PORT=$(grep '^PORT=' $APP_DIR/.env 2>/dev/null | cut -d'=' -f2 || echo "5000")
if lsof -i :$PORT &>/dev/null; then
    echo -e "${YELLOW}! Port $PORT is in use${NC}"
    echo "Processes using port $PORT:"
    lsof -i :$PORT
    read -p "Kill these processes? (y/n): " KILL_PROC
    if [ "$KILL_PROC" = "y" ]; then
        lsof -ti :$PORT | xargs kill -9 2>/dev/null
        echo "✓ Processes killed"
    fi
else
    echo "✓ Port $PORT is available"
fi
echo ""

echo -e "${YELLOW}[6/8] Testing manual startup...${NC}"
echo "Attempting to start app as catabot user..."
timeout 5 sudo -u catabot bash -c "cd $APP_DIR && source venv/bin/activate && python3 app.py" 2>&1 | head -20 &
MANUAL_PID=$!
sleep 3
if ps -p $MANUAL_PID > /dev/null 2>&1; then
    echo "✓ App starts successfully"
    kill $MANUAL_PID 2>/dev/null
else
    echo -e "${RED}✗ App failed to start manually${NC}"
    echo "Check the error above for details"
fi
echo ""

echo -e "${YELLOW}[7/8] Reloading systemd configuration...${NC}"
systemctl daemon-reload
echo "✓ Systemd reloaded"
echo ""

echo -e "${YELLOW}[8/8] Starting service...${NC}"
systemctl start catabot
sleep 2

if systemctl is-active --quiet catabot; then
    echo -e "${GREEN}✓ Service started successfully!${NC}"
    echo ""
    echo "Service status:"
    systemctl status catabot --no-pager -l | head -15
    echo ""
    echo -e "${GREEN}╔════════════════════════════════════════════════════════╗${NC}"
    echo -e "${GREEN}║              Fix completed successfully!               ║${NC}"
    echo -e "${GREEN}╚════════════════════════════════════════════════════════╝${NC}"
    echo ""
    echo "Next steps:"
    echo "  - View logs: sudo journalctl -u catabot -f"
    echo "  - Test access: curl http://localhost:$PORT"
    echo "  - Run verification: sudo ./verify_deployment.sh"
else
    echo -e "${RED}✗ Service failed to start${NC}"
    echo ""
    echo "Showing last 30 lines of logs:"
    journalctl -u catabot -n 30 --no-pager
    echo ""
    echo -e "${RED}╔════════════════════════════════════════════════════════╗${NC}"
    echo -e "${RED}║           Fix failed - manual intervention needed      ║${NC}"
    echo -e "${RED}╚════════════════════════════════════════════════════════╝${NC}"
    echo ""
    echo "Recommended actions:"
    echo "  1. Check logs: sudo journalctl -u catabot -n 100"
    echo "  2. Test manually: sudo -u catabot bash -c 'cd $APP_DIR && source venv/bin/activate && python3 app.py'"
    echo "  3. Run diagnostics: sudo ./diagnose.sh"
    echo "  4. See troubleshooting guide: cat TROUBLESHOOTING.md"
    exit 1
fi
