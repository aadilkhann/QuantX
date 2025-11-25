# Deployment Guide
# QuantX Trading System

**Version**: 1.0  
**Date**: November 25, 2025

---

## Table of Contents

1. [Prerequisites](#1-prerequisites)
2. [Development Setup](#2-development-setup)
3. [Docker Deployment](#3-docker-deployment)
4. [Production Deployment](#4-production-deployment)
5. [Configuration](#5-configuration)
6. [Monitoring](#6-monitoring)
7. [Troubleshooting](#7-troubleshooting)

---

## 1. Prerequisites

### 1.1 System Requirements

**Minimum**:
- CPU: 2 cores
- RAM: 4 GB
- Disk: 20 GB SSD
- OS: Linux (Ubuntu 20.04+), macOS, Windows 10+

**Recommended**:
- CPU: 4+ cores
- RAM: 16 GB
- Disk: 100 GB SSD
- OS: Linux (Ubuntu 22.04)

### 1.2 Software Requirements

- **Python**: 3.11 or higher
- **Docker**: 20.10+ (optional but recommended)
- **Docker Compose**: 2.0+
- **PostgreSQL**: 14+ (if not using Docker)
- **Redis**: 6+ (if not using Docker)
- **Git**: 2.30+

---

## 2. Development Setup

### 2.1 Clone Repository

```bash
cd /Users/adii/Builds/Algo-Trading
git clone https://github.com/yourusername/QuantX.git
cd QuantX
```

### 2.2 Install Python Dependencies

**Using Poetry (Recommended)**:

```bash
# Install Poetry
curl -sSL https://install.python-poetry.org | python3 -

# Install dependencies
poetry install

# Activate virtual environment
poetry shell
```

**Using pip**:

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2.3 Set Up Environment Variables

```bash
# Copy environment template
cp .env.example .env

# Edit .env with your configuration
nano .env
```

**Example `.env`**:
```bash
# Application
APP_ENV=development
DEBUG=true
SECRET_KEY=your-secret-key-here

# Database
DATABASE_URL=postgresql://quantx:password@localhost:5432/quantx
REDIS_URL=redis://localhost:6379/0

# API
API_HOST=0.0.0.0
API_PORT=8000

# Brokers (add your API keys)
ZERODHA_API_KEY=your-api-key
ZERODHA_API_SECRET=your-api-secret

# Data Providers
ALPHA_VANTAGE_API_KEY=your-api-key
POLYGON_API_KEY=your-api-key
```

### 2.4 Set Up Database

**Using Docker**:
```bash
docker run -d \
  --name quantx-postgres \
  -e POSTGRES_USER=quantx \
  -e POSTGRES_PASSWORD=password \
  -e POSTGRES_DB=quantx \
  -p 5432:5432 \
  postgres:14
```

**Manual Installation**:
```bash
# Install PostgreSQL
sudo apt-get install postgresql-14

# Create database
sudo -u postgres psql
CREATE DATABASE quantx;
CREATE USER quantx WITH PASSWORD 'password';
GRANT ALL PRIVILEGES ON DATABASE quantx TO quantx;
\q
```

**Run Migrations**:
```bash
# Using Alembic
alembic upgrade head
```

### 2.5 Set Up Redis

**Using Docker**:
```bash
docker run -d \
  --name quantx-redis \
  -p 6379:6379 \
  redis:6
```

**Manual Installation**:
```bash
sudo apt-get install redis-server
sudo systemctl start redis
```

### 2.6 Run Development Server

```bash
# Start API server
python -m quantx.api.main

# Or using uvicorn directly
uvicorn quantx.api.main:app --reload --host 0.0.0.0 --port 8000
```

**Verify Installation**:
```bash
curl http://localhost:8000/health
# Expected: {"status": "healthy"}
```

---

## 3. Docker Deployment

### 3.1 Build Docker Image

```bash
# Build image
docker build -t quantx:latest .

# Verify image
docker images | grep quantx
```

### 3.2 Docker Compose Setup

**Create `docker-compose.yml`**:

```yaml
version: '3.8'

services:
  # PostgreSQL Database
  postgres:
    image: postgres:14
    container_name: quantx-postgres
    environment:
      POSTGRES_USER: quantx
      POSTGRES_PASSWORD: ${DB_PASSWORD}
      POSTGRES_DB: quantx
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U quantx"]
      interval: 10s
      timeout: 5s
      retries: 5

  # Redis Cache
  redis:
    image: redis:6
    container_name: quantx-redis
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 3s
      retries: 5

  # QuantX API
  api:
    build: .
    container_name: quantx-api
    environment:
      DATABASE_URL: postgresql://quantx:${DB_PASSWORD}@postgres:5432/quantx
      REDIS_URL: redis://redis:6379/0
      SECRET_KEY: ${SECRET_KEY}
    ports:
      - "8000:8000"
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy
    volumes:
      - ./data:/app/data
      - ./logs:/app/logs
    command: uvicorn quantx.api.main:app --host 0.0.0.0 --port 8000

  # Prometheus Monitoring
  prometheus:
    image: prom/prometheus:latest
    container_name: quantx-prometheus
    ports:
      - "9090:9090"
    volumes:
      - ./configs/prometheus.yml:/etc/prometheus/prometheus.yml
      - prometheus_data:/prometheus
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'

  # Grafana Dashboard
  grafana:
    image: grafana/grafana:latest
    container_name: quantx-grafana
    ports:
      - "3000:3000"
    environment:
      GF_SECURITY_ADMIN_PASSWORD: ${GRAFANA_PASSWORD}
    volumes:
      - grafana_data:/var/lib/grafana
    depends_on:
      - prometheus

volumes:
  postgres_data:
  redis_data:
  prometheus_data:
  grafana_data:
```

### 3.3 Start Services

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Check status
docker-compose ps
```

### 3.4 Stop Services

```bash
# Stop all services
docker-compose down

# Stop and remove volumes
docker-compose down -v
```

---

## 4. Production Deployment

### 4.1 Server Setup

**Update System**:
```bash
sudo apt-get update
sudo apt-get upgrade -y
```

**Install Dependencies**:
```bash
sudo apt-get install -y \
  python3.11 \
  python3-pip \
  postgresql-14 \
  redis-server \
  nginx \
  supervisor
```

### 4.2 Application Deployment

**Clone Repository**:
```bash
cd /opt
sudo git clone https://github.com/yourusername/QuantX.git
cd QuantX
```

**Install Dependencies**:
```bash
sudo pip3 install -r requirements.txt
```

**Set Up Environment**:
```bash
sudo cp .env.example .env
sudo nano .env
# Update with production values
```

**Run Migrations**:
```bash
alembic upgrade head
```

### 4.3 Nginx Configuration

**Create Nginx Config** (`/etc/nginx/sites-available/quantx`):

```nginx
upstream quantx_api {
    server 127.0.0.1:8000;
}

server {
    listen 80;
    server_name your-domain.com;

    # Redirect HTTP to HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name your-domain.com;

    # SSL Configuration
    ssl_certificate /etc/letsencrypt/live/your-domain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/your-domain.com/privkey.pem;

    # Security Headers
    add_header Strict-Transport-Security "max-age=31536000" always;
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;

    # API Proxy
    location /api/ {
        proxy_pass http://quantx_api;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # WebSocket
    location /ws {
        proxy_pass http://quantx_api;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }

    # Static Files
    location /static/ {
        alias /opt/QuantX/static/;
    }
}
```

**Enable Site**:
```bash
sudo ln -s /etc/nginx/sites-available/quantx /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### 4.4 Supervisor Configuration

**Create Supervisor Config** (`/etc/supervisor/conf.d/quantx.conf`):

```ini
[program:quantx-api]
command=/usr/bin/python3 -m uvicorn quantx.api.main:app --host 0.0.0.0 --port 8000 --workers 4
directory=/opt/QuantX
user=www-data
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=/var/log/quantx/api.log
environment=PATH="/usr/bin",PYTHONPATH="/opt/QuantX"
```

**Start Service**:
```bash
sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl start quantx-api
```

### 4.5 SSL Certificate (Let's Encrypt)

```bash
# Install Certbot
sudo apt-get install certbot python3-certbot-nginx

# Obtain certificate
sudo certbot --nginx -d your-domain.com

# Auto-renewal
sudo certbot renew --dry-run
```

---

## 5. Configuration

### 5.1 Application Configuration

**`configs/config.yaml`**:

```yaml
app:
  name: QuantX
  version: 0.1.0
  environment: production
  debug: false

database:
  url: ${DATABASE_URL}
  pool_size: 20
  max_overflow: 10

redis:
  url: ${REDIS_URL}
  max_connections: 50

api:
  host: 0.0.0.0
  port: 8000
  workers: 4
  cors_origins:
    - https://your-domain.com

logging:
  level: INFO
  format: json
  file: /var/log/quantx/app.log

backtesting:
  max_concurrent: 10
  timeout: 3600

risk:
  max_position_size: 0.1
  max_daily_loss: 0.02
  max_drawdown: 0.15
```

### 5.2 Broker Configuration

**`configs/brokers/zerodha.yaml`**:

```yaml
broker: zerodha
api_key: ${ZERODHA_API_KEY}
api_secret: ${ZERODHA_API_SECRET}
timeout: 30
retry_attempts: 3
```

---

## 6. Monitoring

### 6.1 Health Checks

```bash
# API Health
curl http://localhost:8000/health

# Database Health
curl http://localhost:8000/health/db

# Redis Health
curl http://localhost:8000/health/redis
```

### 6.2 Prometheus Metrics

Access metrics at: `http://localhost:9090`

**Key Metrics**:
- `quantx_api_requests_total`: Total API requests
- `quantx_api_latency_seconds`: API latency
- `quantx_backtests_running`: Running backtests
- `quantx_live_sessions_active`: Active live trading sessions

### 6.3 Grafana Dashboards

Access dashboard at: `http://localhost:3000`

**Default Login**:
- Username: `admin`
- Password: Set in `GRAFANA_PASSWORD`

---

## 7. Troubleshooting

### 7.1 Common Issues

**Issue**: Database connection failed

**Solution**:
```bash
# Check PostgreSQL status
sudo systemctl status postgresql

# Check connection
psql -h localhost -U quantx -d quantx

# Check logs
sudo tail -f /var/log/postgresql/postgresql-14-main.log
```

**Issue**: Redis connection failed

**Solution**:
```bash
# Check Redis status
sudo systemctl status redis

# Test connection
redis-cli ping

# Check logs
sudo tail -f /var/log/redis/redis-server.log
```

**Issue**: API not responding

**Solution**:
```bash
# Check if process is running
ps aux | grep uvicorn

# Check logs
sudo tail -f /var/log/quantx/api.log

# Restart service
sudo supervisorctl restart quantx-api
```

### 7.2 Logs Location

- **Application**: `/var/log/quantx/app.log`
- **API**: `/var/log/quantx/api.log`
- **Nginx**: `/var/log/nginx/access.log`, `/var/log/nginx/error.log`
- **PostgreSQL**: `/var/log/postgresql/postgresql-14-main.log`
- **Redis**: `/var/log/redis/redis-server.log`

### 7.3 Performance Tuning

**PostgreSQL**:
```sql
-- Increase connection pool
ALTER SYSTEM SET max_connections = 200;

-- Tune memory
ALTER SYSTEM SET shared_buffers = '4GB';
ALTER SYSTEM SET effective_cache_size = '12GB';

-- Restart
sudo systemctl restart postgresql
```

**Redis**:
```bash
# Edit /etc/redis/redis.conf
maxmemory 2gb
maxmemory-policy allkeys-lru

# Restart
sudo systemctl restart redis
```

---

## 8. Backup & Recovery

### 8.1 Database Backup

```bash
# Backup
pg_dump -U quantx quantx > backup_$(date +%Y%m%d).sql

# Restore
psql -U quantx quantx < backup_20250101.sql
```

### 8.2 Automated Backups

**Create Backup Script** (`scripts/backup.sh`):

```bash
#!/bin/bash
BACKUP_DIR="/backups/quantx"
DATE=$(date +%Y%m%d_%H%M%S)

# Database backup
pg_dump -U quantx quantx | gzip > $BACKUP_DIR/db_$DATE.sql.gz

# Data backup
tar -czf $BACKUP_DIR/data_$DATE.tar.gz /opt/QuantX/data

# Keep only last 7 days
find $BACKUP_DIR -type f -mtime +7 -delete
```

**Add to Crontab**:
```bash
# Run daily at 2 AM
0 2 * * * /opt/QuantX/scripts/backup.sh
```

---

**Deployment Guide Version**: 1.0  
**Last Updated**: November 25, 2025  
**Support**: devops@quantx.io
