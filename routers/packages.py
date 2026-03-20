# routers/packages.py
# All endpoints related to packages
# GET /api/packages/search  — student searches for their package
# POST /api/packages/add    — admin registers a new package
# GET /api/packages/all     — admin views all packages
# PUT /api/packages/{id}/status — admin updates package status

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_
from typing import List
from database import get_db
from models import Package
from schemas import PackageCreate, PackageResponse, PackageStatusUpdate
from auth import get_current_admin
import uuid

# APIRouter groups all package-related routes together
# prefix means every route here starts with /api/packages
router = APIRouter(prefix="/api/packages", tags=["packages"])

@router.get("/search", response_model=List[PackageResponse])
def search_packages(
    q: str = Query(..., min_length=1, description="Search by name or registration number"),
    db: Session = Depends(get_db)
):
    """
    Student-facing search endpoint.
    Searches packages by student name OR registration number.
    No authentication required.
    """
    search_term = f"%{q}%"
    results = db.query(Package).filter(
        or_(
            Package.student_name.ilike(search_term),
            Package.registration_number.ilike(search_term)
        )
    ).all()

    return results

@router.post("/add", response_model=PackageResponse)
def add_package(
    package: PackageCreate,
    db: Session = Depends(get_db),
    current_admin: str = Depends(get_current_admin)  # requires admin login
):
    """
    Admin-only endpoint to register a new arriving package.
    Status defaults to ARRIVED automatically.
    
    Example: POST /api/packages/add
    Body: { student_name, registration_number, package_description, date_arrived }
    """
    new_package = Package(
        student_name=package.student_name,
        registration_number=package.registration_number,
        package_description=package.package_description,
        date_arrived=package.date_arrived,
        status="ARRIVED"  # always starts as ARRIVED
    )
    db.add(new_package)
    db.commit()
    db.refresh(new_package)  # refresh to get the auto-generated id and timestamps
    return new_package


@router.get("/all", response_model=List[PackageResponse])
def get_all_packages(
    db: Session = Depends(get_db),
    current_admin: str = Depends(get_current_admin)
):
    """
    Admin-only endpoint to view all packages in the system.
    Returns packages sorted by newest first.
    """
    return db.query(Package).order_by(Package.created_at.desc()).all()


@router.put("/{package_id}/status", response_model=PackageResponse)
def update_package_status(
    package_id: str,
    status_update: PackageStatusUpdate,
    db: Session = Depends(get_db),
    current_admin: str = Depends(get_current_admin)
):
    """
    Admin-only endpoint to manually update a package status.
    
    Example: PUT /api/packages/some-uuid/status
    Body: { "status": "READY_FOR_PICKUP" }
    """
    # Validate the status value
    valid_statuses = ["ARRIVED", "READY_FOR_PICKUP", "PICKUP_REQUESTED", "PICKED_UP"]
    if status_update.status not in valid_statuses:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid status. Must be one of: {valid_statuses}"
        )

    package = db.query(Package).filter(Package.id == package_id).first()
    if not package:
        raise HTTPException(status_code=404, detail="Package not found")

    package.status = status_update.status
    db.commit()
    db.refresh(package)
    return package