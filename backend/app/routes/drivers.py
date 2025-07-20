from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import and_, func
from typing import Optional
from datetime import date, datetime, timedelta
from app.database import get_db
from app.auth import get_admin_user, get_current_active_user
from app.models.user import User
from app.models.driver import Driver
from app.models.vehicle_assignment import VehicleAssignment, AssignmentStatus
from app.models.transport_request import TransportRequest
from pydantic import BaseModel, validator
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/drivers", tags=["Drivers"])


class DriverCreate(BaseModel):
    employee_id: str
    license_number: str
    license_expiry: date
    phone: str
    first_name: str
    last_name: str
    experience_years: int = 0

    @validator('license_expiry')
    def validate_license_expiry(cls, v):
        if v <= date.today():
            raise ValueError('License expiry date must be in the future')
        return v

    @validator('experience_years')
    def validate_experience(cls, v):
        if v < 0 or v > 50:
            raise ValueError('Experience years must be between 0 and 50')
        return v


class DriverUpdate(BaseModel):
    license_number: Optional[str] = None
    license_expiry: Optional[date] = None
    phone: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    experience_years: Optional[int] = None
    is_available: Optional[bool] = None
    is_active: Optional[bool] = None

    @validator('license_expiry')
    def validate_license_expiry(cls, v):
        if v and v <= date.today():
            raise ValueError('License expiry date must be in the future')
        return v

    @validator('experience_years')
    def validate_experience(cls, v):
        if v is not None and (v < 0 or v > 50):
            raise ValueError('Experience years must be between 0 and 50')
        return v


class DriverAvailabilityUpdate(BaseModel):
    is_available: bool


@router.get("/")
async def get_drivers(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    is_active: Optional[bool] = None,
    is_available: Optional[bool] = None,
    admin_user: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """
    Get all drivers (Admin only)
    """
    query = db.query(Driver)
    
    # Apply filters
    if is_active is not None:
        query = query.filter(Driver.is_active == is_active)
    if is_available is not None:
        query = query.filter(Driver.is_available == is_available)
    
    # Get total count
    total = query.count()
    
    # Apply pagination
    drivers = query.order_by(Driver.employee_id).offset((page - 1) * limit).limit(limit).all()
    
    # Add additional info for each driver
    driver_responses = []
    for driver in drivers:
        driver_dict = driver.to_dict()
        
        # Check license status
        today = date.today()
        license_status = "valid"
        if driver.license_expiry <= today + timedelta(days=30):
            license_status = "expiring_soon"
        if driver.license_expiry <= today:
            license_status = "expired"
        
        # Calculate assignments in last 30 days
        month_ago = today - timedelta(days=30)
        assignments_count = db.query(VehicleAssignment).join(TransportRequest).filter(
            and_(
                VehicleAssignment.driver_id == driver.id,
                TransportRequest.request_date >= month_ago,
                VehicleAssignment.status == AssignmentStatus.COMPLETED
            )
        ).count()
        
        # Get current assignment if any
        current_assignment = db.query(VehicleAssignment).join(TransportRequest).filter(
            and_(
                VehicleAssignment.driver_id == driver.id,
                VehicleAssignment.status.in_([AssignmentStatus.ASSIGNED, AssignmentStatus.IN_PROGRESS])
            )
        ).first()
        
        current_assignment_info = None
        if current_assignment:
            current_assignment_info = {
                "request_id": current_assignment.request_id,
                "origin": current_assignment.request.origin,
                "destination": current_assignment.request.destination,
                "estimated_departure": current_assignment.estimated_departure.strftime("%H:%M:%S") if current_assignment.estimated_departure else None,
                "estimated_arrival": current_assignment.estimated_arrival.strftime("%H:%M:%S") if current_assignment.estimated_arrival else None,
                "status": current_assignment.status.value
            }
        
        driver_dict.update({
            "license_status": license_status,
            "assignments_last_30_days": assignments_count,
            "current_assignment": current_assignment_info
        })
        
        driver_responses.append(driver_dict)
    
    return {
        "drivers": driver_responses,
        "pagination": {
            "page": page,
            "limit": limit,
            "total": total,
            "pages": (total + limit - 1) // limit
        }
    }


@router.post("/")
async def create_driver(
    driver_data: DriverCreate,
    admin_user: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """
    Create new driver (Admin only)
    """
    # Check if employee_id already exists
    existing_driver = db.query(Driver).filter(
        Driver.employee_id == driver_data.employee_id
    ).first()
    
    if existing_driver:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Driver with this employee ID already exists"
        )
    
    # Check if license number already exists
    existing_license = db.query(Driver).filter(
        Driver.license_number == driver_data.license_number
    ).first()
    
    if existing_license:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Driver with this license number already exists"
        )
    
    # Create new driver
    driver = Driver(**driver_data.dict())
    db.add(driver)
    db.commit()
    db.refresh(driver)
    
    logger.info(f"Admin {admin_user.employee_id} created driver {driver.employee_id}")
    
    return {
        "message": "Driver created successfully",
        "id": driver.id,
        "driver": driver.to_dict()
    }


@router.get("/{driver_id}")
async def get_driver(
    driver_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get specific driver details
    """
    driver = db.query(Driver).filter(Driver.id == driver_id).first()
    
    if not driver:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Driver not found"
        )
    
    # Non-admin users can only see active drivers
    if current_user.role.value not in ['admin', 'super_admin'] and not driver.is_active:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Driver not found"
        )
    
    driver_dict = driver.to_dict()
    
    # Add detailed assignment history for admin users
    if current_user.role.value in ['admin', 'super_admin']:
        recent_assignments = db.query(VehicleAssignment).join(TransportRequest).join(User).filter(
            VehicleAssignment.driver_id == driver_id
        ).order_by(VehicleAssignment.assignment_date.desc()).limit(20).all()
        
        assignments_data = []
        for assignment in recent_assignments:
            assignments_data.append({
                **assignment.to_dict(),
                'request': assignment.request.to_dict(),
                'user': assignment.request.user.to_dict(),
                'vehicle': assignment.vehicle.to_dict()
            })
        
        # Calculate performance metrics
        completed_assignments = [a for a in recent_assignments if a.status == AssignmentStatus.COMPLETED]
        total_completed = len(completed_assignments)
        
        # Calculate average rating (placeholder - would need rating system)
        performance_metrics = {
            "total_assignments": len(recent_assignments),
            "completed_assignments": total_completed,
            "completion_rate": (total_completed / len(recent_assignments) * 100) if recent_assignments else 0,
            "average_rating": 4.5,  # Placeholder
            "on_time_percentage": 95.0  # Placeholder
        }
        
        driver_dict.update({
            'recent_assignments': assignments_data,
            'performance_metrics': performance_metrics
        })
    
    return driver_dict


@router.put("/{driver_id}")
async def update_driver(
    driver_id: int,
    driver_data: DriverUpdate,
    admin_user: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """
    Update driver details (Admin only)
    """
    driver = db.query(Driver).filter(Driver.id == driver_id).first()
    
    if not driver:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Driver not found"
        )
    
    # Check for duplicate license number if updating
    if driver_data.license_number and driver_data.license_number != driver.license_number:
        existing_license = db.query(Driver).filter(
            and_(
                Driver.license_number == driver_data.license_number,
                Driver.id != driver_id
            )
        ).first()
        
        if existing_license:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Another driver with this license number already exists"
            )
    
    # Update fields
    update_data = driver_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(driver, field, value)
    
    db.commit()
    db.refresh(driver)
    
    logger.info(f"Admin {admin_user.employee_id} updated driver {driver.employee_id}")
    
    return {
        "message": "Driver updated successfully",
        "driver": driver.to_dict()
    }


@router.delete("/{driver_id}")
async def delete_driver(
    driver_id: int,
    admin_user: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """
    Delete driver (Admin only)
    """
    driver = db.query(Driver).filter(Driver.id == driver_id).first()

    if not driver:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Driver not found"
        )

    # Check if driver has active assignments
    active_assignments = db.query(VehicleAssignment).join(TransportRequest).filter(
        and_(
            VehicleAssignment.driver_id == driver_id,
            VehicleAssignment.status.in_([AssignmentStatus.ASSIGNED, AssignmentStatus.IN_PROGRESS])
        )
    ).count()

    if active_assignments > 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete driver with active assignments. Please complete or reassign active trips first."
        )

    # Check if driver has any historical assignments (for data integrity)
    historical_assignments = db.query(VehicleAssignment).filter(
        VehicleAssignment.driver_id == driver_id
    ).count()

    if historical_assignments > 0:
        # Soft delete for drivers with historical data to preserve referential integrity
        driver.is_active = False
        driver.is_available = False
        db.commit()

        logger.info(f"Admin {admin_user.employee_id} soft-deleted driver {driver.employee_id} (has historical assignments)")
        return {"message": "Driver deleted successfully", "type": "soft_delete"}
    else:
        # Hard delete for drivers with no historical data
        db.delete(driver)
        db.commit()

        logger.info(f"Admin {admin_user.employee_id} hard-deleted driver {driver.employee_id} (no historical assignments)")
        return {"message": "Driver deleted successfully", "type": "hard_delete"}


@router.get("/available/now")
async def get_available_drivers(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get currently available drivers
    """
    available_drivers = db.query(Driver).filter(
        and_(
            Driver.is_active == True,
            Driver.is_available == True,
            Driver.license_expiry > date.today()
        )
    ).all()
    
    driver_responses = []
    for driver in available_drivers:
        driver_dict = driver.to_dict()
        
        # Check if driver has any assignments today
        today = date.today()
        today_assignments = db.query(VehicleAssignment).join(TransportRequest).filter(
            and_(
                VehicleAssignment.driver_id == driver.id,
                TransportRequest.request_date == today,
                VehicleAssignment.status.in_([AssignmentStatus.ASSIGNED, AssignmentStatus.IN_PROGRESS])
            )
        ).count()
        
        driver_dict['assignments_today'] = today_assignments
        driver_responses.append(driver_dict)
    
    return {
        "available_drivers": driver_responses,
        "count": len(driver_responses)
    }


@router.put("/{driver_id}/availability")
async def update_driver_availability(
    driver_id: int,
    availability_data: DriverAvailabilityUpdate,
    admin_user: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """
    Update driver availability status (Admin only)
    """
    driver = db.query(Driver).filter(Driver.id == driver_id).first()
    if not driver:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Driver not found"
        )

    # Update availability
    driver.is_available = availability_data.is_available

    db.commit()
    db.refresh(driver)

    logger.info(f"Admin {admin_user.employee_id} updated availability for driver {driver.employee_id} to {availability_data.is_available}")

    return {
        "message": "Driver availability updated successfully",
        "driver": driver.to_dict()
    }





@router.put("/{driver_id}/toggle-status")
async def toggle_driver_status(
    driver_id: int,
    admin_user: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """
    Toggle driver active status
    """
    driver = db.query(Driver).filter(Driver.id == driver_id).first()
    if not driver:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Driver not found"
        )

    # Toggle the status
    driver.is_active = not driver.is_active
    db.commit()

    status_text = "activated" if driver.is_active else "deactivated"
    logger.info(f"Admin {admin_user.employee_id} {status_text} driver {driver.employee_id}")

    return {
        "message": f"Driver {status_text} successfully",
        "is_active": driver.is_active
    }
