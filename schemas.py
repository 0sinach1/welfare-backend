# schemas.py
from pydantic import BaseModel
from typing import Optional, List
from datetime import date, time, datetime
from uuid import UUID

class PackageCreate(BaseModel):
    student_name: str
    registration_number: str
    package_description: str
    date_arrived: date

class PackageResponse(BaseModel):
    id: UUID
    student_name: str
    registration_number: str
    package_description: str
    date_arrived: date
    status: str
    created_at: datetime

    class Config:
        orm_mode = True  # pydantic v1 uses orm_mode not from_attributes

class PackageStatusUpdate(BaseModel):
    status: str

class PickupRequestCreate(BaseModel):
    package_id: UUID
    registration_number: str
    pickup_type: str

class PickupRequestResponse(BaseModel):
    id: UUID
    package_id: UUID
    registration_number: str
    pickup_type: str
    request_time: datetime
    approved: bool

    class Config:
        orm_mode = True

class PickupRecordCreate(BaseModel):
    package_id: UUID
    registration_number: str
    collected_by: str
    pickup_date: date
    pickup_time: time

class PickupRecordResponse(BaseModel):
    id: UUID
    package_id: UUID
    registration_number: str
    collected_by: str
    pickup_date: date
    pickup_time: time
    status: str

    class Config:
        orm_mode = True

class AdminLogin(BaseModel):
    username: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class DashboardStats(BaseModel):
    total_packages: int
    arrived_today: int
    awaiting_pickup: int
    pickup_requests: int
    emergency_requests: int
    picked_up_today: int
    pending_notifications: int

class NotificationCreate(BaseModel):
    student_name: str
    registration_number: str
    package_description: str
    sender_name: Optional[str] = None

class NotificationResponse(BaseModel):
    id: UUID
    student_name: str
    registration_number: str
    package_description: str
    sender_name: Optional[str] = None
    status: str
    package_id: Optional[UUID] = None
    rejection_reason: Optional[str] = None
    created_at: datetime

    class Config:
        orm_mode = True

class NotificationApprove(BaseModel):
    rejection_reason: Optional[str] = None
