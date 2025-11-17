#!/bin/bash

# CataBot Deployment Script for Linux
# This script sets up CataBot on a Linux server with systemd service

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
APP_NAME="catabot"
APP_DIR="/opt/catabot"
APP_USER="catabot"
PYTHON_VERSION="3.9"

echo -e "${GREEN}=== CataBot Deployment Script ===${NC}"
echo ""

# Check if running as root
if [ "$EUID" -ne 0 ]; then 
    echo -e "${RED}Please run as root (use sudo)${NC}"
    exit 1
fi

# Function to print status
print_status() {
    echo -e "${GREEN}[✓]${NC} $1"
}

print_error() {
    echo -e "${RED}[✗]${NC} $1"
}

print_info() {
    echo -e "${YELLOW}[i]${NC} $1"
}

# Prompt for configuration
echo -e "${YELLOW}Configuration:${NC}"
echo ""

# Port number
read -p "Enter port number for CataBot (default: 5000): " PORT
PORT=${PORT:-5000}

# Validate port number
if ! [[ "$PORT" =~ ^[0-9]+$ ]] || [ "$PORT" -lt 1024 ] || [ "$PORT" -gt 65535 ]; then
    echo -e "${RED}Invalid port number. Using default: 5000${NC}"
    PORT=5000
fi

# Domain name
read -p "Enter domain name (or press Enter for IP-based access): " DOMAIN_NAME
if [ -z "$DOMAIN_NAME" ]; then
    DOMAIN_NAME="_"
    print_info "Using IP-based access"
else
    print_info "Domain: $DOMAIN_NAME"
fi

# SSL setup
if [ "$DOMAIN_NAME" != "_" ]; then
    read -p "Set up SSL with Let's Encrypt? (y/n, default: n): " SETUP_SSL
    SETUP_SSL=${SETUP_SSL:-n}
else
    SETUP_SSL="n"
fi

echo ""
echo -e "${GREEN}Configuration Summary:${NC}"
echo "  Port: $PORT"
echo "  Domain: $DOMAIN_NAME"
echo "  SSL: $([ "$SETUP_SSL" = "y" ] && echo "Yes" || echo "No")"
echo ""
read -p "Continue with deployment? (y/n): " CONFIRM
if [ "$CONFIRM" != "y" ]; then
    echo -e "${YELLOW}Deployment cancelled${NC}"
    exit 0
fi
echo ""

# Step 1: Update system
echo -e "${YELLOW}Step 1: Updating system packages...${NC}"
apt-get update
apt-get upgrade -y
print_status "System updated"

# Step 2: Install dependencies
echo -e "${YELLOW}Step 2: Installing dependencies...${NC}"
apt-get install -y \
    python3 \
    python3-pip \
    python3-venv \
    git \
    nginx \
    supervisor \
    poppler-utils \
    tesseract-ocr \
    libtesseract-dev \
    libpoppler-cpp-dev
print_status "Dependencies installed"

# Step 3: Create application user
echo -e "${YELLOW}Step 3: Creating application user...${NC}"
if id "$APP_USER" &>/dev/null; then
    print_info "User $APP_USER already exists"
else
    useradd -r -s /bin/bash -d $APP_DIR $APP_USER
    print_status "User $APP_USER created"
fi

# Step 4: Create application directory
echo -e "${YELLOW}Step 4: Setting up application directory...${NC}"
mkdir -p $APP_DIR
mkdir -p $APP_DIR/pdfs
mkdir -p $APP_DIR/uploads
mkdir -p $APP_DIR/job_history
mkdir -p $APP_DIR/logs
print_status "Directories created"

# Step 5: Copy application files
echo -e "${YELLOW}Step 5: Copying application files...${NC}"
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cp -r $SCRIPT_DIR/* $APP_DIR/ 2>/dev/null || print_info "Running from target directory"
print_status "Files copied"

# Step 6: Set up Python virtual environment
echo -e "${YELLOW}Step 6: Setting up Python virtual environment...${NC}"
cd $APP_DIR
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
print_status "Virtual environment created and dependencies installed"

# Step 7: Set permissions
echo -e "${YELLOW}Step 7: Setting permissions...${NC}"
chown -R $APP_USER:$APP_USER $APP_DIR
chmod -R 755 $APP_DIR
chmod -R 775 $APP_DIR/pdfs
chmod -R 775 $APP_DIR/uploads
chmod -R 775 $APP_DIR/job_history
chmod -R 775 $APP_DIR/logs
print_status "Permissions set"

# Step 8: Create systemd service
echo -e "${YELLOW}Step 8: Creating systemd service...${NC}"
cat > /etc/systemd/system/${APP_NAME}.service << EOF
[Unit]
Description=CataBot - Academic Paper Cataloging System
After=network.target

[Service]
Type=simple
User=$APP_USER
WorkingDirectory=$APP_DIR
Environment="PATH=$APP_DIR/venv/bin:/usr/local/bin:/usr/bin:/bin"
EnvironmentFile=$APP_DIR/.env
ExecStart=$APP_DIR/venv/bin/python3 $APP_DIR/app.py
Restart=always
RestartSec=10
KillMode=mixed
KillSignal=SIGTERM
TimeoutStopSec=30

# Logging
StandardOutput=append:$APP_DIR/logs/app.log
StandardError=append:$APP_DIR/logs/error.log
SyslogIdentifier=catabot

[Install]
WantedBy=multi-user.target
EOF
print_status "Systemd service created"

# Step 9: Create Nginx configuration
echo -e "${YELLOW}Step 9: Configuring Nginx...${NC}"
cat > /etc/nginx/sites-available/${APP_NAME} << EOF
server {
    listen 80;
    server_name $DOMAIN_NAME;

    client_max_body_size 100M;

    location / {
        proxy_pass http://127.0.0.1:$PORT;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        
        # WebSocket support (if needed)
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection "upgrade";
        
        # Timeouts for long-running requests
        proxy_connect_timeout 600;
        proxy_send_timeout 600;
        proxy_read_timeout 600;
        send_timeout 600;
    }

    location /static {
        alias $APP_DIR/static;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }
}
EOF

# Enable Nginx site
ln -sf /etc/nginx/sites-available/${APP_NAME} /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default
nginx -t && systemctl reload nginx
print_status "Nginx configured"

# Step 10: Create environment file template
echo -e "${YELLOW}Step 10: Creating environment configuration...${NC}"
if [ ! -f "$APP_DIR/.env" ]; then
    cat > $APP_DIR/.env << EOF
# CataBot Configuration
FLASK_ENV=production
FLASK_DEBUG=0
SECRET_KEY=$(openssl rand -hex 32)

# OpenAI API (optional)
OPENAI_API_KEY=

# Anthropic API (optional)
ANTHROPIC_API_KEY=

# Server Configuration
HOST=0.0.0.0
PORT=$PORT
EOF
    chown $APP_USER:$APP_USER $APP_DIR/.env
    chmod 600 $APP_DIR/.env
    print_status "Environment file created"
    print_info "Edit $APP_DIR/.env to add your API keys"
else
    print_info "Environment file already exists"
fi

# Step 11: Enable and start services
echo -e "${YELLOW}Step 11: Starting services...${NC}"
systemctl daemon-reload
systemctl enable ${APP_NAME}
systemctl start ${APP_NAME}
systemctl enable nginx
systemctl start nginx
print_status "Services started"

# Step 12: Configure firewall (if ufw is installed)
if command -v ufw &> /dev/null; then
    echo -e "${YELLOW}Step 12: Configuring firewall...${NC}"
    ufw allow 80/tcp
    ufw allow 443/tcp
    print_status "Firewall configured"
else
    print_info "UFW not installed, skipping firewall configuration"
fi

# Step 13: Create maintenance scripts
echo -e "${YELLOW}Step 13: Creating maintenance scripts...${NC}"

# Backup script
cat > $APP_DIR/backup.sh << 'EOF'
#!/bin/bash
BACKUP_DIR="/var/backups/catabot"
DATE=$(date +%Y%m%d_%H%M%S)
mkdir -p $BACKUP_DIR
tar -czf $BACKUP_DIR/catabot_backup_$DATE.tar.gz \
    /opt/catabot/job_history \
    /opt/catabot/settings.json \
    /opt/catabot/.env
find $BACKUP_DIR -name "catabot_backup_*.tar.gz" -mtime +7 -delete
echo "Backup completed: $BACKUP_DIR/catabot_backup_$DATE.tar.gz"
EOF

# Update script
cat > $APP_DIR/update.sh << 'EOF'
#!/bin/bash
cd /opt/catabot
sudo systemctl stop catabot
source venv/bin/activate
git pull
pip install -r requirements.txt
sudo systemctl start catabot
echo "Update completed"
EOF

# Log rotation script
cat > $APP_DIR/rotate_logs.sh << 'EOF'
#!/bin/bash
LOG_DIR="/opt/catabot/logs"
DATE=$(date +%Y%m%d)
cd $LOG_DIR
if [ -f app.log ]; then
    mv app.log app.log.$DATE
    gzip app.log.$DATE
fi
if [ -f error.log ]; then
    mv error.log error.log.$DATE
    gzip error.log.$DATE
fi
find $LOG_DIR -name "*.gz" -mtime +30 -delete
sudo systemctl restart catabot
EOF

chmod +x $APP_DIR/backup.sh
chmod +x $APP_DIR/update.sh
chmod +x $APP_DIR/rotate_logs.sh
print_status "Maintenance scripts created"

# Step 14: Set up cron jobs
echo -e "${YELLOW}Step 14: Setting up cron jobs...${NC}"
(crontab -u $APP_USER -l 2>/dev/null; echo "0 2 * * * $APP_DIR/backup.sh") | crontab -u $APP_USER -
(crontab -u $APP_USER -l 2>/dev/null; echo "0 3 * * 0 $APP_DIR/rotate_logs.sh") | crontab -u $APP_USER -
print_status "Cron jobs configured"

# Step 15: Set up SSL (if requested)
if [ "$SETUP_SSL" = "y" ]; then
    echo -e "${YELLOW}Step 15: Setting up SSL with Let's Encrypt...${NC}"
    
    # Install Certbot
    if ! command -v certbot &> /dev/null; then
        apt-get install -y certbot python3-certbot-nginx
    fi
    
    # Obtain certificate
    certbot --nginx -d $DOMAIN_NAME --non-interactive --agree-tos --register-unsafely-without-email
    
    if [ $? -eq 0 ]; then
        print_status "SSL certificate obtained and configured"
        
        # Set up auto-renewal
        (crontab -l 2>/dev/null; echo "0 0 * * * certbot renew --quiet") | crontab -
        print_status "SSL auto-renewal configured"
    else
        print_error "SSL setup failed. You can set it up manually later with: sudo certbot --nginx -d $DOMAIN_NAME"
    fi
else
    print_info "Skipping SSL setup. You can set it up later with: sudo certbot --nginx -d $DOMAIN_NAME"
fi

# Final status check
echo ""
echo -e "${GREEN}=== Deployment Complete ===${NC}"
echo ""
echo "Service Status:"
systemctl status ${APP_NAME} --no-pager | head -n 10
echo ""
echo -e "${GREEN}CataBot is now running!${NC}"
echo ""
if [ "$DOMAIN_NAME" != "_" ]; then
    if [ "$SETUP_SSL" = "y" ]; then
        echo "Access the application at: https://$DOMAIN_NAME"
    else
        echo "Access the application at: http://$DOMAIN_NAME"
    fi
else
    echo "Access the application at: http://$(hostname -I | awk '{print $1}'):$PORT"
fi
echo ""
echo "Useful commands:"
echo "  - View logs:        sudo journalctl -u ${APP_NAME} -f"
echo "  - Restart service:  sudo systemctl restart ${APP_NAME}"
echo "  - Stop service:     sudo systemctl stop ${APP_NAME}"
echo "  - Check status:     sudo systemctl status ${APP_NAME}"
echo "  - Backup data:      sudo $APP_DIR/backup.sh"
echo "  - Update app:       sudo $APP_DIR/update.sh"
echo ""
echo -e "${YELLOW}Important:${NC}"
echo "  1. Edit $APP_DIR/.env to add your API keys"
if [ "$SETUP_SSL" != "y" ] && [ "$DOMAIN_NAME" != "_" ]; then
    echo "  2. Set up SSL with: sudo certbot --nginx -d $DOMAIN_NAME"
fi
echo "  2. Backups run daily at 2 AM (check with: sudo crontab -u $APP_USER -l)"
echo "  3. Logs are rotated weekly"
echo ""
echo -e "${GREEN}Deployment completed successfully!${NC}"
echo ""
