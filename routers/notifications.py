# routers/notifications.py
# Handles all package notification endpoints
#
# POST /api/notifications/create       — student reports expected package
# GET  /api/notifications              — admin views all notifications  
# PUT  /api/notifications/{id}/approve — admin approves → auto-creates package
# PUT  /api/notifications/{id}/reject  — admin rejects with reason

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import or_
from typing import List
from database import get_db
from models import PackageNotification, Package
from schemas import (
    NotificationCreate,
    NotificationResponse,
    NotificationApprove,
    PackageResponse
)
from auth import get_current_admin
from datetime import date

router = APIRouter(prefix="/api/notifications", tags=["notifications"])


@router.post("/create", response_model=NotificationResponse)
def create_notification(
    notification: NotificationCreate,
    db: Session = Depends(get_db)
):
    """
    Student-facing — no auth required.
    Called when student searches and finds nothing.
    Creates a PENDING notification that admin will review.
    """
    # Check if student already has a pending notification
    # to prevent duplicate submissions
    existing = db.query(PackageNotification).filter(
        PackageNotification.registration_number == notification.registration_number,
        PackageNotification.status == "PENDING"
    ).first()

    if existing:
        raise HTTPException(
            status_code=400,
            detail="You already have a pending notification. Please wait for admin review."
        )

    new_notification = PackageNotification(
        student_name=notification.student_name,
        registration_number=notification.registration_number,
        package_description=notification.package_description,
        sender_name=notification.sender_name,
        status="PENDING"
    )
    db.add(new_notification)
    db.commit()
    db.refresh(new_notification)
    return new_notification


@router.get("", response_model=List[NotificationResponse])
def get_all_notifications(
    db: Session = Depends(get_db),
    current_admin: str = Depends(get_current_admin)
):
    """
    Admin-only — returns all notifications newest first.
    Admin sees this in the dashboard notifications panel.
    """
    return db.query(PackageNotification).order_by(
        PackageNotification.created_at.desc()
    ).all()


@router.get("/pending", response_model=List[NotificationResponse])
def get_pending_notifications(
    db: Session = Depends(get_db),
    current_admin: str = Depends(get_current_admin)
):
    """Admin-only — returns only PENDING notifications"""
    return db.query(PackageNotification).filter(
        PackageNotification.status == "PENDING"
    ).order_by(PackageNotification.created_at.desc()).all()


@router.get("/search", response_model=List[NotificationResponse])
def search_notifications(
    q: str,
    db: Session = Depends(get_db)
):
    """
    Student-facing — no auth required.
    Called by search page to show student their
    pending notification status when no package found.
    """
    search_term = f"%{q}%"
    return db.query(PackageNotification).filter(
        or_(
            PackageNotification.student_name.ilike(search_term),
            PackageNotification.registration_number.ilike(search_term)
        )
    ).all()


@router.put("/{notification_id}/approve", response_model=PackageResponse)
def approve_notification(
    notification_id: str,
    db: Session = Depends(get_db),
    current_admin: str = Depends(get_current_admin)
):
    """
    Admin-only.
    When admin approves a notification:
    1. Auto-creates a proper Package row with ARRIVED status
    2. Links the notification to the new package
    3. Updates notification status to APPROVED
    
    Student can now search and find their package normally.
    """
    notification = db.query(PackageNotification).filter(
        PackageNotification.id == notification_id
    ).first()

    if not notification:
        raise HTTPException(status_code=404, detail="Notification not found")

    if notification.status != "PENDING":
        raise HTTPException(
            status_code=400,
            detail=f"Notification is already {notification.status}"
        )

    # Auto-create the package from notification details
    new_package = Package(
        student_name=notification.student_name,
        registration_number=notification.registration_number,
        package_description=notification.package_description,
        date_arrived=date.today(),
        status="ARRIVED"
    )
    db.add(new_package)
    db.flush()  # flush to get the new package id before committing

    # Link notification to the new package and mark approved
    notification.status = "APPROVED"
    notification.package_id = new_package.id

    db.commit()
    db.refresh(new_package)
    return new_package


@router.put("/{notification_id}/reject")
def reject_notification(
    notification_id: str,
    data: NotificationApprove,
    db: Session = Depends(get_db),
    current_admin: str = Depends(get_current_admin)
):
    """
    Admin-only.
    Rejects a notification with an optional reason.
    Student will see REJECTED status when they search again.
    """
    notification = db.query(PackageNotification).filter(
        PackageNotification.id == notification_id
    ).first()

    if not notification:
        raise HTTPException(status_code=404, detail="Notification not found")

    notification.status = "REJECTED"
    notification.rejection_reason = data.rejection_reason

    db.commit()
    return {
        "message": "Notification rejected",
        "id": notification_id,
        "reason": data.rejection_reason
    }