#!/usr/bin/env python3
"""
HAL Smart Vehicle Transport Management System - Demo Version
This is a simplified version that runs without database setup
"""

from fastapi import FastAPI, HTTPException, Depends, status, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from typing import List, Optional, Dict
from datetime import datetime, date, time, timedelta
from jose import JWTError, jwt
import logging
import asyncio
import json

# Import Phase 2 Advanced Services
from route_optimization_service import route_optimizer
from automated_scheduling_service import automated_scheduler, SchedulingRequest, Priority
from vehicle_maintenance_service import vehicle_maintenance_service, fuel_management_service
from driver_analytics_service import driver_analytics_service
from ml_algorithms_enhanced import route_optimizer, demand_forecaster, assignment_optimizer
from gps_tracking import gps_tracker, get_demo_route, simulate_all_trips

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration
SECRET_KEY = "hal-transport-demo-secret-key"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Simple password hashing for demo (not for production)
import hashlib

def simple_hash(password):
    return hashlib.sha256(password.encode()).hexdigest()

def verify_simple_password(plain_password, hashed_password):
    computed_hash = simple_hash(plain_password)
    logger.debug(f"Password verification: {computed_hash} == {hashed_password}")
    return computed_hash == hashed_password
security = HTTPBearer()

# Create FastAPI app
app = FastAPI(
    title="HAL Smart Vehicle Transport Management System - DEMO",
    version="1.0.0",
    description="Demo version of the Smart Vehicle Transport Management System for Hindustan Aeronautics Limited (HAL)"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# WebSocket Connection Manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
        self.trip_rooms: Dict[str, set] = {}  # trip_id -> set of user_ids

    async def connect(self, websocket: WebSocket, user_id: str):
        await websocket.accept()
        self.active_connections[user_id] = websocket
        logger.info(f"WebSocket connected: {user_id}")

    def disconnect(self, user_id: str):
        if user_id in self.active_connections:
            del self.active_connections[user_id]
            # Remove from all trip rooms
            for trip_id, users in self.trip_rooms.items():
                users.discard(user_id)
            logger.info(f"WebSocket disconnected: {user_id}")

    async def send_personal_message(self, message: dict, user_id: str):
        if user_id in self.active_connections:
            try:
                await self.active_connections[user_id].send_text(json.dumps(message))
                return True
            except Exception as e:
                logger.error(f"Error sending message to {user_id}: {e}")
                self.disconnect(user_id)
        return False

    async def broadcast_to_trip(self, message: dict, trip_id: str):
        if trip_id in self.trip_rooms:
            disconnected_users = []
            for user_id in self.trip_rooms[trip_id]:
                success = await self.send_personal_message(message, user_id)
                if not success:
                    disconnected_users.append(user_id)

            # Clean up disconnected users
            for user_id in disconnected_users:
                self.trip_rooms[trip_id].discard(user_id)

    def join_trip_room(self, user_id: str, trip_id: str):
        if trip_id not in self.trip_rooms:
            self.trip_rooms[trip_id] = set()
        self.trip_rooms[trip_id].add(user_id)
        logger.info(f"User {user_id} joined trip room {trip_id}")

    def leave_trip_room(self, user_id: str, trip_id: str):
        if trip_id in self.trip_rooms:
            self.trip_rooms[trip_id].discard(user_id)
            logger.info(f"User {user_id} left trip room {trip_id}")

# Create connection manager instance
manager = ConnectionManager()

# In-memory data storage (for demo purposes)
# Initialize users after function definitions
DEMO_USERS = {}

DEMO_VEHICLES = [
    {
        "id": 1,
        "registration_number": "KA01AB1234",
        "make": "Tata",
        "model": "Starbus",
        "year": 2020,
        "type": "bus",
        "capacity": 40,
        "fuel_type": "diesel",
        "status": "available",
        "insurance_expiry": "2024-12-31",
        "insurance_provider": "HDFC ERGO",
        "insurance_policy_number": "POL123456789",
        "last_maintenance": "2024-06-15",
        "next_maintenance": "2024-12-15",
        "maintenance_type": "routine",
        "safety_status": "compliant",
        "created_at": "2024-01-01T00:00:00",
        "is_active": True
    },
    {
        "id": 2,
        "registration_number": "KA01CD5678",
        "make": "Toyota",
        "model": "Innova",
        "year": 2022,
        "type": "suv",
        "capacity": 7,
        "fuel_type": "petrol",
        "status": "available",
        "insurance_expiry": "2025-03-31",
        "insurance_provider": "ICICI Lombard",
        "insurance_policy_number": "POL987654321",
        "last_maintenance": "2024-05-20",
        "next_maintenance": "2024-11-20",
        "maintenance_type": "routine",
        "safety_status": "compliant",
        "created_at": "2024-01-01T00:00:00",
        "is_active": True
    },
    {
        "id": 3,
        "registration_number": "KA01EF9012",
        "make": "Mahindra",
        "model": "Bolero",
        "year": 2021,
        "type": "van",
        "capacity": 12,
        "fuel_type": "diesel",
        "status": "maintenance",
        "insurance_expiry": "2024-08-31",  # Expired for testing
        "insurance_provider": "Bajaj Allianz",
        "insurance_policy_number": "POL456789123",
        "last_maintenance": "2024-07-10",
        "next_maintenance": "2025-01-10",
        "maintenance_type": "major",
        "safety_status": "non_compliant",  # Insurance expired
        "created_at": "2024-01-01T00:00:00",
        "is_active": True
    },
    {
        "id": 4,
        "registration_number": "KA01GH3456",
        "make": "Maruti",
        "model": "Swift Dzire",
        "year": 2023,
        "type": "sedan",
        "capacity": 4,
        "fuel_type": "petrol",
        "status": "in_use",
        "insurance_expiry": "2025-06-30",
        "last_maintenance": "2024-04-15",
        "next_maintenance": "2024-10-15",
        "created_at": "2024-01-01T00:00:00",
        "is_active": True
    }
]

DEMO_DRIVERS = [
    {
        "id": 1,
        "employee_id": "DRV001",
        "first_name": "Rajesh",
        "last_name": "Kumar",
        "phone": "+91-9876543210",
        "email": "rajesh.kumar@hal.co.in",
        "license_number": "KA0120230001234",
        "license_type": "Heavy Vehicle",
        "license_expiry": "2025-06-30",
        "date_of_birth": "1985-03-15",
        "address": "123 MG Road, Bangalore, Karnataka 560001",
        "emergency_contact": "Sunita Kumar",
        "emergency_phone": "+91-9876543211",
        "status": "active",
        "rating": 4.8,
        "total_trips": 245,
        "created_at": "2024-01-01T00:00:00",
        "is_active": True
    },
    {
        "id": 2,
        "employee_id": "DRV002",
        "first_name": "Suresh",
        "last_name": "Reddy",
        "phone": "+91-9876543220",
        "email": "suresh.reddy@hal.co.in",
        "license_number": "KA0120230001235",
        "license_type": "Light Vehicle",
        "license_expiry": "2024-12-31",
        "date_of_birth": "1990-07-22",
        "address": "456 Brigade Road, Bangalore, Karnataka 560025",
        "emergency_contact": "Lakshmi Reddy",
        "emergency_phone": "+91-9876543221",
        "status": "active",
        "rating": 4.6,
        "total_trips": 189,
        "created_at": "2024-01-01T00:00:00",
        "is_active": True
    },
    {
        "id": 3,
        "employee_id": "DRV003",
        "first_name": "Amit",
        "last_name": "Sharma",
        "phone": "+91-9876543230",
        "email": "amit.sharma@hal.co.in",
        "license_number": "KA0120230001236",
        "license_type": "Heavy Vehicle",
        "license_expiry": "2025-03-31",
        "date_of_birth": "1988-11-10",
        "address": "789 Commercial Street, Bangalore, Karnataka 560001",
        "emergency_contact": "Priya Sharma",
        "emergency_phone": "+91-9876543231",
        "status": "on_leave",
        "rating": 4.9,
        "total_trips": 312,
        "created_at": "2024-01-01T00:00:00",
        "is_active": True
    },
    {
        "id": 4,
        "employee_id": "DRV004",
        "first_name": "Mohammed",
        "last_name": "Ali",
        "phone": "+91-9876543240",
        "email": "mohammed.ali@hal.co.in",
        "license_number": "KA0120230001237",
        "license_type": "Light Vehicle",
        "license_expiry": "2024-09-30",
        "date_of_birth": "1992-05-18",
        "address": "321 Residency Road, Bangalore, Karnataka 560025",
        "emergency_contact": "Fatima Ali",
        "emergency_phone": "+91-9876543241",
        "status": "active",
        "rating": 4.7,
        "total_trips": 156,
        "created_at": "2024-01-01T00:00:00",
        "is_active": True
    }
]

DEMO_REQUESTS = []
request_counter = 1

# Pydantic models
class LoginRequest(BaseModel):
    employee_id: str
    password: str

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int
    user: dict

class TransportRequestCreate(BaseModel):
    origin: str
    destination: str
    request_date: date
    request_time: time
    passenger_count: int = 1
    purpose: Optional[str] = None
    priority: str = "medium"

class CreateUserRequest(BaseModel):
    employee_id: str
    email: str
    first_name: str
    last_name: str
    phone: str
    department: str
    designation: str
    role: str  # 'employee' or 'admin'
    password: str

class UpdateUserRequest(BaseModel):
    email: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone: Optional[str] = None
    department: Optional[str] = None
    designation: Optional[str] = None
    role: Optional[str] = None
    is_active: Optional[bool] = None

class PasswordResetRequest(BaseModel):
    new_password: str

class VehicleCreateRequest(BaseModel):
    registration_number: str
    make: str
    model: str
    year: int
    type: str
    capacity: Optional[int] = None
    fuel_type: str = "petrol"
    status: str = "available"
    insurance_expiry: Optional[str] = None
    last_maintenance: Optional[str] = None
    next_maintenance: Optional[str] = None

class VehicleUpdateRequest(BaseModel):
    registration_number: Optional[str] = None
    make: Optional[str] = None
    model: Optional[str] = None
    year: Optional[int] = None
    type: Optional[str] = None
    capacity: Optional[int] = None
    fuel_type: Optional[str] = None
    status: Optional[str] = None
    insurance_expiry: Optional[str] = None
    last_maintenance: Optional[str] = None
    next_maintenance: Optional[str] = None

class DriverCreateRequest(BaseModel):
    employee_id: str
    first_name: str
    last_name: str
    phone: str
    email: str
    license_number: str
    license_type: str
    license_expiry: str
    date_of_birth: str
    address: str
    emergency_contact: str
    emergency_phone: str
    status: str = "active"

class DriverUpdateRequest(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    license_number: Optional[str] = None
    license_type: Optional[str] = None
    license_expiry: Optional[str] = None
    date_of_birth: Optional[str] = None
    address: Optional[str] = None
    emergency_contact: Optional[str] = None
    emergency_phone: Optional[str] = None
    status: Optional[str] = None

class AssignmentRequest(BaseModel):
    vehicle_id: int
    driver_id: int
    notes: Optional[str] = None

# Initialize demo users
def init_demo_users():
    global DEMO_USERS
    DEMO_USERS = {
        "HAL001": {
            "id": 1,
            "employee_id": "HAL001",
            "email": "admin@hal.co.in",
            "password_hash": simple_hash("admin123"),
            "first_name": "System",
            "last_name": "Administrator",
            "phone": "+91-9876543210",
            "department": "IT",
            "designation": "System Administrator",
            "role": "admin",
            "is_active": True,
            "permissions": ["approve_requests", "assign_vehicles", "assign_drivers", "manage_users", "view_analytics", "safety_override"]
        },
        "HAL002": {
            "id": 2,
            "employee_id": "HAL002",
            "email": "driver@hal.co.in",
            "password_hash": simple_hash("driver123"),
            "first_name": "Rajesh",
            "last_name": "Kumar",
            "phone": "+91-9876543211",
            "department": "Transport",
            "designation": "Senior Driver",
            "role": "transport",  # Changed from "driver" to "transport"
            "is_active": True,
            "license_number": "DL123456789",
            "license_expiry": "2025-12-31",
            "rating": 4.5,
            "permissions": ["view_assigned_trips", "update_trip_status", "view_profile"]
        },
        "HAL003": {
            "id": 3,
            "employee_id": "HAL003",
            "email": "john.doe@hal.co.in",
            "password_hash": simple_hash("employee123"),
            "first_name": "John",
            "last_name": "Doe",
            "phone": "+91-9876543212",
            "department": "Engineering",
            "designation": "Senior Engineer",
            "role": "employee",
            "is_active": True,
            "permissions": ["create_requests", "view_own_requests", "track_status"]
        },
        "HAL004": {
            "id": 4,
            "employee_id": "HAL004",
            "email": "mike.transport@hal.co.in",
            "password_hash": simple_hash("transport123"),
            "first_name": "Mike",
            "last_name": "Transport",
            "phone": "+91-9876543213",
            "department": "Transport",
            "designation": "Transport Operator",
            "role": "transport",
            "is_active": True,
            "license_number": "DL987654321",
            "license_expiry": "2024-08-15",  # Expiring soon for testing
            "rating": 4.2,
            "permissions": ["view_assigned_trips", "update_trip_status", "view_profile"]
        },
        "HAL005": {
            "id": 5,
            "employee_id": "HAL005",
            "email": "sarah.employee@hal.co.in",
            "password_hash": simple_hash("emp123"),
            "first_name": "Sarah",
            "last_name": "Employee",
            "phone": "+91-9876543214",
            "department": "Finance",
            "designation": "Finance Officer",
            "role": "employee",
            "is_active": True,
            "permissions": ["create_requests", "view_own_requests", "track_status"]
        }
    }

# Safety Validation System
def validate_vehicle_safety(vehicle: dict) -> dict:
    """Validate vehicle safety requirements"""
    issues = []
    warnings = []

    # Check insurance expiry
    insurance_expiry = datetime.strptime(vehicle["insurance_expiry"], "%Y-%m-%d").date()
    today = date.today()
    days_to_insurance_expiry = (insurance_expiry - today).days

    if days_to_insurance_expiry < 0:
        issues.append(f"Insurance expired {abs(days_to_insurance_expiry)} days ago")
    elif days_to_insurance_expiry <= 7:
        warnings.append(f"Insurance expires in {days_to_insurance_expiry} days")

    # Check maintenance schedule
    next_maintenance = datetime.strptime(vehicle["next_maintenance"], "%Y-%m-%d").date()
    days_to_maintenance = (next_maintenance - today).days

    if days_to_maintenance < 0:
        issues.append(f"Maintenance overdue by {abs(days_to_maintenance)} days")
    elif days_to_maintenance <= 7:
        warnings.append(f"Maintenance due in {days_to_maintenance} days")

    # Check vehicle status
    if vehicle["status"] != "available":
        issues.append(f"Vehicle status is '{vehicle['status']}', not available")

    return {
        "vehicle_id": vehicle["id"],
        "is_safe": len(issues) == 0,
        "issues": issues,
        "warnings": warnings,
        "safety_score": max(0, 100 - (len(issues) * 50) - (len(warnings) * 10))
    }

def validate_driver_safety(driver: dict) -> dict:
    """Validate driver safety requirements"""
    issues = []
    warnings = []

    # Check license expiry
    if "license_expiry" in driver:
        license_expiry = datetime.strptime(driver["license_expiry"], "%Y-%m-%d").date()
        today = date.today()
        days_to_license_expiry = (license_expiry - today).days

        if days_to_license_expiry < 0:
            issues.append(f"License expired {abs(days_to_license_expiry)} days ago")
        elif days_to_license_expiry <= 30:
            warnings.append(f"License expires in {days_to_license_expiry} days")

    # Check driver status
    if not driver.get("is_active", True):
        issues.append("Driver is not active")

    # Check driver rating
    rating = driver.get("rating", 0)
    if rating < 3.0:
        warnings.append(f"Driver rating is low ({rating}/5.0)")

    return {
        "driver_id": driver["id"],
        "is_safe": len(issues) == 0,
        "issues": issues,
        "warnings": warnings,
        "safety_score": max(0, 100 - (len(issues) * 50) - (len(warnings) * 10))
    }

def validate_assignment_safety(vehicle: dict, driver: dict) -> dict:
    """Validate complete assignment safety"""
    vehicle_safety = validate_vehicle_safety(vehicle)
    driver_safety = validate_driver_safety(driver)

    all_issues = vehicle_safety["issues"] + driver_safety["issues"]
    all_warnings = vehicle_safety["warnings"] + driver_safety["warnings"]

    return {
        "is_safe": len(all_issues) == 0,
        "can_approve": len(all_issues) == 0,
        "vehicle_safety": vehicle_safety,
        "driver_safety": driver_safety,
        "overall_issues": all_issues,
        "overall_warnings": all_warnings,
        "overall_safety_score": min(vehicle_safety["safety_score"], driver_safety["safety_score"])
    }

# Helper functions
def verify_password(plain_password: str, hashed_password: str) -> bool:
    return verify_simple_password(plain_password, hashed_password)

def check_permission(user: dict, required_permission: str) -> bool:
    """Check if user has required permission"""
    user_permissions = user.get("permissions", [])
    return required_permission in user_permissions

def require_permission(required_permission: str):
    """Decorator to require specific permission"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            # Get current user from kwargs or dependency injection
            current_user = kwargs.get('current_user')
            if not current_user:
                raise HTTPException(status_code=401, detail="Authentication required")

            if not check_permission(current_user, required_permission):
                raise HTTPException(
                    status_code=403,
                    detail=f"Permission '{required_permission}' required"
                )

            return func(*args, **kwargs)
        return wrapper
    return decorator

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire, "type": "access"})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        token = credentials.credentials
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        employee_id: str = payload.get("sub")
        if employee_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    user = DEMO_USERS.get(employee_id)
    if user is None:
        raise credentials_exception
    
    return user

# API Endpoints
@app.get("/")
async def root():
    return {
        "message": "HAL Smart Vehicle Transport Management System - DEMO",
        "version": "1.0.0",
        "status": "running",
        "docs": "/docs",
        "demo_credentials": {
            "admin": "HAL001 / admin123",
            "driver": "HAL002 / driver123",
            "employee": "HAL003 / employee123"
        }
    }

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "version": "1.0.0-demo",
        "environment": "demo",
        "database": "in-memory"
    }

@app.post("/api/v1/auth/login", response_model=TokenResponse)
async def login(login_data: LoginRequest):
    logger.info(f"Login attempt for employee_id: '{login_data.employee_id}' (length: {len(login_data.employee_id)})")
    logger.info(f"Available users: {list(DEMO_USERS.keys())}")

    # Strip whitespace from employee_id
    employee_id = login_data.employee_id.strip()

    user = DEMO_USERS.get(employee_id)
    if not user:
        logger.warning(f"User not found: '{employee_id}' (stripped)")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect employee ID or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not verify_password(login_data.password, user["password_hash"]):
        logger.warning(f"Invalid password for user: {employee_id}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect employee ID or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Check if user is active
    if not user.get("is_active", True):
        logger.warning(f"Inactive user attempted login: {employee_id}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Account is deactivated. Please contact administrator.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user["employee_id"]}, expires_delta=access_token_expires
    )
    refresh_token = create_access_token(data={"sub": user["employee_id"]})
    
    user_data = {k: v for k, v in user.items() if k != "password_hash"}
    
    logger.info(f"User {user['employee_id']} logged in successfully")
    
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        user=user_data
    )

@app.get("/api/v1/auth/profile")
async def get_profile(current_user: dict = Depends(get_current_user)):
    return {k: v for k, v in current_user.items() if k != "password_hash"}

@app.post("/api/v1/requests/")
async def create_request(
    request_data: TransportRequestCreate,
    current_user: dict = Depends(get_current_user)
):
    """Create a transport request - Employee role only (like Uber passenger)"""
    if current_user["role"] != "employee":
        raise HTTPException(status_code=403, detail="Only Employees can create transport requests")

    if not check_permission(current_user, "create_requests"):
        raise HTTPException(status_code=403, detail="Insufficient permissions to create requests")

    global request_counter

    new_request = {
        "id": request_counter,
        "user_id": current_user["id"],
        "user_name": f"{current_user['first_name']} {current_user['last_name']}",
        "employee_id": current_user["employee_id"],
        "department": current_user["department"],
        "origin": request_data.origin,
        "destination": request_data.destination,
        "request_date": request_data.request_date.isoformat(),
        "request_time": request_data.request_time.strftime("%H:%M:%S"),
        "passenger_count": request_data.passenger_count,
        "purpose": request_data.purpose,
        "priority": request_data.priority,
        "status": "pending",
        "created_at": datetime.now().isoformat(),
        "status_history": [
            {
                "status": "pending",
                "timestamp": datetime.now().isoformat(),
                "message": "Request submitted and awaiting admin approval"
            }
        ],
        "estimated_approval_time": "15-30 minutes",
        "tracking_enabled": True
    }

    DEMO_REQUESTS.append(new_request)
    request_counter += 1

    logger.info(f"Employee {current_user['employee_id']} created transport request {new_request['id']}")

    return {
        "success": True,
        "message": "Transport request created successfully",
        "request": new_request,
        "next_steps": [
            "Your request is now pending admin approval",
            "You will be notified once a vehicle and driver are assigned",
            "Track your request status in real-time"
        ]
    }

@app.get("/api/v1/requests/")
async def get_user_requests(current_user: dict = Depends(get_current_user)):
    """Get user's transport requests with detailed tracking - Employee role"""
    if current_user["role"] != "employee":
        raise HTTPException(status_code=403, detail="Only Employees can view their requests")

    if not check_permission(current_user, "view_own_requests"):
        raise HTTPException(status_code=403, detail="Insufficient permissions to view requests")

    user_requests = [req for req in DEMO_REQUESTS if req["user_id"] == current_user["id"]]

    # Enhance requests with real-time tracking info
    enhanced_requests = []
    for req in user_requests:
        enhanced_req = req.copy()

        # Add driver and vehicle info if assigned
        if req.get("assigned_driver_id"):
            driver = next((u for u in DEMO_USERS.values() if u["id"] == req["assigned_driver_id"]), None)
            if driver:
                enhanced_req["assigned_driver"] = {
                    "name": f"{driver['first_name']} {driver['last_name']}",
                    "phone": driver["phone"],
                    "rating": driver.get("rating", 0),
                    "license_number": driver.get("license_number")
                }

        if req.get("assigned_vehicle_id"):
            vehicle = next((v for v in DEMO_VEHICLES if v["id"] == req["assigned_vehicle_id"]), None)
            if vehicle:
                enhanced_req["assigned_vehicle"] = {
                    "registration_number": vehicle["registration_number"],
                    "make": vehicle["make"],
                    "model": vehicle["model"],
                    "type": vehicle["type"],
                    "capacity": vehicle["capacity"]
                }

        # Add status-specific information
        if req["status"] == "pending":
            enhanced_req["status_message"] = "Awaiting admin approval and assignment"
            enhanced_req["estimated_wait_time"] = "15-30 minutes"
        elif req["status"] == "approved":
            enhanced_req["status_message"] = "Approved! Driver will contact you shortly"
            enhanced_req["can_track_driver"] = True
        elif req["status"] == "in_progress":
            enhanced_req["status_message"] = "Trip in progress"
            enhanced_req["can_track_live"] = True
        elif req["status"] == "completed":
            enhanced_req["status_message"] = "Trip completed successfully"
            enhanced_req["can_rate"] = True
        elif req["status"] == "rejected":
            enhanced_req["status_message"] = "Request rejected by admin"

        enhanced_requests.append(enhanced_req)

    return {
        "requests": enhanced_requests,
        "summary": {
            "total": len(user_requests),
            "pending": len([r for r in user_requests if r["status"] == "pending"]),
            "approved": len([r for r in user_requests if r["status"] == "approved"]),
            "in_progress": len([r for r in user_requests if r["status"] == "in_progress"]),
            "completed": len([r for r in user_requests if r["status"] == "completed"])
        },
        "pagination": {
            "page": 1,
            "limit": 10,
            "total": len(user_requests),
            "pages": 1
        }
    }

@app.get("/api/v1/requests/{request_id}/track")
async def track_request(request_id: int, current_user: dict = Depends(get_current_user)):
    """Track a specific request in real-time - Employee role"""
    if current_user["role"] != "employee":
        raise HTTPException(status_code=403, detail="Only Employees can track their requests")

    if not check_permission(current_user, "track_status"):
        raise HTTPException(status_code=403, detail="Insufficient permissions to track requests")

    # Find the request
    request = next((r for r in DEMO_REQUESTS if r["id"] == request_id), None)
    if not request:
        raise HTTPException(status_code=404, detail="Request not found")

    # Verify ownership
    if request["user_id"] != current_user["id"]:
        raise HTTPException(status_code=403, detail="You can only track your own requests")

    # Get detailed tracking information
    tracking_info = {
        "request": request,
        "current_status": request["status"],
        "status_history": request.get("status_history", []),
        "timeline": []
    }

    # Build timeline based on status
    if request["status"] in ["approved", "in_progress", "completed"]:
        if request.get("assigned_driver_id"):
            driver = next((u for u in DEMO_USERS.values() if u["id"] == request["assigned_driver_id"]), None)
            if driver:
                tracking_info["driver"] = {
                    "name": f"{driver['first_name']} {driver['last_name']}",
                    "phone": driver["phone"],
                    "rating": driver.get("rating", 0),
                    "current_location": "En route to pickup"  # Mock location
                }

        if request.get("assigned_vehicle_id"):
            vehicle = next((v for v in DEMO_VEHICLES if v["id"] == request["assigned_vehicle_id"]), None)
            if vehicle:
                tracking_info["vehicle"] = {
                    "registration_number": vehicle["registration_number"],
                    "make": vehicle["make"],
                    "model": vehicle["model"],
                    "estimated_arrival": "5-10 minutes"  # Mock ETA
                }

    return tracking_info

@app.get("/api/v1/admin/dashboard")
async def get_dashboard_stats(current_user: dict = Depends(get_current_user)):
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Only Admin can access dashboard")
    
    total_requests = len(DEMO_REQUESTS)
    pending_requests = len([req for req in DEMO_REQUESTS if req["status"] == "pending"])
    approved_requests = len([req for req in DEMO_REQUESTS if req["status"] == "approved"])
    
    return {
        "summary": {
            "total_requests_today": total_requests,
            "pending_requests": pending_requests,
            "approved_requests": approved_requests,
            "completed_trips": 0,
            "active_vehicles": len(DEMO_VEHICLES),
            "available_drivers": 3
        },
        "trends": {
            "requests_last_7_days": [2, 5, 3, 7, 4, 6, total_requests],
            "popular_routes": [
                {"route": "HAL Main Gate to Electronic City", "count": 15, "percentage": 45.5},
                {"route": "HAL Complex to Whitefield", "count": 10, "percentage": 30.3},
                {"route": "HAL to Airport", "count": 8, "percentage": 24.2}
            ]
        }
    }

@app.get("/api/v1/vehicles/")
async def get_vehicles(current_user: dict = Depends(get_current_user)):
    return {
        "vehicles": DEMO_VEHICLES,
        "pagination": {
            "page": 1,
            "limit": 20,
            "total": len(DEMO_VEHICLES),
            "pages": 1
        }
    }

@app.post("/api/v1/admin/vehicles/")
async def create_vehicle(
    vehicle_data: VehicleCreateRequest,
    current_user: dict = Depends(get_current_user)
):
    """Create a new vehicle - Admin only"""
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Only Admin can create vehicles")

    # Check if registration number already exists
    if any(v["registration_number"] == vehicle_data.registration_number for v in DEMO_VEHICLES):
        raise HTTPException(status_code=400, detail="Registration number already exists")

    # Create new vehicle
    new_vehicle_id = len(DEMO_VEHICLES) + 1
    new_vehicle = {
        "id": new_vehicle_id,
        "registration_number": vehicle_data.registration_number,
        "make": vehicle_data.make,
        "model": vehicle_data.model,
        "year": vehicle_data.year,
        "type": vehicle_data.type,
        "capacity": vehicle_data.capacity,
        "fuel_type": vehicle_data.fuel_type,
        "status": vehicle_data.status,
        "insurance_expiry": vehicle_data.insurance_expiry,
        "last_maintenance": vehicle_data.last_maintenance,
        "next_maintenance": vehicle_data.next_maintenance,
        "created_at": datetime.now().isoformat(),
        "created_by": current_user["employee_id"]
    }

    DEMO_VEHICLES.append(new_vehicle)

    logger.info(f"Vehicle {vehicle_data.registration_number} created by {current_user['employee_id']}")

    return {
        "message": "Vehicle created successfully",
        "vehicle": new_vehicle
    }

@app.put("/api/v1/admin/vehicles/{vehicle_id}")
async def update_vehicle(
    vehicle_id: int,
    vehicle_data: VehicleUpdateRequest,
    current_user: dict = Depends(get_current_user)
):
    """Update vehicle information - Admin only"""
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Only Admin can update vehicles")

    # Find the vehicle
    vehicle = next((v for v in DEMO_VEHICLES if v["id"] == vehicle_id), None)
    if not vehicle:
        raise HTTPException(status_code=404, detail="Vehicle not found")

    # Update only provided fields
    update_data = vehicle_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        if field == "registration_number" and value != vehicle["registration_number"]:
            # Check if new registration number already exists
            if any(v["registration_number"] == value for v in DEMO_VEHICLES if v["id"] != vehicle_id):
                raise HTTPException(status_code=400, detail="Registration number already exists")
        vehicle[field] = value

    vehicle["updated_at"] = datetime.now().isoformat()
    vehicle["updated_by"] = current_user["employee_id"]

    logger.info(f"Vehicle {vehicle_id} updated by {current_user['employee_id']}")

    return {
        "message": "Vehicle updated successfully",
        "vehicle": vehicle
    }

@app.delete("/api/v1/admin/vehicles/{vehicle_id}")
async def delete_vehicle(
    vehicle_id: int,
    current_user: dict = Depends(get_current_user)
):
    """Delete vehicle - Admin only"""
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Only Admin can delete vehicles")

    # Find the vehicle
    vehicle_index = next((i for i, v in enumerate(DEMO_VEHICLES) if v["id"] == vehicle_id), None)
    if vehicle_index is None:
        raise HTTPException(status_code=404, detail="Vehicle not found")

    # Check if vehicle is currently in use
    vehicle = DEMO_VEHICLES[vehicle_index]
    if vehicle["status"] == "in_use":
        raise HTTPException(status_code=400, detail="Cannot delete vehicle that is currently in use")

    deleted_vehicle = DEMO_VEHICLES.pop(vehicle_index)

    logger.info(f"Vehicle {vehicle_id} deleted by {current_user['employee_id']}")

    return {
        "message": "Vehicle deleted successfully",
        "deleted_vehicle_id": vehicle_id
    }

@app.put("/api/v1/admin/vehicles/{vehicle_id}/toggle-status")
async def toggle_vehicle_status(
    vehicle_id: int,
    current_user: dict = Depends(get_current_user)
):
    """Toggle vehicle status between available and maintenance - Admin only"""
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Only Admin can change vehicle status")

    # Find the vehicle
    vehicle = next((v for v in DEMO_VEHICLES if v["id"] == vehicle_id), None)
    if not vehicle:
        raise HTTPException(status_code=404, detail="Vehicle not found")

    # Toggle status
    if vehicle["status"] == "available":
        vehicle["status"] = "maintenance"
    elif vehicle["status"] == "maintenance":
        vehicle["status"] = "available"
    else:
        # For other statuses, set to available
        vehicle["status"] = "available"

    vehicle["status_changed_at"] = datetime.now().isoformat()
    vehicle["status_changed_by"] = current_user["employee_id"]

    logger.info(f"Vehicle {vehicle_id} status changed to {vehicle['status']} by {current_user['employee_id']}")

    return {
        "message": f"Vehicle status changed to {vehicle['status']}",
        "status": vehicle["status"]
    }

@app.get("/api/v1/drivers/")
async def get_drivers(current_user: dict = Depends(get_current_user)):
    """Get all drivers"""
    return {
        "drivers": DEMO_DRIVERS,
        "pagination": {
            "page": 1,
            "limit": 20,
            "total": len(DEMO_DRIVERS),
            "pages": 1
        }
    }

@app.post("/api/v1/admin/drivers/")
async def create_driver(
    driver_data: DriverCreateRequest,
    current_user: dict = Depends(get_current_user)
):
    """Create a new driver - Admin only"""
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Only Admin can create drivers")

    # Check if employee ID already exists
    if any(d["employee_id"] == driver_data.employee_id for d in DEMO_DRIVERS):
        raise HTTPException(status_code=400, detail="Employee ID already exists")

    # Check if license number already exists
    if any(d["license_number"] == driver_data.license_number for d in DEMO_DRIVERS):
        raise HTTPException(status_code=400, detail="License number already exists")

    # Create new driver
    new_driver_id = len(DEMO_DRIVERS) + 1
    new_driver = {
        "id": new_driver_id,
        "employee_id": driver_data.employee_id,
        "first_name": driver_data.first_name,
        "last_name": driver_data.last_name,
        "phone": driver_data.phone,
        "email": driver_data.email,
        "license_number": driver_data.license_number,
        "license_type": driver_data.license_type,
        "license_expiry": driver_data.license_expiry,
        "date_of_birth": driver_data.date_of_birth,
        "address": driver_data.address,
        "emergency_contact": driver_data.emergency_contact,
        "emergency_phone": driver_data.emergency_phone,
        "status": driver_data.status,
        "rating": 0.0,
        "total_trips": 0,
        "created_at": datetime.now().isoformat(),
        "created_by": current_user["employee_id"],
        "is_active": True
    }

    DEMO_DRIVERS.append(new_driver)

    logger.info(f"Driver {driver_data.employee_id} created by {current_user['employee_id']}")

    return {
        "message": "Driver created successfully",
        "driver": new_driver
    }

@app.put("/api/v1/admin/drivers/{driver_id}")
async def update_driver(
    driver_id: int,
    driver_data: DriverUpdateRequest,
    current_user: dict = Depends(get_current_user)
):
    """Update driver information - Admin only"""
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Only Admin can update drivers")

    # Find the driver
    driver = next((d for d in DEMO_DRIVERS if d["id"] == driver_id), None)
    if not driver:
        raise HTTPException(status_code=404, detail="Driver not found")

    # Update only provided fields
    update_data = driver_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        if field == "license_number" and value != driver["license_number"]:
            # Check if new license number already exists
            if any(d["license_number"] == value for d in DEMO_DRIVERS if d["id"] != driver_id):
                raise HTTPException(status_code=400, detail="License number already exists")
        driver[field] = value

    driver["updated_at"] = datetime.now().isoformat()
    driver["updated_by"] = current_user["employee_id"]

    logger.info(f"Driver {driver_id} updated by {current_user['employee_id']}")

    return {
        "message": "Driver updated successfully",
        "driver": driver
    }

@app.delete("/api/v1/admin/drivers/{driver_id}")
async def delete_driver(
    driver_id: int,
    current_user: dict = Depends(get_current_user)
):
    """Delete driver - Admin only"""
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Only Admin can delete drivers")

    # Find the driver
    driver_index = next((i for i, d in enumerate(DEMO_DRIVERS) if d["id"] == driver_id), None)
    if driver_index is None:
        raise HTTPException(status_code=404, detail="Driver not found")

    # Check if driver is currently assigned to active trips
    driver = DEMO_DRIVERS[driver_index]
    # In a real system, you would check for active assignments

    deleted_driver = DEMO_DRIVERS.pop(driver_index)

    logger.info(f"Driver {driver_id} deleted by {current_user['employee_id']}")

    return {
        "message": "Driver deleted successfully",
        "deleted_driver_id": driver_id
    }

@app.put("/api/v1/admin/drivers/{driver_id}/toggle-status")
async def toggle_driver_status(
    driver_id: int,
    current_user: dict = Depends(get_current_user)
):
    """Toggle driver status - Admin only"""
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Only Admin can change driver status")

    # Find the driver
    driver = next((d for d in DEMO_DRIVERS if d["id"] == driver_id), None)
    if not driver:
        raise HTTPException(status_code=404, detail="Driver not found")

    # Toggle status
    if driver["status"] == "active":
        driver["status"] = "inactive"
    elif driver["status"] == "inactive":
        driver["status"] = "active"
    else:
        # For other statuses like on_leave, set to active
        driver["status"] = "active"

    driver["status_changed_at"] = datetime.now().isoformat()
    driver["status_changed_by"] = current_user["employee_id"]

    logger.info(f"Driver {driver_id} status changed to {driver['status']} by {current_user['employee_id']}")

    return {
        "message": f"Driver status changed to {driver['status']}",
        "status": driver["status"]
    }

@app.get("/api/v1/admin/requests")
async def get_all_requests(current_user: dict = Depends(get_current_user)):
    """Get all transport requests for admin view"""
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Only Admin can access all requests")

    return {
        "requests": DEMO_REQUESTS,
        "total": len(DEMO_REQUESTS)
    }

@app.post("/api/v1/admin/requests/{request_id}/approve")
async def approve_request_with_assignment(
    request_id: int,
    assignment_data: dict,
    current_user: dict = Depends(get_current_user)
):
    """Approve a transport request with vehicle/driver assignment and safety validation - Admin only"""
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Only Admin can approve requests")

    if not check_permission(current_user, "approve_requests"):
        raise HTTPException(status_code=403, detail="Insufficient permissions to approve requests")

    # Find the request
    request = next((r for r in DEMO_REQUESTS if r["id"] == request_id), None)
    if not request:
        raise HTTPException(status_code=404, detail="Request not found")

    if request["status"] != "pending":
        raise HTTPException(status_code=400, detail="Only pending requests can be approved")

    # Validate required assignment data
    vehicle_id = assignment_data.get("vehicle_id")
    driver_id = assignment_data.get("driver_id")

    if not vehicle_id or not driver_id:
        raise HTTPException(status_code=400, detail="Both vehicle_id and driver_id are required for approval")

    # Find vehicle and driver
    vehicle = next((v for v in DEMO_VEHICLES if v["id"] == vehicle_id), None)
    driver = next((d for d in DEMO_DRIVERS if d["id"] == driver_id), None)

    if not vehicle:
        raise HTTPException(status_code=404, detail="Vehicle not found")
    if not driver:
        raise HTTPException(status_code=404, detail="Driver not found")

    # Perform safety validation
    safety_validation = validate_assignment_safety(vehicle, driver)
    safety_override = assignment_data.get("safety_override", False)

    # Check if assignment is safe (no critical issues) or if admin is overriding
    if not safety_validation["can_approve"] and not safety_override:
        return {
            "success": False,
            "message": "Cannot approve due to safety issues",
            "safety_validation": safety_validation,
            "requires_override": True
        }

    # If there are safety issues but admin is overriding, check permissions
    if not safety_validation["can_approve"] and safety_override:
        if not check_permission(current_user, "safety_override"):
            return {
                "success": False,
                "message": "Safety override permission required",
                "safety_validation": safety_validation,
                "requires_override": True
            }

    # Check for safety override if there are warnings (for non-critical issues)
    if safety_validation["overall_warnings"] and not safety_override:
        if not check_permission(current_user, "safety_override"):
            return {
                "success": False,
                "message": "Safety warnings detected. Admin override required.",
                "safety_validation": safety_validation,
                "requires_override": True
            }

    # Update request with assignment
    request["status"] = "approved"
    request["approved_by"] = current_user["employee_id"]
    request["approved_at"] = datetime.now().isoformat()
    request["assigned_vehicle_id"] = vehicle_id
    request["assigned_driver_id"] = driver_id
    request["safety_validation"] = safety_validation
    request["safety_override_used"] = safety_override

    # Update vehicle status
    vehicle["status"] = "assigned"
    vehicle["assigned_to_request"] = request_id

    # Update driver status
    driver["status"] = "assigned"
    driver["assigned_to_request"] = request_id

    logger.info(f"Request {request_id} approved by {current_user['employee_id']} with vehicle {vehicle_id} and driver {driver_id}")

    return {
        "success": True,
        "message": "Request approved successfully with assignments",
        "request": request,
        "assigned_vehicle": vehicle,
        "assigned_driver": driver,
        "safety_validation": safety_validation
    }

@app.get("/api/v1/admin/requests/{request_id}/assignment-options")
async def get_assignment_options(request_id: int, current_user: dict = Depends(get_current_user)):
    """Get available vehicles and drivers for assignment - Admin only"""
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Only Admin can access assignment options")

    # Find the request
    request = next((r for r in DEMO_REQUESTS if r["id"] == request_id), None)
    if not request:
        raise HTTPException(status_code=404, detail="Request not found")

    # Get available vehicles
    available_vehicles = []
    for vehicle in DEMO_VEHICLES:
        if vehicle["status"] == "available":
            safety_check = validate_vehicle_safety(vehicle)
            available_vehicles.append({
                **vehicle,
                "safety_validation": safety_check
            })

    # Get available drivers (transport role users)
    available_drivers = []
    for user in DEMO_USERS.values():
        if user["role"] == "transport" and user.get("status", "active") == "active":
            safety_check = validate_driver_safety(user)
            available_drivers.append({
                **user,
                "safety_validation": safety_check
            })

    return {
        "request": request,
        "available_vehicles": available_vehicles,
        "available_drivers": available_drivers,
        "assignment_requirements": {
            "passenger_count": request.get("passenger_count", 1),
            "trip_type": request.get("trip_type", "one_way"),
            "priority": request.get("priority", "medium")
        }
    }

@app.put("/api/v1/admin/requests/{request_id}/reject")
async def reject_request(request_id: int, current_user: dict = Depends(get_current_user)):
    """Reject a transport request - Admin only"""
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Only Admin can reject requests")

    # Find the request
    request = next((r for r in DEMO_REQUESTS if r["id"] == request_id), None)
    if not request:
        raise HTTPException(status_code=404, detail="Request not found")

    if request["status"] != "pending":
        raise HTTPException(status_code=400, detail="Only pending requests can be rejected")

    # Update request status
    request["status"] = "rejected"
    request["rejected_by"] = current_user["employee_id"]
    request["rejected_at"] = datetime.now().isoformat()

    logger.info(f"Request {request_id} rejected by {current_user['employee_id']}")

    return {
        "message": "Request rejected successfully",
        "request": request
    }

@app.put("/api/v1/admin/requests/{request_id}/cancel")
async def cancel_request(request_id: int, current_user: dict = Depends(get_current_user)):
    """Cancel a transport request - Admin only"""
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Only Admin can cancel requests")

    # Find the request
    request = next((r for r in DEMO_REQUESTS if r["id"] == request_id), None)
    if not request:
        raise HTTPException(status_code=404, detail="Request not found")

    if request["status"] in ["completed", "cancelled"]:
        raise HTTPException(status_code=400, detail="Cannot cancel completed or already cancelled requests")

    # Update request status
    request["status"] = "cancelled"
    request["cancelled_by"] = current_user["employee_id"]
    request["cancelled_at"] = datetime.now().isoformat()

    logger.info(f"Request {request_id} cancelled by {current_user['employee_id']}")

    return {
        "message": "Request cancelled successfully",
        "request": request
    }

@app.put("/api/v1/admin/requests/{request_id}/complete")
async def complete_request(request_id: int, current_user: dict = Depends(get_current_user)):
    """Mark a transport request as completed - Admin only"""
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Only Admin can complete requests")

    # Find the request
    request = next((r for r in DEMO_REQUESTS if r["id"] == request_id), None)
    if not request:
        raise HTTPException(status_code=404, detail="Request not found")

    if request["status"] != "approved":
        raise HTTPException(status_code=400, detail="Only approved requests can be completed")

    # Update request status
    request["status"] = "completed"
    request["completed_by"] = current_user["employee_id"]
    request["completed_at"] = datetime.now().isoformat()

    logger.info(f"Request {request_id} completed by {current_user['employee_id']}")

    return {
        "message": "Request completed successfully",
        "request": request
    }

@app.put("/api/v1/admin/requests/{request_id}/assign")
async def assign_request(
    request_id: int,
    assignment_data: AssignmentRequest,
    current_user: dict = Depends(get_current_user)
):
    """Assign vehicle and driver to a request - Admin only"""
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Only Admin can assign resources")

    # Find the request
    request = next((r for r in DEMO_REQUESTS if r["id"] == request_id), None)
    if not request:
        raise HTTPException(status_code=404, detail="Request not found")

    if request["status"] != "approved":
        raise HTTPException(status_code=400, detail="Only approved requests can be assigned")

    # Find the vehicle
    vehicle = next((v for v in DEMO_VEHICLES if v["id"] == assignment_data.vehicle_id), None)
    if not vehicle:
        raise HTTPException(status_code=404, detail="Vehicle not found")

    if vehicle["status"] != "available":
        raise HTTPException(status_code=400, detail="Vehicle is not available")

    # Find the driver
    driver = next((d for d in DEMO_DRIVERS if d["id"] == assignment_data.driver_id), None)
    if not driver:
        raise HTTPException(status_code=404, detail="Driver not found")

    if driver["status"] != "active":
        raise HTTPException(status_code=400, detail="Driver is not active")

    # Update request with assignment
    request["assigned_vehicle_id"] = assignment_data.vehicle_id
    request["assigned_driver_id"] = assignment_data.driver_id
    request["assigned_vehicle"] = f"{vehicle['make']} {vehicle['model']} ({vehicle['registration_number']})"
    request["assigned_driver"] = f"{driver['first_name']} {driver['last_name']} ({driver['employee_id']})"
    request["assignment_notes"] = assignment_data.notes
    request["assigned_at"] = datetime.now().isoformat()
    request["assigned_by"] = current_user["employee_id"]

    # Update vehicle and driver status
    vehicle["status"] = "in_use"
    driver["status"] = "on_trip"

    logger.info(f"Request {request_id} assigned vehicle {assignment_data.vehicle_id} and driver {assignment_data.driver_id} by {current_user['employee_id']}")

    return {
        "message": "Request assigned successfully",
        "request": request,
        "assigned_vehicle": vehicle,
        "assigned_driver": driver
    }

# User Management Endpoints (Admin Only)
@app.post("/api/v1/admin/users/")
async def create_user(
    user_data: CreateUserRequest,
    current_user: dict = Depends(get_current_user)
):
    """Create a new user (Employee or Driver) - Admin only"""
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Only Admin can create users")

    # Check if employee_id already exists
    if user_data.employee_id in DEMO_USERS:
        raise HTTPException(status_code=400, detail="Employee ID already exists")

    # Validate role
    if user_data.role not in ["employee", "admin"]:
        raise HTTPException(status_code=400, detail="Role must be 'employee' or 'admin'")

    # Create new user
    new_user_id = len(DEMO_USERS) + 1
    new_user = {
        "id": new_user_id,
        "employee_id": user_data.employee_id,
        "email": user_data.email,
        "password_hash": simple_hash(user_data.password),
        "first_name": user_data.first_name,
        "last_name": user_data.last_name,
        "phone": user_data.phone,
        "department": user_data.department,
        "designation": user_data.designation,
        "role": user_data.role,
        "is_active": True,
        "created_at": datetime.now().isoformat(),
        "created_by": current_user["employee_id"]
    }

    DEMO_USERS[user_data.employee_id] = new_user

    # Return user without password hash
    user_response = {k: v for k, v in new_user.items() if k != "password_hash"}

    logger.info(f"User {current_user['employee_id']} created new user {user_data.employee_id}")

    return {
        "message": "User created successfully",
        "user": user_response
    }

@app.get("/api/v1/admin/users/")
async def get_all_users(current_user: dict = Depends(get_current_user)):
    """Get all users - Admin only"""
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Only Admin can manage users")

    # Return users without password hashes
    users = []
    for user in DEMO_USERS.values():
        user_data = {k: v for k, v in user.items() if k != "password_hash"}
        users.append(user_data)

    return {
        "users": users,
        "total": len(users)
    }

@app.put("/api/v1/admin/users/{employee_id}")
async def update_user(
    employee_id: str,
    user_data: UpdateUserRequest,
    current_user: dict = Depends(get_current_user)
):
    """Update user information - Admin only"""
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Only Admin can update users")

    if employee_id not in DEMO_USERS:
        raise HTTPException(status_code=404, detail="User not found")

    user = DEMO_USERS[employee_id]

    # Update only provided fields
    update_data = user_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        if field == "role" and value not in ["employee", "admin"]:
            raise HTTPException(status_code=400, detail="Role must be 'employee' or 'admin'")
        user[field] = value

    user["updated_at"] = datetime.now().isoformat()
    user["updated_by"] = current_user["employee_id"]

    # Return user without password hash
    user_response = {k: v for k, v in user.items() if k != "password_hash"}

    logger.info(f"User {current_user['employee_id']} updated user {employee_id}")

    return {
        "message": "User updated successfully",
        "user": user_response
    }

@app.delete("/api/v1/admin/users/{employee_id}")
async def delete_user(
    employee_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Delete user - Admin only"""
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Only Admin can delete users")

    if employee_id not in DEMO_USERS:
        raise HTTPException(status_code=404, detail="User not found")

    if employee_id == current_user["employee_id"]:
        raise HTTPException(status_code=400, detail="Cannot delete your own account")

    deleted_user = DEMO_USERS.pop(employee_id)

    logger.info(f"User {current_user['employee_id']} deleted user {employee_id}")

    return {
        "message": "User deleted successfully",
        "deleted_user_id": employee_id
    }

@app.post("/api/v1/admin/users/{employee_id}/reset-password")
async def reset_user_password(
    employee_id: str,
    password_data: PasswordResetRequest,
    current_user: dict = Depends(get_current_user)
):
    """Reset user password - Admin only"""
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Only Admin can reset passwords")

    if employee_id not in DEMO_USERS:
        raise HTTPException(status_code=404, detail="User not found")

    user = DEMO_USERS[employee_id]
    user["password_hash"] = simple_hash(password_data.new_password)
    user["password_reset_at"] = datetime.now().isoformat()
    user["password_reset_by"] = current_user["employee_id"]

    logger.info(f"User {current_user['employee_id']} reset password for user {employee_id}")

    return {
        "message": "Password reset successfully"
    }

@app.put("/api/v1/admin/users/{employee_id}/status")
async def toggle_user_status(
    employee_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Activate/Deactivate user - Admin only"""
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Only Admin can change user status")

    if employee_id not in DEMO_USERS:
        raise HTTPException(status_code=404, detail="User not found")

    if employee_id == current_user["employee_id"]:
        raise HTTPException(status_code=400, detail="Cannot change your own status")

    user = DEMO_USERS[employee_id]
    user["is_active"] = not user["is_active"]
    user["status_changed_at"] = datetime.now().isoformat()
    user["status_changed_by"] = current_user["employee_id"]

    status_text = "activated" if user["is_active"] else "deactivated"

    logger.info(f"User {current_user['employee_id']} {status_text} user {employee_id}")

    return {
        "message": f"User {status_text} successfully",
        "is_active": user["is_active"]
    }

@app.post("/api/v1/ml/route-optimization")
async def optimize_routes(
    optimization_data: dict,
    current_user: dict = Depends(get_current_user)
):
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Only Admin can access ML features")

    # Use real genetic algorithm for route optimization
    requests = optimization_data.get("requests", [])

    try:
        optimization_result = route_optimizer.optimize(requests)

        return {
            "success": True,
            "algorithm": "Genetic Algorithm with Haversine Distance",
            "optimized_route": optimization_result["optimized_route"],
            "total_distance_km": optimization_result["total_distance"],
            "estimated_fuel_liters": optimization_result["fuel_estimate"],
            "efficiency_score": optimization_result["efficiency_score"],
            "optimization_time_ms": optimization_result["optimization_time_ms"],
            "parameters": {
                "population_size": route_optimizer.population_size,
                "generations": route_optimizer.generations,
                "mutation_rate": route_optimizer.mutation_rate
            }
        }
    except Exception as e:
        logger.error(f"Route optimization error: {str(e)}")
        return {
            "success": False,
            "error": "Route optimization failed",
            "fallback_result": {
                "optimized_route": requests,
                "total_distance_km": 50.0,
                "optimization_time_ms": 100
            }
        }

@app.get("/api/v1/analytics/demand-forecast")
async def get_demand_forecast(
    days: int = 7,
    current_user: dict = Depends(get_current_user)
):
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Only Admin can access analytics")

    try:
        # Use real time series analysis for demand forecasting
        forecast_result = demand_forecaster.forecast(days)

        return {
            "success": True,
            "algorithm": "Time Series Analysis with Seasonal Decomposition",
            "forecast": forecast_result["forecast"],
            "model_accuracy": forecast_result["model_accuracy"],
            "processing_time_ms": forecast_result["processing_time_ms"],
            "last_updated": forecast_result["last_updated"],
            "model_details": {
                "historical_data_points": 90,
                "trend_analysis": forecast_result["historical_trend"],
                "seasonal_patterns": "Weekly and monthly patterns detected"
            }
        }
    except Exception as e:
        logger.error(f"Demand forecasting error: {str(e)}")
        return {
            "success": False,
            "error": "Demand forecasting failed",
            "fallback_forecast": [
                {
                    "date": (date.today() + timedelta(days=i+1)).isoformat(),
                    "predicted_requests": 15 + (i % 3) * 2,
                    "confidence": 0.75
                } for i in range(days)
            ]
        }

@app.get("/api/v1/admin/analytics")
async def get_admin_analytics(
    range: str = "7days",
    current_user: dict = Depends(get_current_user)
):
    """Get comprehensive admin analytics"""
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Only Admin can access analytics")

    try:
        # Calculate date range
        if range == "7days":
            days = 7
        elif range == "30days":
            days = 30
        elif range == "90days":
            days = 90
        else:
            days = 7

        # Get demand forecast
        forecast_result = demand_forecaster.forecast(days)

        # Generate analytics data
        total_requests = len(DEMO_REQUESTS)
        pending_requests = len([r for r in DEMO_REQUESTS if r["status"] == "pending"])
        approved_requests = len([r for r in DEMO_REQUESTS if r["status"] == "approved"])
        completed_requests = len([r for r in DEMO_REQUESTS if r["status"] == "completed"])

        # Vehicle utilization
        total_vehicles = len(DEMO_VEHICLES)
        available_vehicles = len([v for v in DEMO_VEHICLES if v["status"] == "available"])

        # Driver performance
        total_drivers = len(DEMO_DRIVERS)
        active_drivers = len([d for d in DEMO_DRIVERS if d["status"] == "active"])

        return {
            "success": True,
            "period": range,
            "summary": {
                "total_requests": total_requests,
                "pending_requests": pending_requests,
                "approved_requests": approved_requests,
                "completed_requests": completed_requests,
                "approval_rate": round((approved_requests + completed_requests) / max(1, total_requests) * 100, 1),
                "completion_rate": round(completed_requests / max(1, approved_requests + completed_requests) * 100, 1)
            },
            "vehicles": {
                "total": total_vehicles,
                "available": available_vehicles,
                "utilization_rate": round((total_vehicles - available_vehicles) / max(1, total_vehicles) * 100, 1)
            },
            "drivers": {
                "total": total_drivers,
                "active": active_drivers,
                "average_rating": round(sum(d["rating"] for d in DEMO_DRIVERS) / max(1, total_drivers), 2)
            },
            "demand_forecast": forecast_result["forecast"][:7],  # Next 7 days
            "request_trends": [
                {"date": "2024-07-08", "requests": 12},
                {"date": "2024-07-09", "requests": 15},
                {"date": "2024-07-10", "requests": 18},
                {"date": "2024-07-11", "requests": 14},
                {"date": "2024-07-12", "requests": 20},
                {"date": "2024-07-13", "requests": 16},
                {"date": "2024-07-14", "requests": total_requests}
            ],
            "trends": {
                "request_growth": "+12.5%",
                "efficiency_improvement": "+8.3%",
                "fuel_savings": "+15.2%"
            }
        }
    except Exception as e:
        logger.error(f"Analytics error: {str(e)}")
        return {
            "success": False,
            "error": "Analytics generation failed",
            "fallback_data": {
                "summary": {"total_requests": 0, "pending_requests": 0},
                "vehicles": {"total": 0, "available": 0},
                "drivers": {"total": 0, "active": 0}
            }
        }

@app.post("/api/v1/ml/vehicle-assignment")
async def optimize_vehicle_assignment(
    assignment_data: dict,
    current_user: dict = Depends(get_current_user)
):
    """ML-based vehicle assignment optimization"""
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Only Admin can access ML features")

    try:
        requests = assignment_data.get("requests", [])
        vehicles = assignment_data.get("vehicles", [])
        drivers = assignment_data.get("drivers", [])

        # Use ML-based assignment optimization
        optimized_assignments = assignment_optimizer.optimize_assignments(requests, vehicles, drivers)

        return {
            "success": True,
            "algorithm": "ML-based Scoring System",
            "optimized_assignments": optimized_assignments,
            "total_assignments": len(optimized_assignments),
            "assignment_efficiency": round(len(optimized_assignments) / max(1, len(requests)), 2),
            "scoring_weights": assignment_optimizer.weights
        }
    except Exception as e:
        logger.error(f"Vehicle assignment optimization error: {str(e)}")
        return {
            "success": False,
            "error": "Vehicle assignment optimization failed",
            "fallback_assignments": []
        }

# Transport (Driver) specific endpoints
@app.get("/api/v1/transport/assigned-trips")
async def get_assigned_trips(current_user: dict = Depends(get_current_user)):
    """Get trips assigned to current transport user - Transport role only"""
    if current_user["role"] != "transport":
        raise HTTPException(status_code=403, detail="Only Transport users can access assigned trips")

    if not check_permission(current_user, "view_assigned_trips"):
        raise HTTPException(status_code=403, detail="Insufficient permissions to view assigned trips")

    # Find requests assigned to this driver
    assigned_requests = []
    for request in DEMO_REQUESTS:
        if request.get("assigned_driver_id") == current_user["id"] and request["status"] in ["approved", "in_progress"]:
            # Get vehicle details
            vehicle = next((v for v in DEMO_VEHICLES if v["id"] == request.get("assigned_vehicle_id")), None)

            assigned_requests.append({
                **request,
                "assigned_vehicle": vehicle,
                "driver_can_start": request["status"] == "approved",
                "driver_can_complete": request["status"] == "in_progress"
            })

    return {
        "assigned_trips": assigned_requests,
        "driver_info": {
            "name": f"{current_user['first_name']} {current_user['last_name']}",
            "license_number": current_user.get("license_number"),
            "rating": current_user.get("rating", 0),
            "status": current_user.get("status", "active")
        }
    }

@app.put("/api/v1/transport/trips/{request_id}/start")
async def start_trip(request_id: int, current_user: dict = Depends(get_current_user)):
    """Start an assigned trip - Transport role only"""
    if current_user["role"] != "transport":
        raise HTTPException(status_code=403, detail="Only Transport users can start trips")

    if not check_permission(current_user, "update_trip_status"):
        raise HTTPException(status_code=403, detail="Insufficient permissions to update trip status")

    # Find the request
    request = next((r for r in DEMO_REQUESTS if r["id"] == request_id), None)
    if not request:
        raise HTTPException(status_code=404, detail="Request not found")

    # Verify assignment
    if request.get("assigned_driver_id") != current_user["id"]:
        raise HTTPException(status_code=403, detail="Trip not assigned to you")

    if request["status"] != "approved":
        raise HTTPException(status_code=400, detail="Only approved trips can be started")

    # Update request status
    request["status"] = "in_progress"
    request["started_at"] = datetime.now().isoformat()
    request["started_by"] = current_user["employee_id"]

    # Start GPS tracking automatically
    try:
        route = get_demo_route(request["origin"], request["destination"])
        tracking_data = gps_tracker.start_trip_tracking(
            trip_id=request_id,
            vehicle_id=request.get("assigned_vehicle_id"),
            driver_id=request.get("assigned_driver_id"),
            route=route
        )
        request["gps_tracking_active"] = True
        request["tracking_id"] = tracking_data.get("trip_id")
    except Exception as e:
        logger.warning(f"Failed to start GPS tracking for trip {request_id}: {e}")
        request["gps_tracking_active"] = False

    logger.info(f"Trip {request_id} started by driver {current_user['employee_id']}")

    return {
        "message": "Trip started successfully",
        "request": request,
        "gps_tracking": request.get("gps_tracking_active", False)
    }

@app.put("/api/v1/transport/trips/{request_id}/complete")
async def complete_trip(request_id: int, completion_data: dict, current_user: dict = Depends(get_current_user)):
    """Complete an assigned trip - Transport role only"""
    if current_user["role"] != "transport":
        raise HTTPException(status_code=403, detail="Only Transport users can complete trips")

    if not check_permission(current_user, "update_trip_status"):
        raise HTTPException(status_code=403, detail="Insufficient permissions to update trip status")

    # Find the request
    request = next((r for r in DEMO_REQUESTS if r["id"] == request_id), None)
    if not request:
        raise HTTPException(status_code=404, detail="Request not found")

    # Verify assignment
    if request.get("assigned_driver_id") != current_user["id"]:
        raise HTTPException(status_code=403, detail="Trip not assigned to you")

    if request["status"] != "in_progress":
        raise HTTPException(status_code=400, detail="Only in-progress trips can be completed")

    # Update request status
    request["status"] = "completed"
    request["completed_at"] = datetime.now().isoformat()
    request["completed_by"] = current_user["employee_id"]
    request["completion_notes"] = completion_data.get("notes", "")
    request["final_odometer"] = completion_data.get("final_odometer")

    # Free up vehicle and driver
    vehicle = next((v for v in DEMO_VEHICLES if v["id"] == request.get("assigned_vehicle_id")), None)
    if vehicle:
        vehicle["status"] = "available"
        vehicle.pop("assigned_to_request", None)

    # Update driver status
    driver = next((u for u in DEMO_USERS.values() if u["id"] == current_user["id"]), None)
    if driver:
        driver["status"] = "active"
        driver.pop("assigned_to_request", None)

    # Stop GPS tracking
    try:
        completed_tracking = gps_tracker.complete_trip(request_id)
        if completed_tracking:
            request["final_tracking_data"] = {
                "total_distance": completed_tracking.get("distance_covered", 0),
                "trip_duration": completed_tracking.get("end_time"),
                "path_recorded": len(completed_tracking.get("path_history", []))
            }
        request["gps_tracking_active"] = False
    except Exception as e:
        logger.warning(f"Failed to stop GPS tracking for trip {request_id}: {e}")

    logger.info(f"Trip {request_id} completed by driver {current_user['employee_id']}")

    return {
        "message": "Trip completed successfully",
        "request": request,
        "tracking_completed": request.get("final_tracking_data") is not None
    }

# GPS Tracking Endpoints
@app.get("/api/v1/gps/trip/{trip_id}")
async def get_trip_gps_tracking(trip_id: int, current_user: dict = Depends(get_current_user)):
    """Get real-time GPS tracking for a trip"""
    # Allow admin, assigned driver, or trip requester to track
    trip_request = next((r for r in DEMO_REQUESTS if r["id"] == trip_id), None)
    if not trip_request:
        raise HTTPException(status_code=404, detail="Trip not found")

    # Check permissions
    if (current_user["role"] == "admin" or
        (current_user["role"] == "transport" and trip_request.get("assigned_driver_id") == current_user["id"]) or
        (current_user["role"] == "employee" and trip_request["user_id"] == current_user["id"])):

        tracking_data = gps_tracker.get_trip_tracking(trip_id)
        if tracking_data:
            return {
                "success": True,
                "tracking": tracking_data,
                "permissions": {
                    "can_view_location": True,
                    "can_view_path": current_user["role"] in ["admin", "transport"],
                    "can_view_eta": True
                }
            }
        else:
            return {"success": False, "message": "Trip tracking not active"}
    else:
        raise HTTPException(status_code=403, detail="Insufficient permissions to track this trip")

@app.get("/api/v1/gps/vehicle/{vehicle_id}")
async def get_vehicle_location(vehicle_id: int, current_user: dict = Depends(get_current_user)):
    """Get current location of a vehicle - Admin only"""
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Only Admin can track vehicle locations")

    location_data = gps_tracker.get_vehicle_location(vehicle_id)
    if location_data:
        return {
            "success": True,
            "vehicle_location": location_data
        }
    else:
        return {
            "success": False,
            "message": "Vehicle location not available"
        }

@app.get("/api/v1/gps/all-active-trips")
async def get_all_active_trips_gps(current_user: dict = Depends(get_current_user)):
    """Get GPS tracking for all active trips - Admin only"""
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Only Admin can view all active trips")

    active_trips = gps_tracker.get_all_active_trips()
    return {
        "success": True,
        "active_trips": active_trips,
        "total_active": len(active_trips)
    }

@app.post("/api/v1/gps/simulate/{trip_id}")
async def start_gps_simulation(trip_id: int, current_user: dict = Depends(get_current_user)):
    """Start GPS simulation for a trip - Admin/Driver only"""
    if current_user["role"] not in ["admin", "transport"]:
        raise HTTPException(status_code=403, detail="Only Admin or Transport users can start GPS simulation")

    trip_request = next((r for r in DEMO_REQUESTS if r["id"] == trip_id), None)
    if not trip_request:
        raise HTTPException(status_code=404, detail="Trip not found")

    if trip_request["status"] != "in_progress":
        raise HTTPException(status_code=400, detail="Trip must be in progress to start GPS tracking")

    # Get route data
    route = get_demo_route(trip_request["origin"], trip_request["destination"])

    # Start GPS tracking
    tracking_data = gps_tracker.start_trip_tracking(
        trip_id=trip_id,
        vehicle_id=trip_request.get("assigned_vehicle_id"),
        driver_id=trip_request.get("assigned_driver_id"),
        route=route
    )

    return {
        "success": True,
        "message": "GPS tracking started",
        "tracking": tracking_data
    }

@app.post("/api/v1/gps/update-location/{trip_id}")
async def update_real_location(trip_id: int, location_data: dict, current_user: dict = Depends(get_current_user)):
    """Update real GPS location from device - Driver/Admin only"""
    if current_user["role"] not in ["admin", "transport"]:
        raise HTTPException(status_code=403, detail="Only Admin or Transport users can update GPS location")

    trip_request = next((r for r in DEMO_REQUESTS if r["id"] == trip_id), None)
    if not trip_request:
        raise HTTPException(status_code=404, detail="Trip not found")

    # Verify driver assignment for transport users
    if current_user["role"] == "transport" and trip_request.get("assigned_driver_id") != current_user["id"]:
        raise HTTPException(status_code=403, detail="Trip not assigned to you")

    # Update GPS tracker with real location
    tracking_data = gps_tracker.update_location(
        trip_id=trip_id,
        latitude=location_data["latitude"],
        longitude=location_data["longitude"],
        speed=location_data.get("speed", 0),
        heading=location_data.get("heading", 0)
    )

    if tracking_data:
        # Store additional metadata
        tracking_data["device_accuracy"] = location_data.get("accuracy", 0)
        tracking_data["device_timestamp"] = location_data.get("timestamp")
        tracking_data["real_gps"] = True

        return {
            "success": True,
            "message": "Location updated successfully",
            "tracking": tracking_data
        }
    else:
        return {
            "success": False,
            "message": "Trip tracking not active"
        }

# Initialize demo users at module level
init_demo_users()

# WebSocket endpoint for real-time updates
@app.websocket("/ws/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: str, token: str = None):
    """WebSocket endpoint for real-time updates"""
    try:
        # Verify token
        if token:
            try:
                payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
                if payload.get("sub") != user_id:
                    await websocket.close(code=1008, reason="Invalid token")
                    return
            except JWTError:
                await websocket.close(code=1008, reason="Invalid token")
                return

        await manager.connect(websocket, user_id)

        # Send welcome message
        await manager.send_personal_message({
            "type": "connected",
            "payload": {
                "message": "Connected to HAL Transport System",
                "user_id": user_id,
                "timestamp": datetime.now().isoformat()
            }
        }, user_id)

        while True:
            # Receive messages from client
            data = await websocket.receive_text()
            try:
                message = json.loads(data)
                await handle_websocket_message(user_id, message)
            except json.JSONDecodeError:
                await manager.send_personal_message({
                    "type": "error",
                    "payload": {"message": "Invalid JSON format"}
                }, user_id)

    except WebSocketDisconnect:
        manager.disconnect(user_id)
    except Exception as e:
        logger.error(f"WebSocket error for user {user_id}: {e}")
        manager.disconnect(user_id)

async def handle_websocket_message(user_id: str, message: dict):
    """Handle incoming WebSocket messages"""
    message_type = message.get("type")
    payload = message.get("payload", {})

    if message_type == "join_trip":
        trip_id = str(payload.get("tripId"))
        manager.join_trip_room(user_id, trip_id)

    elif message_type == "leave_trip":
        trip_id = str(payload.get("tripId"))
        manager.leave_trip_room(user_id, trip_id)

    elif message_type == "gps_update":
        # Handle GPS location updates
        trip_id = payload.get("tripId")
        location = payload.get("location")

        if trip_id and location:
            # Broadcast to all users in trip room
            await manager.broadcast_to_trip({
                "type": "gps_update",
                "payload": {
                    "tripId": trip_id,
                    "location": location,
                    "timestamp": datetime.now().isoformat(),
                    "userId": user_id
                }
            }, str(trip_id))

# ============================================================================
# PHASE 2: ADVANCED TRANSPORT FEATURES API ENDPOINTS
# ============================================================================

@app.get("/api/v1/admin/route-optimization/{request_id}")
async def get_route_optimization(request_id: int, current_user: dict = Depends(get_current_user)):
    """Get route optimization for a specific request"""
    if not check_permission(current_user, "admin"):
        raise HTTPException(status_code=403, detail="Admin access required")

    # Get request details
    request = next((r for r in DEMO_REQUESTS if r["id"] == request_id), None)
    if not request:
        raise HTTPException(status_code=404, detail="Request not found")

    # Get optimized route
    optimized_route = await route_optimizer.optimize_single_route(
        request["origin"],
        request["destination"]
    )

    return {
        "success": True,
        "request_id": request_id,
        "route_optimization": optimized_route
    }

@app.get("/api/v1/admin/vehicle-maintenance/{vehicle_id}")
async def get_vehicle_maintenance_report(
    vehicle_id: int,
    current_user: dict = Depends(get_current_user)
):
    """Get comprehensive vehicle maintenance report"""
    if not check_permission(current_user, "admin"):
        raise HTTPException(status_code=403, detail="Admin access required")

    # Generate maintenance report
    maintenance_report = await vehicle_maintenance_service.generate_maintenance_report(vehicle_id)

    return {
        "success": True,
        "maintenance_report": maintenance_report
    }

@app.get("/api/v1/admin/driver-analytics/{driver_id}")
async def get_driver_performance_analytics(
    driver_id: int,
    period_days: int = 30,
    current_user: dict = Depends(get_current_user)
):
    """Get comprehensive driver performance analytics"""
    if not check_permission(current_user, "admin"):
        raise HTTPException(status_code=403, detail="Admin access required")

    # Generate performance report
    performance_report = await driver_analytics_service.generate_performance_report(
        driver_id, period_days
    )

    return {
        "success": True,
        "performance_report": performance_report
    }

@app.get("/api/v1/admin/fleet-analytics")
async def get_fleet_analytics(current_user: dict = Depends(get_current_user)):
    """Get comprehensive fleet analytics dashboard"""
    if not check_permission(current_user, "admin"):
        raise HTTPException(status_code=403, detail="Admin access required")

    # Generate fleet-wide analytics
    fleet_analytics = {
        "total_vehicles": len(DEMO_VEHICLES),
        "active_vehicles": len([v for v in DEMO_VEHICLES if v["status"] == "active"]),
        "total_drivers": len(DEMO_DRIVERS),
        "active_drivers": len([d for d in DEMO_DRIVERS if d["status"] == "available"]),
        "route_optimization_savings": {
            "time_saved_minutes": random.randint(120, 300),
            "fuel_saved_liters": random.randint(50, 150),
            "cost_saved_rupees": random.randint(5000, 15000)
        },
        "maintenance_alerts": random.randint(2, 8),
        "fuel_efficiency_average": round(random.uniform(14.5, 18.2), 1),
        "driver_performance_average": round(random.uniform(78.5, 89.2), 1)
    }

    return {
        "success": True,
        "fleet_analytics": fleet_analytics,
        "generated_at": datetime.now().isoformat()
    }

# Start GPS simulation background task
@app.on_event("startup")
async def startup_event():
    """Start background tasks on application startup"""
    import asyncio
    asyncio.create_task(simulate_all_trips())

if __name__ == "__main__":
    import uvicorn

    print("🚀 Starting HAL Transport Management System - PROFESSIONAL EDITION")
    print("📋 Three-Tier Role System:")
    print("   🔧 Admin (Full Control): HAL001 / admin123")
    print("      • Approve requests • Assign vehicles/drivers • Safety override")
    print("   🚗 Transport (Driver): HAL002 / driver123 or HAL004 / transport123")
    print("      • View assigned trips • Start/complete trips • GPS tracking")
    print("   👤 Employee (Passenger): HAL003 / employee123 or HAL005 / emp123")
    print("      • Create requests • Track trips • View status")
    print("")
    print("🌟 PHASE 2 FEATURES ACTIVE:")
    print("   🗺️  Route Optimization with Real Traffic Data")
    print("   🤖 AI-Powered Automated Scheduling")
    print("   🔧 Predictive Vehicle Maintenance Tracking")
    print("   ⛽ Advanced Fuel Management System")
    print("   📊 Comprehensive Driver Performance Analytics")
    print("")
    print("📖 API Documentation: http://localhost:8000/docs")
    print("🌐 Frontend: http://localhost:3000")
    print("🔌 WebSocket: ws://localhost:8000/ws/{user_id}")

    uvicorn.run(
        "demo_app:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
