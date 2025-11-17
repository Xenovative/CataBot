# CataBot Deployment Without Nginx

## Quick Deploy (Recommended)

The deploy script now skips Nginx by default:

```bash
chmod +x deploy.sh
sudo ./deploy.sh
```

When prompted:
- **Port**: Enter your desired port (default: 5000)
- **Domain**: Press Enter to skip
- **Install Nginx?**: Press Enter or type `n` (default is No)

The application will run directly on the specified port.

## Access the Application

After deployment:

```bash
# From the server
curl http://localhost:5000

# From another machine (replace with your server IP)
curl http://YOUR_SERVER_IP:5000
```

## Firewall Configuration

Make sure your firewall allows the application port:

```bash
# Allow the port (replace 5000 with your port)
sudo ufw allow 5000/tcp

# Check firewall status
sudo ufw status
```

## Advantages of No-Nginx Setup

✅ **Simpler deployment** - Fewer components to configure
✅ **Faster setup** - No reverse proxy configuration needed
✅ **Direct access** - Application serves requests directly
✅ **Easier debugging** - One less layer to troubleshoot

## Disadvantages

❌ **No SSL termination** - HTTPS requires additional setup
❌ **No load balancing** - Can't easily distribute load
❌ **No static file optimization** - Nginx serves static files more efficiently
❌ **Port exposure** - Application port directly exposed

## When to Use This Setup

- **Development/Testing** environments
- **Internal networks** where Nginx isn't needed
- **Quick deployments** for evaluation
- **Troubleshooting** Nginx issues

## When to Add Nginx Later

Consider adding Nginx when you need:
- **SSL/HTTPS** support
- **Domain name** routing
- **Multiple applications** on same server
- **Static file caching**
- **Load balancing**

## Adding Nginx Later

If you want to add Nginx after deployment:

### 1. Install Nginx

```bash
sudo apt-get update
sudo apt-get install -y nginx
```

### 2. Create Nginx Configuration

```bash
sudo nano /etc/nginx/sites-available/catabot
```

Add:

```nginx
server {
    listen 80;
    server_name your-domain.com;  # or use _ for IP-based

    client_max_body_size 100M;

    location / {
        proxy_pass http://127.0.0.1:5000;  # Use your port
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        
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

### 3. Enable Site

```bash
sudo ln -s /etc/nginx/sites-available/catabot /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### 4. Update Firewall

```bash
# Allow HTTP/HTTPS
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp

# Optionally remove direct application port
sudo ufw delete allow 5000/tcp
```

### 5. Add SSL (Optional)

```bash
sudo apt-get install -y certbot python3-certbot-nginx
sudo certbot --nginx -d your-domain.com
```

## Security Considerations

### Without Nginx

1. **Application directly exposed** - Make sure your Flask app is secure
2. **Port-based access** - Use firewall rules carefully
3. **No request filtering** - Application handles all requests directly

### Recommendations

```bash
# 1. Use strong SECRET_KEY in .env
sudo nano /opt/catabot/.env
# Set: SECRET_KEY=<long-random-string>

# 2. Restrict access by IP (if needed)
sudo ufw allow from YOUR_IP_ADDRESS to any port 5000

# 3. Monitor logs regularly
sudo journalctl -u catabot -f

# 4. Keep system updated
sudo apt-get update && sudo apt-get upgrade -y
```

## Performance Tuning

### For Production Without Nginx

Consider using Gunicorn instead of Flask's built-in server:

```bash
# Install Gunicorn
cd /opt/catabot
sudo -u catabot bash -c "source venv/bin/activate && pip install gunicorn"

# Update service file
sudo nano /etc/systemd/system/catabot.service
```

Change `ExecStart` to:
```ini
ExecStart=/opt/catabot/venv/bin/gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

Then:
```bash
sudo systemctl daemon-reload
sudo systemctl restart catabot
```

## Monitoring

```bash
# Check service status
sudo systemctl status catabot

# View real-time logs
sudo journalctl -u catabot -f

# Check port is listening
sudo netstat -tlnp | grep 5000

# Test from command line
curl http://localhost:5000
```

## Troubleshooting

### Can't Access from External IP

```bash
# 1. Check if service is running
sudo systemctl status catabot

# 2. Check if port is listening on all interfaces
sudo netstat -tlnp | grep 5000
# Should show: 0.0.0.0:5000 (not 127.0.0.1:5000)

# 3. Verify .env has correct HOST
cat /opt/catabot/.env | grep HOST
# Should be: HOST=0.0.0.0

# 4. Check firewall
sudo ufw status | grep 5000

# 5. Test locally first
curl http://localhost:5000
```

### Connection Refused

```bash
# Check if app is actually running
ps aux | grep python | grep app.py

# Check logs for errors
sudo journalctl -u catabot -n 50

# Try manual start to see errors
sudo -u catabot bash -c "cd /opt/catabot && source venv/bin/activate && python3 app.py"
```

## Summary

**No-Nginx deployment is perfect for:**
- Quick testing and development
- Internal network deployments
- Simpler troubleshooting
- Learning and evaluation

**Add Nginx when you need:**
- Production-grade setup
- SSL/HTTPS support
- Domain-based routing
- Better performance and security

The deploy script now makes this choice easy - just say "no" to Nginx during setup!
