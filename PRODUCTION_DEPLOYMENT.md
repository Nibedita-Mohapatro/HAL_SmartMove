# HAL Transport Management System - Production Deployment Guide

## 🚀 Quick Start

### Prerequisites
- Ubuntu 20.04 LTS or later
- Minimum 4GB RAM, 2 CPU cores
- 50GB disk space
- Domain name configured (e.g., transport.hal.co.in)
- SSL certificate (Let's Encrypt recommended)

### One-Command Deployment
```bash
sudo ./deploy.sh
```

## 📋 Manual Deployment Steps

### 1. System Preparation
```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install required packages
sudo apt install -y python3 python3-pip python3-venv mysql-server redis-server nginx supervisor git curl wget unzip certbot python3-certbot-nginx

# Install Node.js 18
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt install -y nodejs
```

### 2. Database Setup
```bash
# Secure MySQL installation
sudo mysql_secure_installation

# Create database and user
sudo mysql < backend/database_setup.sql
```

### 3. Application Setup
```bash
# Create application user
sudo useradd -r -s /bin/bash -d /var/www/hal-transport hal-transport

# Create directories
sudo mkdir -p /var/www/hal-transport /var/log/hal-transport /var/backups/hal-transport
sudo chown -R hal-transport:hal-transport /var/www/hal-transport /var/log/hal-transport /var/backups/hal-transport

# Copy application files
sudo cp -r backend /var/www/hal-transport/
sudo cp -r frontend /var/www/hal-transport/
sudo chown -R hal-transport:hal-transport /var/www/hal-transport
```

### 4. Backend Configuration
```bash
# Setup Python virtual environment
sudo -u hal-transport python3 -m venv /var/www/hal-transport/backend/venv
sudo -u hal-transport /var/www/hal-transport/backend/venv/bin/pip install -r /var/www/hal-transport/backend/requirements.txt

# Configure environment
sudo -u hal-transport cp /var/www/hal-transport/backend/.env.production /var/www/hal-transport/backend/.env
# Edit .env file with your production values
```

### 5. Frontend Build
```bash
cd /var/www/hal-transport/frontend
sudo -u hal-transport npm install
sudo -u hal-transport npm run build
```

### 6. Service Configuration
```bash
# Create systemd service
sudo cp deployment/hal-transport.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable hal-transport
sudo systemctl start hal-transport
```

### 7. Nginx Configuration
```bash
# Copy Nginx configuration
sudo cp deployment/nginx.conf /etc/nginx/sites-available/hal-transport
sudo ln -s /etc/nginx/sites-available/hal-transport /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

### 8. SSL Certificate
```bash
# Get SSL certificate
sudo certbot --nginx -d transport.hal.co.in -d www.transport.hal.co.in
```

## 🔧 Configuration

### Environment Variables (.env)
```bash
# Security
SECRET_KEY=your-super-secret-key-change-this-in-production
JWT_SECRET_KEY=your-jwt-secret-key-change-this-in-production

# Database
DATABASE_URL=mysql+pymysql://hal_user:secure_password@localhost:3306/hal_transport

# Email (for notifications)
SMTP_HOST=smtp.gmail.com
SMTP_USER=your-email@hal.co.in
SMTP_PASSWORD=your-app-password

# File uploads
UPLOAD_DIR=/var/www/hal-transport/uploads
MAX_FILE_SIZE=10485760

# CORS
ALLOWED_ORIGINS=https://transport.hal.co.in,https://www.hal.co.in
```

### Database Configuration
- Default super admin: `HAL001` / `admin123`
- Change default password after first login
- Regular database backups are configured automatically

## 🔒 Security Checklist

### Application Security
- [ ] Change default admin password
- [ ] Update SECRET_KEY and JWT_SECRET_KEY
- [ ] Configure CORS origins
- [ ] Enable HTTPS only
- [ ] Set up rate limiting
- [ ] Configure file upload restrictions

### Server Security
- [ ] Configure firewall (UFW)
- [ ] Disable root SSH login
- [ ] Set up fail2ban
- [ ] Regular security updates
- [ ] Monitor logs
- [ ] Backup encryption

### Database Security
- [ ] Change default database passwords
- [ ] Restrict database access
- [ ] Enable binary logging
- [ ] Regular security patches
- [ ] Encrypted backups

## 📊 Monitoring & Maintenance

### Health Checks
```bash
# Application health
curl https://transport.hal.co.in/health

# Service status
sudo systemctl status hal-transport
sudo systemctl status nginx
sudo systemctl status mysql
sudo systemctl status redis-server
```

### Log Monitoring
```bash
# Application logs
sudo journalctl -u hal-transport -f

# Nginx logs
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log

# Application logs
sudo tail -f /var/log/hal-transport/app.log
```

### Backup & Recovery
```bash
# Manual backup
sudo /usr/local/bin/hal-transport-backup

# Restore from backup
mysql -u hal_user -p hal_transport < /var/backups/hal-transport/backup_file.sql
```

## 🚨 Troubleshooting

### Common Issues

#### Application won't start
```bash
# Check logs
sudo journalctl -u hal-transport -n 50

# Check configuration
sudo -u hal-transport /var/www/hal-transport/backend/venv/bin/python -c "from main import app; print('Config OK')"
```

#### Database connection issues
```bash
# Test database connection
mysql -u hal_user -p hal_transport -e "SELECT 1;"

# Check MySQL status
sudo systemctl status mysql
```

#### Frontend not loading
```bash
# Check Nginx configuration
sudo nginx -t

# Check build files
ls -la /var/www/hal-transport/frontend/build/
```

### Performance Optimization

#### Database Optimization
```sql
-- Add indexes for better performance
CREATE INDEX idx_requests_date_status ON transport_requests(request_date, status);
CREATE INDEX idx_vehicles_status_type ON vehicles(status, type);

-- Optimize MySQL configuration
# Edit /etc/mysql/mysql.conf.d/mysqld.cnf
innodb_buffer_pool_size = 1G
query_cache_size = 256M
```

#### Application Optimization
```bash
# Increase worker processes
# Edit /etc/systemd/system/hal-transport.service
ExecStart=/var/www/hal-transport/backend/venv/bin/gunicorn -w 8 -k uvicorn.workers.UvicornWorker -b 127.0.0.1:8000 main:app
```

## 📞 Support

### System Requirements
- **Minimum**: 2 CPU cores, 4GB RAM, 50GB storage
- **Recommended**: 4 CPU cores, 8GB RAM, 100GB SSD
- **High Load**: 8 CPU cores, 16GB RAM, 200GB SSD

### Scaling Considerations
- Use load balancer for multiple app instances
- Implement Redis clustering for sessions
- Consider database read replicas
- Use CDN for static assets
- Implement caching strategies

### Maintenance Schedule
- **Daily**: Automated backups, log rotation
- **Weekly**: Security updates, performance monitoring
- **Monthly**: Full system backup, capacity planning
- **Quarterly**: Security audit, dependency updates

## 📝 Change Log

### Version 1.0.0
- Initial production release
- Complete user, vehicle, driver, and request management
- Analytics dashboard with interactive charts
- Document management system
- Assignment system with AI suggestions
- Production-ready deployment configuration

---

**For technical support, contact the HAL IT Department or refer to the system documentation.**
