# HAL SmartMove - Production Deployment Guide

## 🎯 **Overview**

This guide covers production deployment of the HAL SmartMove Transport Management System with security, scalability, and reliability considerations.

## 🏗️ **Deployment Architecture**

### **Recommended Production Setup**
```
Internet → Load Balancer → Web Server (Nginx) → Application Server (Gunicorn) → Database (PostgreSQL)
                                              ↓
                                         Static Files (CDN)
```

## 🐳 **Docker Deployment (Recommended)**

### **1. Docker Compose Setup**

Create `docker-compose.prod.yml`:

```yaml
version: '3.8'

services:
  database:
    image: postgres:15
    environment:
      POSTGRES_DB: hal_transport
      POSTGRES_USER: hal_user
      POSTGRES_PASSWORD: ${DB_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    networks:
      - hal_network

  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile.prod
    environment:
      DATABASE_URL: postgresql://hal_user:${DB_PASSWORD}@database:5432/hal_transport
      SECRET_KEY: ${SECRET_KEY}
      FRONTEND_URL: ${FRONTEND_URL}
    depends_on:
      - database
    networks:
      - hal_network

  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile.prod
    environment:
      REACT_APP_API_URL: ${API_URL}
    networks:
      - hal_network

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/nginx/ssl
    depends_on:
      - backend
      - frontend
    networks:
      - hal_network

volumes:
  postgres_data:

networks:
  hal_network:
    driver: bridge
```

### **2. Backend Dockerfile**

Create `backend/Dockerfile.prod`:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install gunicorn

# Copy application code
COPY . .

# Create non-root user
RUN useradd --create-home --shell /bin/bash app
RUN chown -R app:app /app
USER app

# Expose port
EXPOSE 8000

# Start application
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "4", "main:app", "-k", "uvicorn.workers.UvicornWorker"]
```

### **3. Frontend Dockerfile**

Create `frontend/Dockerfile.prod`:

```dockerfile
# Build stage
FROM node:18-alpine as build

WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production

COPY . .
RUN npm run build

# Production stage
FROM nginx:alpine

COPY --from=build /app/build /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
```

## ☁️ **Cloud Deployment Options**

### **AWS Deployment**

#### **1. Using AWS ECS**
```bash
# Build and push images
docker build -t hal-backend ./backend
docker build -t hal-frontend ./frontend

# Tag for ECR
docker tag hal-backend:latest <account-id>.dkr.ecr.<region>.amazonaws.com/hal-backend:latest
docker tag hal-frontend:latest <account-id>.dkr.ecr.<region>.amazonaws.com/hal-frontend:latest

# Push to ECR
docker push <account-id>.dkr.ecr.<region>.amazonaws.com/hal-backend:latest
docker push <account-id>.dkr.ecr.<region>.amazonaws.com/hal-frontend:latest
```

#### **2. Using AWS Elastic Beanstalk**
```bash
# Install EB CLI
pip install awsebcli

# Initialize application
eb init hal-transport-system

# Create environment
eb create production

# Deploy
eb deploy
```

### **Google Cloud Platform**

#### **Using Cloud Run**
```bash
# Build and deploy backend
gcloud builds submit --tag gcr.io/PROJECT-ID/hal-backend ./backend
gcloud run deploy hal-backend --image gcr.io/PROJECT-ID/hal-backend --platform managed

# Build and deploy frontend
gcloud builds submit --tag gcr.io/PROJECT-ID/hal-frontend ./frontend
gcloud run deploy hal-frontend --image gcr.io/PROJECT-ID/hal-frontend --platform managed
```

### **Azure Deployment**

#### **Using Azure Container Instances**
```bash
# Create resource group
az group create --name hal-transport --location eastus

# Deploy containers
az container create --resource-group hal-transport --name hal-backend --image hal-backend:latest
az container create --resource-group hal-transport --name hal-frontend --image hal-frontend:latest
```

## 🔧 **Production Configuration**

### **Environment Variables**

Create `.env.prod`:

```env
# Database
DATABASE_URL=postgresql://user:password@db-host:5432/hal_transport

# Security
SECRET_KEY=your-super-secret-production-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# CORS
FRONTEND_URL=https://your-domain.com

# Email (Optional)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password

# Monitoring
SENTRY_DSN=your-sentry-dsn-here
LOG_LEVEL=INFO
```

### **Nginx Configuration**

Create `nginx.conf`:

```nginx
upstream backend {
    server backend:8000;
}

upstream frontend {
    server frontend:80;
}

server {
    listen 80;
    server_name your-domain.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name your-domain.com;

    ssl_certificate /etc/nginx/ssl/cert.pem;
    ssl_certificate_key /etc/nginx/ssl/key.pem;

    # Security headers
    add_header X-Frame-Options DENY;
    add_header X-Content-Type-Options nosniff;
    add_header X-XSS-Protection "1; mode=block";

    # Frontend
    location / {
        proxy_pass http://frontend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    # Backend API
    location /api/ {
        proxy_pass http://backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Static files
    location /static/ {
        alias /var/www/static/;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
}
```

## 🔒 **Security Configuration**

### **1. SSL/TLS Setup**

#### **Using Let's Encrypt**
```bash
# Install certbot
sudo apt-get install certbot python3-certbot-nginx

# Obtain certificate
sudo certbot --nginx -d your-domain.com

# Auto-renewal
sudo crontab -e
# Add: 0 12 * * * /usr/bin/certbot renew --quiet
```

### **2. Database Security**
```sql
-- Create dedicated database user
CREATE USER hal_app WITH PASSWORD 'strong-password';
CREATE DATABASE hal_transport OWNER hal_app;

-- Grant minimal permissions
GRANT CONNECT ON DATABASE hal_transport TO hal_app;
GRANT USAGE ON SCHEMA public TO hal_app;
GRANT CREATE ON SCHEMA public TO hal_app;
```

### **3. Firewall Configuration**
```bash
# Ubuntu/Debian
sudo ufw allow 22/tcp
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable

# CentOS/RHEL
sudo firewall-cmd --permanent --add-service=ssh
sudo firewall-cmd --permanent --add-service=http
sudo firewall-cmd --permanent --add-service=https
sudo firewall-cmd --reload
```

## 📊 **Monitoring & Logging**

### **1. Application Monitoring**

#### **Health Check Endpoint**
```python
# Add to backend/main.py
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow(),
        "version": "1.0.0"
    }
```

#### **Prometheus Metrics**
```python
# Install prometheus-client
pip install prometheus-client

# Add metrics endpoint
from prometheus_client import Counter, Histogram, generate_latest

REQUEST_COUNT = Counter('http_requests_total', 'Total HTTP requests')
REQUEST_LATENCY = Histogram('http_request_duration_seconds', 'HTTP request latency')

@app.get("/metrics")
async def metrics():
    return Response(generate_latest(), media_type="text/plain")
```

### **2. Log Configuration**

Create `logging.conf`:

```ini
[loggers]
keys=root,hal

[handlers]
keys=consoleHandler,fileHandler

[formatters]
keys=simpleFormatter

[logger_root]
level=INFO
handlers=consoleHandler

[logger_hal]
level=INFO
handlers=consoleHandler,fileHandler
qualname=hal
propagate=0

[handler_consoleHandler]
class=StreamHandler
level=INFO
formatter=simpleFormatter
args=(sys.stdout,)

[handler_fileHandler]
class=FileHandler
level=INFO
formatter=simpleFormatter
args=('/var/log/hal-transport.log',)

[formatter_simpleFormatter]
format=%(asctime)s - %(name)s - %(levelname)s - %(message)s
```

## 🚀 **Deployment Process**

### **1. Pre-deployment Checklist**
- [ ] Environment variables configured
- [ ] Database migrations applied
- [ ] SSL certificates installed
- [ ] Backup procedures in place
- [ ] Monitoring configured
- [ ] Load testing completed

### **2. Deployment Steps**
```bash
# 1. Backup current system
./scripts/backup.sh

# 2. Pull latest code
git pull origin main

# 3. Build and deploy
docker-compose -f docker-compose.prod.yml up -d --build

# 4. Run migrations
docker-compose exec backend python migrate.py

# 5. Verify deployment
./scripts/health-check.sh

# 6. Update monitoring
./scripts/update-monitoring.sh
```

### **3. Rollback Procedure**
```bash
# Quick rollback
docker-compose -f docker-compose.prod.yml down
docker-compose -f docker-compose.prod.yml up -d --build <previous-tag>

# Database rollback (if needed)
./scripts/restore-backup.sh <backup-timestamp>
```

## 📈 **Scaling Considerations**

### **Horizontal Scaling**
- Use load balancer (AWS ALB, GCP Load Balancer)
- Multiple backend instances
- Database read replicas
- CDN for static assets

### **Vertical Scaling**
- Increase server resources
- Optimize database queries
- Implement caching (Redis)
- Use connection pooling

## 🔧 **Maintenance**

### **Regular Tasks**
- Database backups (daily)
- Log rotation (weekly)
- Security updates (monthly)
- Performance monitoring (continuous)
- SSL certificate renewal (automatic)

### **Backup Strategy**
```bash
# Database backup
pg_dump hal_transport > backup_$(date +%Y%m%d_%H%M%S).sql

# Application backup
tar -czf app_backup_$(date +%Y%m%d_%H%M%S).tar.gz /app

# Automated backup script
0 2 * * * /scripts/backup.sh
```

## 📞 **Production Support**

### **Monitoring Alerts**
- Application downtime
- High error rates
- Database connection issues
- SSL certificate expiration
- Disk space warnings

### **Emergency Contacts**
- System Administrator: admin@hal.com
- Database Administrator: dba@hal.com
- Security Team: security@hal.com

**Next Steps**: Configure monitoring, set up automated backups, and establish incident response procedures.
