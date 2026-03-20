# schemas.py
# Pydantic schemas validate incoming request data and shape outgoing responses
# Think of them as contracts — what data must look like going in and coming out

from pydantic import BaseModel
from typing import Optional
from datetime import date, time, datetime
from uuid import UUID

# ── PACKAGE SCHEMAS ──────────────────────────────

class PackageCreate(BaseModel):
    """Shape of data needed to register a new package"""
    student_name: str
    registration_number: str
    package_description: str
    date_arrived: date

class PackageResponse(BaseModel):
    """Shape of package data returned to the client"""
    id: UUID
    student_name: str
    registration_number: str
    package_description: str
    date_arrived: date
    status: str
    created_at: datetime

    class Config:
        from_attributes = True  # allows SQLAlchemy objects to be serialized

class PackageStatusUpdate(BaseModel):
    """Shape of data needed to update a package status"""
    status: str

# ── PICKUP REQUEST SCHEMAS ────────────────────────

class PickupRequestCreate(BaseModel):
    """Shape of data needed to submit a pickup request"""
    package_id: UUID
    registration_number: str
    pickup_type: str  # "normal" or "emergency"

class PickupRequestResponse(BaseModel):
    id: UUID
    package_id: UUID
    registration_number: str
    pickup_type: str
    request_time: datetime
    approved: bool

    class Config:
        from_attributes = True

# ── PICKUP RECORD SCHEMAS ─────────────────────────

class PickupRecordCreate(BaseModel):
    """Shape of data needed to record a physical package collection"""
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
        from_attributes = True

# ── AUTH SCHEMAS ──────────────────────────────────

class AdminLogin(BaseModel):
    """Shape of admin login credentials"""
    username: str
    password: str

class Token(BaseModel):
    """Shape of JWT token returned after successful login"""
    access_token: str
    token_type: str

# ── DASHBOARD SCHEMA ──────────────────────────────

class DashboardStats(BaseModel):
    """Shape of admin dashboard summary data"""
    total_packages: int
    arrived_today: int
    awaiting_pickup: int
    pickup_requests: int
    emergency_requests: int
    picked_up_today: int
    pending_notifications: int 

    
# ── NOTIFICATION SCHEMAS ──────────────────────────────

class NotificationCreate(BaseModel):
    """Shape of data when student reports an expected package"""
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
        from_attributes = True

class NotificationApprove(BaseModel):
    """Shape of data when admin approves a notification"""
    rejection_reason: Optional[str] = None