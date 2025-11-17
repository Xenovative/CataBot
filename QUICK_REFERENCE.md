# CataBot Quick Reference

## Service Management

```bash
# Start service
sudo systemctl start catabot

# Stop service
sudo systemctl stop catabot

# Restart service
sudo systemctl restart catabot

# Check status
sudo systemctl status catabot

# Enable on boot
sudo systemctl enable catabot

# Disable on boot
sudo systemctl disable catabot

# Reload systemd after config changes
sudo systemctl daemon-reload
```

## Logs

```bash
# View live logs (systemd journal)
sudo journalctl -u catabot -f

# View last 50 lines
sudo journalctl -u catabot -n 50

# View application logs
sudo tail -f /opt/catabot/logs/app.log
sudo tail -f /opt/catabot/logs/error.log

# View all logs since boot
sudo journalctl -u catabot --since today
```

## Diagnostics

```bash
# Run diagnostic script
sudo ./diagnose.sh

# Check if service is running
systemctl is-active catabot

# Check environment variables
sudo systemctl show catabot | grep Environment

# Test application manually
sudo -u catabot bash
cd /opt/catabot
source venv/bin/activate
python3 app.py
```

## Configuration

```bash
# Edit environment variables
sudo nano /opt/catabot/.env

# Edit service configuration
sudo nano /etc/systemd/system/catabot.service

# Edit Nginx configuration
sudo nano /etc/nginx/sites-available/catabot

# Test Nginx configuration
sudo nginx -t

# Reload Nginx
sudo systemctl reload nginx
```

## Updates

```bash
# Stop service
sudo systemctl stop catabot

# Pull latest code (if using git)
cd /opt/catabot
sudo -u catabot git pull

# Update dependencies
sudo -u catabot bash -c "source venv/bin/activate && pip install -r requirements.txt"

# Start service
sudo systemctl start catabot
```

## Troubleshooting

```bash
# Port already in use
sudo lsof -i :5000
sudo kill -9 <PID>

# Fix permissions
sudo chown -R catabot:catabot /opt/catabot
sudo chmod 600 /opt/catabot/.env
sudo chmod -R 775 /opt/catabot/{pdfs,uploads,job_history,logs}

# Reinstall dependencies
cd /opt/catabot
sudo -u catabot bash -c "source venv/bin/activate && pip install --force-reinstall -r requirements.txt"

# Check Python dependencies
/opt/catabot/venv/bin/python3 -c "import flask; print('Flask OK')"
/opt/catabot/venv/bin/python3 -c "import openai; print('OpenAI OK')"
```

## Backup & Restore

```bash
# Manual backup
sudo tar -czf catabot_backup_$(date +%Y%m%d).tar.gz \
    /opt/catabot/job_history \
    /opt/catabot/settings.json \
    /opt/catabot/.env

# Restore backup
sudo tar -xzf catabot_backup_YYYYMMDD.tar.gz -C /
sudo chown -R catabot:catabot /opt/catabot
sudo systemctl restart catabot
```

## Monitoring

```bash
# Check disk usage
df -h /opt/catabot

# Check memory usage
free -h

# Check process
ps aux | grep python

# Check system resources
top
htop  # if installed
```

## Network

```bash
# Check if port is accessible
curl http://localhost:5000

# Check from external
curl http://your-domain.com

# Check Nginx status
sudo systemctl status nginx

# Check firewall
sudo ufw status
```

## SSL/HTTPS

```bash
# Setup SSL with Let's Encrypt
sudo certbot --nginx -d your-domain.com

# Renew SSL certificate
sudo certbot renew

# Test renewal
sudo certbot renew --dry-run

# Check certificate expiry
sudo certbot certificates
```

## Performance

```bash
# Check service resource usage
systemctl status catabot

# View detailed process info
sudo journalctl -u catabot --since "1 hour ago"

# Monitor in real-time
watch -n 1 'systemctl status catabot | head -20'
```

## Emergency Commands

```bash
# Force kill service
sudo systemctl kill catabot

# Clear all logs
sudo truncate -s 0 /opt/catabot/logs/*.log

# Reset to clean state
sudo systemctl stop catabot
sudo rm -rf /opt/catabot/uploads/*
sudo rm -rf /opt/catabot/pdfs/*
sudo systemctl start catabot

# Complete reinstall (DANGEROUS - backs up data first)
sudo systemctl stop catabot
sudo tar -czf /tmp/catabot_backup.tar.gz /opt/catabot/job_history /opt/catabot/.env
sudo rm -rf /opt/catabot
# Then re-run deploy.sh
```

## File Locations

```
/opt/catabot/              # Application root
/opt/catabot/.env          # Environment configuration
/opt/catabot/venv/         # Python virtual environment
/opt/catabot/logs/         # Application logs
/opt/catabot/pdfs/         # Downloaded PDFs
/opt/catabot/uploads/      # Uploaded files
/opt/catabot/job_history/  # Job history JSON files
/opt/catabot/output/       # Generated catalogs

/etc/systemd/system/catabot.service    # Systemd service
/etc/nginx/sites-available/catabot     # Nginx config
/etc/nginx/sites-enabled/catabot       # Nginx symlink
```

## Important URLs

```
http://localhost:5000              # Local access
http://your-domain.com             # Public access (via Nginx)
http://localhost:5000/api/config   # API configuration
http://localhost:5000/api/jobs     # Current jobs
http://localhost:5000/api/history  # Job history
```

## Cron Jobs

```bash
# View catabot user crontab
sudo crontab -u catabot -l

# Edit catabot user crontab
sudo crontab -u catabot -e

# Default jobs:
# 0 2 * * * /opt/catabot/backup.sh          # Daily backup at 2 AM
# 0 3 * * 0 /opt/catabot/rotate_logs.sh     # Weekly log rotation
```
