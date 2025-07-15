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
        "summary": {
            "total_requests_today": total_requests_today,
            "pending_requests": pending_requests,
            "approved_requests": approved_requests_today,
            "completed_trips": completed_trips_today,
            "active_vehicles": active_vehicles,
            "available_drivers": available_drivers
        },
        "trends": {
            "requests_last_7_days": daily_requests,
            "popular_routes": routes_data
        }
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
    query = db.query(TransportRequest).join(User)
    
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


@router.put("/requests/{request_id}/approve")
async def approve_request(
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
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Vehicle or driver is already assigned at this time"
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
        estimated_departure=approval_data.estimated_departure,
        estimated_arrival=approval_data.estimated_arrival,
        notes=approval_data.notes
    )
    
    db.add(assignment)
    db.commit()
    db.refresh(assignment)
    
    logger.info(f"Admin {admin_user.employee_id} approved request {request_id}")
    
    return {
        "message": "Request approved successfully",
        "assignment_id": assignment.id
    }


@router.put("/requests/{request_id}/reject")
async def reject_request(
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
