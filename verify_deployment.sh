#!/bin/bash

# CataBot Deployment Verification Script
# Run this after deployment to verify everything is working

set +e  # Don't exit on error

GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

PASSED=0
FAILED=0
WARNINGS=0

echo -e "${GREEN}╔════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║     CataBot Deployment Verification Script            ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════════════════════╝${NC}"
echo ""

# Function to print test result
test_result() {
    local test_name="$1"
    local result="$2"
    local message="$3"
    
    if [ "$result" = "pass" ]; then
        echo -e "${GREEN}✓${NC} $test_name"
        ((PASSED++))
    elif [ "$result" = "fail" ]; then
        echo -e "${RED}✗${NC} $test_name"
        if [ -n "$message" ]; then
            echo -e "  ${RED}→${NC} $message"
        fi
        ((FAILED++))
    elif [ "$result" = "warn" ]; then
        echo -e "${YELLOW}!${NC} $test_name"
        if [ -n "$message" ]; then
            echo -e "  ${YELLOW}→${NC} $message"
        fi
        ((WARNINGS++))
    fi
}

# Test 1: Check if running as root
echo -e "${YELLOW}[System Checks]${NC}"
if [ "$EUID" -eq 0 ]; then
    test_result "Running as root/sudo" "pass"
else
    test_result "Running as root/sudo" "warn" "Some checks may be limited without root access"
fi

# Test 2: Check application directory
if [ -d "/opt/catabot" ]; then
    test_result "Application directory exists" "pass"
else
    test_result "Application directory exists" "fail" "/opt/catabot not found"
fi

# Test 3: Check application user
if id "catabot" &>/dev/null; then
    test_result "Application user exists" "pass"
else
    test_result "Application user exists" "fail" "User 'catabot' not found"
fi

# Test 4: Check required directories
echo ""
echo -e "${YELLOW}[Directory Structure]${NC}"
for dir in pdfs uploads job_history logs; do
    if [ -d "/opt/catabot/$dir" ]; then
        test_result "Directory: $dir" "pass"
    else
        test_result "Directory: $dir" "fail" "Missing directory"
    fi
done

# Test 5: Check Python virtual environment
echo ""
echo -e "${YELLOW}[Python Environment]${NC}"
if [ -f "/opt/catabot/venv/bin/python3" ]; then
    test_result "Virtual environment" "pass"
    
    # Check Python version
    PYTHON_VERSION=$(/opt/catabot/venv/bin/python3 --version 2>&1)
    echo -e "  ${GREEN}→${NC} $PYTHON_VERSION"
else
    test_result "Virtual environment" "fail" "venv not found"
fi

# Test 6: Check Python dependencies
if [ -f "/opt/catabot/venv/bin/python3" ]; then
    DEPS=("flask" "requests" "openai" "beautifulsoup4" "PyPDF2")
    for dep in "${DEPS[@]}"; do
        if /opt/catabot/venv/bin/python3 -c "import ${dep,,}" 2>/dev/null; then
            test_result "Dependency: $dep" "pass"
        else
            test_result "Dependency: $dep" "fail" "Module not installed"
        fi
    done
fi

# Test 7: Check configuration files
echo ""
echo -e "${YELLOW}[Configuration Files]${NC}"
if [ -f "/opt/catabot/.env" ]; then
    test_result ".env file exists" "pass"
    
    # Check if .env has required variables
    REQUIRED_VARS=("FLASK_ENV" "SECRET_KEY" "HOST" "PORT")
    for var in "${REQUIRED_VARS[@]}"; do
        if grep -q "^${var}=" /opt/catabot/.env 2>/dev/null; then
            test_result "  Variable: $var" "pass"
        else
            test_result "  Variable: $var" "warn" "Not set in .env"
        fi
    done
    
    # Check .env permissions
    PERMS=$(stat -c "%a" /opt/catabot/.env 2>/dev/null)
    if [ "$PERMS" = "600" ]; then
        test_result ".env permissions (600)" "pass"
    else
        test_result ".env permissions" "warn" "Current: $PERMS, recommended: 600"
    fi
else
    test_result ".env file exists" "fail" "File not found"
fi

if [ -f "/opt/catabot/requirements.txt" ]; then
    test_result "requirements.txt exists" "pass"
else
    test_result "requirements.txt exists" "fail" "File not found"
fi

if [ -f "/opt/catabot/app.py" ]; then
    test_result "app.py exists" "pass"
else
    test_result "app.py exists" "fail" "File not found"
fi

# Test 8: Check systemd service
echo ""
echo -e "${YELLOW}[Systemd Service]${NC}"
if [ -f "/etc/systemd/system/catabot.service" ]; then
    test_result "Service file exists" "pass"
    
    # Check if service is enabled
    if systemctl is-enabled --quiet catabot 2>/dev/null; then
        test_result "Service enabled" "pass"
    else
        test_result "Service enabled" "warn" "Service won't start on boot"
    fi
    
    # Check if service is active
    if systemctl is-active --quiet catabot 2>/dev/null; then
        test_result "Service running" "pass"
    else
        test_result "Service running" "fail" "Service is not active"
    fi
    
    # Check if EnvironmentFile is set
    if grep -q "EnvironmentFile=/opt/catabot/.env" /etc/systemd/system/catabot.service 2>/dev/null; then
        test_result "EnvironmentFile configured" "pass"
    else
        test_result "EnvironmentFile configured" "fail" "Missing in service file"
    fi
else
    test_result "Service file exists" "fail" "File not found"
fi

# Test 9: Check Nginx
echo ""
echo -e "${YELLOW}[Nginx Configuration]${NC}"
if command -v nginx &> /dev/null; then
    test_result "Nginx installed" "pass"
    
    if [ -f "/etc/nginx/sites-available/catabot" ]; then
        test_result "Nginx config exists" "pass"
    else
        test_result "Nginx config exists" "fail" "Config file not found"
    fi
    
    if [ -L "/etc/nginx/sites-enabled/catabot" ]; then
        test_result "Nginx site enabled" "pass"
    else
        test_result "Nginx site enabled" "warn" "Site not enabled"
    fi
    
    # Test Nginx configuration
    if nginx -t &>/dev/null; then
        test_result "Nginx config valid" "pass"
    else
        test_result "Nginx config valid" "fail" "Configuration has errors"
    fi
    
    # Check if Nginx is running
    if systemctl is-active --quiet nginx 2>/dev/null; then
        test_result "Nginx running" "pass"
    else
        test_result "Nginx running" "fail" "Nginx is not active"
    fi
else
    test_result "Nginx installed" "warn" "Nginx not found (optional)"
fi

# Test 10: Check network connectivity
echo ""
echo -e "${YELLOW}[Network Tests]${NC}"

# Get port from .env
PORT=$(grep '^PORT=' /opt/catabot/.env 2>/dev/null | cut -d'=' -f2 || echo "5000")

# Check if port is listening
if lsof -i :$PORT &>/dev/null || netstat -tuln 2>/dev/null | grep -q ":$PORT "; then
    test_result "Port $PORT listening" "pass"
    
    # Try to connect to the application
    if curl -s -o /dev/null -w "%{http_code}" http://localhost:$PORT 2>/dev/null | grep -q "200\|302\|404"; then
        test_result "Application responding" "pass"
    else
        test_result "Application responding" "fail" "No response from application"
    fi
else
    test_result "Port $PORT listening" "fail" "Port not in use"
fi

# Test 11: Check firewall
echo ""
echo -e "${YELLOW}[Firewall]${NC}"
if command -v ufw &> /dev/null; then
    if ufw status 2>/dev/null | grep -q "Status: active"; then
        test_result "UFW firewall active" "pass"
        
        # Check if HTTP/HTTPS ports are allowed
        if ufw status 2>/dev/null | grep -q "80/tcp.*ALLOW"; then
            test_result "HTTP port allowed" "pass"
        else
            test_result "HTTP port allowed" "warn" "Port 80 not allowed"
        fi
        
        if ufw status 2>/dev/null | grep -q "443/tcp.*ALLOW"; then
            test_result "HTTPS port allowed" "pass"
        else
            test_result "HTTPS port allowed" "warn" "Port 443 not allowed"
        fi
    else
        test_result "UFW firewall" "warn" "Firewall not active"
    fi
else
    test_result "UFW firewall" "warn" "UFW not installed"
fi

# Test 12: Check logs
echo ""
echo -e "${YELLOW}[Logs]${NC}"
if [ -f "/opt/catabot/logs/app.log" ]; then
    test_result "Application log exists" "pass"
    
    # Check if log is being written
    if [ -s "/opt/catabot/logs/app.log" ]; then
        test_result "Application log has content" "pass"
        LOG_SIZE=$(du -h /opt/catabot/logs/app.log | cut -f1)
        echo -e "  ${GREEN}→${NC} Log size: $LOG_SIZE"
    else
        test_result "Application log has content" "warn" "Log file is empty"
    fi
else
    test_result "Application log exists" "warn" "Log file not created yet"
fi

# Check for recent errors
if [ -f "/opt/catabot/logs/error.log" ] && [ -s "/opt/catabot/logs/error.log" ]; then
    ERROR_COUNT=$(wc -l < /opt/catabot/logs/error.log)
    if [ "$ERROR_COUNT" -gt 0 ]; then
        test_result "Error log" "warn" "$ERROR_COUNT error(s) logged"
    fi
fi

# Test 13: Check disk space
echo ""
echo -e "${YELLOW}[System Resources]${NC}"
DISK_USAGE=$(df -h /opt/catabot | awk 'NR==2 {print $5}' | sed 's/%//')
if [ "$DISK_USAGE" -lt 80 ]; then
    test_result "Disk space" "pass"
    echo -e "  ${GREEN}→${NC} Usage: ${DISK_USAGE}%"
elif [ "$DISK_USAGE" -lt 90 ]; then
    test_result "Disk space" "warn" "Usage: ${DISK_USAGE}%"
else
    test_result "Disk space" "fail" "Usage: ${DISK_USAGE}% (critically low)"
fi

# Check memory
MEM_AVAILABLE=$(free -m | awk 'NR==2 {print $7}')
if [ "$MEM_AVAILABLE" -gt 500 ]; then
    test_result "Available memory" "pass"
    echo -e "  ${GREEN}→${NC} Available: ${MEM_AVAILABLE}MB"
elif [ "$MEM_AVAILABLE" -gt 200 ]; then
    test_result "Available memory" "warn" "Available: ${MEM_AVAILABLE}MB"
else
    test_result "Available memory" "fail" "Available: ${MEM_AVAILABLE}MB (critically low)"
fi

# Summary
echo ""
echo -e "${GREEN}╔════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║                    Test Summary                        ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "${GREEN}Passed:${NC}   $PASSED"
echo -e "${YELLOW}Warnings:${NC} $WARNINGS"
echo -e "${RED}Failed:${NC}   $FAILED"
echo ""

# Overall result
if [ $FAILED -eq 0 ]; then
    if [ $WARNINGS -eq 0 ]; then
        echo -e "${GREEN}✓ All tests passed! Deployment is successful.${NC}"
        exit 0
    else
        echo -e "${YELLOW}⚠ Deployment is functional but has warnings.${NC}"
        echo -e "${YELLOW}  Review warnings above and address if needed.${NC}"
        exit 0
    fi
else
    echo -e "${RED}✗ Deployment has critical issues.${NC}"
    echo -e "${RED}  Please fix the failed tests above.${NC}"
    echo ""
    echo "Suggested actions:"
    echo "  1. Run diagnostic script: sudo ./diagnose.sh"
    echo "  2. Check service logs: sudo journalctl -u catabot -n 50"
    echo "  3. Test manual startup: sudo -u catabot bash -c 'cd /opt/catabot && source venv/bin/activate && python3 app.py'"
    exit 1
fi
