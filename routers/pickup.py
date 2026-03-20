# routers/pickup.py
# All endpoints related to pickup requests and pickup records
#
# POST /api/pickup/request        — student submits pickup request
# POST /api/pickup/record         — admin records physical collection
# GET  /api/pickup/requests       — admin views all pickup requests
# GET  /api/pickup/requests/emergency — admin views emergency requests only

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from database import get_db
from models import Package, PickupRequest, PickupRecord
from schemas import (
    PickupRequestCreate, PickupRequestResponse,
    PickupRecordCreate, PickupRecordResponse
)
from auth import get_current_admin

router = APIRouter(prefix="/api/pickup", tags=["pickup"])


@router.post("/request", response_model=PickupRequestResponse)
def request_pickup(
    request: PickupRequestCreate,
    db: Session = Depends(get_db)
):
    """
    Student-facing endpoint — no auth required.
    When student clicks 'Request Pickup', this endpoint:
    1. Creates a new PickupRequest row
    2. Automatically updates the package status to PICKUP_REQUESTED
    """
    # First check the package actually exists
    package = db.query(Package).filter(
        Package.id == request.package_id
    ).first()

    if not package:
        raise HTTPException(status_code=404, detail="Package not found")

    # Prevent duplicate requests on already-requested packages
    if package.status == "PICKED_UP":
        raise HTTPException(
            status_code=400,
            detail="This package has already been picked up"
        )

    # Create the pickup request record
    new_request = PickupRequest(
        package_id=request.package_id,
        registration_number=request.registration_number,
        pickup_type=request.pickup_type,
        approved=False  # admin must approve emergency pickups
    )
    db.add(new_request)

    # Automatically update the package status
    package.status = "PICKUP_REQUESTED"
    db.commit()
    db.refresh(new_request)
    return new_request


@router.post("/record", response_model=PickupRecordResponse)
def record_pickup(
    record: PickupRecordCreate,
    db: Session = Depends(get_db),
    current_admin: str = Depends(get_current_admin)
):
    """
    Admin-only endpoint.
    When student physically collects their package, admin records it here.
    This:
    1. Creates a PickupRecord row
    2. Automatically updates the package status to PICKED_UP
    """
    # Check the package exists
    package = db.query(Package).filter(
        Package.id == record.package_id
    ).first()

    if not package:
        raise HTTPException(status_code=404, detail="Package not found")

    # Create the pickup record
    new_record = PickupRecord(
        package_id=record.package_id,
        registration_number=record.registration_number,
        collected_by=record.collected_by,
        pickup_date=record.pickup_date,
        pickup_time=record.pickup_time,
        status="PICKED_UP"
    )
    db.add(new_record)

    # Update package status to final state
    package.status = "PICKED_UP"
    db.commit()
    db.refresh(new_record)
    return new_record


@router.get("/requests", response_model=List[PickupRequestResponse])
def get_all_pickup_requests(
    db: Session = Depends(get_db),
    current_admin: str = Depends(get_current_admin)
):
    """Admin-only — returns all pickup requests, newest first"""
    return db.query(PickupRequest).order_by(
        PickupRequest.request_time.desc()
    ).all()


@router.get("/requests/emergency", response_model=List[PickupRequestResponse])
def get_emergency_requests(
    db: Session = Depends(get_db),
    current_admin: str = Depends(get_current_admin)
):
    """Admin-only — returns only emergency pickup requests"""
    return db.query(PickupRequest).filter(
        PickupRequest.pickup_type == "emergency"
    ).order_by(PickupRequest.request_time.desc()).all()