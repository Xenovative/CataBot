# CataBot Deployment Guide for Linux Servers

## Quick Start

### Prerequisites
- Ubuntu 20.04+ or Debian 11+ (or similar Linux distribution)
- Root or sudo access
- At least 2GB RAM
- 10GB free disk space

### One-Command Deployment

```bash
# Download and run deployment script
curl -O https://your-repo/deploy.sh
chmod +x deploy.sh
sudo ./deploy.sh
```

Or if you have the repository:

```bash
cd CataBot
chmod +x deploy.sh
sudo ./deploy.sh
```

## Manual Deployment

### Step 1: System Preparation

```bash
# Update system
sudo apt-get update
sudo apt-get upgrade -y

# Install dependencies
sudo apt-get install -y \
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
```

### Step 2: Create Application User

```bash
# Create dedicated user
sudo useradd -r -s /bin/bash -d /opt/catabot catabot

# Create directories
sudo mkdir -p /opt/catabot
sudo mkdir -p /opt/catabot/{pdfs,uploads,job_history,logs}
```

### Step 3: Install Application

```bash
# Clone or copy application
cd /opt/catabot
sudo git clone https://your-repo/CataBot.git .

# Or copy files
sudo cp -r /path/to/CataBot/* /opt/catabot/
```

### Step 4: Set Up Python Environment

```bash
# Create virtual environment
cd /opt/catabot
sudo python3 -m venv venv
sudo chown -R catabot:catabot venv

# Activate and install dependencies
sudo -u catabot bash -c "source venv/bin/activate && pip install --upgrade pip && pip install -r requirements.txt"
```

### Step 5: Configure Application

```bash
# Copy from example (recommended)
sudo cp /opt/catabot/.env.example /opt/catabot/.env

# Or create manually
sudo nano /opt/catabot/.env
```

Add/edit the following:

```bash
# Flask Configuration
FLASK_ENV=production
FLASK_DEBUG=0
SECRET_KEY=your-secret-key-here

# API Keys (optional)
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...

# Server Configuration
HOST=0.0.0.0
PORT=5000
```

### Step 6: Set Permissions

```bash
sudo chown -R catabot:catabot /opt/catabot
sudo chmod -R 755 /opt/catabot
sudo chmod -R 775 /opt/catabot/{pdfs,uploads,job_history,logs}
sudo chmod 600 /opt/catabot/.env
```

### Step 7: Create Systemd Service

```bash
sudo nano /etc/systemd/system/catabot.service
```

Add:

```ini
[Unit]
Description=CataBot - Academic Paper Cataloging System
After=network.target

[Service]
Type=simple
User=catabot
WorkingDirectory=/opt/catabot
Environment="PATH=/opt/catabot/venv/bin:/usr/local/bin:/usr/bin:/bin"
EnvironmentFile=/opt/catabot/.env
ExecStart=/opt/catabot/venv/bin/python3 /opt/catabot/app.py
Restart=always
RestartSec=10
KillMode=mixed
KillSignal=SIGTERM
TimeoutStopSec=30

# Logging
StandardOutput=append:/opt/catabot/logs/app.log
StandardError=append:/opt/catabot/logs/error.log
SyslogIdentifier=catabot

[Install]
WantedBy=multi-user.target
```

Enable and start:

```bash
sudo systemctl daemon-reload
sudo systemctl enable catabot
sudo systemctl start catabot
sudo systemctl status catabot
```

### Step 8: Configure Nginx

```bash
sudo nano /etc/nginx/sites-available/catabot
```

Add:

```nginx
server {
    listen 80;
    server_name your-domain.com;

    client_max_body_size 100M;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        
        # Timeouts for long-running requests
        proxy_connect_timeout 600;
        proxy_send_timeout 600;
        proxy_read_timeout 600;
        send_timeout 600;
    }

    location /static {
        alias /opt/catabot/static;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }
}
```

Enable site:

```bash
sudo ln -s /etc/nginx/sites-available/catabot /etc/nginx/sites-enabled/
sudo rm /etc/nginx/sites-enabled/default
sudo nginx -t
sudo systemctl reload nginx
```

### Step 9: Configure Firewall

```bash
# Allow HTTP and HTTPS
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable
```

### Step 10: Set Up SSL (Optional but Recommended)

```bash
# Install Certbot
sudo apt-get install -y certbot python3-certbot-nginx

# Obtain certificate
sudo certbot --nginx -d your-domain.com

# Auto-renewal
sudo certbot renew --dry-run
```

## Maintenance

### View Logs

```bash
# Application logs
sudo journalctl -u catabot -f

# Nginx logs
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log

# Application file logs
sudo tail -f /opt/catabot/logs/app.log
sudo tail -f /opt/catabot/logs/error.log
```

### Restart Service

```bash
sudo systemctl restart catabot
sudo systemctl restart nginx
```

### Update Application

```bash
cd /opt/catabot
sudo systemctl stop catabot
sudo -u catabot git pull
sudo -u catabot bash -c "source venv/bin/activate && pip install -r requirements.txt"
sudo systemctl start catabot
```

### Backup Data

```bash
# Manual backup
sudo tar -czf catabot_backup_$(date +%Y%m%d).tar.gz \
    /opt/catabot/job_history \
    /opt/catabot/settings.json \
    /opt/catabot/.env

# Automated backup (add to crontab)
sudo crontab -e
# Add: 0 2 * * * /opt/catabot/backup.sh
```

### Monitor Resources

```bash
# Check disk usage
df -h /opt/catabot

# Check memory usage
free -h

# Check service status
sudo systemctl status catabot

# Check process
ps aux | grep python
```

## Troubleshooting

> **📖 For detailed troubleshooting of service failures, see [TROUBLESHOOTING.md](TROUBLESHOOTING.md)**

### Service Won't Start

```bash
# Check logs
sudo journalctl -u catabot -n 50 --no-pager

# Check service status
sudo systemctl status catabot

# Check permissions
ls -la /opt/catabot
ls -la /opt/catabot/.env

# Verify .env file exists and is readable
sudo cat /opt/catabot/.env

# Test manually as the catabot user
sudo -u catabot bash
cd /opt/catabot
source venv/bin/activate
python3 app.py

# If manual test works but service doesn't, check:
# 1. Environment file is properly loaded
sudo systemctl show catabot | grep Environment

# 2. Python dependencies are installed in venv
/opt/catabot/venv/bin/python3 -c "import flask; print('Flask OK')"

# 3. Reload systemd after any service file changes
sudo systemctl daemon-reload
sudo systemctl restart catabot
```

### Port Already in Use

```bash
# Find process using port 5000
sudo lsof -i :5000

# Kill process
sudo kill -9 <PID>

# Or change port in .env file
```

### Nginx 502 Bad Gateway

```bash
# Check if CataBot is running
sudo systemctl status catabot

# Check Nginx configuration
sudo nginx -t

# Check firewall
sudo ufw status
```

### Out of Memory

```bash
# Check memory
free -h

# Restart service
sudo systemctl restart catabot

# Consider adding swap
sudo fallocate -l 2G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
```

### PDF Processing Fails

```bash
# Check Tesseract installation
tesseract --version

# Check Poppler installation
pdfinfo -v

# Reinstall if needed
sudo apt-get install --reinstall poppler-utils tesseract-ocr
```

## Performance Tuning

### Nginx Optimization

```nginx
# Add to /etc/nginx/nginx.conf
worker_processes auto;
worker_connections 1024;

# Enable gzip
gzip on;
gzip_types text/plain text/css application/json application/javascript;
```

### Systemd Service Optimization

```ini
# Add to service file
[Service]
LimitNOFILE=65536
Nice=-5
```

### Python Optimization

```bash
# Use production WSGI server (Gunicorn)
pip install gunicorn

# Update service ExecStart
ExecStart=/opt/catabot/venv/bin/gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

## Security Best Practices

### 1. Use HTTPS Only

```nginx
# Redirect HTTP to HTTPS
server {
    listen 80;
    server_name your-domain.com;
    return 301 https://$server_name$request_uri;
}
```

### 2. Secure Environment File

```bash
sudo chmod 600 /opt/catabot/.env
sudo chown catabot:catabot /opt/catabot/.env
```

### 3. Enable Fail2Ban

```bash
sudo apt-get install fail2ban
sudo systemctl enable fail2ban
sudo systemctl start fail2ban
```

### 4. Regular Updates

```bash
# System updates
sudo apt-get update && sudo apt-get upgrade -y

# Python packages
cd /opt/catabot
source venv/bin/activate
pip list --outdated
```

### 5. Limit File Upload Size

```nginx
# In Nginx config
client_max_body_size 100M;
```

## Monitoring

### Set Up Monitoring Script

```bash
#!/bin/bash
# /opt/catabot/monitor.sh

if ! systemctl is-active --quiet catabot; then
    echo "CataBot is down! Restarting..."
    systemctl restart catabot
    echo "CataBot restarted at $(date)" >> /opt/catabot/logs/monitor.log
fi
```

Add to crontab:

```bash
*/5 * * * * /opt/catabot/monitor.sh
```

### Log Rotation

```bash
# Create /etc/logrotate.d/catabot
/opt/catabot/logs/*.log {
    daily
    rotate 7
    compress
    delaycompress
    notifempty
    create 0640 catabot catabot
    sharedscripts
    postrotate
        systemctl reload catabot > /dev/null 2>&1 || true
    endscript
}
```

## Scaling

### Horizontal Scaling

Use load balancer (e.g., HAProxy) with multiple instances:

```bash
# Instance 1: Port 5001
# Instance 2: Port 5002
# Instance 3: Port 5003
```

### Vertical Scaling

```bash
# Increase workers in Gunicorn
gunicorn -w 8 -b 0.0.0.0:5000 app:app

# Increase system resources
# - Add more RAM
# - Use faster CPU
# - Use SSD storage
```

## Uninstall

```bash
# Stop services
sudo systemctl stop catabot
sudo systemctl disable catabot

# Remove files
sudo rm /etc/systemd/system/catabot.service
sudo rm /etc/nginx/sites-enabled/catabot
sudo rm /etc/nginx/sites-available/catabot
sudo rm -rf /opt/catabot

# Remove user
sudo userdel catabot

# Reload services
sudo systemctl daemon-reload
sudo systemctl reload nginx
```

## Support

For issues and questions:
- Check logs first
- Review this documentation
- Check GitHub issues
- Contact support

## License

See LICENSE file for details.
