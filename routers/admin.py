# routers/admin.py
# Admin-specific endpoints
# POST /api/auth/login      — admin login, returns JWT token
# GET  /api/admin/dashboard — returns dashboard statistics

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import date
from database import get_db
from models import Package, PickupRequest
from schemas import AdminLogin, Token, DashboardStats
from auth import authenticate_admin, create_access_token, get_current_admin

router = APIRouter(tags=["admin"])


@router.post("/api/auth/login", response_model=Token)
def admin_login(credentials: AdminLogin):
    """
    Admin login endpoint — no auth required (this IS the auth).
    Receives username + password.
    Returns a JWT token if credentials are valid.
    Frontend stores this token and sends it with every admin request.
    """
    is_valid = authenticate_admin(credentials.username, credentials.password)

    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password"
        )

    # Create JWT token with admin username embedded inside
    access_token = create_access_token(data={"sub": credentials.username})

    return {
        "access_token": access_token,
        "token_type": "bearer"
    }

@router.get("/api/admin/dashboard", response_model=DashboardStats)
def get_dashboard_stats(
    db: Session = Depends(get_db),
    current_admin: str = Depends(get_current_admin)
):
    from models import PackageNotification
    today = date.today()

    total_packages      = db.query(Package).count()
    arrived_today       = db.query(Package).filter(Package.date_arrived == today).count()
    awaiting_pickup     = db.query(Package).filter(Package.status.in_(["ARRIVED", "READY_FOR_PICKUP"])).count()
    pickup_requests     = db.query(Package).filter(Package.status == "PICKUP_REQUESTED").count()
    emergency_requests  = db.query(PickupRequest).filter(PickupRequest.pickup_type == "emergency", PickupRequest.approved == False).count()
    picked_up_today     = db.query(Package).filter(Package.status == "PICKED_UP", Package.updated_at >= str(today)).count()
    pending_notifications = db.query(PackageNotification).filter(PackageNotification.status == "PENDING").count()

    return {
        "total_packages": total_packages,
        "arrived_today": arrived_today,
        "awaiting_pickup": awaiting_pickup,
        "pickup_requests": pickup_requests,
        "emergency_requests": emergency_requests,
        "picked_up_today": picked_up_today,
        "pending_notifications": pending_notifications,
    }