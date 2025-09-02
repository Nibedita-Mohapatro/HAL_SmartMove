# 🚀 HAL SmartMove Transport Management System

*"Hassle-Free Transport at Your Fingertips. From booking to tracking, manage your travel needs with speed, clarity, and control."*

## 🎯 **Quick Start**

### **Instant Setup (Recommended)**
```bash
# Clone the repository
git clone <repository-url>
cd hal-transport-system

# Run the application (one command!)
python run_app.py
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

**Made with ❤️ for Hindustan Aeronautics Limited (HAL)**
