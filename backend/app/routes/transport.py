from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from typing import Optional, List
from datetime import datetime, date
import logging

from app.database import get_db
from app.auth import get_current_active_user
from app.models.user import User, UserRole
from app.models.transport_request import TransportRequest, RequestStatus
from app.models.vehicle_assignment import VehicleAssignment, AssignmentStatus
from app.models.vehicle import Vehicle
from app.models.driver import Driver

router = APIRouter(prefix="/transport", tags=["Transport Management"])
logger = logging.getLogger(__name__)


def get_transport_user(current_user: User = Depends(get_current_active_user)):
    """Dependency to ensure user has transport role"""
    if current_user.role not in [UserRole.TRANSPORT, UserRole.ADMIN, UserRole.SUPER_ADMIN]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Transport role required"
        )
    return current_user


@router.get("/assigned-trips")
async def get_assigned_trips(
    transport_user: User = Depends(get_transport_user),
    db: Session = Depends(get_db)
):
    """
    Get trips assigned to the current transport user (driver)
    """
    # Find driver record for this user
    driver = db.query(Driver).filter(Driver.employee_id == transport_user.employee_id).first()
    
    if not driver:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Driver profile not found"
        )
    
    # Get assigned trips
    assigned_trips = db.query(VehicleAssignment).join(TransportRequest).filter(
        and_(
            VehicleAssignment.driver_id == driver.id,
            VehicleAssignment.status.in_([AssignmentStatus.ASSIGNED, AssignmentStatus.IN_PROGRESS])
        )
    ).all()
    
    trips_data = []
    for assignment in assigned_trips:
        trip_data = {
            "assignment_id": assignment.id,
            "request_id": assignment.request_id,
            "status": assignment.status.value,
            "estimated_departure": assignment.estimated_departure.isoformat() if assignment.estimated_departure else None,
            "estimated_arrival": assignment.estimated_arrival.isoformat() if assignment.estimated_arrival else None,
            "actual_departure": assignment.started_at.isoformat() if assignment.started_at else None,
            "actual_arrival": assignment.completed_at.isoformat() if assignment.completed_at else None,
            "notes": assignment.notes
        }
        
        # Add request details
        if assignment.request:
            trip_data.update({
                "origin": assignment.request.origin,
                "destination": assignment.request.destination,
                "request_date": assignment.request.request_date.isoformat(),
                "request_time": assignment.request.request_time.isoformat(),
                "passenger_count": assignment.request.passenger_count,
                "purpose": assignment.request.purpose,
                "priority": assignment.request.priority.value
            })
            
            # Add user details
            if assignment.request.user:
                trip_data["passenger"] = {
                    "name": f"{assignment.request.user.first_name} {assignment.request.user.last_name}",
                    "employee_id": assignment.request.user.employee_id,
                    "phone": assignment.request.user.phone,
                    "department": assignment.request.user.department
                }
        
        # Add vehicle details
        if assignment.vehicle:
            trip_data["vehicle"] = {
                "id": assignment.vehicle.id,
                "number": assignment.vehicle.vehicle_number,
                "type": assignment.vehicle.vehicle_type.value,
                "capacity": assignment.vehicle.capacity
            }
        
        trips_data.append(trip_data)
    
    return {
        "assigned_trips": trips_data,
        "count": len(trips_data),
        "driver": {
            "id": driver.id,
            "name": f"{driver.first_name} {driver.last_name}",
            "employee_id": driver.employee_id,
            "phone": driver.phone,
            "license_number": driver.license_number,
            "license_expiry": driver.license_expiry.isoformat() if driver.license_expiry else None,
            "experience_years": driver.experience_years,
            "is_active": driver.is_active,
            "is_available": driver.is_available
        }
    }


@router.put("/trip/{assignment_id}/start")
async def start_trip(
    assignment_id: int,
    transport_user: User = Depends(get_transport_user),
    db: Session = Depends(get_db)
):
    """
    Mark trip as started
    """
    # Find driver record
    driver = db.query(Driver).filter(Driver.employee_id == transport_user.employee_id).first()
    
    if not driver:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Driver profile not found"
        )
    
    # Get assignment
    assignment = db.query(VehicleAssignment).filter(
        and_(
            VehicleAssignment.id == assignment_id,
            VehicleAssignment.driver_id == driver.id
        )
    ).first()
    
    if not assignment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Assignment not found"
        )
    
    if assignment.status != AssignmentStatus.ASSIGNED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Trip can only be started from assigned status"
        )
    
    # Start the trip
    assignment.status = AssignmentStatus.IN_PROGRESS
    assignment.started_at = datetime.utcnow()
    
    db.commit()
    db.refresh(assignment)
    
    logger.info(f"Driver {transport_user.employee_id} started trip {assignment_id}")
    
    return {
        "message": "Trip started successfully",
        "assignment_id": assignment_id,
        "started_at": assignment.started_at.isoformat()
    }


@router.put("/trip/{assignment_id}/complete")
async def complete_trip(
    assignment_id: int,
    transport_user: User = Depends(get_transport_user),
    db: Session = Depends(get_db)
):
    """
    Mark trip as completed
    """
    # Find driver record
    driver = db.query(Driver).filter(Driver.employee_id == transport_user.employee_id).first()
    
    if not driver:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Driver profile not found"
        )
    
    # Get assignment
    assignment = db.query(VehicleAssignment).filter(
        and_(
            VehicleAssignment.id == assignment_id,
            VehicleAssignment.driver_id == driver.id
        )
    ).first()
    
    if not assignment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Assignment not found"
        )
    
    if assignment.status != AssignmentStatus.IN_PROGRESS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Trip can only be completed from in-progress status"
        )
    
    # Complete the trip
    assignment.status = AssignmentStatus.COMPLETED
    assignment.completed_at = datetime.utcnow()

    # Update request status
    if assignment.request:
        assignment.request.status = RequestStatus.COMPLETED

    # Set driver back to available when trip is completed
    if assignment.driver:
        assignment.driver.is_available = True

    db.commit()
    db.refresh(assignment)
    
    logger.info(f"Driver {transport_user.employee_id} completed trip {assignment_id}")
    
    return {
        "message": "Trip completed successfully",
        "assignment_id": assignment_id,
        "completed_at": assignment.completed_at.isoformat()
    }


@router.get("/schedule")
async def get_driver_schedule(
    date_from: Optional[date] = Query(None),
    date_to: Optional[date] = Query(None),
    transport_user: User = Depends(get_transport_user),
    db: Session = Depends(get_db)
):
    """
    Get driver's schedule for specified date range
    """
    # Find driver record
    driver = db.query(Driver).filter(Driver.employee_id == transport_user.employee_id).first()
    
    if not driver:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Driver profile not found"
        )
    
    # Set default date range if not provided
    if not date_from:
        date_from = date.today()
    if not date_to:
        date_to = date_from
    
    # Get assignments in date range
    assignments = db.query(VehicleAssignment).join(TransportRequest).filter(
        and_(
            VehicleAssignment.driver_id == driver.id,
            TransportRequest.request_date >= date_from,
            TransportRequest.request_date <= date_to
        )
    ).order_by(TransportRequest.request_date, TransportRequest.request_time).all()
    
    schedule_data = []
    for assignment in assignments:
        schedule_item = {
            "assignment_id": assignment.id,
            "date": assignment.request.request_date.isoformat(),
            "time": assignment.request.request_time.isoformat(),
            "origin": assignment.request.origin,
            "destination": assignment.request.destination,
            "passenger_count": assignment.request.passenger_count,
            "status": assignment.status.value,
            "estimated_departure": assignment.estimated_departure.isoformat() if assignment.estimated_departure else None,
            "estimated_arrival": assignment.estimated_arrival.isoformat() if assignment.estimated_arrival else None,
            "vehicle": {
                "number": assignment.vehicle.vehicle_number,
                "type": assignment.vehicle.vehicle_type.value
            } if assignment.vehicle else None,
            "passenger": {
                "name": f"{assignment.request.user.first_name} {assignment.request.user.last_name}",
                "employee_id": assignment.request.user.employee_id,
                "department": assignment.request.user.department
            } if assignment.request.user else None
        }
        
        schedule_data.append(schedule_item)
    
    return {
        "schedule": schedule_data,
        "date_range": {
            "from": date_from.isoformat(),
            "to": date_to.isoformat()
        },
        "count": len(schedule_data),
        "driver": {
            "name": f"{driver.first_name} {driver.last_name}",
            "employee_id": driver.employee_id
        }
    }
