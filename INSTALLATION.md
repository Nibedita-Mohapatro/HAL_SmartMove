# 🚀 HAL Transport Management System - Installation Guide

This comprehensive guide will help you set up the HAL Transport Management System on your local machine or server.

## 📋 Prerequisites

Before starting the installation, ensure you have the following software installed:

### Required Software
- **Node.js** (v16.0.0 or higher) - [Download](https://nodejs.org/)
- **Python** (v3.8.0 or higher) - [Download](https://python.org/)
- **MySQL** (v8.0 or higher) - [Download](https://dev.mysql.com/downloads/)
- **Git** - [Download](https://git-scm.com/)

### System Requirements
- **RAM**: Minimum 4GB, Recommended 8GB
- **Storage**: Minimum 2GB free space
- **OS**: Windows 10+, macOS 10.15+, or Linux (Ubuntu 18.04+)

## 🔧 Quick Installation (Recommended)

### Step 1: Clone the Repository
```bash
git clone <repository-url>
cd smart-vehicle-tracker
```

### Step 2: Run Automated Setup
```bash
chmod +x setup.sh
./setup.sh
```

The automated setup script will:
- ✅ Check all system requirements
- ✅ Install all dependencies (frontend & backend)
- ✅ Create necessary configuration files
- ✅ Set up the database
- ✅ Start both applications automatically

### Step 3: Access the Application
After successful setup:
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs

## 🛠️ Manual Installation

If you prefer to install manually or the automated script doesn't work:

### Backend Setup

#### 1. Navigate to Backend Directory
```bash
cd backend
```

#### 2. Create Virtual Environment
```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
# On Linux/macOS:
source venv/bin/activate
# On Windows:
venv\Scripts\activate
```

#### 3. Install Dependencies
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

#### 4. Configure Environment Variables
Create a `.env` file in the backend directory:
```bash
cp .env.example .env
```

Edit the `.env` file with your configuration:
```env
# Database Configuration
DATABASE_URL=mysql://username:password@localhost/hal_transport_db

# JWT Configuration
SECRET_KEY=your-super-secret-key-change-this-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Google Maps API (optional)
GOOGLE_MAPS_API_KEY=your-google-maps-api-key-here

# Environment
ENVIRONMENT=development
```

#### 5. Set Up Database
```sql
-- Connect to MySQL
mysql -u root -p

-- Create database
CREATE DATABASE hal_transport_db;

-- Create user (optional)
CREATE USER 'hal_user'@'localhost' IDENTIFIED BY 'hal_password';
GRANT ALL PRIVILEGES ON hal_transport_db.* TO 'hal_user'@'localhost';
FLUSH PRIVILEGES;
```

#### 6. Initialize Database Tables
```bash
python -c "from app.database import create_tables; create_tables()"
```

#### 7. Start Backend Server
```bash
python main.py
```

The backend will be available at: http://localhost:8000

### Frontend Setup

#### 1. Navigate to Frontend Directory
```bash
cd frontend
```

#### 2. Install Dependencies
```bash
npm install
```

#### 3. Configure Environment Variables
Create a `.env` file in the frontend directory:
```env
# API Configuration
REACT_APP_API_URL=http://localhost:8000

# Google Maps API (optional)
REACT_APP_GOOGLE_MAPS_API_KEY=your-google-maps-api-key-here

# Environment
REACT_APP_ENVIRONMENT=development
```

#### 4. Start Frontend Server
```bash
npm start
```

The frontend will be available at: http://localhost:3000

## 🗄️ Database Configuration

### MySQL Setup

#### Option 1: Local MySQL Installation

1. **Install MySQL**:
   - **Ubuntu/Debian**: `sudo apt-get install mysql-server`
   - **CentOS/RHEL**: `sudo yum install mysql-server`
   - **macOS**: `brew install mysql`
   - **Windows**: Download from [MySQL Downloads](https://dev.mysql.com/downloads/)

2. **Start MySQL Service**:
   - **Linux**: `sudo systemctl start mysql`
   - **macOS**: `brew services start mysql`
   - **Windows**: Start from Services panel

3. **Secure Installation**:
   ```bash
   sudo mysql_secure_installation
   ```

#### Option 2: Docker MySQL (Alternative)

```bash
# Run MySQL in Docker container
docker run --name hal-mysql \
  -e MYSQL_ROOT_PASSWORD=rootpassword \
  -e MYSQL_DATABASE=hal_transport_db \
  -e MYSQL_USER=hal_user \
  -e MYSQL_PASSWORD=hal_password \
  -p 3306:3306 \
  -d mysql:8.0
```

### Database Schema

The application will automatically create the following tables:
- `users` - User accounts and authentication
- `transport_requests` - Transport booking requests
- `vehicles` - Vehicle information
- `drivers` - Driver profiles
- `vehicle_assignments` - Trip assignments
- `gps_locations` - GPS tracking data

## 🔑 Default User Accounts

The system comes with pre-configured user accounts:

| Role | Employee ID | Password | Permissions |
|------|-------------|----------|-------------|
| **Super Admin** | HAL001 | admin123 | Full system access |
| **Transport** | HAL002 | transport123 | Driver/Transport management |
| **Employee** | HAL003 | employee123 | Basic employee access |

⚠️ **Security Note**: Change these default passwords in production!

## 🌐 Production Deployment

### Environment Configuration

#### Backend Production Settings
```env
# Production Database
DATABASE_URL=mysql://user:password@production-host/hal_transport_db

# Strong Secret Key
SECRET_KEY=generate-a-strong-secret-key-for-production

# Security Settings
ENVIRONMENT=production
CORS_ORIGINS=["https://yourdomain.com"]

# External Services
GOOGLE_MAPS_API_KEY=your-production-api-key
```

#### Frontend Production Settings
```env
REACT_APP_API_URL=https://api.yourdomain.com
REACT_APP_GOOGLE_MAPS_API_KEY=your-production-api-key
REACT_APP_ENVIRONMENT=production
```

### Build for Production

#### Frontend Build
```bash
cd frontend
npm run build
```

#### Backend Production Server
```bash
cd backend
pip install gunicorn
gunicorn -w 4 -k uvicorn.workers.UvicornWorker app.main:app --bind 0.0.0.0:8000
```

### Nginx Configuration (Optional)
```nginx
server {
    listen 80;
    server_name yourdomain.com;

    # Frontend
    location / {
        root /path/to/frontend/build;
        try_files $uri $uri/ /index.html;
    }

    # Backend API
    location /api/ {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

## 🧪 Testing the Installation

### 1. Backend API Test
```bash
curl http://localhost:8000/health
```
Expected response: `{"status": "healthy"}`

### 2. Frontend Test
Open http://localhost:3000 in your browser and verify:
- ✅ Login page loads
- ✅ Can login with default credentials
- ✅ Dashboard displays correctly

### 3. Database Test
```bash
# Login to MySQL
mysql -u root -p

# Check database
USE hal_transport_db;
SHOW TABLES;
```

### 4. End-to-End Test
1. Login as admin (HAL001/admin123)
2. Create a new user
3. Login as employee (HAL003/employee123)
4. Create a transport request
5. Login as admin and approve the request

## 🚨 Troubleshooting

### Common Issues

#### Backend Won't Start
```bash
# Check Python version
python3 --version

# Check if virtual environment is activated
which python

# Check dependencies
pip list

# Check database connection
python -c "from app.database import engine; print(engine.url)"
```

#### Frontend Won't Start
```bash
# Check Node.js version
node --version

# Clear npm cache
npm cache clean --force

# Delete node_modules and reinstall
rm -rf node_modules package-lock.json
npm install
```

#### Database Connection Issues
```bash
# Check MySQL status
sudo systemctl status mysql

# Test connection
mysql -u root -p -e "SELECT 1;"

# Check database exists
mysql -u root -p -e "SHOW DATABASES;"
```

#### Port Already in Use
```bash
# Find process using port 3000
lsof -i :3000

# Find process using port 8000
lsof -i :8000

# Kill process
kill -9 <PID>
```

### Log Files

Check these log files for debugging:
- **Backend**: `backend.log` (if using setup script)
- **Frontend**: `frontend.log` (if using setup script)
- **MySQL**: `/var/log/mysql/error.log` (Linux)

### Getting Help

If you encounter issues:
1. Check the troubleshooting section above
2. Review the log files
3. Ensure all prerequisites are installed
4. Verify environment variables are set correctly
5. Check firewall settings for ports 3000 and 8000

## 🔄 Updates and Maintenance

### Updating the Application
```bash
# Pull latest changes
git pull origin main

# Update backend dependencies
cd backend
source venv/bin/activate
pip install -r requirements.txt

# Update frontend dependencies
cd ../frontend
npm install

# Restart applications
./setup.sh
```

### Database Backup
```bash
# Create backup
mysqldump -u root -p hal_transport_db > backup_$(date +%Y%m%d).sql

# Restore backup
mysql -u root -p hal_transport_db < backup_20231201.sql
```

---

**🎉 Congratulations! Your HAL Transport Management System is now ready to use!**

For additional support, please refer to the main README.md file or contact the development team.
