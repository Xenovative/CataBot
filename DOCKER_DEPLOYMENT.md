# Docker Deployment Guide

## Quick Start with Docker

### Prerequisites
- Docker installed
- Docker Compose installed
- At least 2GB RAM
- 10GB free disk space

### One-Command Deployment

```bash
# Clone repository
git clone https://your-repo/CataBot.git
cd CataBot

# Create environment file
cp .env.example .env
nano .env  # Add your API keys

# Start with Docker Compose
docker-compose up -d
```

Access at: http://localhost

## Docker Deployment Options

### Option 1: Docker Compose (Recommended)

```bash
# Start services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down

# Restart services
docker-compose restart

# Update and restart
docker-compose pull
docker-compose up -d
```

### Option 2: Docker Only

```bash
# Build image
docker build -t catabot:latest .

# Run container
docker run -d \
  --name catabot \
  -p 5000:5000 \
  -v $(pwd)/pdfs:/app/pdfs \
  -v $(pwd)/uploads:/app/uploads \
  -v $(pwd)/job_history:/app/job_history \
  -v $(pwd)/logs:/app/logs \
  -e OPENAI_API_KEY=your-key \
  catabot:latest

# View logs
docker logs -f catabot

# Stop container
docker stop catabot

# Remove container
docker rm catabot
```

## Environment Configuration

Create `.env` file:

```bash
# API Keys
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...

# Flask Configuration
FLASK_ENV=production
FLASK_DEBUG=0
SECRET_KEY=your-secret-key
```

## Volume Management

### Persistent Data

Docker Compose automatically creates volumes for:
- `pdfs/` - Downloaded PDF files
- `uploads/` - Uploaded files
- `job_history/` - Job history data
- `logs/` - Application logs

### Backup Volumes

```bash
# Backup all data
docker run --rm \
  -v catabot_job_history:/data \
  -v $(pwd):/backup \
  alpine tar czf /backup/catabot_backup_$(date +%Y%m%d).tar.gz /data

# Restore data
docker run --rm \
  -v catabot_job_history:/data \
  -v $(pwd):/backup \
  alpine tar xzf /backup/catabot_backup_20250117.tar.gz -C /
```

## Nginx Configuration

The Docker Compose setup includes Nginx as a reverse proxy.

### Enable SSL

1. Get SSL certificates (Let's Encrypt):

```bash
# Install Certbot
sudo apt-get install certbot

# Get certificate
sudo certbot certonly --standalone -d your-domain.com

# Copy certificates
mkdir ssl
sudo cp /etc/letsencrypt/live/your-domain.com/fullchain.pem ssl/
sudo cp /etc/letsencrypt/live/your-domain.com/privkey.pem ssl/
```

2. Update `nginx.conf`:

```nginx
server {
    listen 443 ssl http2;
    server_name your-domain.com;

    ssl_certificate /etc/nginx/ssl/fullchain.pem;
    ssl_certificate_key /etc/nginx/ssl/privkey.pem;
    
    # ... rest of configuration
}

server {
    listen 80;
    server_name your-domain.com;
    return 301 https://$server_name$request_uri;
}
```

3. Restart Nginx:

```bash
docker-compose restart nginx
```

## Monitoring

### View Logs

```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f catabot
docker-compose logs -f nginx

# Last 100 lines
docker-compose logs --tail=100 catabot
```

### Check Status

```bash
# Service status
docker-compose ps

# Resource usage
docker stats catabot

# Health check
docker inspect --format='{{.State.Health.Status}}' catabot
```

## Maintenance

### Update Application

```bash
# Pull latest code
git pull

# Rebuild and restart
docker-compose build
docker-compose up -d

# Or force recreate
docker-compose up -d --force-recreate
```

### Clean Up

```bash
# Remove stopped containers
docker container prune

# Remove unused images
docker image prune -a

# Remove unused volumes
docker volume prune

# Full cleanup
docker system prune -a --volumes
```

### Database Backup

```bash
# Create backup script
cat > backup.sh << 'EOF'
#!/bin/bash
BACKUP_DIR="./backups"
DATE=$(date +%Y%m%d_%H%M%S)
mkdir -p $BACKUP_DIR

docker-compose exec -T catabot tar czf - \
  /app/job_history \
  /app/settings.json \
  > $BACKUP_DIR/catabot_backup_$DATE.tar.gz

echo "Backup created: $BACKUP_DIR/catabot_backup_$DATE.tar.gz"
EOF

chmod +x backup.sh
./backup.sh
```

## Scaling

### Multiple Instances

```yaml
# docker-compose.yml
services:
  catabot:
    # ... configuration
    deploy:
      replicas: 3
```

### Load Balancing

Update `nginx.conf`:

```nginx
upstream catabot_backend {
    server catabot_1:5000;
    server catabot_2:5000;
    server catabot_3:5000;
}

server {
    location / {
        proxy_pass http://catabot_backend;
        # ... rest of configuration
    }
}
```

## Troubleshooting

### Container Won't Start

```bash
# Check logs
docker-compose logs catabot

# Check container status
docker-compose ps

# Inspect container
docker inspect catabot
```

### Port Already in Use

```bash
# Find process using port
sudo lsof -i :5000

# Change port in docker-compose.yml
ports:
  - "8000:5000"
```

### Permission Issues

```bash
# Fix volume permissions
sudo chown -R $USER:$USER pdfs uploads job_history logs
```

### Out of Memory

```bash
# Increase memory limit in docker-compose.yml
services:
  catabot:
    mem_limit: 2g
    mem_reservation: 1g
```

## Production Deployment

### Security Checklist

- [ ] Use HTTPS/SSL
- [ ] Set strong SECRET_KEY
- [ ] Secure API keys in .env
- [ ] Enable firewall
- [ ] Regular backups
- [ ] Monitor logs
- [ ] Update regularly
- [ ] Limit file upload size
- [ ] Use non-root user in container

### Performance Optimization

```yaml
# docker-compose.yml
services:
  catabot:
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 2G
        reservations:
          cpus: '1'
          memory: 1G
```

### Health Monitoring

```bash
# Add monitoring service
services:
  prometheus:
    image: prom/prometheus
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml
    ports:
      - "9090:9090"

  grafana:
    image: grafana/grafana
    ports:
      - "3000:3000"
    depends_on:
      - prometheus
```

## Migration from VM to Docker

```bash
# 1. Backup data from VM
ssh user@vm "cd /opt/catabot && tar czf - job_history settings.json" > backup.tar.gz

# 2. Extract to Docker volumes
tar xzf backup.tar.gz -C ./job_history/

# 3. Start Docker containers
docker-compose up -d

# 4. Verify data
docker-compose exec catabot ls -la /app/job_history
```

## Support

For Docker-specific issues:
- Check Docker logs
- Review Docker documentation
- Check container health status
- Verify volume mounts
- Check network connectivity
