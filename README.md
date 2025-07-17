# 🚗 HAL Transport Management System

[![License](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.8+-green.svg)](https://python.org)
[![Node.js](https://img.shields.io/badge/Node.js-16+-green.svg)](https://nodejs.org)
[![React](https://img.shields.io/badge/React-18+-blue.svg)](https://reactjs.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-Latest-green.svg)](https://fastapi.tiangolo.com)

## 🌟 Project Overview

A comprehensive, enterprise-grade web-based transport management system designed specifically for **Hindustan Aeronautics Limited (HAL)** to streamline employee transportation services. The system features real-time GPS tracking, intelligent vehicle assignment, route optimization, and advanced ML/AI capabilities for demand prediction and operational efficiency.

### 🎯 Key Highlights
- **Real-time GPS tracking** with live vehicle monitoring
- **ML/AI-powered** route optimization and demand prediction
- **Role-based access control** (Admin, Driver, Employee)
- **Professional dashboard** with comprehensive analytics
- **Mobile-responsive design** with modern UI/UX
- **Enterprise-grade security** with JWT authentication

## 🛠️ Technical Stack

### Frontend
- **Framework**: React.js 18+ with JavaScript
- **Styling**: Tailwind CSS for modern, responsive design
- **Maps**: Leaflet with React-Leaflet for GPS tracking
- **Charts**: Chart.js for analytics and reporting
- **HTTP Client**: Axios for API communication
- **Routing**: React Router DOM for navigation

### Backend
- **Framework**: FastAPI (Python 3.8+)
- **Authentication**: JWT with bcrypt password hashing
- **Database ORM**: SQLAlchemy with MySQL
- **API Documentation**: Auto-generated with Swagger/OpenAPI
- **Background Tasks**: Celery with Redis
- **ML/AI**: scikit-learn, pandas, numpy for predictive analytics

### Database & Infrastructure
- **Primary Database**: MySQL 5.7+
- **Caching**: Redis for session management
- **File Storage**: Local file system with upload management
- **Deployment**: Production-ready with Nginx and Gunicorn

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

## ✨ Core Features

### 🏠 Landing Page
- **Professional HAL Branding**: Corporate identity with aerospace theme
- **Company Showcase**: About HAL section highlighting aerospace achievements
- **Interactive Gallery**: Aircraft, facilities, and operations showcase
- **Portal Navigation**: Seamless access to employee and admin interfaces

### 👥 Employee Module
- **Secure Authentication**: JWT-based login with role-based access
- **Smart Request Form**: Origin, destination, date/time, purpose, passenger count
- **Real-time Tracking**: Live status updates (pending/approved/rejected)
- **Request Management**: Modification and cancellation capabilities
- **Personal Analytics**: Individual request history and usage patterns
- **Mobile Responsive**: Optimized for mobile and tablet devices

### 🔧 Admin Module
- **Executive Dashboard**: Real-time metrics and KPI monitoring
- **Request Management**: Comprehensive approval workflow
- **Fleet Management**: Vehicle and driver assignment optimization
- **Resource Planning**: Fleet availability and utilization tracking
- **Advanced Analytics**: Detailed reporting and business intelligence
- **Schedule Management**: Recurring trips and route planning

### 🚗 Driver Module
- **Driver Dashboard**: Trip assignments and schedule management
- **GPS Integration**: Real-time location tracking and navigation
- **Trip Management**: Start/end trip functionality with status updates
- **Vehicle Maintenance**: Maintenance alerts and reporting
- **Performance Metrics**: Driver analytics and feedback system

### 🤖 ML/AI Features
- **Intelligent Assignment**: AI-powered vehicle allocation based on historical patterns
- **Route Optimization**: Machine learning algorithms for traffic-aware routing
- **Demand Prediction**: Predictive analytics for resource planning
- **Smart Scheduling**: Automated scheduling for recurring and optimal trips
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
