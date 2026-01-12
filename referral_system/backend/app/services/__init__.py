"""
Service package initializer
"""
from .referral_service import ReferralService
from .payment_service import PaymentService
from .wallet_service import WalletService
from .fraud_service import FraudDetectionService
from .admin_service import AdminService

__all__ = [
    'ReferralService',
    'PaymentService',
    'WalletService',
    'FraudDetectionService',
    'AdminService'
]
