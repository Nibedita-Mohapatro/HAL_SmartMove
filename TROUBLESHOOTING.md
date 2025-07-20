# HAL SmartMove - Troubleshooting Guide

## 🔧 **Common Issues & Solutions**

This guide helps resolve common issues you might encounter with the HAL SmartMove Transport Management System.

## 🚀 **Startup Issues**

### **Backend Won't Start**

#### **Issue**: `ModuleNotFoundError` or `ImportError`
```bash
ModuleNotFoundError: No module named 'fastapi'
```

**Solution**:
```bash
cd backend
venv\Scripts\activate  # Windows
# source venv/bin/activate  # macOS/Linux
pip install -r requirements.txt
```

#### **Issue**: `Port 8000 already in use`
```bash
ERROR: [Errno 10048] Only one usage of each socket address is normally permitted
```

**Solution**:
```bash
# Windows
netstat -ano | findstr :8000
taskkill /PID <process-id> /F

# macOS/Linux
lsof -ti:8000 | xargs kill -9
```

#### **Issue**: Database connection error
```bash
sqlalchemy.exc.OperationalError: (sqlite3.OperationalError) no such table: users
```

**Solution**:
```bash
cd backend
python fix_database_schema.py
python create_default_users.py
python create_default_drivers.py
```

### **Frontend Won't Start**

#### **Issue**: `npm start` fails
```bash
Error: Cannot find module 'react-scripts'
```

**Solution**:
```bash
cd frontend
rm -rf node_modules package-lock.json
npm install
npm start
```

#### **Issue**: `Port 3000 already in use`
```bash
Something is already running on port 3000
```

**Solution**:
```bash
# Windows
netstat -ano | findstr :3000
taskkill /PID <process-id> /F

# macOS/Linux
lsof -ti:3000 | xargs kill -9

# Or use different port
PORT=3001 npm start
```

#### **Issue**: Build errors
```bash
Module build failed: Error: ENOENT: no such file or directory
```

**Solution**:
```bash
cd frontend
npm run build
# If build fails, check for missing dependencies
npm install --save-dev @types/node
```

## 🔐 **Authentication Issues**

### **Login Problems**

#### **Issue**: "Invalid credentials" error
**Symptoms**: Can't login with correct credentials

**Solution**:
1. Verify credentials:
   - Admin: `HAL001` / `admin123`
   - Employee: `HAL003` / `employee123`
   - Transport: `HAL002` / `transport123`

2. Check if users exist in database:
```bash
cd backend
python -c "
from app.database import SessionLocal
from app.models.user import User
db = SessionLocal()
users = db.query(User).all()
for u in users:
    print(f'{u.employee_id}: {u.first_name} {u.last_name} ({u.role.value})')
db.close()
"
```

3. Recreate default users if missing:
```bash
python create_default_users.py
```

#### **Issue**: Token expired error
**Symptoms**: Logged out unexpectedly, "Token expired" message

**Solution**:
- Simply log in again
- Tokens expire after 30 minutes for security
- This is normal behavior

#### **Issue**: CORS errors in browser console
```bash
Access to fetch at 'http://localhost:8000' from origin 'http://localhost:3000' has been blocked by CORS policy
```

**Solution**:
1. Ensure backend is running on port 8000
2. Check CORS configuration in `backend/main.py`
3. Restart backend service

## 📊 **Database Issues**

### **Data Problems**

#### **Issue**: Empty database or missing data
**Symptoms**: No users, drivers, or vehicles in the system

**Solution**:
```bash
cd backend
# Recreate database schema
python fix_database_schema.py

# Add default data
python create_default_users.py
python create_default_drivers.py

# Verify data
python verify_system_integrity.py
```

#### **Issue**: Database locked error
```bash
sqlite3.OperationalError: database is locked
```

**Solution**:
1. Stop all backend processes
2. Wait 30 seconds
3. Restart backend
4. If persists, restart computer

#### **Issue**: Foreign key constraint errors
```bash
FOREIGN KEY constraint failed
```

**Solution**:
```bash
cd backend
python fix_database_schema.py
# This script handles constraint issues
```

## 🔄 **API Issues**

### **Request Failures**

#### **Issue**: 404 Not Found errors
**Symptoms**: API endpoints returning 404

**Solution**:
1. Check backend is running: `http://localhost:8000/docs`
2. Verify API endpoint URLs in frontend code
3. Check for typos in endpoint paths

#### **Issue**: 500 Internal Server Error
**Symptoms**: Server errors on API calls

**Solution**:
1. Check backend terminal for error details
2. Look for Python traceback
3. Common causes:
   - Database connection issues
   - Missing required fields
   - Invalid data types

#### **Issue**: Network errors
```bash
TypeError: Failed to fetch
```

**Solution**:
1. Ensure backend is running
2. Check network connectivity
3. Verify firewall settings
4. Try accessing `http://localhost:8000/health`

## 🎨 **Frontend Issues**

### **UI Problems**

#### **Issue**: Blank white screen
**Symptoms**: Frontend loads but shows nothing

**Solution**:
1. Check browser console for JavaScript errors
2. Clear browser cache and cookies
3. Try incognito/private browsing mode
4. Restart frontend development server

#### **Issue**: Styling issues or broken layout
**Symptoms**: UI looks wrong or components overlap

**Solution**:
1. Clear browser cache
2. Check if Tailwind CSS is loading
3. Restart frontend server
4. Check for CSS conflicts

#### **Issue**: Components not updating
**Symptoms**: Data doesn't refresh after changes

**Solution**:
1. Hard refresh browser (Ctrl+F5)
2. Check React DevTools for state issues
3. Verify API calls are completing successfully
4. Check for JavaScript errors in console

## 🚛 **Feature-Specific Issues**

### **Driver Management** ✅ **Recently Fixed**

#### **Issue**: Driver deletion not working
**Status**: ✅ **RESOLVED**

**Previous Problem**: Drivers remained in system after deletion
**Solution Applied**: 
- Fixed backend deletion logic
- Added proper frontend filtering
- Enhanced user feedback

**If Still Having Issues**:
```bash
cd backend
python test_driver_deletion.py
# This will verify the fix is working
```

### **Transport Requests**

#### **Issue**: Can't create transport requests
**Symptoms**: Form submission fails

**Solution**:
1. Check all required fields are filled
2. Verify date is in future
3. Check backend logs for validation errors
4. Ensure user has correct permissions

#### **Issue**: Approval workflow not working
**Symptoms**: Can't approve or assign requests

**Solution**:
1. Verify admin user permissions
2. Check if vehicles and drivers exist
3. Ensure request is in "pending" status
4. Check for assignment conflicts

### **GPS Tracking**

#### **Issue**: GPS tracking not working
**Symptoms**: "Track GPS" button doesn't work

**Solution**:
1. Feature is currently simulated
2. Check if trip status is "in_progress"
3. Verify browser allows location access
4. Check console for JavaScript errors

## 🔧 **System Maintenance**

### **Performance Issues**

#### **Issue**: Slow loading times
**Symptoms**: Pages take long to load

**Solution**:
1. Check system resources (CPU, RAM)
2. Restart both frontend and backend
3. Clear browser cache
4. Check for large database queries

#### **Issue**: High memory usage
**Symptoms**: System becomes sluggish

**Solution**:
1. Restart backend service
2. Check for memory leaks in logs
3. Monitor database connection pool
4. Consider upgrading system resources

### **Data Integrity**

#### **Issue**: Inconsistent data
**Symptoms**: Data doesn't match between screens

**Solution**:
```bash
cd backend
python verify_system_integrity.py
# This checks and fixes data consistency
```

## 🆘 **Emergency Procedures**

### **Complete System Reset**

If all else fails, perform a complete reset:

```bash
# 1. Stop all services
# Kill backend and frontend processes

# 2. Reset database
cd backend
rm -f hal_transport_system.db
python fix_database_schema.py
python create_default_users.py
python create_default_drivers.py

# 3. Reset frontend
cd ../frontend
rm -rf node_modules package-lock.json
npm install

# 4. Restart services
cd ../backend
venv\Scripts\activate
python main.py

# In new terminal:
cd frontend
npm start
```

### **Backup and Restore**

#### **Create Backup**
```bash
# Database backup
cp backend/hal_transport_system.db backup_$(date +%Y%m%d_%H%M%S).db

# Full system backup
tar -czf hal_backup_$(date +%Y%m%d_%H%M%S).tar.gz .
```

#### **Restore Backup**
```bash
# Restore database
cp backup_YYYYMMDD_HHMMSS.db backend/hal_transport_system.db

# Restart services
cd backend && python main.py
cd frontend && npm start
```

## 📞 **Getting Additional Help**

### **Log Collection**

When reporting issues, collect these logs:

1. **Backend Logs**: Terminal output from `python main.py`
2. **Frontend Logs**: Browser console (F12 → Console)
3. **Network Logs**: Browser Network tab (F12 → Network)
4. **System Info**: OS version, Python version, Node.js version

### **Diagnostic Commands**

Run these to gather system information:

```bash
# System versions
python --version
node --version
npm --version

# Backend health
curl http://localhost:8000/health

# Database check
cd backend && python verify_system_integrity.py

# Frontend build test
cd frontend && npm run build
```

### **Contact Information**

- **Documentation**: Check README.md and other .md files
- **Known Issues**: Check GitHub issues (if applicable)
- **System Status**: Run health checks above

## ✅ **Prevention Tips**

### **Regular Maintenance**
- Restart services weekly
- Clear browser cache regularly
- Monitor disk space
- Keep dependencies updated

### **Best Practices**
- Always use virtual environment for backend
- Don't modify core system files
- Test changes in development first
- Keep backups of working configurations

### **Monitoring**
- Check logs regularly for warnings
- Monitor system performance
- Verify data integrity periodically
- Test critical workflows monthly

**Remember**: Most issues can be resolved by restarting services and clearing caches. When in doubt, try the complete system reset procedure above.**
