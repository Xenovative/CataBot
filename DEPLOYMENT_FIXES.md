# Deployment Script Fixes

## Issues Fixed

### 1. **Missing Environment File Loading**
**Problem:** The systemd service wasn't loading the `.env` file, causing the application to fail to start or run with incorrect configuration.

**Fix:** Added `EnvironmentFile=/opt/catabot/.env` to the systemd service configuration.

### 2. **Incorrect Python Path**
**Problem:** Service used `python` instead of `python3`, which may not exist on some systems.

**Fix:** Changed `ExecStart` to use `python3` explicitly.

### 3. **Incomplete PATH Environment**
**Problem:** The PATH only included the venv bin directory, potentially missing system binaries.

**Fix:** Extended PATH to include system directories: `/opt/catabot/venv/bin:/usr/local/bin:/usr/bin:/bin`

### 4. **Missing Service Management Options**
**Problem:** Service didn't have proper shutdown handling and timeout configurations.

**Fix:** Added:
- `KillMode=mixed` - Proper process group termination
- `KillSignal=SIGTERM` - Graceful shutdown signal
- `TimeoutStopSec=30` - Timeout for shutdown
- `SyslogIdentifier=catabot` - Better log identification

### 5. **Hard-coded Debug Mode**
**Problem:** `app.py` always ran in debug mode, which is insecure and inefficient for production.

**Fix:** Modified `app.py` to:
- Load environment variables from `.env` file
- Read `FLASK_DEBUG`, `HOST`, and `PORT` from environment
- Default to production mode (debug=False)

## Files Modified

1. **deploy.sh** - Updated systemd service template
2. **app.py** - Added environment variable loading and production mode support
3. **DEPLOYMENT.md** - Updated documentation with correct service configuration
4. **diagnose.sh** (NEW) - Created diagnostic tool for troubleshooting

## How to Apply Fixes

### For New Deployments
Simply run the updated deploy script:
```bash
sudo ./deploy.sh
```

### For Existing Deployments

1. **Update the systemd service file:**
```bash
sudo nano /etc/systemd/system/catabot.service
```

Add/modify these lines in the `[Service]` section:
```ini
Environment="PATH=/opt/catabot/venv/bin:/usr/local/bin:/usr/bin:/bin"
EnvironmentFile=/opt/catabot/.env
ExecStart=/opt/catabot/venv/bin/python3 /opt/catabot/app.py
KillMode=mixed
KillSignal=SIGTERM
TimeoutStopSec=30
SyslogIdentifier=catabot
```

2. **Ensure .env file exists and is correct:**
```bash
sudo nano /opt/catabot/.env
```

Should contain:
```bash
FLASK_ENV=production
FLASK_DEBUG=0
SECRET_KEY=your-secret-key-here
HOST=0.0.0.0
PORT=5000
OPENAI_API_KEY=your-key-here
```

3. **Update app.py:**
```bash
cd /opt/catabot
sudo -u catabot git pull  # If using git
# Or manually copy the updated app.py
```

4. **Reload and restart:**
```bash
sudo systemctl daemon-reload
sudo systemctl restart catabot
sudo systemctl status catabot
```

## Verification

### Check if service is running:
```bash
sudo systemctl status catabot
```

### View logs:
```bash
# Systemd journal
sudo journalctl -u catabot -f

# Application logs
sudo tail -f /opt/catabot/logs/app.log
sudo tail -f /opt/catabot/logs/error.log
```

### Test the application:
```bash
curl http://localhost:5000
```

### Run diagnostics:
```bash
chmod +x diagnose.sh
sudo ./diagnose.sh
```

## Common Issues After Fix

### Service still won't start
1. Check logs: `sudo journalctl -u catabot -n 50`
2. Test manually: `sudo -u catabot bash -c "cd /opt/catabot && source venv/bin/activate && python3 app.py"`
3. Check permissions: `ls -la /opt/catabot/.env`
4. Verify dependencies: `/opt/catabot/venv/bin/python3 -c "import flask"`

### Port already in use
```bash
sudo lsof -i :5000
sudo kill -9 <PID>
sudo systemctl restart catabot
```

### Permission denied errors
```bash
sudo chown -R catabot:catabot /opt/catabot
sudo chmod 600 /opt/catabot/.env
sudo chmod -R 775 /opt/catabot/{pdfs,uploads,job_history,logs}
```

### Missing dependencies
```bash
cd /opt/catabot
sudo -u catabot bash -c "source venv/bin/activate && pip install -r requirements.txt"
sudo systemctl restart catabot
```

## Testing Checklist

- [ ] Service starts successfully: `sudo systemctl start catabot`
- [ ] Service status shows active: `sudo systemctl status catabot`
- [ ] Application responds: `curl http://localhost:5000`
- [ ] Nginx proxies correctly: `curl http://your-domain.com`
- [ ] Logs are being written: `ls -lh /opt/catabot/logs/`
- [ ] Environment variables loaded: `sudo systemctl show catabot | grep Environment`
- [ ] Service restarts on failure: `sudo systemctl restart catabot`
- [ ] Service starts on boot: `sudo systemctl is-enabled catabot`

## Additional Recommendations

1. **Use Gunicorn for production** (more robust than Flask dev server):
```bash
pip install gunicorn
# Update ExecStart in service file:
ExecStart=/opt/catabot/venv/bin/gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

2. **Set up log rotation** (already included in deploy.sh):
```bash
sudo nano /etc/logrotate.d/catabot
```

3. **Monitor service health**:
```bash
# Add to crontab
*/5 * * * * systemctl is-active --quiet catabot || systemctl restart catabot
```

4. **Enable firewall**:
```bash
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable
```

## Support

If issues persist after applying these fixes:
1. Run the diagnostic script: `sudo ./diagnose.sh`
2. Check all logs: `sudo journalctl -u catabot -n 100`
3. Test manual startup: `sudo -u catabot bash -c "cd /opt/catabot && source venv/bin/activate && python3 app.py"`
4. Verify all dependencies are installed
5. Check system resources (memory, disk space)
