"""
Main API routers - Users, Orders, Referrals, Wallet, Withdrawals, Fraud Detection
"""
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from typing import Optional
from ..database import get_db
from ..models import User
from ..schemas import *
from ..auth import get_current_user, get_current_admin, log_admin_action
from ..services import (
    ReferralService, PaymentService, WalletService,
    FraudDetectionService, AdminService
)

# User Management Router
user_router = APIRouter(prefix="/users", tags=["Users"])

@user_router.post("/create", response_model=UserResponse)
async def create_user(
    user_data: UserCreate,
    request: Request,
    db: Session = Depends(get_db)
):
    """Create a new user (called from Telegram bot)"""
    try:
        user = ReferralService.create_user_with_referral(
            db=db,
            telegram_id=user_data.telegram_id,
            username=user_data.username,
            first_name=user_data.first_name,
            last_name=user_data.last_name,
            referred_by_code=user_data.referred_by_code,
            device_id=user_data.device_id,
            ip_address=user_data.ip_address or request.client.host
        )
        return user
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@user_router.get("/{telegram_id}", response_model=UserResponse)
async def get_user(telegram_id: int, db: Session = Depends(get_db)):
    """Get user by telegram ID"""
    user = db.query(User).filter(User.telegram_id == telegram_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@user_router.get("/{telegram_id}/referral-stats")
async def get_user_referral_stats(telegram_id: int, db: Session = Depends(get_db)):
    """Get user's referral statistics"""
    user = db.query(User).filter(User.telegram_id == telegram_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    stats = ReferralService.get_referral_stats(db, user.id)
    return stats


@user_router.get("/{telegram_id}/referral-tree")
async def get_user_referral_tree(telegram_id: int, db: Session = Depends(get_db)):
    """Get user's complete referral tree"""
    user = db.query(User).filter(User.telegram_id == telegram_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    tree = ReferralService.get_referral_tree(db, user.id)
    return tree


# Order Management Router
order_router = APIRouter(prefix="/orders", tags=["Orders"])

@order_router.post("/create", response_model=OrderResponse)
async def create_order(
    order_data: OrderCreate,
    db: Session = Depends(get_db)
):
    """Create a new order"""
    try:
        order = PaymentService.create_order(
            db=db,
            user_id=order_data.user_id,
            payment_method=order_data.payment_method,
            upi_id=order_data.upi_id,
            transaction_id=order_data.transaction_id
        )
        return order
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@order_router.post("/{order_id}/payment-success", response_model=OrderResponse)
async def process_payment_success(
    order_id: str,
    transaction_id: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Process successful payment"""
    try:
        order = PaymentService.process_successful_payment(
            db=db,
            order_id=order_id,
            transaction_id=transaction_id
        )
        
        # Run fraud checks
        if order.upi_id:
            FraudDetectionService.run_fraud_checks(db, order.user_id, order.upi_id)
        
        return order
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@order_router.get("/{order_id}", response_model=OrderResponse)
async def get_order(order_id: str, db: Session = Depends(get_db)):
    """Get order by ID"""
    from ..models import Order
    order = db.query(Order).filter(Order.order_id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return order


# Wallet Router
wallet_router = APIRouter(prefix="/wallet", tags=["Wallet"])

@wallet_router.get("/{user_id}", response_model=WalletResponse)
async def get_wallet(user_id: int, db: Session = Depends(get_db)):
    """Get user wallet"""
    wallet = WalletService.get_wallet(db, user_id)
    return wallet


@wallet_router.get("/{user_id}/transactions")
async def get_wallet_transactions(
    user_id: int,
    limit: int = 50,
    offset: int = 0,
    db: Session = Depends(get_db)
):
    """Get wallet transaction history"""
    transactions = WalletService.get_transaction_history(db, user_id, limit, offset)
    return [
        {
            'id': t.id,
            'transaction_type': t.transaction_type,
            'amount': float(t.amount),
            'balance_before': float(t.balance_before),
            'balance_after': float(t.balance_after),
            'status': t.status,
            'referral_level': t.referral_level,
            'description': t.description,
            'available_at': t.available_at,
            'created_at': t.created_at
        }
        for t in transactions
    ]


# Withdrawal Router
withdrawal_router = APIRouter(prefix="/withdrawals", tags=["Withdrawals"])

@withdrawal_router.post("/create", response_model=WithdrawalResponse)
async def create_withdrawal_request(
    withdrawal_data: WithdrawalCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a withdrawal request"""
    try:
        withdrawal = WalletService.create_withdrawal_request(
            db=db,
            user_id=current_user.id,
            amount=withdrawal_data.amount,
            withdrawal_method=withdrawal_data.withdrawal_method,
            upi_id=withdrawal_data.upi_id,
            bank_account=withdrawal_data.bank_account,
            ifsc_code=withdrawal_data.ifsc_code,
            account_holder_name=withdrawal_data.account_holder_name
        )
        return withdrawal
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@withdrawal_router.get("/my-withdrawals")
async def get_my_withdrawals(
    limit: int = 50,
    offset: int = 0,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get current user's withdrawal history"""
    withdrawals = WalletService.get_user_withdrawals(db, current_user.id, limit, offset)
    return withdrawals


@withdrawal_router.post("/{withdrawal_id}/cancel", response_model=WithdrawalResponse)
async def cancel_withdrawal(
    withdrawal_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Cancel a pending withdrawal"""
    try:
        withdrawal = WalletService.cancel_withdrawal(db, withdrawal_id, current_user.id)
        return withdrawal
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# Admin Withdrawal Management
@withdrawal_router.get("/admin/all")
async def get_all_withdrawals(
    status: Optional[str] = None,
    limit: int = 100,
    offset: int = 0,
    current_user: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Get all withdrawal requests (admin only)"""
    withdrawals = WalletService.get_all_withdrawals(db, status, limit, offset)
    return withdrawals


@withdrawal_router.post("/{withdrawal_id}/approve", response_model=WithdrawalResponse)
async def approve_withdrawal(
    withdrawal_id: str,
    payment_reference: Optional[str] = None,
    admin_notes: Optional[str] = None,
    current_user: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Approve a withdrawal request"""
    try:
        withdrawal = WalletService.approve_withdrawal(
            db, withdrawal_id, current_user.id, payment_reference, admin_notes
        )
        
        log_admin_action(
            db, current_user.id, "withdrawal_approved",
            f"Approved withdrawal {withdrawal_id}",
            "withdrawal", withdrawal.id
        )
        
        return withdrawal
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@withdrawal_router.post("/{withdrawal_id}/paid", response_model=WithdrawalResponse)
async def mark_withdrawal_paid(
    withdrawal_id: str,
    payment_reference: Optional[str] = None,
    current_user: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Mark withdrawal as paid"""
    try:
        withdrawal = WalletService.mark_withdrawal_paid(db, withdrawal_id, payment_reference)
        
        log_admin_action(
            db, current_user.id, "withdrawal_paid",
            f"Marked withdrawal {withdrawal_id} as paid",
            "withdrawal", withdrawal.id
        )
        
        return withdrawal
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@withdrawal_router.post("/{withdrawal_id}/reject", response_model=WithdrawalResponse)
async def reject_withdrawal(
    withdrawal_id: str,
    rejection_reason: str,
    admin_notes: Optional[str] = None,
    current_user: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Reject a withdrawal request"""
    try:
        withdrawal = WalletService.reject_withdrawal(
            db, withdrawal_id, current_user.id, rejection_reason, admin_notes
        )
        
        log_admin_action(
            db, current_user.id, "withdrawal_rejected",
            f"Rejected withdrawal {withdrawal_id}: {rejection_reason}",
            "withdrawal", withdrawal.id
        )
        
        return withdrawal
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@withdrawal_router.get("/admin/statistics")
async def get_withdrawal_statistics(
    current_user: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Get withdrawal statistics"""
    return WalletService.get_withdrawal_statistics(db)


# Fraud Detection Router
fraud_router = APIRouter(prefix="/fraud", tags=["Fraud Detection"])

@fraud_router.get("/flags")
async def get_fraud_flags(
    severity: Optional[str] = None,
    resolved: Optional[bool] = None,
    limit: int = 100,
    offset: int = 0,
    current_user: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Get all fraud flags"""
    flags = FraudDetectionService.get_all_flags(db, severity, resolved, limit, offset)
    return flags


@fraud_router.get("/user/{user_id}/flags")
async def get_user_fraud_flags(
    user_id: int,
    include_resolved: bool = False,
    current_user: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Get fraud flags for a specific user"""
    flags = FraudDetectionService.get_user_flags(db, user_id, include_resolved)
    return flags


@fraud_router.post("/flags/create", response_model=FraudFlagResponse)
async def create_fraud_flag(
    flag_data: FraudFlagCreate,
    current_user: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Create a manual fraud flag"""
    flag = FraudDetectionService.create_flag(
        db=db,
        user_id=flag_data.user_id,
        flag_type=flag_data.flag_type,
        severity=flag_data.severity,
        description=flag_data.description or "Manual flag",
        auto_detected=False,
        flagged_by=current_user.id
    )
    
    log_admin_action(
        db, current_user.id, "fraud_flag_created",
        f"Created fraud flag for user {flag_data.user_id}",
        "fraud_flag", flag.id
    )
    
    return flag


@fraud_router.post("/flags/{flag_id}/resolve")
async def resolve_fraud_flag(
    flag_id: int,
    resolution_notes: Optional[str] = None,
    current_user: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Resolve a fraud flag"""
    try:
        flag = FraudDetectionService.resolve_flag(db, flag_id, current_user.id, resolution_notes)
        
        log_admin_action(
            db, current_user.id, "fraud_flag_resolved",
            f"Resolved fraud flag {flag_id}",
            "fraud_flag", flag.id
        )
        
        return flag
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@fraud_router.post("/user/{user_id}/block")
async def block_user(
    user_id: int,
    reason: str,
    current_user: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Block a user account"""
    try:
        FraudDetectionService.block_user(db, user_id, current_user.id, reason)
        
        log_admin_action(
            db, current_user.id, "user_blocked",
            f"Blocked user {user_id}: {reason}",
            "user", user_id
        )
        
        return {"message": "User blocked successfully"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@fraud_router.post("/user/{user_id}/unblock")
async def unblock_user(
    user_id: int,
    current_user: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Unblock a user account"""
    try:
        FraudDetectionService.unblock_user(db, user_id, current_user.id)
        
        log_admin_action(
            db, current_user.id, "user_unblocked",
            f"Unblocked user {user_id}",
            "user", user_id
        )
        
        return {"message": "User unblocked successfully"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@fraud_router.post("/user/{user_id}/run-checks")
async def run_fraud_checks(
    user_id: int,
    upi_id: Optional[str] = None,
    current_user: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Run fraud detection checks on a user"""
    flags = FraudDetectionService.run_fraud_checks(db, user_id, upi_id)
    return {"flags_created": flags}


# System Settings Router
settings_router = APIRouter(prefix="/settings", tags=["System Settings"])

@settings_router.get("/all")
async def get_all_settings(
    current_user: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Get all system settings"""
    settings = AdminService.get_system_settings(db)
    return settings


@settings_router.put("/{setting_key}")
async def update_setting(
    setting_key: str,
    update_data: SystemSettingUpdate,
    current_user: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Update a system setting"""
    try:
        setting = AdminService.update_system_setting(
            db, setting_key, update_data.setting_value, current_user.id
        )
        
        log_admin_action(
            db, current_user.id, "setting_updated",
            f"Updated setting {setting_key} to {update_data.setting_value}",
            "system_setting", setting.id
        )
        
        return setting
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# Referral Tracking Router
referral_router = APIRouter(prefix="/referrals", tags=["Referrals"])

@referral_router.post("/track-click")
async def track_referral_click(
    referral_data: ReferralClick,
    request: Request,
    db: Session = Depends(get_db)
):
    """Track a referral link click"""
    success = ReferralService.track_referral_click(
        db=db,
        referral_code=referral_data.referral_code,
        ip_address=referral_data.ip_address or request.client.host
    )
    
    return {"success": success}


@referral_router.get("/leaderboard")
async def get_referral_leaderboard(
    limit: int = 10,
    db: Session = Depends(get_db)
):
    """Get top referrers leaderboard"""
    leaderboard = ReferralService.get_top_referrers(db, limit)
    return leaderboard
