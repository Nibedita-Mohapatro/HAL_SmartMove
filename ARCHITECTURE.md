# HAL SmartMove - System Architecture Documentation

## 🏗️ **System Overview**

HAL SmartMove is a modern, scalable transport management system built with a microservices-inspired architecture using React frontend and FastAPI backend.

## 📊 **High-Level Architecture**

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Web Browser   │    │   Mobile App    │    │  Admin Panel    │
│   (React SPA)   │    │   (Future)      │    │   (React)       │
└─────────┬───────┘    └─────────┬───────┘    └─────────┬───────┘
          │                      │                      │
          └──────────────────────┼──────────────────────┘
                                 │
                    ┌─────────────┴─────────────┐
                    │     Load Balancer         │
                    │      (Nginx)              │
                    └─────────────┬─────────────┘
                                  │
                    ┌─────────────┴─────────────┐
                    │     API Gateway           │
                    │    (FastAPI + CORS)       │
                    └─────────────┬─────────────┘
                                  │
          ┌───────────────────────┼───────────────────────┐
          │                       │                       │
    ┌─────┴─────┐         ┌─────┴─────┐         ┌─────┴─────┐
    │   Auth    │         │ Transport │         │   Admin   │
    │ Service   │         │ Service   │         │ Service   │
    └─────┬─────┘         └─────┬─────┘         └─────┬─────┘
          │                     │                     │
          └─────────────────────┼─────────────────────┘
                                │
                    ┌─────────────┴─────────────┐
                    │     Database Layer        │
                    │    (SQLite/PostgreSQL)    │
                    └───────────────────────────┘
```

## 🎯 **Core Components**

### **1. Frontend Layer (React SPA)**

#### **Technology Stack**
- **Framework**: React 18.x
- **Routing**: React Router v6
- **Styling**: Tailwind CSS
- **HTTP Client**: Fetch API
- **State Management**: React Hooks + Context

#### **Component Architecture**
```
src/
├── components/
│   ├── common/              # Reusable UI components
│   │   ├── Button.js
│   │   ├── Modal.js
│   │   └── LoadingSpinner.js
│   ├── auth/                # Authentication components
│   │   ├── LoginForm.js
│   │   └── ProtectedRoute.js
│   ├── dashboard/           # Dashboard components
│   │   ├── AdminDashboard.js
│   │   ├── EmployeeDashboard.js
│   │   └── TransportDashboard.js
│   ├── transport/           # Transport management
│   │   ├── RequestForm.js
│   │   ├── RequestList.js
│   │   └── TripTracker.js
│   ├── admin/               # Admin components
│   │   ├── UserManagement.js
│   │   ├── VehicleManagement.js
│   │   └── DriverManagement.js
│   └── layout/              # Layout components
│       ├── Header.js
│       ├── Sidebar.js
│       └── Footer.js
├── hooks/                   # Custom React hooks
├── utils/                   # Utility functions
├── contexts/                # React contexts
└── App.js                   # Main application component
```

#### **Key Features**
- **Responsive Design**: Mobile-first approach
- **Role-based UI**: Different interfaces for different user roles
- **Real-time Updates**: WebSocket integration for live updates
- **Offline Support**: Service worker for basic offline functionality

### **2. Backend Layer (FastAPI)**

#### **Technology Stack**
- **Framework**: FastAPI 0.104.x
- **ORM**: SQLAlchemy 2.0
- **Authentication**: JWT with python-jose
- **Validation**: Pydantic v2
- **Server**: Uvicorn (ASGI)

#### **Service Architecture**
```
app/
├── models/                  # Database models
│   ├── user.py             # User model
│   ├── driver.py           # Driver model
│   ├── vehicle.py          # Vehicle model
│   ├── transport_request.py # Transport request model
│   └── vehicle_assignment.py # Assignment model
├── routes/                  # API endpoints
│   ├── auth.py             # Authentication endpoints
│   ├── users.py            # User management
│   ├── drivers.py          # Driver management
│   ├── vehicles.py         # Vehicle management
│   ├── transport.py        # Transport requests
│   └── admin.py            # Admin operations
├── schemas/                 # Pydantic schemas
├── services/                # Business logic
├── utils/                   # Utility functions
├── auth.py                  # Authentication logic
├── database.py              # Database configuration
└── main.py                  # Application entry point
```

#### **API Design Principles**
- **RESTful**: Standard HTTP methods and status codes
- **Versioned**: `/api/v1/` prefix for future compatibility
- **Documented**: Auto-generated OpenAPI/Swagger docs
- **Validated**: Request/response validation with Pydantic

### **3. Database Layer**

#### **Schema Design**
```sql
-- Core Tables
Users (id, employee_id, first_name, last_name, email, role, is_active)
Drivers (id, employee_id, first_name, last_name, license_number, is_active)
Vehicles (id, vehicle_number, type, capacity, fuel_type, is_active)
TransportRequests (id, user_id, origin, destination, status, created_at)
VehicleAssignments (id, request_id, vehicle_id, driver_id, status)

-- Relationships
Users 1:N TransportRequests
TransportRequests 1:1 VehicleAssignments
VehicleAssignments N:1 Vehicles
VehicleAssignments N:1 Drivers
```

#### **Data Flow**
1. **User Authentication**: JWT tokens stored in localStorage
2. **Request Creation**: Employee submits transport request
3. **Admin Approval**: Admin reviews and approves requests
4. **Assignment**: Admin assigns vehicle and driver
5. **Tracking**: Real-time status updates during trip
6. **Completion**: Trip marked complete with feedback

## 🔐 **Security Architecture**

### **Authentication Flow**
```
1. User Login → Backend validates credentials
2. Backend generates JWT token
3. Frontend stores token in localStorage
4. All API requests include Authorization header
5. Backend validates token on each request
6. Token expires after 30 minutes (configurable)
```

### **Authorization Levels**
- **Admin**: Full system access
- **Transport**: Manage trips and assignments
- **Employee**: Create and view own requests
- **Driver**: View assigned trips (future feature)

### **Security Measures**
- **Password Hashing**: bcrypt with salt
- **JWT Tokens**: Signed with secret key
- **CORS Protection**: Configured for frontend domain
- **Input Validation**: Pydantic schemas
- **SQL Injection Prevention**: SQLAlchemy ORM

## 📡 **API Architecture**

### **Endpoint Structure**
```
/api/v1/
├── auth/
│   ├── POST /login          # User authentication
│   ├── POST /logout         # Token invalidation
│   └── GET /me              # Current user info
├── users/
│   ├── GET /                # List users (admin)
│   ├── POST /               # Create user (admin)
│   ├── GET /{id}            # Get user details
│   ├── PUT /{id}            # Update user
│   └── DELETE /{id}         # Delete user (admin)
├── drivers/
│   ├── GET /                # List drivers
│   ├── POST /               # Create driver
│   ├── GET /{id}            # Get driver details
│   ├── PUT /{id}            # Update driver
│   └── DELETE /{id}         # Delete driver
├── vehicles/
│   ├── GET /                # List vehicles
│   ├── POST /               # Create vehicle
│   ├── GET /{id}            # Get vehicle details
│   ├── PUT /{id}            # Update vehicle
│   └── DELETE /{id}         # Delete vehicle
├── requests/
│   ├── GET /                # List requests
│   ├── POST /               # Create request
│   ├── GET /{id}            # Get request details
│   ├── PUT /{id}            # Update request
│   ├── POST /{id}/approve   # Approve request
│   └── POST /{id}/assign    # Assign vehicle/driver
└── admin/
    ├── GET /dashboard       # Dashboard statistics
    ├── GET /reports         # System reports
    └── GET /analytics       # Usage analytics
```

### **Response Format**
```json
{
  "success": true,
  "data": { ... },
  "message": "Operation successful",
  "timestamp": "2025-07-21T00:00:00Z"
}
```

### **Error Format**
```json
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid input data",
    "details": { ... }
  },
  "timestamp": "2025-07-21T00:00:00Z"
}
```

## 🔄 **Data Flow Patterns**

### **Request Lifecycle**
```
1. Employee creates transport request
   ↓
2. Request stored with "pending" status
   ↓
3. Admin receives notification
   ↓
4. Admin reviews and approves request
   ↓
5. Admin assigns vehicle and driver
   ↓
6. Assignment created with "assigned" status
   ↓
7. Driver receives notification
   ↓
8. Trip begins - status "in_progress"
   ↓
9. Real-time GPS tracking (future)
   ↓
10. Trip completed - status "completed"
    ↓
11. Feedback collection (future)
```

### **State Management**
- **Frontend**: React hooks for local state, Context for global state
- **Backend**: SQLAlchemy sessions for database state
- **Database**: ACID transactions for data consistency

## 🚀 **Performance Considerations**

### **Frontend Optimization**
- **Code Splitting**: Lazy loading of components
- **Caching**: Browser caching for static assets
- **Bundling**: Webpack optimization
- **Compression**: Gzip compression for assets

### **Backend Optimization**
- **Database Indexing**: Optimized queries
- **Connection Pooling**: Efficient database connections
- **Caching**: Redis for session storage (future)
- **Async Processing**: FastAPI async capabilities

### **Scalability Patterns**
- **Horizontal Scaling**: Multiple backend instances
- **Load Balancing**: Nginx or cloud load balancer
- **Database Scaling**: Read replicas, sharding
- **Microservices**: Service decomposition (future)

## 🔧 **Development Workflow**

### **Local Development**
1. Backend runs on http://localhost:8000
2. Frontend runs on http://localhost:3000
3. Hot reload enabled for both services
4. SQLite database for development
5. CORS configured for cross-origin requests

### **Testing Strategy**
- **Unit Tests**: pytest for backend, Jest for frontend
- **Integration Tests**: API endpoint testing
- **E2E Tests**: Playwright for user workflows
- **Load Tests**: Artillery or similar tools

### **CI/CD Pipeline**
```
1. Code commit → Git webhook
2. Automated tests run
3. Build Docker images
4. Deploy to staging
5. Run integration tests
6. Deploy to production
7. Health checks
8. Rollback if issues
```

## 📊 **Monitoring & Observability**

### **Metrics Collection**
- **Application Metrics**: Request count, response time, error rate
- **System Metrics**: CPU, memory, disk usage
- **Business Metrics**: Active users, trip completion rate

### **Logging Strategy**
- **Structured Logging**: JSON format for easy parsing
- **Log Levels**: DEBUG, INFO, WARNING, ERROR, CRITICAL
- **Centralized Logging**: ELK stack or cloud logging

### **Health Checks**
- **Liveness Probe**: `/health` endpoint
- **Readiness Probe**: Database connectivity check
- **Dependency Checks**: External service availability

## 🔮 **Future Architecture Considerations**

### **Planned Enhancements**
- **Microservices**: Split into smaller services
- **Event-Driven**: Message queues for async processing
- **Real-time Features**: WebSocket for live updates
- **Mobile App**: React Native or Flutter
- **AI/ML**: Route optimization, demand prediction

### **Technology Evolution**
- **Database**: Migration to PostgreSQL for production
- **Caching**: Redis for session and data caching
- **Search**: Elasticsearch for advanced search
- **Monitoring**: Prometheus + Grafana stack
- **Security**: OAuth2/OIDC integration

This architecture provides a solid foundation for the HAL SmartMove system while maintaining flexibility for future growth and enhancements.
