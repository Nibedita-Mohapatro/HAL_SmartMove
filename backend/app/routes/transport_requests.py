from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from typing import Optional
from datetime import datetime
from app.database import get_db
from app.auth import get_current_active_user, get_admin_user
from app.models.user import User
from app.models.transport_request import TransportRequest, RequestStatus
from app.models.vehicle_assignment import VehicleAssignment, AssignmentStatus
from app.models.vehicle import Vehicle
from app.models.driver import Driver
from app.schemas.transport_request import (
    TransportRequestCreate, TransportRequestUpdate, TransportRequestResponse,
    TransportRequestWithUser, RequestApproval, RequestRejection,
    PaginatedRequestResponse
)
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/requests", tags=["Transport Requests"])


@router.post("/", response_model=TransportRequestResponse)
async def create_request(
    request_data: TransportRequestCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Create new transport request
    """
    # Check if user has pending requests for the exact same date/time (only prevent exact duplicates)
    existing_request = db.query(TransportRequest).filter(
        and_(
            TransportRequest.user_id == current_user.id,
            TransportRequest.request_date == request_data.request_date,
            TransportRequest.request_time == request_data.request_time,
            TransportRequest.status.in_([RequestStatus.PENDING, RequestStatus.APPROVED])
        )
    ).first()

    if existing_request:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You already have a request for this exact date and time. Please choose a different time."
        )

    # Check for reasonable time gaps (prevent requests within 30 minutes of each other)
    from datetime import datetime, timedelta
    request_datetime = datetime.combine(request_data.request_date, request_data.request_time)

    # Check for nearby requests (within 30 minutes)
    nearby_requests = db.query(TransportRequest).filter(
        and_(
            TransportRequest.user_id == current_user.id,
            TransportRequest.request_date == request_data.request_date,
            TransportRequest.status.in_([RequestStatus.PENDING, RequestStatus.APPROVED])
        )
    ).all()

    for nearby_req in nearby_requests:
        nearby_datetime = datetime.combine(nearby_req.request_date, nearby_req.request_time)
        time_diff = abs((request_datetime - nearby_datetime).total_seconds() / 60)  # minutes

        if time_diff < 30:  # Less than 30 minutes apart
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"You have another request at {nearby_req.request_time}. Please ensure at least 30 minutes gap between requests."
            )
    
    # Create new request
    db_request = TransportRequest(
        user_id=current_user.id,
        **request_data.dict()
    )
    
    db.add(db_request)
    db.commit()
    db.refresh(db_request)
    
    logger.info(f"User {current_user.employee_id} created transport request {db_request.id}")
    
    return TransportRequestResponse.from_orm(db_request)


@router.get("/", response_model=PaginatedRequestResponse)
async def get_user_requests(
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    status: Optional[RequestStatus] = None,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get current user's transport requests
    """
    query = db.query(TransportRequest).filter(TransportRequest.user_id == current_user.id)
    
    if status:
        query = query.filter(TransportRequest.status == status)
    
    # Get total count
    total = query.count()
    
    # Apply pagination
    requests = query.order_by(TransportRequest.created_at.desc()).offset((page - 1) * limit).limit(limit).all()
    
    # Convert to response format
    request_responses = []
    for request in requests:
        request_dict = request.to_dict()
        request_dict['user'] = request.user.to_dict()
        
        if request.approver:
            request_dict['approver'] = request.approver.to_dict()
        
        if hasattr(request, 'vehicle_assignment') and request.vehicle_assignment:
            assignment = request.vehicle_assignment[0]  # Assuming one assignment per request
            request_dict['vehicle_assignment'] = {
                **assignment.to_dict(),
                'vehicle': assignment.vehicle.to_dict(),
                'driver': assignment.driver.to_dict()
            }
        
        request_responses.append(request_dict)
    
    return PaginatedRequestResponse(
        requests=request_responses,
        pagination={
            "page": page,
            "limit": limit,
            "total": total,
            "pages": (total + limit - 1) // limit
        }
    )


@router.get("/{request_id}", response_model=TransportRequestWithUser)
async def get_request(
    request_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get specific transport request
    """
    request = db.query(TransportRequest).filter(TransportRequest.id == request_id).first()
    
    if not request:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Request not found"
        )
    
    # Check if user owns the request or is admin
    if request.user_id != current_user.id and current_user.role.value not in ['admin', 'super_admin']:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view this request"
        )
    
    # Build response
    request_dict = request.to_dict()
    request_dict['user'] = request.user.to_dict()
    
    if request.approver:
        request_dict['approver'] = request.approver.to_dict()
    
    # Get vehicle assignment if exists
    assignment = db.query(VehicleAssignment).filter(VehicleAssignment.request_id == request_id).first()
    if assignment:
        request_dict['vehicle_assignment'] = {
            **assignment.to_dict(),
            'vehicle': assignment.vehicle.to_dict(),
            'driver': assignment.driver.to_dict()
        }
    
    return request_dict


@router.put("/{request_id}", response_model=TransportRequestResponse)
async def update_request(
    request_id: int,
    request_data: TransportRequestUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Update transport request (only if pending)
    """
    request = db.query(TransportRequest).filter(
        and_(
            TransportRequest.id == request_id,
            TransportRequest.user_id == current_user.id
        )
    ).first()
    
    if not request:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Request not found"
        )
    
    if request.status != RequestStatus.PENDING:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Can only update pending requests"
        )
    
    # Update fields
    update_data = request_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(request, field, value)
    
    db.commit()
    db.refresh(request)
    
    logger.info(f"User {current_user.employee_id} updated request {request_id}")
    
    return TransportRequestResponse.from_orm(request)


@router.delete("/{request_id}")
async def cancel_request(
    request_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Cancel transport request
    """
    request = db.query(TransportRequest).filter(
        and_(
            TransportRequest.id == request_id,
            TransportRequest.user_id == current_user.id
        )
    ).first()
    
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
    
    # Cancel the request
    request.status = RequestStatus.CANCELLED
    
    # Cancel vehicle assignment if exists
    assignment = db.query(VehicleAssignment).filter(VehicleAssignment.request_id == request_id).first()
    if assignment:
        assignment.status = AssignmentStatus.CANCELLED
    
    db.commit()
    
    logger.info(f"User {current_user.employee_id} cancelled request {request_id}")
    
    return {"message": "Request cancelled successfully"}
