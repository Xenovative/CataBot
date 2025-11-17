# CataBot Troubleshooting Guide

## Service Exit Code 1 (Main Process Failure)

If you see this error:
```
catabot.service: Main process exited, code=exited, status=1/FAILURE
catabot.service: Failed with result 'exit-code'
```

### Step 1: Check the Error Logs

```bash
# View systemd journal (most recent errors)
sudo journalctl -u catabot -n 100 --no-pager

# View application error log
sudo tail -50 /opt/catabot/logs/error.log

# View application output log
sudo tail -50 /opt/catabot/logs/app.log
```

### Step 2: Test Manual Startup

This will show the actual error message:

```bash
# Switch to catabot user
sudo -u catabot bash

# Navigate to app directory
cd /opt/catabot

# Activate virtual environment
source venv/bin/activate

# Try to start the app
python3 app.py
```

If it fails, you'll see the actual Python error.

### Step 3: Common Causes and Fixes

#### A. Missing Python Dependencies

**Symptom:** `ModuleNotFoundError: No module named 'flask'` or similar

**Fix:**
```bash
cd /opt/catabot
sudo -u catabot bash -c "source venv/bin/activate && pip install -r requirements.txt"
sudo systemctl restart catabot
```

#### B. Missing or Incorrect .env File

**Symptom:** Service starts but crashes immediately, or "KeyError" in logs

**Fix:**
```bash
# Check if .env exists
ls -la /opt/catabot/.env

# If missing, create it
sudo nano /opt/catabot/.env
```

Add minimum required content:
```bash
FLASK_ENV=production
FLASK_DEBUG=0
SECRET_KEY=$(openssl rand -hex 32)
HOST=0.0.0.0
PORT=5000
```

Then:
```bash
sudo chown catabot:catabot /opt/catabot/.env
sudo chmod 600 /opt/catabot/.env
sudo systemctl restart catabot
```

#### C. Port Already in Use

**Symptom:** `OSError: [Errno 98] Address already in use`

**Fix:**
```bash
# Find what's using port 5000
sudo lsof -i :5000

# Kill the process (replace <PID> with actual process ID)
sudo kill -9 <PID>

# Or change the port in .env
sudo nano /opt/catabot/.env
# Change PORT=5000 to PORT=5001 (or another free port)

# Restart service
sudo systemctl restart catabot
```

#### D. Permission Errors

**Symptom:** `PermissionError: [Errno 13] Permission denied`

**Fix:**
```bash
# Fix ownership
sudo chown -R catabot:catabot /opt/catabot

# Fix permissions
sudo chmod -R 755 /opt/catabot
sudo chmod -R 775 /opt/catabot/{pdfs,uploads,job_history,logs}
sudo chmod 600 /opt/catabot/.env

# Restart service
sudo systemctl restart catabot
```

#### E. Missing Templates Directory

**Symptom:** `jinja2.exceptions.TemplateNotFound` or `templates directory not found`

**Fix:**
```bash
# Check if templates exist
ls -la /opt/catabot/templates/

# If missing, ensure all files were copied
cd /path/to/source/CataBot
sudo cp -r templates /opt/catabot/
sudo chown -R catabot:catabot /opt/catabot/templates

# Restart service
sudo systemctl restart catabot
```

#### F. Import Errors from Custom Modules

**Symptom:** `ModuleNotFoundError: No module named 'pdf_extractor'` or similar

**Fix:**
```bash
# Verify all Python files are present
ls -la /opt/catabot/*.py

# Should see:
# - app.py
# - pdf_extractor.py
# - web_crawler.py
# - ai_classifier.py
# - catalog_generator.py
# - journal_sources.py
# - config.py

# If any are missing, copy them
sudo cp missing_file.py /opt/catabot/
sudo chown catabot:catabot /opt/catabot/missing_file.py

# Restart service
sudo systemctl restart catabot
```

#### G. Python Version Mismatch

**Symptom:** `SyntaxError` or version-related errors

**Fix:**
```bash
# Check Python version
/opt/catabot/venv/bin/python3 --version

# Should be 3.8 or higher
# If not, recreate virtual environment
cd /opt/catabot
sudo rm -rf venv
sudo -u catabot python3 -m venv venv
sudo -u catabot bash -c "source venv/bin/activate && pip install -r requirements.txt"

# Restart service
sudo systemctl restart catabot
```

### Step 4: Use the Startup Script for Better Errors

The startup script (`start.sh`) provides better error messages:

```bash
# Test the startup script directly
sudo -u catabot /opt/catabot/start.sh
```

This will show exactly which import or configuration is failing.

### Step 5: Check System Resources

```bash
# Check disk space
df -h /opt/catabot

# Check memory
free -h

# Check if system is overloaded
top
```

### Step 6: Verify Service Configuration

```bash
# Check service file syntax
sudo systemctl cat catabot

# Reload systemd if you made changes
sudo systemctl daemon-reload

# Check service status
sudo systemctl status catabot -l
```

## Complete Diagnostic Workflow

Run these commands in order:

```bash
# 1. Check service status
sudo systemctl status catabot

# 2. View recent logs
sudo journalctl -u catabot -n 50

# 3. Run diagnostic script
sudo ./diagnose.sh

# 4. Test manual startup
sudo -u catabot bash -c "cd /opt/catabot && source venv/bin/activate && python3 app.py"

# 5. Check for specific errors in logs
sudo grep -i error /opt/catabot/logs/*.log | tail -20

# 6. Verify all dependencies
/opt/catabot/venv/bin/pip list | grep -E "flask|requests|openai|beautifulsoup4"
```

## Still Not Working?

### Enable Debug Mode Temporarily

```bash
# Edit .env
sudo nano /opt/catabot/.env

# Change:
FLASK_DEBUG=1

# Restart
sudo systemctl restart catabot

# Watch logs in real-time
sudo journalctl -u catabot -f
```

### Reinstall Dependencies

```bash
cd /opt/catabot
sudo -u catabot bash -c "source venv/bin/activate && pip install --force-reinstall -r requirements.txt"
sudo systemctl restart catabot
```

### Check for Conflicting Processes

```bash
# Check if another instance is running
ps aux | grep python | grep catabot

# Kill any orphaned processes
sudo pkill -f "python.*app.py"

# Restart service
sudo systemctl restart catabot
```

### Verify Network Configuration

```bash
# Check if port is accessible
curl http://localhost:5000

# Check if nginx is interfering
sudo systemctl status nginx

# Test without nginx
sudo systemctl stop nginx
sudo systemctl restart catabot
curl http://localhost:5000
sudo systemctl start nginx
```

## Getting Help

When asking for help, provide:

1. **Full error logs:**
   ```bash
   sudo journalctl -u catabot -n 100 --no-pager > catabot_error.log
   ```

2. **Diagnostic output:**
   ```bash
   sudo ./diagnose.sh > diagnostic_output.txt
   ```

3. **Manual startup attempt:**
   ```bash
   sudo -u catabot bash -c "cd /opt/catabot && source venv/bin/activate && python3 app.py" 2>&1 | tee manual_start.log
   ```

4. **System information:**
   ```bash
   uname -a
   python3 --version
   cat /etc/os-release
   ```

## Quick Fix Checklist

- [ ] Dependencies installed: `pip list | grep flask`
- [ ] .env file exists: `ls -la /opt/catabot/.env`
- [ ] Correct permissions: `ls -ld /opt/catabot`
- [ ] Port available: `lsof -i :5000`
- [ ] All Python files present: `ls /opt/catabot/*.py`
- [ ] Templates directory exists: `ls /opt/catabot/templates/`
- [ ] Virtual environment works: `source venv/bin/activate && python3 --version`
- [ ] Service file correct: `systemctl cat catabot`
- [ ] Logs directory writable: `sudo -u catabot touch /opt/catabot/logs/test.log`
- [ ] Manual startup works: `sudo -u catabot bash -c "cd /opt/catabot && source venv/bin/activate && python3 app.py"`
