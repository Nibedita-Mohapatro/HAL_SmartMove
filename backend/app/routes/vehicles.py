from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func
from typing import Optional, List
from datetime import date, time, datetime, timedelta
from app.database import get_db
from app.auth import get_admin_user, get_current_active_user
from app.models.user import User
from app.models.vehicle import Vehicle, VehicleType, FuelType
from app.models.vehicle_assignment import VehicleAssignment, AssignmentStatus
from app.models.transport_request import TransportRequest, RequestStatus
from pydantic import BaseModel
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/vehicles", tags=["Vehicles"])


class VehicleCreate(BaseModel):
    vehicle_number: str
    vehicle_type: VehicleType
    capacity: int
    fuel_type: FuelType
    model: Optional[str] = None
    year_of_manufacture: Optional[int] = None
    insurance_expiry: Optional[date] = None
    fitness_certificate_expiry: Optional[date] = None
    current_location: Optional[str] = None


class VehicleUpdate(BaseModel):
    capacity: Optional[int] = None
    model: Optional[str] = None
    year_of_manufacture: Optional[int] = None
    insurance_expiry: Optional[date] = None
    fitness_certificate_expiry: Optional[date] = None
    current_location: Optional[str] = None
    is_active: Optional[bool] = None


class VehicleAvailabilityQuery(BaseModel):
    date: date
    time: time
    duration: int = 120  # minutes


@router.get("/")
async def get_vehicles(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    vehicle_type: Optional[VehicleType] = None,
    is_active: Optional[bool] = None,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get all vehicles (admin) or active vehicles (employee)
    """
    query = db.query(Vehicle)
    
    # Non-admin users can only see active vehicles
    if current_user.role.value not in ['admin', 'super_admin']:
        query = query.filter(Vehicle.is_active == True)
    
    # Apply filters
    if vehicle_type:
        query = query.filter(Vehicle.vehicle_type == vehicle_type)
    if is_active is not None:
        query = query.filter(Vehicle.is_active == is_active)
    
    # Get total count
    total = query.count()
    
    # Apply pagination
    vehicles = query.order_by(Vehicle.vehicle_number).offset((page - 1) * limit).limit(limit).all()
    
    # Add maintenance status and utilization info for each vehicle
    vehicle_responses = []
    for vehicle in vehicles:
        vehicle_dict = vehicle.to_dict()
        
        # Check maintenance status
        today = date.today()
        maintenance_status = "good"
        next_maintenance = None
        
        if vehicle.insurance_expiry and vehicle.insurance_expiry <= today + timedelta(days=30):
            maintenance_status = "insurance_expiring"
        if vehicle.fitness_certificate_expiry and vehicle.fitness_certificate_expiry <= today + timedelta(days=30):
            maintenance_status = "fitness_expiring"
        if vehicle.insurance_expiry and vehicle.insurance_expiry <= today:
            maintenance_status = "insurance_expired"
        if vehicle.fitness_certificate_expiry and vehicle.fitness_certificate_expiry <= today:
            maintenance_status = "fitness_expired"
        
        # Calculate utilization (assignments in last 30 days)
        month_ago = today - timedelta(days=30)
        assignments_count = db.query(VehicleAssignment).join(TransportRequest).filter(
            and_(
                VehicleAssignment.vehicle_id == vehicle.id,
                TransportRequest.request_date >= month_ago,
                VehicleAssignment.status == AssignmentStatus.COMPLETED
            )
        ).count()
        
        vehicle_dict.update({
            "maintenance_status": maintenance_status,
            "assignments_last_30_days": assignments_count,
            "next_maintenance": next_maintenance
        })
        
        vehicle_responses.append(vehicle_dict)
    
    return {
        "vehicles": vehicle_responses,
        "pagination": {
            "page": page,
            "limit": limit,
            "total": total,
            "pages": (total + limit - 1) // limit
        }
    }


@router.post("/")
async def create_vehicle(
    vehicle_data: VehicleCreate,
    admin_user: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """
    Create new vehicle (Admin only)
    """
    # Check if vehicle number already exists
    existing_vehicle = db.query(Vehicle).filter(
        Vehicle.vehicle_number == vehicle_data.vehicle_number
    ).first()
    
    if existing_vehicle:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Vehicle with this number already exists"
        )
    
    # Create new vehicle
    vehicle = Vehicle(**vehicle_data.dict())
    db.add(vehicle)
    db.commit()
    db.refresh(vehicle)
    
    logger.info(f"Admin {admin_user.employee_id} created vehicle {vehicle.vehicle_number}")
    
    return {
        "message": "Vehicle created successfully",
        "vehicle": vehicle.to_dict()
    }


@router.get("/{vehicle_id}")
async def get_vehicle(
    vehicle_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get specific vehicle details
    """
    vehicle = db.query(Vehicle).filter(Vehicle.id == vehicle_id).first()
    
    if not vehicle:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Vehicle not found"
        )
    
    # Non-admin users can only see active vehicles
    if current_user.role.value not in ['admin', 'super_admin'] and not vehicle.is_active:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Vehicle not found"
        )
    
    vehicle_dict = vehicle.to_dict()
    
    # Add recent assignments for admin users
    if current_user.role.value in ['admin', 'super_admin']:
        recent_assignments = db.query(VehicleAssignment).join(TransportRequest).join(User).filter(
            VehicleAssignment.vehicle_id == vehicle_id
        ).order_by(VehicleAssignment.assignment_date.desc()).limit(10).all()
        
        assignments_data = []
        for assignment in recent_assignments:
            assignments_data.append({
                **assignment.to_dict(),
                'request': assignment.request.to_dict(),
                'user': assignment.request.user.to_dict(),
                'driver': assignment.driver.to_dict()
            })
        
        vehicle_dict['recent_assignments'] = assignments_data
    
    return vehicle_dict


@router.put("/{vehicle_id}")
async def update_vehicle(
    vehicle_id: int,
    vehicle_data: VehicleUpdate,
    admin_user: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """
    Update vehicle details (Admin only)
    """
    vehicle = db.query(Vehicle).filter(Vehicle.id == vehicle_id).first()
    
    if not vehicle:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Vehicle not found"
        )
    
    # Update fields
    update_data = vehicle_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(vehicle, field, value)
    
    db.commit()
    db.refresh(vehicle)
    
    logger.info(f"Admin {admin_user.employee_id} updated vehicle {vehicle.vehicle_number}")
    
    return {
        "message": "Vehicle updated successfully",
        "vehicle": vehicle.to_dict()
    }


@router.delete("/{vehicle_id}")
async def delete_vehicle(
    vehicle_id: int,
    admin_user: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """
    Deactivate vehicle (Admin only)
    """
    vehicle = db.query(Vehicle).filter(Vehicle.id == vehicle_id).first()
    
    if not vehicle:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Vehicle not found"
        )
    
    # Check if vehicle has active assignments
    active_assignments = db.query(VehicleAssignment).join(TransportRequest).filter(
        and_(
            VehicleAssignment.vehicle_id == vehicle_id,
            VehicleAssignment.status.in_([AssignmentStatus.ASSIGNED, AssignmentStatus.IN_PROGRESS])
        )
    ).count()
    
    if active_assignments > 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot deactivate vehicle with active assignments"
        )
    
    # Deactivate instead of delete
    vehicle.is_active = False
    db.commit()
    
    logger.info(f"Admin {admin_user.employee_id} deactivated vehicle {vehicle.vehicle_number}")
    
    return {"message": "Vehicle deactivated successfully"}


@router.post("/availability")
async def check_vehicle_availability(
    query_data: VehicleAvailabilityQuery,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Check vehicle availability for specific date and time
    """
    end_time = (datetime.combine(date.today(), query_data.time) + 
                timedelta(minutes=query_data.duration)).time()
    
    # Get all active vehicles
    all_vehicles = db.query(Vehicle).filter(Vehicle.is_active == True).all()
    
    # Get busy vehicles for the specified time slot
    busy_vehicle_ids = db.query(VehicleAssignment.vehicle_id).join(TransportRequest).filter(
        and_(
            TransportRequest.request_date == query_data.date,
            VehicleAssignment.status.in_([AssignmentStatus.ASSIGNED, AssignmentStatus.IN_PROGRESS]),
            or_(
                # Assignment overlaps with requested time
                and_(
                    VehicleAssignment.estimated_departure <= query_data.time,
                    VehicleAssignment.estimated_arrival >= query_data.time
                ),
                and_(
                    VehicleAssignment.estimated_departure <= end_time,
                    VehicleAssignment.estimated_arrival >= end_time
                ),
                and_(
                    VehicleAssignment.estimated_departure >= query_data.time,
                    VehicleAssignment.estimated_arrival <= end_time
                )
            )
        )
    ).subquery()
    
    # Separate available and busy vehicles
    available_vehicles = []
    busy_vehicles = []
    
    for vehicle in all_vehicles:
        vehicle_dict = {
            "id": vehicle.id,
            "vehicle_number": vehicle.vehicle_number,
            "vehicle_type": vehicle.vehicle_type.value,
            "capacity": vehicle.capacity,
            "current_location": vehicle.current_location
        }
        
        # Check if vehicle is busy
        is_busy = db.query(VehicleAssignment).join(TransportRequest).filter(
            and_(
                VehicleAssignment.vehicle_id == vehicle.id,
                TransportRequest.request_date == query_data.date,
                VehicleAssignment.status.in_([AssignmentStatus.ASSIGNED, AssignmentStatus.IN_PROGRESS]),
                or_(
                    and_(
                        VehicleAssignment.estimated_departure <= query_data.time,
                        VehicleAssignment.estimated_arrival >= query_data.time
                    ),
                    and_(
                        VehicleAssignment.estimated_departure <= end_time,
                        VehicleAssignment.estimated_arrival >= end_time
                    ),
                    and_(
                        VehicleAssignment.estimated_departure >= query_data.time,
                        VehicleAssignment.estimated_arrival <= end_time
                    )
                )
            )
        ).first()
        
        if is_busy:
            vehicle_dict.update({
                "busy_until": is_busy.estimated_arrival.strftime("%H:%M:%S"),
                "current_assignment": f"Trip from {is_busy.request.origin} to {is_busy.request.destination}"
            })
            busy_vehicles.append(vehicle_dict)
        else:
            available_vehicles.append(vehicle_dict)
    
    return {
        "available_vehicles": available_vehicles,
        "busy_vehicles": busy_vehicles,
        "query": {
            "date": query_data.date.isoformat(),
            "time": query_data.time.strftime("%H:%M:%S"),
            "duration_minutes": query_data.duration
        }
    }
