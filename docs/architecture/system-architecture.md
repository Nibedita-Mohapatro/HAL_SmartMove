# System Architecture - HAL Smart Vehicle Transport Management System

## Overview

The HAL Smart Vehicle Transport Management System follows a modern microservices architecture with clear separation of concerns, scalability, and maintainability in mind.

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                        Frontend Layer                           │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐ │
│  │   Landing Page  │  │ Employee Portal │  │  Admin Portal   │ │
│  │   (React.js)    │  │   (React.js)    │  │   (React.js)    │ │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                      API Gateway Layer                         │
│  ┌─────────────────────────────────────────────────────────────┐ │
│  │              FastAPI Application                           │ │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐ │ │
│  │  │    Auth     │  │   Routes    │  │    Middleware       │ │ │
│  │  │  Service    │  │  Handler    │  │   (CORS, Logging)   │ │ │
│  │  └─────────────┘  └─────────────┘  └─────────────────────┘ │ │
│  └─────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                     Business Logic Layer                       │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐ │
│  │   User Service  │  │ Request Service │  │ Vehicle Service │ │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘ │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐ │
│  │ Driver Service  │  │Schedule Service │  │Analytics Service│ │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                      ML/AI Services Layer                      │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐ │
│  │Route Optimizer  │  │Demand Predictor │  │Vehicle Assigner │ │
│  │   (Genetic      │  │   (Time Series  │  │  (Optimization  │ │
│  │   Algorithm)    │  │    Models)      │  │   Algorithms)   │ │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                       Data Layer                               │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐ │
│  │     MySQL       │  │     Redis       │  │   File Storage  │ │
│  │   (Primary DB)  │  │   (Caching)     │  │   (Documents)   │ │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
```

## Component Details

### Frontend Layer

#### Landing Page
- **Technology**: React.js with Tailwind CSS
- **Purpose**: Public-facing information about HAL and system access
- **Features**:
  - Company information and branding
  - About HAL section with aerospace achievements
  - Image gallery of aircraft and facilities
  - Authentication portals for employees and admins

#### Employee Portal
- **Technology**: React.js with responsive design
- **Purpose**: Employee interface for transport requests
- **Key Components**:
  - Request form with validation
  - Status tracking dashboard
  - Personal history and analytics
  - Profile management

#### Admin Portal
- **Technology**: React.js with advanced data visualization
- **Purpose**: Administrative interface for transport management
- **Key Components**:
  - Real-time dashboard with metrics
  - Request approval workflow
  - Vehicle and driver management
  - Reporting and analytics tools

### Backend Layer

#### FastAPI Application
- **Framework**: FastAPI (Python)
- **Features**:
  - Automatic API documentation (Swagger/OpenAPI)
  - High performance with async support
  - Built-in data validation
  - JWT-based authentication

#### Core Services

##### Authentication Service
- JWT token management
- Role-based access control (Employee, Admin, Super Admin)
- Password hashing and validation
- Session management

##### Request Service
- Trip request creation and management
- Status tracking and updates
- Approval workflow
- Modification and cancellation handling

##### Vehicle Service
- Fleet management
- Vehicle availability tracking
- Maintenance scheduling
- Driver assignment

##### Analytics Service
- Real-time metrics calculation
- Historical data analysis
- Report generation
- Performance monitoring

### ML/AI Services Layer

#### Route Optimizer
- **Algorithm**: Genetic Algorithm with Ant Colony Optimization
- **Purpose**: Find optimal routes for multiple vehicles
- **Features**:
  - Multi-objective optimization (time, fuel, capacity)
  - Real-time traffic consideration
  - Dynamic re-routing capabilities

#### Demand Predictor
- **Algorithm**: LSTM Neural Networks with seasonal decomposition
- **Purpose**: Forecast transport demand
- **Features**:
  - Historical pattern analysis
  - Seasonal trend recognition
  - Event-based demand spikes prediction

#### Vehicle Assigner
- **Algorithm**: Hungarian Algorithm with ML enhancements
- **Purpose**: Optimal vehicle-request matching
- **Features**:
  - Capacity optimization
  - Driver skill matching
  - Fuel efficiency consideration

### Data Layer

#### MySQL Database
- **Purpose**: Primary data storage
- **Features**:
  - ACID compliance
  - Complex relationship management
  - Transaction support
  - Backup and recovery

#### Redis Cache
- **Purpose**: Performance optimization
- **Features**:
  - Session storage
  - Frequently accessed data caching
  - Real-time data temporary storage

#### File Storage
- **Purpose**: Document and media storage
- **Features**:
  - User profile images
  - Vehicle documents
  - Report exports
  - System logs

## Security Architecture

### Authentication & Authorization
- JWT tokens with refresh mechanism
- Role-based access control (RBAC)
- API rate limiting
- Input validation and sanitization

### Data Security
- Database encryption at rest
- HTTPS/TLS for data in transit
- Sensitive data masking in logs
- Regular security audits

## Scalability Considerations

### Horizontal Scaling
- Stateless API design
- Load balancer ready
- Database connection pooling
- Microservices architecture

### Performance Optimization
- Redis caching layer
- Database query optimization
- Async processing for ML tasks
- CDN for static assets

## Deployment Architecture

### Development Environment
- Docker containers for consistency
- Local MySQL and Redis instances
- Hot reload for development

### Production Environment
- Kubernetes orchestration
- Load balancers
- Database clustering
- Monitoring and logging

## Technology Justification

### FastAPI vs Django/Flask
- **FastAPI**: Chosen for high performance, automatic documentation, and modern async support
- Better suited for ML integration and real-time features

### MySQL vs PostgreSQL
- **MySQL**: Chosen for HAL's existing infrastructure compatibility and excellent performance for read-heavy workloads

### React.js vs Vue.js/Angular
- **React.js**: Large ecosystem, excellent community support, and flexibility for complex UI requirements
