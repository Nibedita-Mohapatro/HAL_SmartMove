from pydantic import BaseModel, validator
from typing import Optional, List
from datetime import date, time, datetime
from app.models.transport_request import Priority, RequestStatus


class TransportRequestCreate(BaseModel):
    origin: str
    destination: str
    request_date: date
    request_time: time
    passenger_count: int = 1
    purpose: Optional[str] = None
    priority: Priority = Priority.MEDIUM

    @validator('passenger_count')
    def validate_passenger_count(cls, v):
        if v < 1 or v > 50:
            raise ValueError('Passenger count must be between 1 and 50')
        return v

    @validator('request_date')
    def validate_request_date(cls, v):
        if v < date.today():
            raise ValueError('Request date cannot be in the past')
        return v


class TransportRequestUpdate(BaseModel):
    passenger_count: Optional[int] = None
    purpose: Optional[str] = None
    priority: Optional[Priority] = None

    @validator('passenger_count')
    def validate_passenger_count(cls, v):
        if v is not None and (v < 1 or v > 50):
            raise ValueError('Passenger count must be between 1 and 50')
        return v


class TransportRequestResponse(BaseModel):
    id: int
    user_id: int
    origin: str
    destination: str
    request_date: date
    request_time: time
    passenger_count: int
    purpose: Optional[str] = None
    priority: Priority
    status: RequestStatus
    approved_by: Optional[int] = None
    approved_at: Optional[datetime] = None
    rejection_reason: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class TransportRequestWithUser(TransportRequestResponse):
    user: dict
    approver: Optional[dict] = None
    vehicle_assignment: Optional[dict] = None


class RequestApproval(BaseModel):
    vehicle_id: int
    driver_id: int
    estimated_departure: time
    estimated_arrival: time
    notes: Optional[str] = None


class RequestRejection(BaseModel):
    rejection_reason: str


class RequestListQuery(BaseModel):
    page: int = 1
    limit: int = 10
    status: Optional[RequestStatus] = None
    date_from: Optional[date] = None
    date_to: Optional[date] = None
    department: Optional[str] = None
    priority: Optional[Priority] = None


class PaginatedRequestResponse(BaseModel):
    requests: List[TransportRequestWithUser]
    pagination: dict
