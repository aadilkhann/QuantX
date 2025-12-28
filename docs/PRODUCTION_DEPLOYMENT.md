# Production Deployment Guide

**QuantX Live Trading System**  
**Version**: 1.0  
**Last Updated**: December 27, 2025

---

## 🎯 Overview

This guide covers deploying QuantX to production for live trading on Indian markets (NSE/BSE).

**Prerequisites**:
- ✅ Phase 1-3 complete (backtesting, ML, live trading)
- ✅ Phase 4 infrastructure (testing, persistence, monitoring)
- ✅ Zerodha account with API access
- ✅ Production server (Linux recommended)

---

## 📋 Pre-Deployment Checklist

### 1. Code Quality ✅
- [ ] All tests passing (target: 70%+ coverage)
- [ ] Linting checks pass (black, flake8, mypy)
- [ ] No critical security vulnerabilities
- [ ] Code reviewed and approved

### 2. Configuration ✅
- [ ] Environment variables configured
- [ ] API keys securely stored
- [ ] Risk limits properly set
- [ ] Logging configured

### 3. Testing ✅
- [ ] Unit tests pass
- [ ] Integration tests pass
- [ ] Paper trading tested successfully
- [ ] Disaster recovery tested

### 4. Monitoring ✅
- [ ] Health endpoints configured
- [ ] Metrics collection enabled
- [ ] Alerting configured
- [ ] Log aggregation set up

---

## 🚀 Deployment Steps

### Step 1: Server Setup

**Recommended Specifications**:
- **OS**: Ubuntu 22.04+ LTS
- **CPU**: 2+ cores
- **RAM**: 4GB+ (8GB recommended)
- **Storage**: 20GB+ SSD
- **Network**: Stable, low-latency connection

**Initial Setup**:
```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Python 3.11+
sudo apt install python3.11 python3.11-venv python3-pip -y

# Install system dependencies
sudo apt install git sqlite3 supervisor nginx -y

# Create quantx user
sudo useradd -m -s /bin/bash quantx
sudo usermod -aG sudo quantx
```

### Step 2: Code Deployment

```bash
# Switch to quantx user
sudo su - quantx

# Clone repository
cd /opt
git clone https://github.com/yourusername/QuantX.git
cd QuantX

# Create virtual environment
python3.11 -m venv venv
source venv/bin/activate

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Set PYTHONPATH
echo 'export PYTHONPATH="/opt/QuantX/src:$PYTHONPATH"' >> ~/.bashrc
source ~/.bashrc
```

### Step 3: Environment Configuration

```bash
# Copy environment template
cp .env.example .env

# Edit configuration
nano .env
```

**Required Environment Variables**:
```bash
# Zerodha Configuration
ZERODHA_API_KEY=your_api_key_here
ZERODHA_API_SECRET=your_api_secret_here
ZERODHA_ACCESS_TOKEN=  # Generated via OAuth
ZERODHA_USER_ID=your_user_id

# Live Trading Safety
LIVE_TRADING_ENABLED=true  # Enable only after thorough testing
LIVE_DATA_ENABLED=true

# Risk Limits
MAX_POSITION_SIZE=100000  # ₹1,00,000
MAX_DAILY_LOSS=10000      # ₹10,000
MAX_DRAWDOWN_PCT=5        # 5%

# Logging
LOG_LEVEL=INFO
LOG_FILE=/var/log/quantx/trading.log

# Database
DB_PATH=/opt/QuantX/data/quantx_state.db

# Monitoring
HEALTH_CHECK_PORT=8080
METRICS_ENABLED=true
```

### Step 4: Database Setup

```bash
# Create data directory
mkdir -p /opt/QuantX/data
mkdir -p /var/log/quantx

# Set permissions
chown -R quantx:quantx /opt/QuantX/data
chown -R quantx:quantx /var/log/quantx

# Initialize state database (automatic on first run)
```

### Step 5: Zerodha Authentication

```bash
# Activate venv
cd /opt/QuantX
source venv/bin/activate

# Run authentication script
PYTHONPATH="$(pwd)/src" python examples/live/zerodha_authentication.py

# Follow prompts to:
# 1. Get login URL
# 2. Authenticate in browser
# 3. Paste request token
# 4. Generate access token
# 5. Save token to .env
```

**Access Token Renewal**:
- Tokens expire after 24 hours
- Must re-authenticate daily
- Consider automated renewal (with TOTP)

### Step 6: Configure Supervisor

**Create supervisor config**:
```bash
sudo nano /etc/supervisor/conf.d/quantx.conf
```

**Configuration**:
```ini
[program:quantx]
command=/opt/QuantX/venv/bin/python /opt/QuantX/examples/live/complete_live_trading.py
directory=/opt/QuantX
user=quantx
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=/var/log/quantx/supervisor.log
environment=PYTHONPATH="/opt/QuantX/src"

[program:quantx-health]
command=/opt/QuantX/venv/bin/python -m quantx.monitoring.health_server
directory=/opt/QuantX
user=quantx
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=/var/log/quantx/health.log
```

**Start services**:
```bash
sudo supervisorctl reload
sudo supervisorctl status
```

### Step 7: Configure Nginx (Health Endpoint)

```bash
sudo nano /etc/nginx/sites-available/quantx
```

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location /health {
        proxy_pass http://localhost:8080/health;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    location /metrics {
        proxy_pass http://localhost:8080/metrics;
        proxy_set_header Host $host;
    }
}
```

```bash
sudo ln -s /etc/nginx/sites-available/quantx /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

---

## 📊 Monitoring Setup

### Health Checks

**Endpoint**: `http://your-server/health`

**Response**:
```json
{
  "status": "healthy",
  "timestamp": "2025-12-27T21:22:00Z",
  "components": {
    "engine": {
      "status": "healthy",
      "uptime": 3600
    },
    "broker": {
      "status": "healthy",
      "connected": true
    },
    "event_bus": {
      "status": "healthy"
    }
  }
}
```

### External Monitoring

**UptimeRobot** (Free):
1. Sign up at uptimerobot.com
2. Add HTTP monitor for `/health`
3. Set check frequency: 5 minutes
4. Configure email/SMS alerting

**Better Uptime** (Alternative):
- More features
- Status pages
- Incident management

### Log Monitoring

```bash
# View live logs
tail -f /var/log/quantx/trading.log

# Search for errors
grep ERROR /var/log/quantx/trading.log

# Monitor system resources
htop
```

---

## 🔒 Security Best Practices

### 1. API Key Security
- ✅ Never commit keys to Git
- ✅ Use environment variables
- ✅ Restrict file permissions: `chmod 600 .env`
- ✅ Consider using vault (HashiCorp Vault)

### 2. Network Security
```bash
# Configure firewall
sudo ufw allow 22/tcp  # SSH
sudo ufw allow 80/tcp  # HTTP
sudo ufw allow 443/tcp # HTTPS
sudo ufw enable

# Disable root SSH
sudo nano /etc/ssh/sshd_config
# Set: PermitRootLogin no
sudo systemctl restart sshd
```

### 3. Access Control
- Use SSH keys (disable password auth)
- Implement fail2ban
- Regular security updates
- Minimal user privileges

---

## 🚨 Disaster Recovery

### Crash Recovery

**Automatic Recovery**:
```python
# On startup, engine checks for crashes
if state_store.has_unrecovered_crash():
    # 1. Load last known state
    last_state = state_store.get_latest_state()
    
    # 2. Verify with broker
    broker_positions = broker.get_positions()
    
    # 3. Reconcile
    sync_report = synchronizer.sync_positions(
        strategy_positions=last_state.positions,
        broker_positions=broker_positions
    )
    
    # 4. Mark recovered
    state_store.mark_crash_recovered(crash_id)
    
    # 5. Resume trading
    engine.start()
```

### Manual Recovery

```bash
# Stop the service
sudo supervisorctl stop quantx

# Check last state
sqlite3 /opt/QuantX/data/quantx_state.db
SELECT * FROM engine_states ORDER BY timestamp DESC LIMIT 1;

# Check for crashes
SELECT * FROM crash_markers WHERE recovered = 0;

# Manual reconciliation if needed
PYTHONPATH="$(pwd)/src" python scripts/manual_reconciliation.py

# Restart service
sudo supervisorctl start quantx
```

---

## 📈 Performance Tuning

### 1. Database Optimization
```bash
# Enable WAL mode for better concurrency
sqlite3 /opt/QuantX/data/quantx_state.db "PRAGMA journal_mode=WAL;"

# Regular cleanup
# Add to crontab
0 2 * * * /opt/QuantX/venv/bin/python -c "from quantx.persistence import StateStore; StateStore().cleanup_old_states()"
```

### 2. System Resources
```bash
# Increase file descriptor limits
sudo nano /etc/security/limits.conf
quantx soft nofile 65536
quantx hard nofile 65536

# Optimize Python
export PYTHONOPTIMIZE=2  # Enable optimizations
```

---

## 🔍 Troubleshooting

### Engine Won't Start
```bash
# Check logs
tail -100 /var/log/quantx/trading.log

# Check supervisor status
sudo supervisorctl status quantx

# Manual start for debugging
cd /opt/QuantX
source venv/bin/activate
PYTHONPATH="$(pwd)/src" python examples/live/complete_live_trading.py
```

### Broker Connection Issues
```bash
# Verify credentials
env | grep ZERODHA

# Test connection
PYTHONPATH="$(pwd)/src" python -c "
from quantx.execution.brokers import ZerodhaBroker
broker = ZerodhaBroker('api_key', 'api_secret', 'access_token')
print(broker.get_account())
"

# Check token expiry (24-hour limit)
```

### Position Sync Failures
```bash
# Manual sync check
PYTHONPATH="$(pwd)/src" python scripts/check_positions.py

# Force reconciliation
PYTHONPATH="$(pwd)/src") python scripts/force_reconcile.py
```

---

## 📞 Emergency Procedures

### Kill Switch
```bash
# Emergency stop (preserves positions)
sudo supervisorctl stop quantx

# Force close all positions (use with caution!)
PYTHONPATH="$(pwd)/src" python scripts/emergency_close_all.py
```

### Contact Information
- **Technical Support**: support@quantx.io
- **Emergency Hotline**: +91-XXXX-XXXXXX
- **Zerodha Support**: 080-40402033

---

## ✅ Post-Deployment Validation

### Day 1 Checklist
- [ ] Health endpoint responding
- [ ] Logs being generated
- [ ] Metrics being collected
- [ ] Positions syncing correctly
- [ ] Orders executing properly
- [ ] P&L tracking accurate

### Week 1 Checklist
- [ ] No unexpected crashes
- [ ] Performance within acceptable limits
- [ ] All alerts working
- [ ] Backup/recovery tested
- [ ] Full week of trading data

---

## 📚 Additional Resources

- [Zerodha API Documentation](https://kite.trade/docs/)
- [QuantX Architecture Guide](./ARCHITECTURE_ASSESSMENT.md)
- [Live Trading Guide](./LIVE_TRADING.md)
- [Phase 3 Completion Summary](./PHASE3_COMPLETE.md)

---

**Status**: Production Deployment Guide  
**Version**: 1.0  
**Maintenance**: Update monthly or after major changes

---

**⚠️ IMPORTANT**: Always test in paper trading mode first! Start with small position sizes and gradually scale up.
