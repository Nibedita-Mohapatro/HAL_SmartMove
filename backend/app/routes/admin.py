from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func, desc
from typing import Optional, List
from datetime import datetime, date, time
from app.database import get_db
from app.auth import get_admin_user, get_current_active_user
from app.models.user import User
from app.models.transport_request import TransportRequest, RequestStatus, Priority
from app.models.vehicle_assignment import VehicleAssignment, AssignmentStatus
from app.models.vehicle import Vehicle
from app.models.driver import Driver
from app.schemas.transport_request import RequestApproval, RequestRejection
from app.auth import get_password_hash
from app.models.user import UserRole
from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/admin", tags=["Admin"])


@router.get("/dashboard")
async def get_dashboard_stats(
    admin_user: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """
    Get dashboard statistics for admin
    """
    today = date.today()

    # Basic counts
    total_requests_today = db.query(TransportRequest).filter(
        func.date(TransportRequest.created_at) == today
    ).count()

    pending_requests = db.query(TransportRequest).filter(
        TransportRequest.status == RequestStatus.PENDING
    ).count()

    approved_requests_today = db.query(TransportRequest).filter(
        and_(
            func.date(TransportRequest.created_at) == today,
            TransportRequest.status == RequestStatus.APPROVED
        )
    ).count()

    completed_trips_today = db.query(VehicleAssignment).filter(
        and_(
            func.date(VehicleAssignment.assignment_date) == today,
            VehicleAssignment.status == AssignmentStatus.COMPLETED
        )
    ).count()

    active_vehicles = db.query(Vehicle).filter(Vehicle.is_active == True).count()
    available_drivers = db.query(Driver).filter(
        and_(Driver.is_active == True, Driver.is_available == True)
    ).count()

    # Real-time resource availability counts
    # Available vehicles: active vehicles not currently assigned to active trips
    assigned_vehicle_ids = db.query(VehicleAssignment.vehicle_id).filter(
        VehicleAssignment.status.in_([AssignmentStatus.ASSIGNED, AssignmentStatus.IN_PROGRESS])
    ).subquery()

    available_vehicles = db.query(Vehicle).filter(
        and_(
            Vehicle.is_active == True,
            ~Vehicle.id.in_(assigned_vehicle_ids)
        )
    ).count()

    # Available drivers: active and available drivers not currently assigned to active trips
    assigned_driver_ids = db.query(VehicleAssignment.driver_id).filter(
        VehicleAssignment.status.in_([AssignmentStatus.ASSIGNED, AssignmentStatus.IN_PROGRESS])
    ).subquery()

    available_drivers_real = db.query(Driver).filter(
        and_(
            Driver.is_active == True,
            Driver.is_available == True,
            ~Driver.id.in_(assigned_driver_ids)
        )
    ).count()

    # Recent requests (last 7 days)
    from datetime import timedelta
    week_ago = today - timedelta(days=7)

    daily_requests = []
    for i in range(7):
        day = week_ago + timedelta(days=i)
        count = db.query(TransportRequest).filter(
            func.date(TransportRequest.created_at) == day
        ).count()
        daily_requests.append(count)

    # Popular routes
    popular_routes = db.query(
        TransportRequest.origin,
        TransportRequest.destination,
        func.count(TransportRequest.id).label('count')
    ).filter(
        TransportRequest.created_at >= week_ago
    ).group_by(
        TransportRequest.origin, TransportRequest.destination
    ).order_by(desc('count')).limit(5).all()

    routes_data = []
    total_route_requests = sum([route.count for route in popular_routes])

    for route in popular_routes:
        percentage = (route.count / total_route_requests * 100) if total_route_requests > 0 else 0
        routes_data.append({
            "route": f"{route.origin} to {route.destination}",
            "count": route.count,
            "percentage": round(percentage, 1)
        })

    return {
        "total_requests_today": total_requests_today,
        "pending_requests": pending_requests,
        "approved_requests_today": approved_requests_today,
        "completed_trips_today": completed_trips_today,
        "active_vehicles": active_vehicles,
        "available_drivers": available_drivers,
        "summary": {
            "total_requests_today": total_requests_today,
            "pending_requests": pending_requests,
            "approved_requests": approved_requests_today,
            "completed_trips": completed_trips_today,
            "active_vehicles": active_vehicles,
            "available_drivers": available_drivers
        },
        "resource_availability": {
            "available_drivers": available_drivers_real,
            "available_vehicles": available_vehicles,
            "pending_requests": pending_requests
        },
        "trends": {
            "requests_last_7_days": daily_requests,
            "popular_routes": routes_data
        }
    }


@router.get("/resource-availability")
async def get_resource_availability(
    admin_user: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """
    Get real-time resource availability counts for dashboard counters
    """
    # Available drivers: active and available drivers not currently assigned to active trips
    assigned_driver_ids = db.query(VehicleAssignment.driver_id).filter(
        VehicleAssignment.status.in_([AssignmentStatus.ASSIGNED, AssignmentStatus.IN_PROGRESS])
    ).subquery()

    available_drivers = db.query(Driver).filter(
        and_(
            Driver.is_active == True,
            Driver.is_available == True,
            ~Driver.id.in_(assigned_driver_ids)
        )
    ).count()

    # Available vehicles: active vehicles not currently assigned to active trips
    assigned_vehicle_ids = db.query(VehicleAssignment.vehicle_id).filter(
        VehicleAssignment.status.in_([AssignmentStatus.ASSIGNED, AssignmentStatus.IN_PROGRESS])
    ).subquery()

    available_vehicles = db.query(Vehicle).filter(
        and_(
            Vehicle.is_active == True,
            ~Vehicle.id.in_(assigned_vehicle_ids)
        )
    ).count()

    # Pending requests: transport requests awaiting assignment
    pending_requests = db.query(TransportRequest).filter(
        TransportRequest.status == RequestStatus.PENDING
    ).count()

    # Calculate availability status for color coding
    total_drivers = db.query(Driver).filter(Driver.is_active == True).count()
    total_vehicles = db.query(Vehicle).filter(Vehicle.is_active == True).count()

    driver_availability_percentage = (available_drivers / total_drivers * 100) if total_drivers > 0 else 0
    vehicle_availability_percentage = (available_vehicles / total_vehicles * 100) if total_vehicles > 0 else 0

    # Determine status levels for color coding
    def get_availability_status(percentage):
        if percentage >= 70:
            return "good"  # Green
        elif percentage >= 30:
            return "warning"  # Orange
        else:
            return "critical"  # Red

    return {
        "available_drivers": available_drivers,
        "available_vehicles": available_vehicles,
        "pending_requests": pending_requests,
        "total_drivers": total_drivers,
        "total_vehicles": total_vehicles,
        "driver_availability_percentage": round(driver_availability_percentage, 1),
        "vehicle_availability_percentage": round(vehicle_availability_percentage, 1),
        "driver_status": get_availability_status(driver_availability_percentage),
        "vehicle_status": get_availability_status(vehicle_availability_percentage),
        "pending_status": "critical" if pending_requests > 10 else "warning" if pending_requests > 5 else "good"
    }


@router.get("/requests")
async def get_all_requests(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    status: Optional[RequestStatus] = None,
    date_from: Optional[date] = None,
    date_to: Optional[date] = None,
    department: Optional[str] = None,
    priority: Optional[Priority] = None,
    admin_user: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """
    Get all transport requests for admin review
    """
    query = db.query(TransportRequest).join(User, TransportRequest.user_id == User.id)

    # Apply filters
    if status:
        query = query.filter(TransportRequest.status == status)
    if date_from:
        query = query.filter(TransportRequest.request_date >= date_from)
    if date_to:
        query = query.filter(TransportRequest.request_date <= date_to)
    if department:
        query = query.filter(User.department.ilike(f"%{department}%"))
    if priority:
        query = query.filter(TransportRequest.priority == priority)

    # Get total count
    total = query.count()

    # Apply pagination and ordering
    requests = query.order_by(
        TransportRequest.created_at.desc()
    ).offset((page - 1) * limit).limit(limit).all()

    # Format response
    request_responses = []
    for request in requests:
        request_dict = request.to_dict()
        request_dict['user'] = {
            "id": request.user.id,
            "name": request.user.full_name,
            "employee_id": request.user.employee_id,
            "department": request.user.department,
            "phone": request.user.phone
        }

        if request.approver:
            request_dict['approver'] = {
                "id": request.approver.id,
                "name": request.approver.full_name,
                "employee_id": request.approver.employee_id
            }

        # Get vehicle assignment if exists
        assignment = db.query(VehicleAssignment).filter(
            VehicleAssignment.request_id == request.id
        ).first()

        if assignment:
            request_dict['vehicle_assignment'] = {
                **assignment.to_dict(),
                'vehicle': assignment.vehicle.to_dict(),
                'driver': assignment.driver.to_dict()
            }

        request_responses.append(request_dict)

    return {
        "requests": request_responses,
        "pagination": {
            "page": page,
            "limit": limit,
            "total": total,
            "pages": (total + limit - 1) // limit
        }
    }


@router.put("/requests/{request_id}/approve-with-assignment")
async def approve_request_with_assignment(
    request_id: int,
    approval_data: RequestApproval,
    admin_user: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """
    Approve transport request and assign vehicle/driver
    """
    # Get the request
    request = db.query(TransportRequest).filter(TransportRequest.id == request_id).first()
    if not request:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Request not found"
        )

    if request.status != RequestStatus.PENDING:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Can only approve pending requests"
        )

    # Verify vehicle exists and is available
    vehicle = db.query(Vehicle).filter(
        and_(Vehicle.id == approval_data.vehicle_id, Vehicle.is_active == True)
    ).first()
    if not vehicle:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Vehicle not found or inactive"
        )

    # Verify driver exists and is available
    driver = db.query(Driver).filter(
        and_(
            Driver.id == approval_data.driver_id,
            Driver.is_active == True,
            Driver.is_available == True
        )
    ).first()
    if not driver:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Driver not found or unavailable"
        )

    # Check for conflicts (same vehicle/driver at same time)
    conflict_check = db.query(VehicleAssignment).join(TransportRequest).filter(
        and_(
            or_(
                VehicleAssignment.vehicle_id == approval_data.vehicle_id,
                VehicleAssignment.driver_id == approval_data.driver_id
            ),
            TransportRequest.request_date == request.request_date,
            VehicleAssignment.status.in_([AssignmentStatus.ASSIGNED, AssignmentStatus.IN_PROGRESS]),
            # Check time overlap
            or_(
                and_(
                    VehicleAssignment.estimated_departure <= approval_data.estimated_departure,
                    VehicleAssignment.estimated_arrival >= approval_data.estimated_departure
                ),
                and_(
                    VehicleAssignment.estimated_departure <= approval_data.estimated_arrival,
                    VehicleAssignment.estimated_arrival >= approval_data.estimated_arrival
                )
            )
        )
    ).first()

    if conflict_check:
        # Get alternative suggestions
        alternative_vehicles = db.query(Vehicle).filter(
            and_(
                Vehicle.is_active == True,
                Vehicle.id != approval_data.vehicle_id
            )
        ).limit(3).all()

        alternative_drivers = db.query(Driver).filter(
            and_(
                Driver.is_active == True,
                Driver.is_available == True,
                Driver.id != approval_data.driver_id
            )
        ).limit(3).all()

        # Check which resource is conflicted
        conflicted_resource = "vehicle" if conflict_check.vehicle_id == approval_data.vehicle_id else "driver"
        if conflict_check.vehicle_id == approval_data.vehicle_id and conflict_check.driver_id == approval_data.driver_id:
            conflicted_resource = "both vehicle and driver"

        suggestions = {
            "alternative_vehicles": [{"id": v.id, "number": v.vehicle_number, "type": v.vehicle_type.value} for v in alternative_vehicles],
            "alternative_drivers": [{"id": d.id, "name": f"{d.first_name} {d.last_name}", "employee_id": d.employee_id} for d in alternative_drivers],
            "conflicted_resource": conflicted_resource,
            "conflict_time": f"{conflict_check.estimated_departure} - {conflict_check.estimated_arrival}"
        }

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "message": f"The selected {conflicted_resource} is already assigned during {conflict_check.estimated_departure} - {conflict_check.estimated_arrival}",
                "suggestions": suggestions
            }
        )

    # Approve the request
    request.status = RequestStatus.APPROVED
    request.approved_by = admin_user.id
    request.approved_at = datetime.utcnow()

    # Create vehicle assignment
    assignment = VehicleAssignment(
        request_id=request_id,
        vehicle_id=approval_data.vehicle_id,
        driver_id=approval_data.driver_id,
        assigned_by=admin_user.id,
        assignment_date=request.request_date,
        estimated_departure=approval_data.estimated_departure,
        estimated_arrival=approval_data.estimated_arrival,
        notes=approval_data.notes
    )

    # Update driver availability to false when assigned
    assigned_driver = db.query(Driver).filter(Driver.id == approval_data.driver_id).first()
    if assigned_driver:
        assigned_driver.is_available = False

    db.add(assignment)
    db.commit()
    db.refresh(assignment)

    logger.info(f"Admin {admin_user.employee_id} approved request {request_id}")

    return {
        "message": "Request approved successfully",
        "assignment_id": assignment.id
    }


@router.put("/requests/{request_id}/reject-with-reason")
async def reject_request_with_reason(
    request_id: int,
    rejection_data: RequestRejection,
    admin_user: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """
    Reject transport request
    """
    request = db.query(TransportRequest).filter(TransportRequest.id == request_id).first()
    if not request:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Request not found"
        )

    if request.status != RequestStatus.PENDING:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Can only reject pending requests"
        )

    # Reject the request
    request.status = RequestStatus.REJECTED
    request.approved_by = admin_user.id
    request.approved_at = datetime.utcnow()
    request.rejection_reason = rejection_data.rejection_reason

    db.commit()

    logger.info(f"Admin {admin_user.employee_id} rejected request {request_id}")

    return {"message": "Request rejected successfully"}

# Unified request action endpoints for frontend compatibility
@router.put("/requests/{request_id}/approve")
async def approve_request_unified(
    request_id: int,
    admin_user: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """
    Approve request (unified endpoint for frontend)
    """
    request = db.query(TransportRequest).filter(TransportRequest.id == request_id).first()
    if not request:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Request not found"
        )

    if request.status != RequestStatus.PENDING:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Can only approve pending requests"
        )

    request.status = RequestStatus.APPROVED
    request.approved_by = admin_user.id
    request.approved_at = datetime.utcnow()

    db.commit()
    logger.info(f"Admin {admin_user.employee_id} approved request {request_id}")

    return {"message": "Request approved successfully", "status": "approved"}


@router.put("/requests/{request_id}/reject")
async def reject_request_unified(
    request_id: int,
    admin_user: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """
    Reject request (unified endpoint for frontend)
    """
    request = db.query(TransportRequest).filter(TransportRequest.id == request_id).first()
    if not request:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Request not found"
        )

    if request.status != RequestStatus.PENDING:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Can only reject pending requests"
        )

    request.status = RequestStatus.REJECTED
    request.approved_by = admin_user.id
    request.approved_at = datetime.utcnow()
    request.rejection_reason = "Rejected by admin"

    db.commit()
    logger.info(f"Admin {admin_user.employee_id} rejected request {request_id}")

    return {"message": "Request rejected successfully", "status": "rejected"}


@router.put("/requests/{request_id}/cancel")
async def cancel_request_unified(
    request_id: int,
    admin_user: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """
    Cancel request (unified endpoint for frontend)
    """
    request = db.query(TransportRequest).filter(TransportRequest.id == request_id).first()
    if not request:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Request not found"
        )

    if request.status in [RequestStatus.COMPLETED, RequestStatus.CANCELLED]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot cancel completed or already cancelled request"
        )

    request.status = RequestStatus.CANCELLED

    # Cancel vehicle assignment if exists and restore driver availability
    assignment = db.query(VehicleAssignment).filter(VehicleAssignment.request_id == request_id).first()
    if assignment:
        assignment.status = AssignmentStatus.CANCELLED
        # Restore driver availability when assignment is cancelled
        if assignment.driver:
            assignment.driver.is_available = True

    db.commit()
    logger.info(f"Admin {admin_user.employee_id} cancelled request {request_id}")

    return {"message": "Request cancelled successfully", "status": "cancelled"}


@router.get("/requests/{request_id}")
async def get_request_details(
    request_id: int,
    admin_user: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """
    Get detailed information about a specific transport request
    """
    request = db.query(TransportRequest).filter(TransportRequest.id == request_id).first()
    if not request:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Request not found"
        )

    # Build request details
    request_dict = request.to_dict()

    # Add user information
    if request.user:
        request_dict['user'] = {
            "id": request.user.id,
            "name": request.user.full_name,
            "employee_id": request.user.employee_id,
            "department": request.user.department,
            "phone": request.user.phone
        }

    if request.approver:
        request_dict['approver'] = {
            "id": request.approver.id,
            "name": request.approver.full_name,
            "employee_id": request.approver.employee_id
        }

    # Get vehicle assignment if exists
    assignment = db.query(VehicleAssignment).filter(
        VehicleAssignment.request_id == request.id
    ).first()

    if assignment:
        request_dict['assignment'] = {
            "id": assignment.id,
            "vehicle": {
                "id": assignment.vehicle.id,
                "vehicle_number": assignment.vehicle.vehicle_number,
                "vehicle_type": assignment.vehicle.vehicle_type.value,
                "capacity": assignment.vehicle.capacity
            } if assignment.vehicle else None,
            "driver": {
                "id": assignment.driver.id,
                "name": f"{assignment.driver.first_name} {assignment.driver.last_name}",
                "employee_id": assignment.driver.employee_id,
                "phone": assignment.driver.phone
            } if assignment.driver else None,
            "status": assignment.status.value,
            "assignment_date": assignment.assignment_date.isoformat() if assignment.assignment_date else None,
            "estimated_departure": assignment.estimated_departure.isoformat() if assignment.estimated_departure else None,
            "estimated_arrival": assignment.estimated_arrival.isoformat() if assignment.estimated_arrival else None,
            "notes": assignment.notes
        }

    return request_dict


@router.get("/requests/{request_id}/available-resources")
async def get_available_resources(
    request_id: int,
    admin_user: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """
    Get available vehicles and drivers for a specific request
    """
    # Get the request
    request = db.query(TransportRequest).filter(TransportRequest.id == request_id).first()
    if not request:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Request not found"
        )

    # Get all active vehicles
    all_vehicles = db.query(Vehicle).filter(Vehicle.is_active == True).all()

    # Get all active and available drivers
    all_drivers = db.query(Driver).filter(
        and_(Driver.is_active == True, Driver.is_available == True)
    ).all()

    # Check which vehicles and drivers are available for this request's time slot
    available_vehicles = []
    available_drivers = []

    for vehicle in all_vehicles:
        # Check if vehicle is busy at request time
        conflict = db.query(VehicleAssignment).join(TransportRequest).filter(
            and_(
                VehicleAssignment.vehicle_id == vehicle.id,
                TransportRequest.request_date == request.request_date,
                VehicleAssignment.status.in_([AssignmentStatus.ASSIGNED, AssignmentStatus.IN_PROGRESS])
            )
        ).first()

        if not conflict:
            available_vehicles.append({
                "id": vehicle.id,
                "vehicle_number": vehicle.vehicle_number,
                "vehicle_type": vehicle.vehicle_type.value,
                "capacity": vehicle.capacity,
                "fuel_type": vehicle.fuel_type.value
            })

    for driver in all_drivers:
        # Check if driver is busy at request time
        conflict = db.query(VehicleAssignment).join(TransportRequest).filter(
            and_(
                VehicleAssignment.driver_id == driver.id,
                TransportRequest.request_date == request.request_date,
                VehicleAssignment.status.in_([AssignmentStatus.ASSIGNED, AssignmentStatus.IN_PROGRESS])
            )
        ).first()

        if not conflict:
            available_drivers.append({
                "id": driver.id,
                "employee_id": driver.employee_id,
                "name": f"{driver.first_name} {driver.last_name}",
                "license_number": driver.license_number,
                "phone": driver.phone
            })

    return {
        "request_id": request_id,
        "request_date": request.request_date.isoformat(),
        "request_time": request.request_time.isoformat(),
        "available_vehicles": available_vehicles,
        "available_drivers": available_drivers,
        "total_available_vehicles": len(available_vehicles),
        "total_available_drivers": len(available_drivers)
    }


@router.get("/requests/{request_id}/assignment-options")
async def get_assignment_options(
    request_id: int,
    admin_user: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """
    Get assignment options (vehicles and drivers) for a specific request
    This is an alias for available-resources to match frontend expectations
    """
    return await get_available_resources(request_id, admin_user, db)


# User Management Schemas
class UserCreate(BaseModel):
    employee_id: str
    email: EmailStr
    first_name: str
    last_name: str
    password: str
    phone: str
    department: str
    designation: str
    role: str = "employee"


class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone: Optional[str] = None
    department: Optional[str] = None
    designation: Optional[str] = None
    role: Optional[str] = None
    is_active: Optional[bool] = None


# User Management Endpoints
@router.post("/users/")
async def create_user(
    user_data: UserCreate,
    admin_user: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """
    Create new user (Admin only)
    """
    # Check if employee_id already exists
    existing_user = db.query(User).filter(User.employee_id == user_data.employee_id).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Employee ID already exists"
        )

    # Check if email already exists
    existing_email = db.query(User).filter(User.email == user_data.email).first()
    if existing_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already exists"
        )

    # Validate and convert role
    role_mapping = {
        "employee": UserRole.EMPLOYEE,
        "admin": UserRole.ADMIN,
        "super_admin": UserRole.SUPER_ADMIN,
        "transport": UserRole.TRANSPORT
    }

    if user_data.role not in role_mapping:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Role must be one of: {', '.join(role_mapping.keys())}"
        )

    user_role = role_mapping[user_data.role]

    # Create new user
    hashed_password = get_password_hash(user_data.password)

    new_user = User(
        employee_id=user_data.employee_id,
        email=user_data.email,
        first_name=user_data.first_name,
        last_name=user_data.last_name,
        password_hash=hashed_password,
        phone=user_data.phone,
        department=user_data.department,
        designation=user_data.designation,
        role=user_role,
        is_active=True,
        created_at=datetime.utcnow()
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    logger.info(f"Admin {admin_user.employee_id} created user {new_user.employee_id}")

    return {
        "message": "User created successfully",
        "id": new_user.id,
        "user": new_user.to_dict()
    }


@router.get("/users/")
async def get_all_users(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    role: Optional[str] = None,
    is_active: Optional[bool] = None,
    admin_user: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """
    Get all users (Admin only)
    """
    query = db.query(User)

    # Apply filters
    if role:
        query = query.filter(User.role == UserRole(role))
    if is_active is not None:
        query = query.filter(User.is_active == is_active)

    # Get total count
    total = query.count()

    # Apply pagination
    offset = (page - 1) * limit
    users = query.offset(offset).limit(limit).all()

    return {
        "users": [user.to_dict() for user in users],
        "pagination": {
            "page": page,
            "limit": limit,
            "total": total,
            "pages": (total + limit - 1) // limit
        }
    }


@router.get("/users/{user_id}")
async def get_user(
    user_id: int,
    admin_user: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """
    Get specific user (Admin only)
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    return {"user": user.to_dict()}


@router.put("/users/{user_id}")
async def update_user(
    user_id: int,
    user_data: UserUpdate,
    admin_user: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """
    Update user (Admin only)
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    # Update only provided fields
    update_data = user_data.dict(exclude_unset=True)

    for field, value in update_data.items():
        if field == "role":
            role_mapping = {
                "employee": UserRole.EMPLOYEE,
                "admin": UserRole.ADMIN,
                "super_admin": UserRole.SUPER_ADMIN,
                "transport": UserRole.TRANSPORT
            }
            if value not in role_mapping:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Role must be one of: {', '.join(role_mapping.keys())}"
                )
            setattr(user, field, role_mapping[value])
        else:
            setattr(user, field, value)

    db.commit()
    db.refresh(user)

    logger.info(f"Admin {admin_user.employee_id} updated user {user.employee_id}")

    return {
        "message": "User updated successfully",
        "user": user.to_dict()
    }


@router.delete("/users/{user_id}")
async def delete_user(
    user_id: int,
    admin_user: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """
    Delete user (Admin only)
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    # Prevent admin from deleting themselves
    if user.id == admin_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete your own account"
        )

    # Soft delete by setting is_active to False
    user.is_active = False
    db.commit()

    logger.info(f"Admin {admin_user.employee_id} deleted user {user.employee_id}")

    return {"message": "User deleted successfully"}


@router.delete("/users/by-employee-id/{employee_id}")
async def delete_user_by_employee_id(
    employee_id: str,
    admin_user: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """
    Delete user by employee ID (Admin only)
    """
    user = db.query(User).filter(User.employee_id == employee_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    # Prevent admin from deleting themselves
    if user.id == admin_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete your own account"
        )

    # Soft delete by setting is_active to False
    user.is_active = False
    db.commit()

    logger.info(f"Admin {admin_user.employee_id} deleted user {user.employee_id}")

    return {"message": "User deleted successfully"}


@router.post("/users/{user_id}/reset-password")
async def reset_user_password(
    user_id: int,
    new_password: str,
    admin_user: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """
    Reset user password (Admin only)
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    # Update password
    user.password_hash = get_password_hash(new_password)
    db.commit()

    logger.info(f"Admin {admin_user.employee_id} reset password for user {user.employee_id}")

    return {"message": "Password reset successfully"}


@router.put("/users/{user_id}/deactivate")
async def deactivate_user(
    user_id: int,
    admin_user: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """
    Deactivate user (Admin only)
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    # Prevent admin from deactivating themselves
    if user.id == admin_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot deactivate your own account"
        )

    # Deactivate user
    user.is_active = False
    db.commit()

    logger.info(f"Admin {admin_user.employee_id} deactivated user {user.employee_id}")

    return {"message": "User deactivated successfully"}


@router.put("/users/{user_id}/activate")
async def activate_user(
    user_id: int,
    admin_user: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """
    Activate user (Admin only)
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    # Activate user
    user.is_active = True
    db.commit()

    logger.info(f"Admin {admin_user.employee_id} activated user {user.employee_id}")

    return {"message": "User activated successfully"}


@router.put("/users/{employee_id}/status")
async def toggle_user_status(
    employee_id: str,
    admin_user: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """
    Toggle user status (Admin only)
    """
    user = db.query(User).filter(User.employee_id == employee_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    # Prevent admin from deactivating themselves
    if user.id == admin_user.id and user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot deactivate your own account"
        )

    # Toggle status
    user.is_active = not user.is_active
    db.commit()

    action = "activated" if user.is_active else "deactivated"
    logger.info(f"Admin {admin_user.employee_id} {action} user {user.employee_id}")

    return {
        "message": f"User {action} successfully",
        "is_active": user.is_active
    }


@router.put("/users/{user_id}/reset-password")
async def reset_user_password(
    user_id: int,
    admin_user: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """
    Reset user password (Admin only)
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    # Generate new temporary password
    import secrets
    import string
    new_password = ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(12))

    # Hash the new password
    user.password_hash = get_password_hash(new_password)
    db.commit()

    logger.info(f"Admin {admin_user.employee_id} reset password for user {user.employee_id}")

    return {
        "message": "Password reset successfully",
        "temporary_password": new_password
    }


# Bulk Operations Schema
class BulkRequestAction(BaseModel):
    request_ids: List[int]
    action: str  # "approve", "reject", "cancel"
    notes: Optional[str] = None
    vehicle_id: Optional[int] = None
    driver_id: Optional[int] = None


@router.post("/requests/bulk-action")
async def bulk_request_action(
    bulk_data: BulkRequestAction,
    admin_user: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """
    Perform bulk actions on multiple requests
    """
    if not bulk_data.request_ids:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No request IDs provided"
        )

    # Get all requests
    requests = db.query(TransportRequest).filter(
        TransportRequest.id.in_(bulk_data.request_ids)
    ).all()

    if len(requests) != len(bulk_data.request_ids):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Some requests not found"
        )

    results = []

    for request in requests:
        try:
            if bulk_data.action == "approve":
                if request.status != RequestStatus.PENDING:
                    results.append({
                        "request_id": request.id,
                        "status": "skipped",
                        "message": "Request not pending"
                    })
                    continue

                # For bulk approval, we need vehicle and driver
                if not bulk_data.vehicle_id or not bulk_data.driver_id:
                    results.append({
                        "request_id": request.id,
                        "status": "failed",
                        "message": "Vehicle and driver required for approval"
                    })
                    continue

                # Check vehicle and driver availability
                vehicle = db.query(Vehicle).filter(Vehicle.id == bulk_data.vehicle_id).first()
                driver = db.query(Driver).filter(Driver.id == bulk_data.driver_id).first()

                if not vehicle or not driver:
                    results.append({
                        "request_id": request.id,
                        "status": "failed",
                        "message": "Vehicle or driver not found"
                    })
                    continue

                # Approve request
                request.status = RequestStatus.APPROVED
                request.approved_by = admin_user.id
                request.approved_at = datetime.utcnow()

                # Create assignment
                assignment = VehicleAssignment(
                    request_id=request.id,
                    vehicle_id=bulk_data.vehicle_id,
                    driver_id=bulk_data.driver_id,
                    assigned_by=admin_user.id,
                    assignment_date=request.request_date,
                    estimated_departure=request.request_time,
                    status=AssignmentStatus.ASSIGNED,
                    notes=bulk_data.notes or "Bulk approval"
                )

                # Update driver availability to false when assigned
                assigned_driver = db.query(Driver).filter(Driver.id == bulk_data.driver_id).first()
                if assigned_driver:
                    assigned_driver.is_available = False

                db.add(assignment)

                results.append({
                    "request_id": request.id,
                    "status": "approved",
                    "message": "Request approved successfully"
                })

            elif bulk_data.action == "reject":
                if request.status != RequestStatus.PENDING:
                    results.append({
                        "request_id": request.id,
                        "status": "skipped",
                        "message": "Request not pending"
                    })
                    continue

                request.status = RequestStatus.REJECTED
                request.rejection_reason = bulk_data.notes or "Bulk rejection"

                results.append({
                    "request_id": request.id,
                    "status": "rejected",
                    "message": "Request rejected successfully"
                })

            elif bulk_data.action == "cancel":
                if request.status not in [RequestStatus.PENDING, RequestStatus.APPROVED]:
                    results.append({
                        "request_id": request.id,
                        "status": "skipped",
                        "message": "Request cannot be cancelled"
                    })
                    continue

                request.status = RequestStatus.CANCELLED

                # Cancel vehicle assignment if exists and restore driver availability
                assignment = db.query(VehicleAssignment).filter(VehicleAssignment.request_id == request.id).first()
                if assignment:
                    assignment.status = AssignmentStatus.CANCELLED
                    # Restore driver availability when assignment is cancelled
                    if assignment.driver:
                        assignment.driver.is_available = True

                results.append({
                    "request_id": request.id,
                    "status": "cancelled",
                    "message": "Request cancelled successfully"
                })

            else:
                results.append({
                    "request_id": request.id,
                    "status": "failed",
                    "message": f"Unknown action: {bulk_data.action}"
                })

        except Exception as e:
            results.append({
                "request_id": request.id,
                "status": "error",
                "message": str(e)
            })

    db.commit()

    logger.info(f"Admin {admin_user.employee_id} performed bulk {bulk_data.action} on {len(bulk_data.request_ids)} requests")

    return {
        "message": f"Bulk {bulk_data.action} completed",
        "results": results,
        "total_processed": len(results),
        "successful": len([r for r in results if r["status"] in ["approved", "rejected", "cancelled"]])
    }
