#!/bin/bash

# HAL Transport Management System - Production Deployment Script
# This script sets up the production environment for the HAL Transport Management System

set -e  # Exit on any error

echo "🚀 Starting HAL Transport Management System Deployment..."

# Configuration
APP_NAME="hal-transport"
APP_USER="hal-transport"
APP_DIR="/var/www/hal-transport"
BACKEND_DIR="$APP_DIR/backend"
FRONTEND_DIR="$APP_DIR/frontend"
LOG_DIR="/var/log/hal-transport"
BACKUP_DIR="/var/backups/hal-transport"
NGINX_CONF="/etc/nginx/sites-available/hal-transport"
SYSTEMD_SERVICE="/etc/systemd/system/hal-transport.service"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if running as root
if [[ $EUID -eq 0 ]]; then
   print_error "This script should not be run as root for security reasons"
   exit 1
fi

# Check if sudo is available
if ! command -v sudo &> /dev/null; then
    print_error "sudo is required but not installed"
    exit 1
fi

print_status "Updating system packages..."
sudo apt update && sudo apt upgrade -y

print_status "Installing required system packages..."
sudo apt install -y \
    python3 \
    python3-pip \
    python3-venv \
    mysql-server \
    redis-server \
    nginx \
    supervisor \
    git \
    curl \
    wget \
    unzip \
    certbot \
    python3-certbot-nginx

# Install Node.js and npm
print_status "Installing Node.js and npm..."
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt install -y nodejs

# Create application user
print_status "Creating application user..."
if ! id "$APP_USER" &>/dev/null; then
    sudo useradd -r -s /bin/bash -d $APP_DIR $APP_USER
    print_success "Created user: $APP_USER"
else
    print_warning "User $APP_USER already exists"
fi

# Create directories
print_status "Creating application directories..."
sudo mkdir -p $APP_DIR $LOG_DIR $BACKUP_DIR
sudo mkdir -p $APP_DIR/uploads
sudo chown -R $APP_USER:$APP_USER $APP_DIR $LOG_DIR $BACKUP_DIR

# Copy application files
print_status "Copying application files..."
sudo cp -r backend $BACKEND_DIR
sudo cp -r frontend $FRONTEND_DIR
sudo chown -R $APP_USER:$APP_USER $APP_DIR

# Setup Python virtual environment
print_status "Setting up Python virtual environment..."
sudo -u $APP_USER python3 -m venv $BACKEND_DIR/venv
sudo -u $APP_USER $BACKEND_DIR/venv/bin/pip install --upgrade pip
sudo -u $APP_USER $BACKEND_DIR/venv/bin/pip install -r $BACKEND_DIR/requirements.txt

# Setup MySQL database
print_status "Setting up MySQL database..."
sudo mysql -e "SOURCE $BACKEND_DIR/database_setup.sql"
print_success "Database setup completed"

# Configure environment variables
print_status "Configuring environment variables..."
sudo -u $APP_USER cp $BACKEND_DIR/.env.production $BACKEND_DIR/.env
print_warning "Please update $BACKEND_DIR/.env with your production values"

# Build frontend
print_status "Building frontend application..."
cd $FRONTEND_DIR
sudo -u $APP_USER npm install
sudo -u $APP_USER npm run build
print_success "Frontend build completed"

# Create systemd service
print_status "Creating systemd service..."
sudo tee $SYSTEMD_SERVICE > /dev/null <<EOF
[Unit]
Description=HAL Transport Management System
After=network.target mysql.service redis.service

[Service]
Type=exec
User=$APP_USER
Group=$APP_USER
WorkingDirectory=$BACKEND_DIR
Environment=PATH=$BACKEND_DIR/venv/bin
ExecStart=$BACKEND_DIR/venv/bin/gunicorn -w 4 -k uvicorn.workers.UvicornWorker -b 127.0.0.1:8000 main:app
ExecReload=/bin/kill -s HUP \$MAINPID
Restart=always
RestartSec=3
StandardOutput=journal
StandardError=journal
SyslogIdentifier=hal-transport

[Install]
WantedBy=multi-user.target
EOF

# Configure Nginx
print_status "Configuring Nginx..."
sudo tee $NGINX_CONF > /dev/null <<EOF
server {
    listen 80;
    server_name transport.hal.co.in www.transport.hal.co.in;
    
    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header Referrer-Policy "no-referrer-when-downgrade" always;
    add_header Content-Security-Policy "default-src 'self' http: https: data: blob: 'unsafe-inline'" always;
    
    # Frontend (React app)
    location / {
        root $FRONTEND_DIR/build;
        index index.html index.htm;
        try_files \$uri \$uri/ /index.html;
        
        # Cache static assets
        location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg)$ {
            expires 1y;
            add_header Cache-Control "public, immutable";
        }
    }
    
    # Backend API
    location /api/ {
        proxy_pass http://127.0.0.1:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_cache_bypass \$http_upgrade;
        
        # Timeout settings
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }
    
    # File uploads
    location /uploads/ {
        alias $APP_DIR/uploads/;
        expires 1d;
        add_header Cache-Control "public";
    }
    
    # Health check
    location /health {
        proxy_pass http://127.0.0.1:8000/health;
        access_log off;
    }
    
    # Deny access to sensitive files
    location ~ /\. {
        deny all;
    }
    
    location ~ \.(env|log|sql)$ {
        deny all;
    }
}
EOF

# Enable Nginx site
sudo ln -sf $NGINX_CONF /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx

# Configure Redis
print_status "Configuring Redis..."
sudo systemctl enable redis-server
sudo systemctl start redis-server

# Configure MySQL
print_status "Configuring MySQL..."
sudo systemctl enable mysql
sudo systemctl start mysql

# Setup SSL certificate
print_status "Setting up SSL certificate..."
print_warning "Run the following command after DNS is configured:"
print_warning "sudo certbot --nginx -d transport.hal.co.in -d www.transport.hal.co.in"

# Setup log rotation
print_status "Setting up log rotation..."
sudo tee /etc/logrotate.d/hal-transport > /dev/null <<EOF
$LOG_DIR/*.log {
    daily
    missingok
    rotate 52
    compress
    delaycompress
    notifempty
    create 644 $APP_USER $APP_USER
    postrotate
        systemctl reload hal-transport
    endscript
}
EOF

# Setup backup script
print_status "Setting up backup script..."
sudo tee /usr/local/bin/hal-transport-backup > /dev/null <<'EOF'
#!/bin/bash
BACKUP_DIR="/var/backups/hal-transport"
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="$BACKUP_DIR/hal_transport_backup_$DATE.sql"

# Create database backup
mysqldump -u hal_user -p hal_transport > $BACKUP_FILE
gzip $BACKUP_FILE

# Remove backups older than 30 days
find $BACKUP_DIR -name "*.sql.gz" -mtime +30 -delete

echo "Backup completed: $BACKUP_FILE.gz"
EOF

sudo chmod +x /usr/local/bin/hal-transport-backup

# Setup cron job for backups
print_status "Setting up backup cron job..."
(sudo crontab -l 2>/dev/null; echo "0 2 * * * /usr/local/bin/hal-transport-backup") | sudo crontab -

# Start services
print_status "Starting services..."
sudo systemctl daemon-reload
sudo systemctl enable hal-transport
sudo systemctl start hal-transport
sudo systemctl enable nginx
sudo systemctl start nginx

# Setup firewall
print_status "Configuring firewall..."
sudo ufw allow 22/tcp
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw --force enable

print_success "🎉 Deployment completed successfully!"
print_status "Next steps:"
echo "1. Update $BACKEND_DIR/.env with your production configuration"
echo "2. Configure DNS to point to this server"
echo "3. Run: sudo certbot --nginx -d transport.hal.co.in"
echo "4. Test the application at http://your-domain.com"
echo "5. Monitor logs: sudo journalctl -u hal-transport -f"

print_status "Service status:"
sudo systemctl status hal-transport --no-pager -l
sudo systemctl status nginx --no-pager -l

print_status "Application should be available at: http://$(hostname -I | awk '{print $1}')"
