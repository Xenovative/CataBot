# Deploy Script Improvements

## Interactive Configuration

The deployment script now prompts for important configuration options before starting the deployment.

## New Features

### 1. **Port Number Configuration**
```bash
Enter port number for CataBot (default: 5000):
```
- Prompts user for custom port
- Validates port range (1024-65535)
- Falls back to 5000 if invalid
- Updates all configurations automatically

### 2. **Domain Name Configuration**
```bash
Enter domain name (or press Enter for IP-based access):
```
- Optional domain name input
- Uses `_` (wildcard) for IP-based access
- Configures Nginx server_name accordingly
- Enables SSL option if domain provided

### 3. **SSL/HTTPS Setup**
```bash
Set up SSL with Let's Encrypt? (y/n, default: n):
```
- Only shown if domain name provided
- Automatically installs Certbot
- Obtains and configures SSL certificate
- Sets up auto-renewal cron job
- Graceful fallback if SSL fails

### 4. **Configuration Summary**
```bash
Configuration Summary:
  Port: 8080
  Domain: example.com
  SSL: Yes

Continue with deployment? (y/n):
```
- Shows all configuration choices
- Allows user to confirm or cancel
- Prevents accidental deployments

## User Experience Flow

### Example 1: Simple IP-based Deployment
```bash
$ sudo ./deploy.sh

=== CataBot Deployment Script ===

Configuration:

Enter port number for CataBot (default: 5000): 
Using port: 5000

Enter domain name (or press Enter for IP-based access): 
[i] Using IP-based access

Configuration Summary:
  Port: 5000
  Domain: _
  SSL: No

Continue with deployment? (y/n): y

[Deployment proceeds...]

Access the application at: http://192.168.1.100:5000
```

### Example 2: Domain with SSL
```bash
$ sudo ./deploy.sh

=== CataBot Deployment Script ===

Configuration:

Enter port number for CataBot (default: 5000): 8080
Using port: 8080

Enter domain name (or press Enter for IP-based access): catabot.example.com
[i] Domain: catabot.example.com

Set up SSL with Let's Encrypt? (y/n, default: n): y

Configuration Summary:
  Port: 8080
  Domain: catabot.example.com
  SSL: Yes

Continue with deployment? (y/n): y

[Deployment proceeds...]
[✓] SSL certificate obtained and configured
[✓] SSL auto-renewal configured

Access the application at: https://catabot.example.com
```

### Example 3: Custom Port, No SSL
```bash
$ sudo ./deploy.sh

=== CataBot Deployment Script ===

Configuration:

Enter port number for CataBot (default: 5000): 3000
Using port: 3000

Enter domain name (or press Enter for IP-based access): myapp.local
[i] Domain: myapp.local

Set up SSL with Let's Encrypt? (y/n, default: n): n

Configuration Summary:
  Port: 3000
  Domain: myapp.local
  SSL: No

Continue with deployment? (y/n): y

[Deployment proceeds...]

Access the application at: http://myapp.local

Important:
  1. Edit /opt/catabot/.env to add your API keys
  2. Set up SSL with: sudo certbot --nginx -d myapp.local
```

## Validation Features

### Port Validation
```bash
# Invalid port (too low)
Enter port number: 80
[✗] Invalid port number. Using default: 5000

# Invalid port (too high)
Enter port number: 99999
[✗] Invalid port number. Using default: 5000

# Invalid port (not a number)
Enter port number: abc
[✗] Invalid port number. Using default: 5000

# Valid port
Enter port number: 8080
[✓] Using port: 8080
```

### SSL Validation
- Only offered if domain name provided
- Checks if Certbot is installed
- Installs if missing
- Handles SSL setup failures gracefully
- Provides manual setup instructions if fails

## Configuration Applied To

The user-provided configuration is automatically applied to:

1. **Nginx Configuration**
   - `server_name` directive
   - `proxy_pass` port
   - SSL certificates (if enabled)

2. **Systemd Service**
   - Port in environment variables

3. **Environment File**
   - PORT variable

4. **Final Instructions**
   - Correct URL displayed
   - SSL setup command (if not configured)

## Benefits

### 1. **Flexibility**
- Users can customize deployment
- No need to edit script manually
- Works for various scenarios

### 2. **Safety**
- Validation prevents errors
- Confirmation before deployment
- Clear summary of choices

### 3. **Automation**
- SSL setup fully automated
- Auto-renewal configured
- No manual certificate management

### 4. **User-Friendly**
- Clear prompts and messages
- Helpful defaults
- Informative error messages

### 5. **Production-Ready**
- SSL/HTTPS support
- Custom ports for multiple instances
- Domain-based configuration

## Technical Details

### Port Range
- Minimum: 1024 (non-privileged)
- Maximum: 65535 (valid TCP port)
- Default: 5000

### Domain Name
- Optional input
- Uses `_` for wildcard (any IP)
- Validates format (basic check)
- Used in Nginx server_name

### SSL Setup
- Uses Let's Encrypt (free)
- Certbot with Nginx plugin
- Non-interactive mode
- Auto-renewal via cron (daily check)

### Configuration Storage
All settings stored in:
- `/etc/nginx/sites-available/catabot` - Nginx config
- `/etc/systemd/system/catabot.service` - Service config
- `/opt/catabot/.env` - Environment variables

## Backward Compatibility

The script maintains backward compatibility:
- Default values for all prompts
- Works without user input (press Enter for defaults)
- No breaking changes to existing deployments

## Future Enhancements

Possible improvements:
- Email for SSL certificate notifications
- Multiple domain support
- Custom application directory
- Database configuration
- Redis/cache configuration
- Custom backup schedule
- Monitoring setup options

## Testing

### Test Scenarios

1. **Default Configuration**
   ```bash
   # Press Enter for all prompts
   # Should use: port 5000, IP-based, no SSL
   ```

2. **Custom Port**
   ```bash
   # Enter: 8080
   # Should configure everything for port 8080
   ```

3. **Domain with SSL**
   ```bash
   # Enter domain and 'y' for SSL
   # Should set up HTTPS automatically
   ```

4. **Invalid Input**
   ```bash
   # Enter invalid port, invalid domain
   # Should handle gracefully with defaults
   ```

5. **Cancel Deployment**
   ```bash
   # Enter 'n' at confirmation
   # Should exit without changes
   ```

## Troubleshooting

### SSL Setup Fails
```bash
[✗] SSL setup failed. You can set it up manually later with: sudo certbot --nginx -d example.com
```
**Causes:**
- Domain not pointing to server
- Port 80/443 blocked
- Certbot rate limit

**Solution:**
- Verify DNS records
- Check firewall
- Run manual command after fixing

### Port Already in Use
```bash
# Check what's using the port
sudo lsof -i :5000

# Kill the process or choose different port
```

### Domain Not Resolving
```bash
# Test DNS
nslookup your-domain.com

# Test from server
curl -I http://your-domain.com
```

## Summary

The improved deployment script provides:
- ✅ Interactive configuration
- ✅ Port customization
- ✅ Domain support
- ✅ Automatic SSL setup
- ✅ Input validation
- ✅ Confirmation prompts
- ✅ Clear feedback
- ✅ Production-ready defaults

Users can now deploy CataBot with their preferred configuration in a single command!
