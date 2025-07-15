# API Specification - HAL Smart Vehicle Transport Management System

## Base URL
```
Development: http://localhost:8000/api/v1
Production: https://transport.hal.co.in/api/v1
```

## Authentication

### JWT Token Authentication
All protected endpoints require a Bearer token in the Authorization header:
```
Authorization: Bearer <jwt_token>
```

### Authentication Endpoints

#### POST /auth/login
Login with employee credentials
```json
Request:
{
  "employee_id": "HAL001",
  "password": "password123"
}

Response:
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "token_type": "bearer",
  "expires_in": 3600,
  "user": {
    "id": 1,
    "employee_id": "HAL001",
    "email": "admin@hal.co.in",
    "first_name": "System",
    "last_name": "Administrator",
    "role": "super_admin",
    "department": "IT"
  }
}
```

#### POST /auth/refresh
Refresh access token
```json
Request:
{
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}

Response:
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "token_type": "bearer",
  "expires_in": 3600
}
```

#### POST /auth/logout
Logout and invalidate tokens
```json
Request: {}
Response: {"message": "Successfully logged out"}
```

## User Management

#### GET /users/profile
Get current user profile
```json
Response:
{
  "id": 1,
  "employee_id": "HAL001",
  "email": "admin@hal.co.in",
  "first_name": "System",
  "last_name": "Administrator",
  "phone": "+91-9876543210",
  "department": "IT",
  "designation": "System Administrator",
  "role": "super_admin",
  "last_login": "2024-01-15T10:30:00Z"
}
```

#### PUT /users/profile
Update user profile
```json
Request:
{
  "phone": "+91-9876543211",
  "designation": "Senior System Administrator"
}

Response:
{
  "message": "Profile updated successfully",
  "user": { /* updated user object */ }
}
```

## Transport Requests

#### POST /requests
Create new transport request
```json
Request:
{
  "origin": "HAL Main Gate, Bangalore",
  "destination": "Electronic City, Bangalore",
  "request_date": "2024-01-20",
  "request_time": "09:00:00",
  "passenger_count": 3,
  "purpose": "Client meeting",
  "priority": "medium"
}

Response:
{
  "id": 123,
  "status": "pending",
  "message": "Request submitted successfully",
  "estimated_approval_time": "2024-01-15T12:00:00Z"
}
```

#### GET /requests
Get user's transport requests (with pagination)
```json
Query Parameters:
- page: int (default: 1)
- limit: int (default: 10)
- status: string (optional)
- date_from: date (optional)
- date_to: date (optional)

Response:
{
  "requests": [
    {
      "id": 123,
      "origin": "HAL Main Gate, Bangalore",
      "destination": "Electronic City, Bangalore",
      "request_date": "2024-01-20",
      "request_time": "09:00:00",
      "passenger_count": 3,
      "purpose": "Client meeting",
      "priority": "medium",
      "status": "pending",
      "created_at": "2024-01-15T10:30:00Z",
      "vehicle_assignment": null
    }
  ],
  "pagination": {
    "page": 1,
    "limit": 10,
    "total": 25,
    "pages": 3
  }
}
```

#### GET /requests/{request_id}
Get specific request details
```json
Response:
{
  "id": 123,
  "origin": "HAL Main Gate, Bangalore",
  "destination": "Electronic City, Bangalore",
  "request_date": "2024-01-20",
  "request_time": "09:00:00",
  "passenger_count": 3,
  "purpose": "Client meeting",
  "priority": "medium",
  "status": "approved",
  "approved_by": {
    "id": 2,
    "name": "Transport Manager",
    "email": "transport@hal.co.in"
  },
  "approved_at": "2024-01-15T11:00:00Z",
  "vehicle_assignment": {
    "vehicle": {
      "id": 1,
      "vehicle_number": "KA01AB1234",
      "vehicle_type": "bus",
      "capacity": 40
    },
    "driver": {
      "id": 1,
      "name": "Ravi Kumar",
      "phone": "9876543210"
    },
    "estimated_departure": "08:45:00",
    "estimated_arrival": "09:30:00"
  }
}
```

#### PUT /requests/{request_id}
Update transport request (only if status is pending)
```json
Request:
{
  "passenger_count": 4,
  "purpose": "Updated: Client meeting with additional attendees"
}

Response:
{
  "message": "Request updated successfully",
  "request": { /* updated request object */ }
}
```

#### DELETE /requests/{request_id}
Cancel transport request
```json
Response:
{
  "message": "Request cancelled successfully"
}
```

## Admin Endpoints

#### GET /admin/requests
Get all transport requests (Admin only)
```json
Query Parameters:
- page: int (default: 1)
- limit: int (default: 20)
- status: string (optional)
- date_from: date (optional)
- date_to: date (optional)
- department: string (optional)
- priority: string (optional)

Response:
{
  "requests": [
    {
      "id": 123,
      "user": {
        "id": 3,
        "name": "John Doe",
        "employee_id": "HAL003",
        "department": "Engineering",
        "phone": "9876543212"
      },
      "origin": "HAL Main Gate, Bangalore",
      "destination": "Electronic City, Bangalore",
      "request_date": "2024-01-20",
      "request_time": "09:00:00",
      "passenger_count": 3,
      "purpose": "Client meeting",
      "priority": "medium",
      "status": "pending",
      "created_at": "2024-01-15T10:30:00Z"
    }
  ],
  "pagination": { /* pagination object */ }
}
```

#### PUT /admin/requests/{request_id}/approve
Approve transport request
```json
Request:
{
  "vehicle_id": 1,
  "driver_id": 1,
  "estimated_departure": "08:45:00",
  "estimated_arrival": "09:30:00",
  "notes": "Approved for client meeting"
}

Response:
{
  "message": "Request approved successfully",
  "assignment_id": 456
}
```

#### PUT /admin/requests/{request_id}/reject
Reject transport request
```json
Request:
{
  "rejection_reason": "Vehicle not available at requested time"
}

Response:
{
  "message": "Request rejected successfully"
}
```

## Vehicle Management

#### GET /admin/vehicles
Get all vehicles
```json
Response:
{
  "vehicles": [
    {
      "id": 1,
      "vehicle_number": "KA01AB1234",
      "vehicle_type": "bus",
      "capacity": 40,
      "fuel_type": "diesel",
      "model": "Tata Starbus",
      "year_of_manufacture": 2020,
      "is_active": true,
      "current_location": "HAL Main Gate",
      "maintenance_status": "good",
      "next_maintenance": "2024-02-15"
    }
  ]
}
```

#### POST /admin/vehicles
Add new vehicle
```json
Request:
{
  "vehicle_number": "KA01GH3456",
  "vehicle_type": "van",
  "capacity": 12,
  "fuel_type": "diesel",
  "model": "Mahindra Bolero",
  "year_of_manufacture": 2023
}

Response:
{
  "message": "Vehicle added successfully",
  "vehicle": { /* created vehicle object */ }
}
```

#### GET /admin/vehicles/availability
Check vehicle availability
```json
Query Parameters:
- date: date (required)
- time: time (required)
- duration: int (minutes, optional, default: 120)

Response:
{
  "available_vehicles": [
    {
      "id": 1,
      "vehicle_number": "KA01AB1234",
      "vehicle_type": "bus",
      "capacity": 40,
      "current_location": "HAL Main Gate"
    }
  ],
  "busy_vehicles": [
    {
      "id": 2,
      "vehicle_number": "KA01CD5678",
      "busy_until": "10:30:00",
      "current_assignment": "Trip to Electronic City"
    }
  ]
}
```

## Analytics & Reporting

#### GET /admin/analytics/dashboard
Get dashboard analytics
```json
Response:
{
  "summary": {
    "total_requests_today": 15,
    "pending_requests": 5,
    "approved_requests": 8,
    "completed_trips": 12,
    "active_vehicles": 8,
    "available_drivers": 6
  },
  "trends": {
    "requests_last_7_days": [12, 15, 18, 14, 16, 13, 15],
    "popular_routes": [
      {
        "route": "HAL to Electronic City",
        "count": 25,
        "percentage": 35.2
      }
    ]
  }
}
```

#### GET /admin/analytics/demand-forecast
Get ML-based demand forecast
```json
Query Parameters:
- days: int (default: 7, max: 30)
- route: string (optional)

Response:
{
  "forecast": [
    {
      "date": "2024-01-21",
      "predicted_requests": 18,
      "confidence": 0.85,
      "peak_hours": ["09:00", "17:30"]
    }
  ],
  "model_accuracy": 0.92,
  "last_updated": "2024-01-15T12:00:00Z"
}
```

## ML/AI Services

#### POST /ml/route-optimization
Get optimized route for multiple requests
```json
Request:
{
  "requests": [
    {
      "id": 123,
      "origin": "HAL Main Gate",
      "destination": "Electronic City",
      "passenger_count": 3,
      "priority": "medium"
    }
  ],
  "available_vehicles": [1, 2, 3],
  "constraints": {
    "max_detour_minutes": 15,
    "fuel_efficiency_weight": 0.3,
    "time_efficiency_weight": 0.7
  }
}

Response:
{
  "optimized_assignments": [
    {
      "vehicle_id": 1,
      "requests": [123, 124],
      "route": [
        {"location": "HAL Main Gate", "arrival": "09:00", "departure": "09:05"},
        {"location": "Electronic City", "arrival": "09:35", "departure": "09:40"}
      ],
      "total_distance": 25.5,
      "estimated_fuel": 3.2,
      "efficiency_score": 0.89
    }
  ],
  "optimization_time_ms": 245
}
```

## Error Responses

All endpoints return consistent error responses:
```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid request data",
    "details": {
      "passenger_count": ["Must be between 1 and 50"]
    }
  },
  "timestamp": "2024-01-15T10:30:00Z"
}
```

### Common Error Codes
- `AUTHENTICATION_REQUIRED`: 401
- `INSUFFICIENT_PERMISSIONS`: 403
- `RESOURCE_NOT_FOUND`: 404
- `VALIDATION_ERROR`: 422
- `INTERNAL_SERVER_ERROR`: 500

## Rate Limiting
- General endpoints: 100 requests per minute per user
- ML endpoints: 10 requests per minute per user
- Authentication endpoints: 5 requests per minute per IP
