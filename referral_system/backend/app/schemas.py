"""
Pydantic schemas for request/response validation
"""
from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional, List
from datetime import datetime
from decimal import Decimal


# ============== User Schemas ==============
class UserBase(BaseModel):
    telegram_id: int
    username: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[EmailStr] = None


class UserCreate(UserBase):
    referred_by_code: Optional[str] = None
    device_id: Optional[str] = None
    ip_address: Optional[str] = None


class UserResponse(UserBase):
    id: int
    referral_code: str
    user_type: str
    is_active: bool
    is_blocked: bool
    is_suspicious: bool
    total_spent: Decimal
    total_orders: int
    join_date: datetime
    
    class Config:
        from_attributes = True


# ============== Referral Schemas ==============
class ReferralClick(BaseModel):
    referral_code: str
    telegram_id: Optional[int] = None
    ip_address: Optional[str] = None


class ReferralStats(BaseModel):
    total_clicks: int
    total_referrals: int
    level1_referrals: int
    level2_referrals: int
    total_buyers: int
    conversion_rate: Decimal
    total_commission_earned: Decimal
    total_commission_paid: Decimal
    pending_commission: Decimal
    
    class Config:
        from_attributes = True


# ============== Order Schemas ==============
class OrderCreate(BaseModel):
    user_id: int
    payment_method: str = "upi"
    upi_id: Optional[str] = None
    transaction_id: Optional[str] = None


class OrderUpdate(BaseModel):
    payment_status: str
    transaction_id: Optional[str] = None
    paid_at: Optional[datetime] = None


class OrderResponse(BaseModel):
    id: int
    order_id: str
    user_id: int
    plan_name: str
    selling_price: Decimal
    making_cost: Decimal
    profit: Decimal
    payment_method: str
    payment_status: str
    referral_source: Optional[int]
    is_wallet_payment: bool
    commission_eligible: bool
    commission_processed: bool
    created_at: datetime
    paid_at: Optional[datetime]
    
    class Config:
        from_attributes = True


# ============== Wallet Schemas ==============
class WalletResponse(BaseModel):
    id: int
    user_id: int
    total_balance: Decimal
    withdrawable_balance: Decimal
    pending_balance: Decimal
    total_earned: Decimal
    total_withdrawn: Decimal
    
    class Config:
        from_attributes = True


class WalletTransactionResponse(BaseModel):
    id: int
    transaction_type: str
    amount: Decimal
    balance_before: Decimal
    balance_after: Decimal
    status: str
    referral_level: Optional[int]
    description: Optional[str]
    available_at: Optional[datetime]
    created_at: datetime
    
    class Config:
        from_attributes = True


# ============== Withdrawal Schemas ==============
class WithdrawalCreate(BaseModel):
    amount: Decimal = Field(..., gt=0)
    withdrawal_method: str = "upi"
    upi_id: Optional[str] = None
    bank_account: Optional[str] = None
    ifsc_code: Optional[str] = None
    account_holder_name: Optional[str] = None
    
    @validator('amount')
    def validate_amount(cls, v):
        if v < 500:
            raise ValueError('Minimum withdrawal amount is ₹500')
        return v


class WithdrawalUpdate(BaseModel):
    status: str
    payment_reference: Optional[str] = None
    rejection_reason: Optional[str] = None
    admin_notes: Optional[str] = None


class WithdrawalResponse(BaseModel):
    id: int
    withdrawal_id: str
    user_id: int
    amount: Decimal
    withdrawal_method: str
    upi_id: Optional[str]
    status: str
    requested_at: datetime
    approved_at: Optional[datetime]
    paid_at: Optional[datetime]
    rejection_reason: Optional[str]
    
    class Config:
        from_attributes = True


# ============== Admin Schemas ==============
class AdminLogin(BaseModel):
    telegram_id: int
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class DashboardStats(BaseModel):
    new_users_today: int
    buyers_today: int
    revenue_today: Decimal
    net_profit_today: Decimal
    referral_payout_today: Decimal
    active_referrers_today: int
    total_users: int
    total_buyers: int
    total_revenue: Decimal
    total_profit: Decimal
    pending_withdrawals: int
    pending_withdrawal_amount: Decimal


class UserManagementFilter(BaseModel):
    search: Optional[str] = None
    user_type: Optional[str] = None
    is_buyer: Optional[bool] = None
    is_suspicious: Optional[bool] = None
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None
    page: int = 1
    limit: int = 50


class OrderFilter(BaseModel):
    search: Optional[str] = None
    payment_status: Optional[str] = None
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None
    page: int = 1
    limit: int = 50


class ReferrerPerformance(BaseModel):
    user_id: int
    telegram_id: int
    username: Optional[str]
    first_name: Optional[str]
    referral_code: str
    stats: ReferralStats
    
    class Config:
        from_attributes = True


class FraudFlagCreate(BaseModel):
    user_id: int
    flag_type: str
    severity: str = "medium"
    description: Optional[str] = None


class FraudFlagResponse(BaseModel):
    id: int
    user_id: int
    flag_type: str
    severity: str
    description: Optional[str]
    auto_detected: bool
    resolved: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


class SystemSettingUpdate(BaseModel):
    setting_value: str


class SystemSettingResponse(BaseModel):
    id: int
    setting_key: str
    setting_value: str
    setting_type: str
    description: Optional[str]
    updated_at: datetime
    
    class Config:
        from_attributes = True


# ============== Pagination ==============
class PaginatedResponse(BaseModel):
    total: int
    page: int
    limit: int
    pages: int
    data: List[dict]


# ============== Generic Response ==============
class MessageResponse(BaseModel):
    message: str
    success: bool = True
    data: Optional[dict] = None
