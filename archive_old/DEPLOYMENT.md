# AYKA Lead Generation - Production Deployment Guide

## Prerequisites

### Server Requirements
- Ubuntu 20.04+ or similar Linux distribution
- 4GB RAM minimum (8GB recommended)
- 20GB disk space minimum
- Python 3.10+
- Node.js 18+
- Docker and Docker Compose
- Nginx
- PostgreSQL 14+ (via Docker)

### Required Services
- Domain name with DNS configured
- SSL certificate (Let's Encrypt recommended)
- SMTP email account (Gmail with app password)
- API Keys:
  - OpenAI API key
  - AssemblyAI API key (for transcription)
  - Serper API key (for web search in event discovery)

## 1. Server Setup

### Initial Server Configuration
```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install required packages
sudo apt install -y git curl build-essential nginx certbot python3-certbot-nginx

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Install Node.js 18
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt install -y nodejs

# Install Python 3.10
sudo apt install -y python3.10 python3.10-venv python3-pip
```

## 2. Clone Repository

```bash
cd /opt
sudo git clone <YOUR_REPO_URL> ayka_lead_gen
sudo chown -R $USER:$USER ayka_lead_gen
cd ayka_lead_gen
```

## 3. Environment Configuration

### Backend Environment Variables
Create `/opt/ayka_lead_gen/.env`:
```bash
# Application
APP_NAME="Ayka Lead Generation"
APP_ENV="production"
DEBUG=false
API_HOST="0.0.0.0"
API_PORT=8000

# Security
SECRET_KEY="<GENERATE_STRONG_SECRET_KEY>"
ALGORITHM="HS256"
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Database - PostgreSQL
DATABASE_URL="postgresql://ayka:YOUR_SECURE_PASSWORD@localhost:5432/ayka"

# OpenAI
OPENAI_API_KEY="sk-..."

# AssemblyAI (for transcription)
ASSEMBLYAI_API_KEY="..."

# Serper (for web search)
SERPER_API_KEY="..."

# Email Configuration (Gmail)
EMAIL_USER="your-email@gmail.com"
EMAIL_PASSWORD="your-app-specific-password"

# Speech-to-Text
STT_PROVIDER="assemblyai"
ENABLE_DIARIZATION=true

# CORS (update with your domain)
CORS_ORIGINS=["https://yourdomain.com", "https://www.yourdomain.com"]

# File Storage
MAX_UPLOAD_SIZE=500000000
```

### Frontend Environment Variables
Create `/opt/ayka_lead_gen/frontend/.env.production`:
```bash
NEXT_PUBLIC_API_URL=https://api.yourdomain.com
```

## 4. Database Setup

### Start PostgreSQL with Docker
```bash
cd /opt/ayka_lead_gen

# Create docker-compose.yml for production (see docker-compose.prod.yml)
docker-compose -f docker-compose.prod.yml up -d postgres

# Wait for PostgreSQL to start
sleep 10

# Run migrations
docker exec -i ayka_db psql -U ayka -d ayka < backend/migrations/create_tables.sql
docker exec -i ayka_db psql -U ayka -d ayka < backend/migrations/add_exhibitors_column.sql
docker exec -i ayka_db psql -U ayka -d ayka < backend/migrations/create_lead_generation_jobs.sql
```

## 5. Backend Setup

```bash
cd /opt/ayka_lead_gen

# Create Python virtual environment
python3.10 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt
pip install -r agent_requirements.txt

# Test backend
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
# Should start without errors, then Ctrl+C to stop
```

## 6. Frontend Setup

```bash
cd /opt/ayka_lead_gen/frontend

# Install dependencies
npm install

# Build for production
npm run build

# Test production build
npm start
# Should start on port 3000, then Ctrl+C to stop
```

## 7. Process Management with Systemd

### Backend Service
Create `/etc/systemd/system/ayka-backend.service`:
```ini
[Unit]
Description=AYKA Backend API
After=network.target postgresql.service

[Service]
Type=simple
User=www-data
Group=www-data
WorkingDirectory=/opt/ayka_lead_gen/backend
Environment="PATH=/opt/ayka_lead_gen/.venv/bin"
ExecStart=/opt/ayka_lead_gen/.venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

### Frontend Service
Create `/etc/systemd/system/ayka-frontend.service`:
```ini
[Unit]
Description=AYKA Frontend
After=network.target

[Service]
Type=simple
User=www-data
Group=www-data
WorkingDirectory=/opt/ayka_lead_gen/frontend
Environment="NODE_ENV=production"
Environment="PORT=3000"
ExecStart=/usr/bin/npm start
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

### Enable and Start Services
```bash
sudo systemctl daemon-reload
sudo systemctl enable ayka-backend
sudo systemctl enable ayka-frontend
sudo systemctl start ayka-backend
sudo systemctl start ayka-frontend

# Check status
sudo systemctl status ayka-backend
sudo systemctl status ayka-frontend
```

## 8. Nginx Configuration

### Create Nginx Config
Create `/etc/nginx/sites-available/ayka`:
```nginx
# API Backend
server {
    listen 80;
    server_name api.yourdomain.com;

    client_max_body_size 500M;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;
        proxy_read_timeout 300s;
        proxy_connect_timeout 75s;
    }
}

# Frontend
server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;

    location / {
        proxy_pass http://127.0.0.1:3000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }
}
```

### Enable Site and Get SSL
```bash
# Enable site
sudo ln -s /etc/nginx/sites-available/ayka /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx

# Get SSL certificates
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com -d api.yourdomain.com

# Auto-renewal is set up automatically by certbot
```

## 9. File Storage Setup

```bash
# Create directories for persistent storage
sudo mkdir -p /opt/ayka_lead_gen/data/recordings
sudo mkdir -p /opt/ayka_lead_gen/data/temp_transcripts
sudo mkdir -p /opt/ayka_lead_gen/data/leads_data

# Set permissions
sudo chown -R www-data:www-data /opt/ayka_lead_gen/data
sudo chmod -R 755 /opt/ayka_lead_gen/data
```

## 10. Logging and Monitoring

### Backend Logs
```bash
# View backend logs
sudo journalctl -u ayka-backend -f

# View frontend logs
sudo journalctl -u ayka-frontend -f
```

### Log Rotation
Create `/etc/logrotate.d/ayka`:
```
/opt/ayka_lead_gen/logs/*.log {
    daily
    missingok
    rotate 14
    compress
    delaycompress
    notifempty
    create 0640 www-data www-data
    sharedscripts
}
```

## 11. Backup Strategy

### Database Backup Script
Create `/opt/ayka_lead_gen/scripts/backup-db.sh`:
```bash
#!/bin/bash
BACKUP_DIR="/opt/ayka_lead_gen/backups"
DATE=$(date +%Y%m%d_%H%M%S)

mkdir -p $BACKUP_DIR

docker exec ayka_db pg_dump -U ayka ayka > $BACKUP_DIR/ayka_backup_$DATE.sql

# Keep only last 7 days
find $BACKUP_DIR -name "ayka_backup_*.sql" -mtime +7 -delete
```

### Set up Cron
```bash
sudo crontab -e
# Add line:
0 2 * * * /opt/ayka_lead_gen/scripts/backup-db.sh
```

## 12. Security Checklist

- [ ] Change all default passwords
- [ ] Set strong SECRET_KEY in .env
- [ ] Enable firewall (UFW)
  ```bash
  sudo ufw allow 22/tcp
  sudo ufw allow 80/tcp
  sudo ufw allow 443/tcp
  sudo ufw enable
  ```
- [ ] Set up fail2ban
  ```bash
  sudo apt install fail2ban
  sudo systemctl enable fail2ban
  ```
- [ ] Restrict PostgreSQL to localhost only
- [ ] Use environment variables for all secrets (never commit .env)
- [ ] Set up regular security updates

## 13. Post-Deployment Verification

```bash
# Check all services are running
sudo systemctl status ayka-backend
sudo systemctl status ayka-frontend
sudo docker ps  # PostgreSQL should be running

# Test API
curl https://api.yourdomain.com/health

# Test frontend
curl https://yourdomain.com

# Check logs
sudo journalctl -u ayka-backend --since "10 minutes ago"
sudo journalctl -u ayka-frontend --since "10 minutes ago"
```

## 14. Troubleshooting

### Backend won't start
```bash
# Check logs
sudo journalctl -u ayka-backend -n 50

# Check if port is in use
sudo netstat -tlnp | grep 8000

# Test manually
cd /opt/ayka_lead_gen/backend
source ../.venv/bin/activate
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### Database connection issues
```bash
# Check if PostgreSQL is running
docker ps | grep postgres

# Test connection
docker exec -it ayka_db psql -U ayka -d ayka

# Check logs
docker logs ayka_db
```

### Frontend build fails
```bash
# Clear cache and rebuild
cd /opt/ayka_lead_gen/frontend
rm -rf .next node_modules
npm install
npm run build
```

## 15. Updating Application

```bash
cd /opt/ayka_lead_gen

# Pull latest changes
git pull origin main

# Backend
source .venv/bin/activate
pip install -r requirements.txt
sudo systemctl restart ayka-backend

# Frontend
cd frontend
npm install
npm run build
sudo systemctl restart ayka-frontend

# Run any new migrations
# Check /backend/migrations/ for new .sql files
```

## 16. Monitoring and Alerts

Consider setting up:
- **Sentry** for error tracking (add SENTRY_DSN to .env)
- **Uptime monitoring** (UptimeRobot, Pingdom)
- **Log aggregation** (Papertrail, Loggly)
- **Performance monitoring** (New Relic, DataDog)

## Support

For issues:
1. Check logs: `sudo journalctl -u ayka-backend -f`
2. Check database: `docker exec -it ayka_db psql -U ayka -d ayka`
3. Verify environment variables are set correctly
4. Check disk space: `df -h`
5. Check memory: `free -h`