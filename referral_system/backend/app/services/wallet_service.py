"""
Wallet and withdrawal management service
"""
from sqlalchemy.orm import Session
from sqlalchemy import and_, desc
from datetime import datetime
from decimal import Decimal
from typing import Optional, List
import uuid
from ..models import Wallet, WalletTransaction, Withdrawal, User
from ..config import settings


class WalletService:
    """Service for wallet operations"""
    
    @staticmethod
    def get_wallet(db: Session, user_id: int) -> Optional[Wallet]:
        """Get user wallet"""
        wallet = db.query(Wallet).filter(Wallet.user_id == user_id).first()
        
        if not wallet:
            # Create wallet if it doesn't exist
            wallet = Wallet(user_id=user_id)
            db.add(wallet)
            db.commit()
            db.refresh(wallet)
        
        return wallet
    
    @staticmethod
    def get_transaction_history(
        db: Session,
        user_id: int,
        limit: int = 50,
        offset: int = 0
    ) -> List[WalletTransaction]:
        """Get wallet transaction history"""
        transactions = db.query(WalletTransaction).filter(
            WalletTransaction.user_id == user_id
        ).order_by(desc(WalletTransaction.created_at)).offset(offset).limit(limit).all()
        
        return transactions
    
    @staticmethod
    def create_withdrawal_request(
        db: Session,
        user_id: int,
        amount: Decimal,
        withdrawal_method: str = "upi",
        upi_id: Optional[str] = None,
        bank_account: Optional[str] = None,
        ifsc_code: Optional[str] = None,
        account_holder_name: Optional[str] = None
    ) -> Withdrawal:
        """Create a withdrawal request"""
        # Validate minimum amount
        if amount < Decimal(str(settings.MIN_WITHDRAWAL_AMOUNT)):
            raise ValueError(f"Minimum withdrawal amount is ₹{settings.MIN_WITHDRAWAL_AMOUNT}")
        
        # Get wallet
        wallet = WalletService.get_wallet(db, user_id)
        
        # Check if sufficient balance
        if wallet.withdrawable_balance < amount:
            raise ValueError("Insufficient withdrawable balance")
        
        # Check for pending withdrawals
        pending_withdrawals = db.query(Withdrawal).filter(
            and_(
                Withdrawal.user_id == user_id,
                Withdrawal.status == "pending"
            )
        ).count()
        
        if pending_withdrawals > 0:
            raise ValueError("You already have a pending withdrawal request")
        
        # Generate withdrawal ID
        withdrawal_id = f"WD{datetime.utcnow().strftime('%Y%m%d')}{str(uuid.uuid4().hex[:8]).upper()}"
        
        # Create withdrawal request
        withdrawal = Withdrawal(
            withdrawal_id=withdrawal_id,
            user_id=user_id,
            wallet_id=wallet.id,
            amount=amount,
            withdrawal_method=withdrawal_method,
            upi_id=upi_id,
            bank_account=bank_account,
            ifsc_code=ifsc_code,
            account_holder_name=account_holder_name,
            status="pending"
        )
        
        db.add(withdrawal)
        
        # Deduct from withdrawable balance (but keep in total for now)
        balance_before = wallet.total_balance
        wallet.withdrawable_balance -= amount
        
        # Create transaction record
        transaction = WalletTransaction(
            wallet_id=wallet.id,
            user_id=user_id,
            transaction_type="withdrawal",
            amount=amount,
            balance_before=balance_before,
            balance_after=balance_before,  # Total doesn't change until approved
            status="pending",
            description=f"Withdrawal request {withdrawal_id}",
            created_at=datetime.utcnow()
        )
        
        db.add(transaction)
        db.commit()
        db.refresh(withdrawal)
        
        return withdrawal
    
    @staticmethod
    def approve_withdrawal(
        db: Session,
        withdrawal_id: str,
        admin_id: int,
        payment_reference: Optional[str] = None,
        admin_notes: Optional[str] = None
    ) -> Withdrawal:
        """Approve a withdrawal request"""
        withdrawal = db.query(Withdrawal).filter(
            Withdrawal.withdrawal_id == withdrawal_id
        ).first()
        
        if not withdrawal:
            raise ValueError("Withdrawal request not found")
        
        if withdrawal.status != "pending":
            raise ValueError("Withdrawal request is not pending")
        
        # Update withdrawal status
        withdrawal.status = "approved"
        withdrawal.approved_at = datetime.utcnow()
        withdrawal.approved_by = admin_id
        withdrawal.payment_reference = payment_reference
        withdrawal.admin_notes = admin_notes
        
        db.commit()
        db.refresh(withdrawal)
        
        return withdrawal
    
    @staticmethod
    def mark_withdrawal_paid(
        db: Session,
        withdrawal_id: str,
        payment_reference: Optional[str] = None
    ) -> Withdrawal:
        """Mark withdrawal as paid"""
        withdrawal = db.query(Withdrawal).filter(
            Withdrawal.withdrawal_id == withdrawal_id
        ).first()
        
        if not withdrawal:
            raise ValueError("Withdrawal request not found")
        
        if withdrawal.status not in ["pending", "approved"]:
            raise ValueError("Withdrawal cannot be marked as paid")
        
        # Update withdrawal
        withdrawal.status = "paid"
        withdrawal.paid_at = datetime.utcnow()
        if payment_reference:
            withdrawal.payment_reference = payment_reference
        
        # Update wallet
        wallet = db.query(Wallet).filter(Wallet.id == withdrawal.wallet_id).first()
        balance_before = wallet.total_balance
        wallet.total_balance -= withdrawal.amount
        wallet.total_withdrawn += withdrawal.amount
        balance_after = wallet.total_balance
        
        # Update transaction
        transaction = db.query(WalletTransaction).filter(
            and_(
                WalletTransaction.wallet_id == wallet.id,
                WalletTransaction.transaction_type == "withdrawal",
                WalletTransaction.description.like(f"%{withdrawal_id}%"),
                WalletTransaction.status == "pending"
            )
        ).first()
        
        if transaction:
            transaction.status = "completed"
            transaction.balance_after = balance_after
            transaction.credited_at = datetime.utcnow()
        
        db.commit()
        db.refresh(withdrawal)
        
        return withdrawal
    
    @staticmethod
    def reject_withdrawal(
        db: Session,
        withdrawal_id: str,
        admin_id: int,
        rejection_reason: str,
        admin_notes: Optional[str] = None
    ) -> Withdrawal:
        """Reject a withdrawal request"""
        withdrawal = db.query(Withdrawal).filter(
            Withdrawal.withdrawal_id == withdrawal_id
        ).first()
        
        if not withdrawal:
            raise ValueError("Withdrawal request not found")
        
        if withdrawal.status != "pending":
            raise ValueError("Withdrawal request is not pending")
        
        # Update withdrawal
        withdrawal.status = "rejected"
        withdrawal.approved_at = datetime.utcnow()
        withdrawal.approved_by = admin_id
        withdrawal.rejection_reason = rejection_reason
        withdrawal.admin_notes = admin_notes
        
        # Refund to withdrawable balance
        wallet = db.query(Wallet).filter(Wallet.id == withdrawal.wallet_id).first()
        wallet.withdrawable_balance += withdrawal.amount
        
        # Cancel transaction
        transaction = db.query(WalletTransaction).filter(
            and_(
                WalletTransaction.wallet_id == wallet.id,
                WalletTransaction.transaction_type == "withdrawal",
                WalletTransaction.description.like(f"%{withdrawal_id}%"),
                WalletTransaction.status == "pending"
            )
        ).first()
        
        if transaction:
            transaction.status = "cancelled"
        
        db.commit()
        db.refresh(withdrawal)
        
        return withdrawal
    
    @staticmethod
    def cancel_withdrawal(
        db: Session,
        withdrawal_id: str,
        user_id: int
    ) -> Withdrawal:
        """User cancels their own withdrawal request"""
        withdrawal = db.query(Withdrawal).filter(
            and_(
                Withdrawal.withdrawal_id == withdrawal_id,
                Withdrawal.user_id == user_id
            )
        ).first()
        
        if not withdrawal:
            raise ValueError("Withdrawal request not found")
        
        if withdrawal.status != "pending":
            raise ValueError("Only pending withdrawals can be cancelled")
        
        # Update withdrawal
        withdrawal.status = "cancelled"
        
        # Refund to withdrawable balance
        wallet = db.query(Wallet).filter(Wallet.id == withdrawal.wallet_id).first()
        wallet.withdrawable_balance += withdrawal.amount
        
        # Cancel transaction
        transaction = db.query(WalletTransaction).filter(
            and_(
                WalletTransaction.wallet_id == wallet.id,
                WalletTransaction.transaction_type == "withdrawal",
                WalletTransaction.description.like(f"%{withdrawal_id}%"),
                WalletTransaction.status == "pending"
            )
        ).first()
        
        if transaction:
            transaction.status = "cancelled"
        
        db.commit()
        db.refresh(withdrawal)
        
        return withdrawal
    
    @staticmethod
    def get_user_withdrawals(
        db: Session,
        user_id: int,
        limit: int = 50,
        offset: int = 0
    ) -> List[Withdrawal]:
        """Get user's withdrawal history"""
        withdrawals = db.query(Withdrawal).filter(
            Withdrawal.user_id == user_id
        ).order_by(desc(Withdrawal.requested_at)).offset(offset).limit(limit).all()
        
        return withdrawals
    
    @staticmethod
    def get_all_withdrawals(
        db: Session,
        status: Optional[str] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[Withdrawal]:
        """Get all withdrawal requests (admin)"""
        query = db.query(Withdrawal)
        
        if status:
            query = query.filter(Withdrawal.status == status)
        
        withdrawals = query.order_by(desc(Withdrawal.requested_at)).offset(offset).limit(limit).all()
        
        return withdrawals
    
    @staticmethod
    def get_withdrawal_statistics(db: Session) -> dict:
        """Get withdrawal statistics"""
        from sqlalchemy import func
        
        total_withdrawals = db.query(func.count(Withdrawal.id)).scalar() or 0
        
        pending_count = db.query(func.count(Withdrawal.id)).filter(
            Withdrawal.status == "pending"
        ).scalar() or 0
        
        pending_amount = db.query(func.sum(Withdrawal.amount)).filter(
            Withdrawal.status == "pending"
        ).scalar() or Decimal('0')
        
        approved_count = db.query(func.count(Withdrawal.id)).filter(
            Withdrawal.status == "approved"
        ).scalar() or 0
        
        paid_count = db.query(func.count(Withdrawal.id)).filter(
            Withdrawal.status == "paid"
        ).scalar() or 0
        
        paid_amount = db.query(func.sum(Withdrawal.amount)).filter(
            Withdrawal.status == "paid"
        ).scalar() or Decimal('0')
        
        rejected_count = db.query(func.count(Withdrawal.id)).filter(
            Withdrawal.status == "rejected"
        ).scalar() or 0
        
        return {
            'total_withdrawals': total_withdrawals,
            'pending_count': pending_count,
            'pending_amount': float(pending_amount),
            'approved_count': approved_count,
            'paid_count': paid_count,
            'paid_amount': float(paid_amount),
            'rejected_count': rejected_count
        }
