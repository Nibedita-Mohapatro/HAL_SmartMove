# HAL SmartMove Transport Management System - Complete Setup Guide

## 🎯 **Overview**

HAL SmartMove is a comprehensive transport management system with a React frontend and FastAPI backend. This guide provides step-by-step instructions for setting up the entire system from scratch.

## 📋 **Prerequisites**

### **Required Software**
- **Python 3.8+** (Backend)
- **Node.js 16+** (Frontend)
- **npm 8+** (Package manager)
- **Git** (Version control)

### **System Requirements**
- **OS**: Windows 10/11, macOS, or Linux
- **RAM**: Minimum 4GB, Recommended 8GB
- **Storage**: 2GB free space
- **Network**: Internet connection for dependencies

## 🚀 **Quick Start (Automated)**

For immediate setup, use our automated script:

```bash
# Clone and run the automated setup
git clone <repository-url>
cd hal-transport-system
python quick_start.py
```

## 📖 **Manual Setup Instructions**

### **Step 1: Clone Repository**

```bash
git clone <repository-url>
cd hal-transport-system
```

### **Step 2: Backend Setup**

#### **2.1 Navigate to Backend Directory**
```bash
cd backend
```

#### **2.2 Create Virtual Environment**
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

#### **2.3 Install Dependencies**
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

#### **2.4 Initialize Database**
```bash
python create_default_users.py
python create_default_drivers.py
python fix_database_schema.py
```

#### **2.5 Verify Backend Setup**
```bash
python verify_system_integrity.py
```

### **Step 3: Frontend Setup**

#### **3.1 Navigate to Frontend Directory**
```bash
cd ../frontend
```

#### **3.2 Install Dependencies**
```bash
npm install
```

#### **3.3 Verify Frontend Setup**
```bash
npm run build
```

### **Step 4: Start Services**

#### **4.1 Start Backend (Terminal 1)**
```bash
cd backend
venv\Scripts\activate  # Windows
# source venv/bin/activate  # macOS/Linux
python main.py
```

Backend will start on: **http://localhost:8000**

#### **4.2 Start Frontend (Terminal 2)**
```bash
cd frontend
npm start
```

Frontend will start on: **http://localhost:3000**

## 🔧 **Configuration**

### **Environment Variables**
Create `.env` file in backend directory:

```env
# Database Configuration
DATABASE_URL=sqlite:///./hal_transport_system.db

# Security
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# CORS Settings
FRONTEND_URL=http://localhost:3000
```

### **Database Configuration**
The system uses SQLite by default. For production, configure PostgreSQL or MySQL:

```env
# PostgreSQL Example
DATABASE_URL=postgresql://user:password@localhost/hal_transport

# MySQL Example  
DATABASE_URL=mysql+pymysql://user:password@localhost/hal_transport
```

## 👥 **Default User Accounts**

### **Administrator**
- **Employee ID**: `HAL001`
- **Password**: `admin123`
- **Role**: Admin (Full system access)

### **Employee**
- **Employee ID**: `HAL003`
- **Password**: `employee123`
- **Role**: Employee (Request transport)

### **Transport Manager**
- **Employee ID**: `HAL002`
- **Password**: `transport123`
- **Role**: Transport (Manage trips)

## 🔍 **Verification Steps**

### **1. Backend Health Check**
```bash
curl http://localhost:8000/health
# Expected: {"status": "healthy"}
```

### **2. Frontend Access**
Open browser: http://localhost:3000
- Should display HAL SmartMove login page

### **3. Login Test**
- Use HAL001/admin123 to verify admin access
- Check dashboard loads properly

### **4. API Test**
```bash
# Test login endpoint
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"employee_id": "HAL001", "password": "admin123"}'
```

## 🛠️ **Development Setup**

### **Backend Development**
```bash
cd backend
venv\Scripts\activate
pip install -e .
python main.py --reload
```

### **Frontend Development**
```bash
cd frontend
npm start
# Enables hot reload for development
```

## 📦 **Dependencies**

### **Backend Dependencies**
- **FastAPI**: Web framework
- **SQLAlchemy**: Database ORM
- **Pydantic**: Data validation
- **python-jose**: JWT handling
- **passlib**: Password hashing
- **uvicorn**: ASGI server

### **Frontend Dependencies**
- **React**: UI framework
- **React Router**: Navigation
- **Tailwind CSS**: Styling
- **Axios**: HTTP client

## 🔒 **Security Notes**

### **Production Deployment**
1. Change default passwords
2. Use environment variables for secrets
3. Enable HTTPS
4. Configure proper CORS settings
5. Use production database

### **Development Security**
- Default credentials are for development only
- SQLite database is not encrypted
- CORS is permissive for development

## 📁 **Project Structure**

```
hal-transport-system/
├── backend/
│   ├── app/
│   │   ├── models/          # Database models
│   │   ├── routes/          # API endpoints
│   │   ├── auth.py          # Authentication
│   │   └── database.py      # Database config
│   ├── main.py              # Backend entry point
│   └── requirements.txt     # Python dependencies
├── frontend/
│   ├── src/
│   │   ├── components/      # React components
│   │   ├── App.js           # Main app component
│   │   └── index.js         # Frontend entry point
│   ├── public/              # Static assets
│   └── package.json         # Node dependencies
└── docs/                    # Documentation
```

## 🆘 **Troubleshooting**

### **Common Issues**

#### **Port Already in Use**
```bash
# Kill process on port 8000
netstat -ano | findstr :8000
taskkill /PID <process-id> /F

# Kill process on port 3000
netstat -ano | findstr :3000
taskkill /PID <process-id> /F
```

#### **Database Connection Error**
```bash
cd backend
python fix_database_schema.py
python create_default_users.py
```

#### **Module Not Found Error**
```bash
cd backend
venv\Scripts\activate
pip install -r requirements.txt
```

#### **Frontend Build Error**
```bash
cd frontend
rm -rf node_modules package-lock.json
npm install
```

## 📞 **Support**

For additional help:
1. Check TROUBLESHOOTING.md
2. Review error logs in terminal
3. Verify all prerequisites are installed
4. Ensure ports 3000 and 8000 are available

## ✅ **Success Indicators**

Setup is complete when:
- ✅ Backend responds on http://localhost:8000
- ✅ Frontend loads on http://localhost:3000
- ✅ Login with HAL001/admin123 works
- ✅ Dashboard displays system statistics
- ✅ No console errors in browser or terminal

**Next Steps**: See USER_GUIDE.md for feature documentation and DEPLOYMENT.md for production deployment.
