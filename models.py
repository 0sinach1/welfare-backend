# models.py
# Each class here = one table in your PostgreSQL database
# SQLAlchemy translates these Python classes into actual database tables

from sqlalchemy import Column, String, Date, Time, Boolean, DateTime, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
import uuid
from database import Base

class Package(Base):
    __tablename__ = "packages"

    id                  = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    student_name        = Column(Text, nullable=False)
    registration_number = Column(Text, nullable=False)
    package_description = Column(Text, nullable=False)
    date_arrived        = Column(Date, nullable=False)
    status              = Column(Text, nullable=False, default="ARRIVED")
    created_at          = Column(DateTime(timezone=True), server_default=func.now())
    updated_at          = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class PickupRequest(Base):
    __tablename__ = "pickup_requests"

    id                  = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    package_id          = Column(UUID(as_uuid=True), nullable=False)
    registration_number = Column(Text, nullable=False)
    pickup_type         = Column(Text, nullable=False, default="normal")
    request_time        = Column(DateTime(timezone=True), server_default=func.now())
    approved            = Column(Boolean, default=False)


class PickupRecord(Base):
    __tablename__ = "pickup_records"

    id                  = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    package_id          = Column(UUID(as_uuid=True), nullable=False)
    registration_number = Column(Text, nullable=False)
    collected_by        = Column(Text, nullable=False)
    pickup_date         = Column(Date, nullable=False)
    pickup_time         = Column(Time, nullable=False)
    status              = Column(Text, nullable=False, default="PICKED_UP")
    created_at          = Column(DateTime(timezone=True), server_default=func.now())


class Admin(Base):
    __tablename__ = "admins"

    id            = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    username      = Column(Text, unique=True, nullable=False)
    password_hash = Column(Text, nullable=False)
    created_at    = Column(DateTime(timezone=True), server_default=func.now())
    
class PackageNotification(Base):
    __tablename__ = "package_notifications"

    id                  = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    student_name        = Column(Text, nullable=False)
    registration_number = Column(Text, nullable=False)
    package_description = Column(Text, nullable=False)
    sender_name         = Column(Text, nullable=True)
    status              = Column(Text, nullable=False, default="PENDING")
    package_id          = Column(UUID(as_uuid=True), nullable=True)
    rejection_reason    = Column(Text, nullable=True)
    created_at          = Column(DateTime(timezone=True), server_default=func.now())
    updated_at          = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())