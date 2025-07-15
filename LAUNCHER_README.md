# HAL Transport Management System - Launcher Guide

This guide explains how to use the launcher scripts to quickly set up and run the HAL Transport Management System.

## 🚀 Quick Start

### Linux/macOS
```bash
# Make the script executable (first time only)
chmod +x launcher.sh

# Run the application
./launcher.sh
```

### Windows
```cmd
# Double-click launcher.bat or run from command prompt
launcher.bat
```

## 📋 Prerequisites

### Required Software
- **Python 3.8+** - Backend runtime
- **Node.js 16+** - Frontend runtime  
- **MySQL 5.7+** - Database
- **Git** - Version control (optional)

### System Dependencies (Linux)
The launcher can automatically install system dependencies:
```bash
./launcher.sh --install-deps
```

This will install:
- Python 3.8+ and pip
- Node.js 18+ and npm
- MySQL server
- Build tools and other dependencies

## 🛠️ Launcher Options

### Linux/macOS Options
```bash
./launcher.sh [OPTIONS]

Options:
  --install-deps    Install system dependencies (requires sudo)
  --setup-only      Only setup environments, don't run servers
  --backend-only    Run only backend server
  --frontend-only   Run only frontend server
  --help           Show help message
```

### Examples
```bash
# First time setup with system dependencies
./launcher.sh --install-deps

# Setup environments only (no server start)
./launcher.sh --setup-only

# Run only backend server
./launcher.sh --backend-only

# Run only frontend server
./launcher.sh --frontend-only

# Normal run (setup + start both servers)
./launcher.sh
```

## 🔧 What the Launcher Does

### 1. System Check
- Verifies Python 3.8+ is installed
- Verifies Node.js 16+ is installed
- Checks for MySQL availability

### 2. Environment Setup
- Creates Python virtual environment (`backend/venv/`)
- Installs Python dependencies from `requirements.txt`
- Installs Node.js dependencies from `package.json`
- Creates log directory (`logs/`)

### 3. Database Setup
- Starts MySQL service (if available)
- Runs database setup scripts (if present)
- Creates necessary database schema

### 4. Server Launch
- **Backend**: Starts FastAPI server on `http://localhost:8000`
- **Frontend**: Starts React development server on `http://localhost:3000`
- Both servers run with hot-reload enabled

## 📁 Directory Structure After Launch

```
smart vehicle tracker/
├── launcher.sh              # Linux/macOS launcher
├── launcher.bat             # Windows launcher
├── logs/                    # Application logs
│   ├── backend.log         # Backend server logs
│   ├── frontend.log        # Frontend server logs
│   ├── backend.pid         # Backend process ID
│   └── frontend.pid        # Frontend process ID
├── backend/
│   ├── venv/               # Python virtual environment
│   ├── requirements.txt    # Python dependencies
│   ├── main.py            # FastAPI application
│   └── ...
└── frontend/
    ├── node_modules/       # Node.js dependencies
    ├── package.json       # Node.js dependencies
    ├── src/               # React source code
    └── ...
```

## 🌐 Access Points

After successful launch:

- **Frontend Application**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **API Redoc**: http://localhost:8000/redoc

## 🛑 Stopping the Application

### Linux/macOS
Press `Ctrl+C` in the launcher terminal to stop both servers gracefully.

### Windows
Close the backend and frontend command windows that opened during launch.

## 🔍 Troubleshooting

### Common Issues

#### 1. Python Not Found
```bash
# Install Python (Ubuntu/Debian)
sudo apt-get update
sudo apt-get install python3 python3-pip python3-venv

# Install Python (macOS with Homebrew)
brew install python@3.11
```

#### 2. Node.js Not Found
```bash
# Install Node.js (Ubuntu/Debian)
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt-get install -y nodejs

# Install Node.js (macOS with Homebrew)
brew install node
```

#### 3. MySQL Connection Issues
```bash
# Start MySQL service (Linux)
sudo systemctl start mysql

# Start MySQL service (macOS)
brew services start mysql

# Check MySQL status
sudo systemctl status mysql
```

#### 4. Port Already in Use
If ports 3000 or 8000 are already in use:

**Backend (Port 8000)**:
```bash
# Find process using port 8000
lsof -i :8000
# Kill the process
kill -9 <PID>
```

**Frontend (Port 3000)**:
```bash
# Find process using port 3000
lsof -i :3000
# Kill the process
kill -9 <PID>
```

#### 5. Permission Issues (Linux/macOS)
```bash
# Make launcher executable
chmod +x launcher.sh

# Fix ownership if needed
sudo chown -R $USER:$USER .
```

### Log Files
Check log files for detailed error information:
- Backend logs: `logs/backend.log`
- Frontend logs: `logs/frontend.log`

### Manual Setup (If Launcher Fails)

#### Backend Setup
```bash
cd backend
python3 -m venv venv
source venv/bin/activate  # Linux/macOS
# or
venv\Scripts\activate.bat  # Windows
pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

#### Frontend Setup
```bash
cd frontend
npm install
npm start
```

## 🔒 Security Notes

- The launcher may require `sudo` privileges for system dependency installation
- Database setup requires MySQL root access
- Default configuration is for development use only
- For production deployment, use the `deploy.sh` script instead

## 📞 Support

If you encounter issues:

1. Check the troubleshooting section above
2. Review log files in the `logs/` directory
3. Ensure all prerequisites are installed
4. Try manual setup if the launcher fails

## 🔄 Updates

To update dependencies:
```bash
# Update Python dependencies
cd backend
source venv/bin/activate
pip install -r requirements.txt --upgrade

# Update Node.js dependencies
cd frontend
npm update
```

## 🎯 Next Steps

After successful launch:

1. Access the application at http://localhost:3000
2. Review the API documentation at http://localhost:8000/docs
3. Configure database settings in `backend/.env`
4. Set up user accounts and test functionality
5. For production deployment, use `deploy.sh`
