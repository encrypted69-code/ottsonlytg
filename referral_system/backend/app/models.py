"""
SQLAlchemy database models
"""
from sqlalchemy import Column, Integer, BigInteger, String, Boolean, DECIMAL, TIMESTAMP, Text, ForeignKey, CheckConstraint, Index
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import JSONB
from datetime import datetime
from .database import Base


class User(Base):
    """User model for customers, referrers, and admins"""
    __tablename__ = "users"
    
    id = Column(BigInteger, primary_key=True, index=True)
    telegram_id = Column(BigInteger, unique=True, nullable=False, index=True)
    username = Column(String(255))
    first_name = Column(String(255))
    last_name = Column(String(255))
    phone = Column(String(20))
    email = Column(String(255))
    referred_by = Column(BigInteger, ForeignKey('users.id', ondelete='SET NULL'))
    referral_level = Column(Integer, default=0)
    referral_code = Column(String(50), unique=True, nullable=False, index=True)
    user_type = Column(String(20), default='customer')
    is_active = Column(Boolean, default=True)
    is_blocked = Column(Boolean, default=False)
    is_suspicious = Column(Boolean, default=False)
    device_id = Column(String(255))
    ip_address = Column(String(45))
    total_spent = Column(DECIMAL(10, 2), default=0.00)
    total_orders = Column(Integer, default=0)
    join_date = Column(TIMESTAMP, default=datetime.utcnow)
    last_active = Column(TIMESTAMP, default=datetime.utcnow)
    created_at = Column(TIMESTAMP, default=datetime.utcnow)
    updated_at = Column(TIMESTAMP, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    referrer = relationship("User", remote_side=[id], backref="referrals")
    wallet = relationship("Wallet", back_populates="user", uselist=False)
    orders = relationship("Order", back_populates="user")
    
    __table_args__ = (
        CheckConstraint('referral_level IN (0, 1, 2)', name='check_referral_level'),
        CheckConstraint("user_type IN ('customer', 'referrer', 'admin', 'super_admin')", name='check_user_type'),
    )


class Referral(Base):
    """Referral tracking model"""
    __tablename__ = "referrals"
    
    id = Column(BigInteger, primary_key=True, index=True)
    referrer_id = Column(BigInteger, ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    referred_user_id = Column(BigInteger, ForeignKey('users.id', ondelete='SET NULL'), index=True)
    referral_code = Column(String(50), nullable=False, index=True)
    clicked_at = Column(TIMESTAMP, default=datetime.utcnow)
    converted = Column(Boolean, default=False, index=True)
    converted_at = Column(TIMESTAMP)
    level = Column(Integer, default=1)
    created_at = Column(TIMESTAMP, default=datetime.utcnow)
    
    __table_args__ = (
        CheckConstraint('level IN (1, 2)', name='check_level'),
    )


class Order(Base):
    """Order model for purchases"""
    __tablename__ = "orders"
    
    id = Column(BigInteger, primary_key=True, index=True)
    order_id = Column(String(100), unique=True, nullable=False, index=True)
    user_id = Column(BigInteger, ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    plan_name = Column(String(255), nullable=False, default='Combo OTT Plan')
    selling_price = Column(DECIMAL(10, 2), nullable=False, default=135.00)
    making_cost = Column(DECIMAL(10, 2), nullable=False, default=42.00)
    profit = Column(DECIMAL(10, 2), nullable=False, default=93.00)
    payment_method = Column(String(50), default='upi')
    payment_status = Column(String(50), default='pending', index=True)
    upi_id = Column(String(255))
    transaction_id = Column(String(255))
    referral_source = Column(BigInteger, ForeignKey('users.id', ondelete='SET NULL'), index=True)
    is_wallet_payment = Column(Boolean, default=False)
    commission_eligible = Column(Boolean, default=True)
    commission_processed = Column(Boolean, default=False)
    created_at = Column(TIMESTAMP, default=datetime.utcnow, index=True)
    paid_at = Column(TIMESTAMP)
    updated_at = Column(TIMESTAMP, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", foreign_keys=[user_id], back_populates="orders")
    
    __table_args__ = (
        CheckConstraint("payment_method IN ('upi', 'wallet', 'other')", name='check_payment_method'),
        CheckConstraint("payment_status IN ('pending', 'success', 'failed', 'refunded')", name='check_payment_status'),
        Index('idx_commission_processing', 'commission_eligible', 'commission_processed'),
    )


class Wallet(Base):
    """Wallet model for user balances"""
    __tablename__ = "wallets"
    
    id = Column(BigInteger, primary_key=True, index=True)
    user_id = Column(BigInteger, ForeignKey('users.id', ondelete='CASCADE'), unique=True, nullable=False, index=True)
    total_balance = Column(DECIMAL(10, 2), default=0.00)
    withdrawable_balance = Column(DECIMAL(10, 2), default=0.00)
    pending_balance = Column(DECIMAL(10, 2), default=0.00)
    total_earned = Column(DECIMAL(10, 2), default=0.00)
    total_withdrawn = Column(DECIMAL(10, 2), default=0.00)
    created_at = Column(TIMESTAMP, default=datetime.utcnow)
    updated_at = Column(TIMESTAMP, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="wallet")
    transactions = relationship("WalletTransaction", back_populates="wallet")


class WalletTransaction(Base):
    """Wallet transaction model"""
    __tablename__ = "wallet_transactions"
    
    id = Column(BigInteger, primary_key=True, index=True)
    wallet_id = Column(BigInteger, ForeignKey('wallets.id', ondelete='CASCADE'), nullable=False, index=True)
    user_id = Column(BigInteger, ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    order_id = Column(BigInteger, ForeignKey('orders.id', ondelete='SET NULL'), index=True)
    transaction_type = Column(String(50), nullable=False, index=True)
    amount = Column(DECIMAL(10, 2), nullable=False)
    balance_before = Column(DECIMAL(10, 2), nullable=False)
    balance_after = Column(DECIMAL(10, 2), nullable=False)
    status = Column(String(50), default='pending', index=True)
    referral_level = Column(Integer)
    description = Column(Text)
    credited_at = Column(TIMESTAMP)
    available_at = Column(TIMESTAMP, index=True)
    created_at = Column(TIMESTAMP, default=datetime.utcnow)
    
    # Relationships
    wallet = relationship("Wallet", back_populates="transactions")
    
    __table_args__ = (
        CheckConstraint("transaction_type IN ('commission_credit', 'withdrawal', 'refund', 'deduction', 'purchase')", name='check_transaction_type'),
        CheckConstraint("status IN ('pending', 'completed', 'cancelled')", name='check_status'),
        CheckConstraint('referral_level IN (1, 2) OR referral_level IS NULL', name='check_referral_level'),
    )


class Withdrawal(Base):
    """Withdrawal request model"""
    __tablename__ = "withdrawals"
    
    id = Column(BigInteger, primary_key=True, index=True)
    withdrawal_id = Column(String(100), unique=True, nullable=False)
    user_id = Column(BigInteger, ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    wallet_id = Column(BigInteger, ForeignKey('wallets.id', ondelete='CASCADE'), nullable=False, index=True)
    amount = Column(DECIMAL(10, 2), nullable=False)
    withdrawal_method = Column(String(50), default='upi')
    upi_id = Column(String(255))
    bank_account = Column(String(255))
    ifsc_code = Column(String(20))
    account_holder_name = Column(String(255))
    status = Column(String(50), default='pending', index=True)
    requested_at = Column(TIMESTAMP, default=datetime.utcnow, index=True)
    approved_at = Column(TIMESTAMP)
    approved_by = Column(BigInteger, ForeignKey('users.id', ondelete='SET NULL'))
    paid_at = Column(TIMESTAMP)
    payment_reference = Column(String(255))
    rejection_reason = Column(Text)
    admin_notes = Column(Text)
    created_at = Column(TIMESTAMP, default=datetime.utcnow)
    updated_at = Column(TIMESTAMP, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    __table_args__ = (
        CheckConstraint("withdrawal_method IN ('upi', 'bank', 'paytm')", name='check_withdrawal_method'),
        CheckConstraint("status IN ('pending', 'approved', 'rejected', 'paid', 'cancelled')", name='check_withdrawal_status'),
    )


class AdminLog(Base):
    """Admin action audit log"""
    __tablename__ = "admin_logs"
    
    id = Column(BigInteger, primary_key=True, index=True)
    admin_id = Column(BigInteger, ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    action_type = Column(String(100), nullable=False, index=True)
    target_type = Column(String(50))
    target_id = Column(BigInteger)
    description = Column(Text)
    ip_address = Column(String(45))
    user_agent = Column(Text)
    metadata = Column(JSONB)
    created_at = Column(TIMESTAMP, default=datetime.utcnow, index=True)


class FraudFlag(Base):
    """Fraud detection flags"""
    __tablename__ = "fraud_flags"
    
    id = Column(BigInteger, primary_key=True, index=True)
    user_id = Column(BigInteger, ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    flag_type = Column(String(100), nullable=False, index=True)
    severity = Column(String(20), default='medium', index=True)
    description = Column(Text)
    metadata = Column(JSONB)
    auto_detected = Column(Boolean, default=True)
    flagged_by = Column(BigInteger, ForeignKey('users.id', ondelete='SET NULL'))
    resolved = Column(Boolean, default=False, index=True)
    resolved_at = Column(TIMESTAMP)
    resolved_by = Column(BigInteger, ForeignKey('users.id', ondelete='SET NULL'))
    resolution_notes = Column(Text)
    created_at = Column(TIMESTAMP, default=datetime.utcnow)
    
    __table_args__ = (
        CheckConstraint("flag_type IN ('duplicate_upi', 'duplicate_device', 'duplicate_ip', 'high_referral_low_conversion', 'suspicious_pattern', 'manual_flag')", name='check_flag_type'),
        CheckConstraint("severity IN ('low', 'medium', 'high', 'critical')", name='check_severity'),
    )


class SystemSetting(Base):
    """System configuration settings"""
    __tablename__ = "system_settings"
    
    id = Column(Integer, primary_key=True, index=True)
    setting_key = Column(String(100), unique=True, nullable=False)
    setting_value = Column(Text, nullable=False)
    setting_type = Column(String(50), default='string')
    description = Column(Text)
    updated_by = Column(BigInteger, ForeignKey('users.id', ondelete='SET NULL'))
    created_at = Column(TIMESTAMP, default=datetime.utcnow)
    updated_at = Column(TIMESTAMP, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    __table_args__ = (
        CheckConstraint("setting_type IN ('string', 'number', 'boolean', 'json')", name='check_setting_type'),
    )


class ReferralStats(Base):
    """Cached referral statistics"""
    __tablename__ = "referral_stats"
    
    id = Column(BigInteger, primary_key=True, index=True)
    user_id = Column(BigInteger, ForeignKey('users.id', ondelete='CASCADE'), unique=True, nullable=False, index=True)
    total_clicks = Column(Integer, default=0)
    total_referrals = Column(Integer, default=0)
    level1_referrals = Column(Integer, default=0)
    level2_referrals = Column(Integer, default=0)
    total_buyers = Column(Integer, default=0)
    conversion_rate = Column(DECIMAL(5, 2), default=0.00)
    total_commission_earned = Column(DECIMAL(10, 2), default=0.00)
    total_commission_paid = Column(DECIMAL(10, 2), default=0.00)
    pending_commission = Column(DECIMAL(10, 2), default=0.00)
    last_updated = Column(TIMESTAMP, default=datetime.utcnow)
