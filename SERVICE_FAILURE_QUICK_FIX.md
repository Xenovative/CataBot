# Quick Fix for Service Exit Code 1

## Your Error
```
catabot.service: Main process exited, code=exited, status=1/FAILURE
```

## Fastest Fix (Run These Commands)

```bash
# 1. See the actual error
sudo journalctl -u catabot -n 50 --no-pager

# 2. Test manually to see what's wrong
sudo -u catabot bash -c "cd /opt/catabot && source venv/bin/activate && python3 app.py"
```

The manual test will show you the **exact error**. Common errors:

### Error: "ModuleNotFoundError: No module named 'flask'"
**Fix:**
```bash
cd /opt/catabot
sudo -u catabot bash -c "source venv/bin/activate && pip install -r requirements.txt"
sudo systemctl restart catabot
```

### Error: "FileNotFoundError: [Errno 2] No such file or directory: '.env'"
**Fix:**
```bash
sudo nano /opt/catabot/.env
```
Add:
```
FLASK_ENV=production
FLASK_DEBUG=0
SECRET_KEY=your-random-secret-key-here
HOST=0.0.0.0
PORT=5000
```
Save and:
```bash
sudo chown catabot:catabot /opt/catabot/.env
sudo chmod 600 /opt/catabot/.env
sudo systemctl restart catabot
```

### Error: "Address already in use" or "Port 5000 is already in use"
**Fix:**
```bash
sudo lsof -i :5000
sudo kill -9 <PID>  # Replace <PID> with the number from above
sudo systemctl restart catabot
```

### Error: "PermissionError: [Errno 13] Permission denied"
**Fix:**
```bash
sudo chown -R catabot:catabot /opt/catabot
sudo chmod -R 775 /opt/catabot/{pdfs,uploads,job_history,logs}
sudo systemctl restart catabot
```

### Error: "ModuleNotFoundError: No module named 'pdf_extractor'"
**Fix:**
```bash
# Make sure all Python files are in /opt/catabot
ls /opt/catabot/*.py
# Should show: app.py, pdf_extractor.py, web_crawler.py, etc.

# If files are missing, copy them from your source
sudo cp /path/to/source/*.py /opt/catabot/
sudo chown catabot:catabot /opt/catabot/*.py
sudo systemctl restart catabot
```

## Automated Emergency Fix

Run this script to automatically fix common issues:

```bash
chmod +x emergency_fix.sh
sudo ./emergency_fix.sh
```

## Still Not Working?

1. **Check the full error log:**
   ```bash
   sudo journalctl -u catabot -n 100 --no-pager > error.log
   cat error.log
   ```

2. **Run diagnostics:**
   ```bash
   chmod +x diagnose.sh
   sudo ./diagnose.sh
   ```

3. **See detailed troubleshooting:**
   ```bash
   cat TROUBLESHOOTING.md
   ```

## Verify It's Working

```bash
# Check service status
sudo systemctl status catabot

# Test the application
curl http://localhost:5000

# Watch logs in real-time
sudo journalctl -u catabot -f
```

## Update Existing Deployment

If you deployed before the fixes, update your service file:

```bash
# Edit service file
sudo nano /etc/systemd/system/catabot.service
```

Change the `EnvironmentFile` line to:
```ini
EnvironmentFile=-/opt/catabot/.env
```
(Note the `-` prefix makes it optional)

And change `ExecStart` to:
```ini
ExecStart=/opt/catabot/start.sh
```

Then:
```bash
sudo systemctl daemon-reload
sudo systemctl restart catabot
```
