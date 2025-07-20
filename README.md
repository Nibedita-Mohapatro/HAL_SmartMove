# 🚀 HAL SmartMove Transport Management System

*"Hassle-Free Transport at Your Fingertips. From booking to tracking, manage your travel needs with speed, clarity, and control."*

[![License](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.8+-green.svg)](https://python.org)
[![Node.js](https://img.shields.io/badge/Node.js-16+-green.svg)](https://nodejs.org)
[![React](https://img.shields.io/badge/React-18+-blue.svg)](https://reactjs.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-Latest-green.svg)](https://fastapi.tiangolo.com)

## 🎯 **Quick Start**

### **Instant Setup (Recommended)**
```bash
# Clone the repository
git clone <repository-url>
cd hal-transport-system

# Run the application (one command!)
python run_app.py
```

### **Alternative Quick Start**
```bash
# For more detailed setup and monitoring
python start_system.py

# For health checks only
python health_check.py
```

## 🌐 **Access the Application**

Once started, access HAL SmartMove at:
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs

## 🔑 **Login Credentials**

| Role | Employee ID | Password | Access Level |
|------|-------------|----------|--------------|
| **Admin** | `HAL001` | `admin123` | Full system control |
| **Employee** | `HAL003` | `employee123` | Request transport |
| **Transport** | `HAL002` | `transport123` | Manage trips |

## ✨ **Key Features**

### **For Administrators**
- 📊 **Dashboard Overview**: System statistics and real-time monitoring
- 👥 **User Management**: Create, edit, and manage system users
- 🚗 **Vehicle Management**: Fleet management with maintenance tracking
- 👨‍✈️ **Driver Management**: Driver registration and license tracking
- 📋 **Request Management**: Approve and assign transport requests
- 🛰️ **GPS Tracking**: Real-time trip monitoring and tracking

### **For Employees**
- 📝 **Request Transport**: Submit transport requests with details
- 📱 **Track Requests**: Monitor request status and assignments
- 📊 **Request History**: View past transport requests
- 🔔 **Notifications**: Real-time updates on request status

### **For Transport Managers**
- 🚛 **Trip Management**: Coordinate and manage active trips
- 📍 **Route Planning**: Optimize routes for efficiency
- 👨‍✈️ **Driver Coordination**: Communicate with drivers
- 📈 **Performance Metrics**: Track operational efficiency

## 🛠️ **Technology Stack**

### **Frontend**
- **Framework**: React 18.x + Tailwind CSS
- **Routing**: React Router v6
- **HTTP Client**: Fetch API
- **State Management**: React Hooks + Context

### **Backend**
- **Framework**: FastAPI + SQLAlchemy
- **Authentication**: JWT with bcrypt
- **Database**: SQLite (dev) / PostgreSQL (prod)
- **Server**: Uvicorn (ASGI)

## 🏗️ System Architecture

```
┌─────────────────────┐    ┌─────────────────────┐    ┌─────────────────────┐
│   Frontend          │    │   Backend API       │    │   ML Services       │
│   (React.js)        │◄──►│   (FastAPI)         │◄──►│   (Python)          │
│                     │    │                     │    │                     │
│   • User Interface  │    │   • REST API        │    │   • Route Optimizer │
│   • Maps & Tracking │    │   • Authentication  │    │   • Demand Predictor│
│   • Analytics       │    │   • WebSockets      │    │   • Analytics Engine│
└─────────────────────┘    └─────────────────────┘    └─────────────────────┘
                                      │
                                      ▼
                          ┌─────────────────────┐
                          │   Database          │
                          │   (MySQL)           │
                          │                     │
                          │   • User Data       │
                          │   • Transport Data  │
                          │   • Analytics Data  │
                          └─────────────────────┘
                                      │
                                      ▼
                          ┌─────────────────────┐
                          │   External Services │
                          │                     │
                          │   • GPS Integration │
                          │   • Maps API        │
                          │   • Notifications   │
                          └─────────────────────┘
```

## 🛠️ **Development**

### **Prerequisites**
- **Python 3.8+** (Backend)
- **Node.js 16+** (Frontend)
- **npm 8+** (Package manager)

### **Development Setup**
```bash
# Backend setup
cd backend
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # macOS/Linux
pip install -r requirements.txt
python main.py

# Frontend setup (new terminal)
cd frontend
npm install
npm start
```

### **Available Scripts**

| Script | Purpose | Usage |
|--------|---------|-------|
| `run_app.py` | Simple app runner | `python run_app.py` |
| `start_system.py` | Full system startup | `python start_system.py` |
| `health_check.py` | System health check | `python health_check.py` |
| `quick_start.py` | Legacy quick start | `python quick_start.py` |

## 🔧 **Recent Updates**

### **✅ Driver Deletion Fix (Latest)**
- **Issue**: Driver deletion functionality was not working
- **Solution**: Implemented smart deletion with data integrity protection
- **Result**: Drivers can now be properly deleted with safety checks

### **✅ Dashboard Streamlining**
- **Issue**: "Approve & Assign" buttons cluttering dashboard
- **Solution**: Moved approval actions to dedicated management tabs
- **Result**: Cleaner dashboard focused on monitoring

### **✅ Error Handling Improvements**
- **Issue**: Runtime errors during approval operations
- **Solution**: Added proper null checks and error handling
- **Result**: Stable operation without crashes
- **Performance Analytics**: Advanced insights and operational intelligence
- **Predictive Maintenance**: Proactive vehicle maintenance alerts

### 📍 GPS Tracking & Real-time Features
- **Live Tracking**: Real-time vehicle location monitoring like Uber
- **Interactive Maps**: Leaflet-based maps with live updates
- **Trip Monitoring**: Complete journey tracking from start to finish
- **Geofencing**: Location-based alerts and boundary management
- **Route Visualization**: Dynamic route display with traffic integration
- **ETA Predictions**: Accurate arrival time estimates
- **Driver Performance**: Real-time monitoring and analytics

### 🔐 Security & Authentication
- **JWT Authentication**: Secure token-based authentication system
- **Role-based Access**: Three-tier access control (Admin/Driver/Employee)
- **Password Security**: Bcrypt hashing with strong password policies
- **Session Management**: Secure session handling with Redis
- **API Security**: Protected endpoints with proper authorization
- **Data Encryption**: Sensitive data protection and secure communication

## 🚀 Quick Start

### Prerequisites
- **Python 3.8+** - Backend runtime
- **Node.js 16+** - Frontend runtime
- **MySQL 5.7+** - Database
- **Git** - Version control

### Option 1: One-Click Launch (Recommended)
```bash
# Clone the repository
git clone https://github.com/sahlswla/transport_ms.git
cd transport_ms

# Make launcher executable and run
chmod +x launcher.sh
./launcher.sh
```

### Option 2: Using Make
```bash
make setup && make start
```

### Option 3: Using npm
```bash
npm install concurrently
npm start
```

### Option 4: Manual Setup
```bash
# Backend setup
cd backend
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate.bat
pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 8000 --reload

# Frontend setup (in a separate terminal)
cd frontend
npm install
npm start
```

## 🌐 Application URLs

After successful launch, access the application at:

- **🖥️ Frontend Application**: http://localhost:3000
- **⚡ Backend API**: http://localhost:8000
- **📚 API Documentation**: http://localhost:8000/docs
- **📖 API Redoc**: http://localhost:8000/redoc

## 📱 User Access

### Default Login Credentials
```
Admin User:
- Email: admin@hal.co.in
- Password: admin123

Driver User:
- Email: driver@hal.co.in
- Password: driver123

Employee User:
- Email: employee@hal.co.in
- Password: employee123
```

## 🛠️ Installation Guide

### System Requirements
- **Operating System**: Linux, macOS, or Windows
- **Memory**: Minimum 4GB RAM (8GB recommended)
- **Storage**: At least 2GB free space
- **Network**: Internet connection for dependency installation

### Automatic Installation (Recommended)
The launcher script handles all dependencies and setup automatically:

```bash
# For Linux/macOS
./launcher.sh --install-deps  # Installs system dependencies
./launcher.sh                 # Sets up and runs the application

# For Windows
launcher.bat                  # Double-click or run from command prompt
```

### Manual Installation Steps

#### 1. Install System Dependencies

**Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install python3 python3-pip python3-venv nodejs npm mysql-server
```

**macOS (with Homebrew):**
```bash
brew install python@3.11 node mysql
```

**Windows:**
- Download and install Python 3.8+ from python.org
- Download and install Node.js 16+ from nodejs.org
- Download and install MySQL from mysql.com

#### 2. Database Setup
```bash
# Start MySQL service
sudo systemctl start mysql  # Linux
brew services start mysql   # macOS

# Create database (run the setup script)
mysql -u root -p < backend/database_setup.sql
```

#### 3. Backend Setup
```bash
cd backend
python3 -m venv venv
source venv/bin/activate     # Linux/macOS
# venv\Scripts\activate.bat  # Windows
pip install -r requirements.txt
```

#### 4. Frontend Setup
```bash
cd frontend
npm install
```

#### 5. Environment Configuration
```bash
# Copy and configure environment file
cp backend/.env.example backend/.env
# Edit .env file with your database credentials
```

### Running the Application
```bash
# Option 1: Use the launcher (recommended)
./launcher.sh

# Option 2: Manual start
# Terminal 1 - Backend
cd backend && source venv/bin/activate && uvicorn main:app --reload

# Terminal 2 - Frontend
cd frontend && npm start
```

## 📁 Project Structure
```
Hal_transport/
├── 🚀 launcher.sh              # Linux/macOS launcher script
├── 🚀 launcher.bat             # Windows launcher script
├── 📋 Makefile                 # Make commands for development
├── 📦 package.json             # npm scripts and dependencies
├── 📚 LAUNCHER_README.md       # Detailed launcher documentation
├── 📖 README.md                # This file
├──
├── backend/                    # Python FastAPI Backend
│   ├── app/
│   │   ├── 🔐 auth/           # Authentication modules
│   │   ├── 🗄️ models/         # Database models
│   │   ├── 🛣️ routes/          # API endpoints
│   │   ├── 🔧 services/       # Business logic
│   │   ├── 🤖 ml/             # Machine learning modules
│   │   ├── 📊 analytics/      # Analytics services
│   │   └── 🔧 config.py       # Configuration settings
│   ├── 📋 requirements.txt     # Python dependencies
│   ├── 🚀 main.py             # FastAPI application entry
│   ├── 🗄️ database_setup.sql  # Database schema
│   └── 🧪 tests/              # Backend tests
│
├── frontend/                   # React.js Frontend
│   ├── src/
│   │   ├── 🧩 components/     # Reusable UI components
│   │   ├── 📄 pages/          # Application pages
│   │   ├── 🔧 services/       # API services
│   │   ├── 🛠️ utils/          # Utility functions
│   │   ├── 🎨 styles/         # CSS and styling
│   │   └── 📱 App.js          # Main React component
│   ├── 📦 package.json        # Node.js dependencies
│   ├── 🌐 public/             # Static assets
│   └── 🧪 tests/              # Frontend tests
│
├── database/                   # Database files
│   ├── 📊 schema.sql          # Database schema
│   └── 🔄 migrations/         # Database migrations
│
├── docs/                       # Documentation
│   ├── 📚 api/                # API documentation
│   ├── 🏗️ architecture/       # System architecture
│   └── 👥 user-guide/         # User manuals
│
├── logs/                       # Application logs (created at runtime)
│   ├── 📝 backend.log         # Backend server logs
│   ├── 📝 frontend.log        # Frontend server logs
│   ├── 🆔 backend.pid         # Backend process ID
│   └── 🆔 frontend.pid        # Frontend process ID
│
└── 🧪 tests/                  # Test files
    ├── backend/               # Backend tests
    └── frontend/              # Frontend tests
```

## 🔧 Troubleshooting

### Common Issues

#### Port Already in Use
```bash
# Check what's using the port
lsof -i :3000  # Frontend
lsof -i :8000  # Backend

# Kill the process
kill -9 <PID>
```

#### Python Virtual Environment Issues
```bash
# Remove and recreate virtual environment
rm -rf backend/venv
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

#### Database Connection Issues
```bash
# Check MySQL status
sudo systemctl status mysql

# Restart MySQL
sudo systemctl restart mysql

# Check database exists
mysql -u root -p -e "SHOW DATABASES;"
```

#### Node.js/npm Issues
```bash
# Clear npm cache
npm cache clean --force

# Remove node_modules and reinstall
rm -rf frontend/node_modules
cd frontend && npm install
```

## 📊 Features Overview

### 🎯 Core Functionality
- **Multi-role Authentication**: Admin, Driver, Employee access levels
- **Transport Request Management**: Complete request lifecycle
- **Real-time GPS Tracking**: Live vehicle monitoring
- **Smart Dashboard**: Role-based analytics and insights
- **Vehicle Fleet Management**: Comprehensive fleet operations

### 🤖 AI/ML Capabilities
- **Route Optimization**: Traffic-aware intelligent routing
- **Demand Prediction**: ML-based resource planning
- **Performance Analytics**: Advanced operational insights
- **Predictive Maintenance**: Proactive vehicle care

### 📱 User Experience
- **Responsive Design**: Mobile-first approach
- **Real-time Updates**: Live status notifications
- **Interactive Maps**: Leaflet-based mapping
- **Professional UI**: Modern, intuitive interface

## 🚀 Deployment

### Development
```bash
./launcher.sh  # Local development server
```

### Production
```bash
chmod +x deploy.sh
./deploy.sh    # Production deployment with Nginx
```

## 📚 Documentation

- **[Launcher Guide](LAUNCHER_README.md)** - Detailed setup instructions
- **[API Documentation](http://localhost:8000/docs)** - Interactive API docs
- **[Architecture Guide](docs/architecture/)** - System design details
- **[User Manual](docs/user-guide/)** - End-user documentation

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is proprietary software developed for **Hindustan Aeronautics Limited (HAL)**.

## 👥 Support

For support and questions:
- **Email**: support@hal.co.in
- **Documentation**: [LAUNCHER_README.md](LAUNCHER_README.md)
- **Issues**: [GitHub Issues](https://github.com/Nibedita-Mohapatro/Hal_transport/issues)

---

**Made with ❤️ for Hindustan Aeronautics Limited (HAL)**
