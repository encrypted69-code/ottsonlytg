"""
Admin dashboard router
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime
from ..database import get_db
from ..models import User
from ..schemas import (
    DashboardStats, UserManagementFilter, OrderFilter,
    PaginatedResponse, MessageResponse
)
from ..auth import get_current_admin, log_admin_action
from ..services import AdminService

router = APIRouter(prefix="/admin/dashboard", tags=["Admin Dashboard"])


@router.get("/stats", response_model=DashboardStats)
async def get_dashboard_stats(
    current_user: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Get dashboard statistics"""
    stats = AdminService.get_dashboard_stats(db)
    return stats


@router.get("/users")
async def get_users(
    search: Optional[str] = None,
    user_type: Optional[str] = None,
    is_buyer: Optional[bool] = None,
    is_suspicious: Optional[bool] = None,
    date_from: Optional[datetime] = None,
    date_to: Optional[datetime] = None,
    page: int = 1,
    limit: int = 50,
    current_user: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Get filtered user list"""
    result = AdminService.get_users(
        db=db,
        search=search,
        user_type=user_type,
        is_buyer=is_buyer,
        is_suspicious=is_suspicious,
        date_from=date_from,
        date_to=date_to,
        page=page,
        limit=limit
    )
    return result


@router.get("/orders")
async def get_orders(
    search: Optional[str] = None,
    payment_status: Optional[str] = None,
    date_from: Optional[datetime] = None,
    date_to: Optional[datetime] = None,
    page: int = 1,
    limit: int = 50,
    current_user: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Get filtered order list"""
    result = AdminService.get_orders(
        db=db,
        search=search,
        payment_status=payment_status,
        date_from=date_from,
        date_to=date_to,
        page=page,
        limit=limit
    )
    return result


@router.get("/referrers")
async def get_referrer_performance(
    page: int = 1,
    limit: int = 50,
    current_user: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Get referrer performance metrics"""
    result = AdminService.get_referrer_performance(db=db, page=page, limit=limit)
    return result


@router.get("/payment-monitoring")
async def get_payment_monitoring(
    days: int = 7,
    current_user: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Get payment monitoring statistics"""
    result = AdminService.get_payment_monitoring(db=db, days=days)
    return result


@router.get("/kpi")
async def get_kpi_metrics(
    days: int = 30,
    current_user: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Get key performance indicators"""
    result = AdminService.get_kpi_metrics(db=db, days=days)
    return result


@router.get("/audit-logs")
async def get_audit_logs(
    admin_id: Optional[int] = None,
    action_type: Optional[str] = None,
    date_from: Optional[datetime] = None,
    date_to: Optional[datetime] = None,
    page: int = 1,
    limit: int = 100,
    current_user: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Get admin audit logs"""
    result = AdminService.get_audit_logs(
        db=db,
        admin_id=admin_id,
        action_type=action_type,
        date_from=date_from,
        date_to=date_to,
        page=page,
        limit=limit
    )
    return result
