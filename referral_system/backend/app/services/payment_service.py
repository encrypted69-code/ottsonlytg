"""
Payment processing and commission calculation service
"""
from sqlalchemy.orm import Session
from sqlalchemy import and_
from datetime import datetime, timedelta
from decimal import Decimal
from typing import Optional
import uuid
from ..models import Order, User, Wallet, WalletTransaction
from ..config import settings
from .referral_service import ReferralService


class PaymentService:
    """Service for payment processing and commission calculation"""
    
    @staticmethod
    def create_order(
        db: Session,
        user_id: int,
        payment_method: str = "upi",
        upi_id: Optional[str] = None,
        transaction_id: Optional[str] = None
    ) -> Order:
        """Create a new order"""
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise ValueError("User not found")
        
        # Generate unique order ID
        order_id = f"ORD{datetime.utcnow().strftime('%Y%m%d')}{str(uuid.uuid4().hex[:8]).upper()}"
        
        # Determine if wallet payment
        is_wallet_payment = payment_method == "wallet"
        
        # Commission not eligible for wallet payments
        commission_eligible = not is_wallet_payment
        
        # Get referral source
        referral_source = user.referred_by
        
        order = Order(
            order_id=order_id,
            user_id=user_id,
            plan_name="Combo OTT Plan",
            selling_price=Decimal(str(settings.COMBO_SELLING_PRICE)),
            making_cost=Decimal(str(settings.COMBO_MAKING_COST)),
            profit=Decimal(str(settings.COMBO_PROFIT)),
            payment_method=payment_method,
            payment_status="pending",
            upi_id=upi_id,
            transaction_id=transaction_id,
            referral_source=referral_source,
            is_wallet_payment=is_wallet_payment,
            commission_eligible=commission_eligible
        )
        
        db.add(order)
        db.commit()
        db.refresh(order)
        
        return order
    
    @staticmethod
    def process_successful_payment(
        db: Session,
        order_id: str,
        transaction_id: Optional[str] = None
    ) -> Order:
        """
        Process a successful payment
        
        This function:
        1. Updates order status
        2. Updates user stats
        3. Marks referral as converted
        4. Creates pending commission entries (to be credited after 24h)
        """
        order = db.query(Order).filter(Order.order_id == order_id).first()
        if not order:
            raise ValueError("Order not found")
        
        if order.payment_status == "success":
            return order  # Already processed
        
        # Update order
        order.payment_status = "success"
        order.paid_at = datetime.utcnow()
        if transaction_id:
            order.transaction_id = transaction_id
        
        # Update user stats
        user = db.query(User).filter(User.id == order.user_id).first()
        user.total_spent += order.selling_price
        user.total_orders += 1
        user.last_active = datetime.utcnow()
        
        # Mark referral as converted (first purchase)
        if user.total_orders == 1:
            ReferralService.mark_referral_converted(db, user.id)
        
        # Process commissions if eligible
        if order.commission_eligible and not order.commission_processed:
            PaymentService._create_pending_commissions(db, order)
            order.commission_processed = True
        
        db.commit()
        db.refresh(order)
        
        return order
    
    @staticmethod
    def _create_pending_commissions(db: Session, order: Order):
        """
        Create pending commission entries for referrers
        
        Business Logic:
        - Level 1 referrer: 30% of profit = ₹28
        - Level 2 referrer: 10% of profit = ₹9
        - Commission held for 24 hours before becoming withdrawable
        """
        user = db.query(User).filter(User.id == order.user_id).first()
        
        if not user or not user.referred_by:
            return
        
        # Get level 1 referrer
        level1_referrer = db.query(User).filter(User.id == user.referred_by).first()
        if level1_referrer and user.referral_level >= 1:
            PaymentService._credit_commission(
                db=db,
                user_id=level1_referrer.id,
                order_id=order.id,
                amount=Decimal(str(settings.LEVEL1_COMMISSION_AMOUNT)),
                level=1,
                description=f"Level 1 commission from order {order.order_id}"
            )
        
        # Get level 2 referrer (referrer's referrer)
        if level1_referrer and level1_referrer.referred_by:
            level2_referrer = db.query(User).filter(User.id == level1_referrer.referred_by).first()
            if level2_referrer:
                PaymentService._credit_commission(
                    db=db,
                    user_id=level2_referrer.id,
                    order_id=order.id,
                    amount=Decimal(str(settings.LEVEL2_COMMISSION_AMOUNT)),
                    level=2,
                    description=f"Level 2 commission from order {order.order_id}"
                )
    
    @staticmethod
    def _credit_commission(
        db: Session,
        user_id: int,
        order_id: int,
        amount: Decimal,
        level: int,
        description: str
    ):
        """Credit commission to user wallet (pending for 24 hours)"""
        wallet = db.query(Wallet).filter(Wallet.user_id == user_id).first()
        if not wallet:
            wallet = Wallet(user_id=user_id)
            db.add(wallet)
            db.flush()
        
        # Update wallet balances
        balance_before = wallet.total_balance
        wallet.pending_balance += amount
        wallet.total_balance += amount
        wallet.total_earned += amount
        balance_after = wallet.total_balance
        
        # Create transaction record (pending)
        available_at = datetime.utcnow() + timedelta(hours=settings.COMMISSION_HOLD_HOURS)
        
        transaction = WalletTransaction(
            wallet_id=wallet.id,
            user_id=user_id,
            order_id=order_id,
            transaction_type="commission_credit",
            amount=amount,
            balance_before=balance_before,
            balance_after=balance_after,
            status="pending",
            referral_level=level,
            description=description,
            available_at=available_at
        )
        
        db.add(transaction)
        db.commit()
    
    @staticmethod
    def process_pending_commissions(db: Session):
        """
        Process pending commissions that are past their hold period
        This should be run as a scheduled job
        """
        now = datetime.utcnow()
        
        # Find all pending transactions past their available_at time
        pending_transactions = db.query(WalletTransaction).filter(
            and_(
                WalletTransaction.status == "pending",
                WalletTransaction.available_at <= now,
                WalletTransaction.transaction_type == "commission_credit"
            )
        ).all()
        
        for transaction in pending_transactions:
            wallet = db.query(Wallet).filter(Wallet.id == transaction.wallet_id).first()
            if wallet:
                # Move from pending to withdrawable
                wallet.pending_balance -= transaction.amount
                wallet.withdrawable_balance += transaction.amount
                
                # Update transaction status
                transaction.status = "completed"
                transaction.credited_at = now
        
        db.commit()
        return len(pending_transactions)
    
    @staticmethod
    def process_wallet_payment(
        db: Session,
        user_id: int,
        amount: Decimal
    ) -> bool:
        """Process payment from user wallet"""
        wallet = db.query(Wallet).filter(Wallet.user_id == user_id).first()
        if not wallet:
            return False
        
        if wallet.withdrawable_balance < amount:
            return False
        
        # Deduct from wallet
        balance_before = wallet.total_balance
        wallet.withdrawable_balance -= amount
        wallet.total_balance -= amount
        balance_after = wallet.total_balance
        
        # Create transaction record
        transaction = WalletTransaction(
            wallet_id=wallet.id,
            user_id=user_id,
            transaction_type="purchase",
            amount=amount,
            balance_before=balance_before,
            balance_after=balance_after,
            status="completed",
            description=f"Payment from wallet",
            credited_at=datetime.utcnow()
        )
        
        db.add(transaction)
        db.commit()
        
        return True
    
    @staticmethod
    def refund_order(
        db: Session,
        order_id: str,
        reason: Optional[str] = None
    ) -> Order:
        """
        Refund an order and reverse commissions
        """
        order = db.query(Order).filter(Order.order_id == order_id).first()
        if not order:
            raise ValueError("Order not found")
        
        if order.payment_status != "success":
            raise ValueError("Only successful orders can be refunded")
        
        # Update order status
        order.payment_status = "refunded"
        
        # Update user stats
        user = db.query(User).filter(User.id == order.user_id).first()
        user.total_spent -= order.selling_price
        user.total_orders -= 1
        
        # Reverse commissions if they were credited
        if order.commission_processed:
            PaymentService._reverse_commissions(db, order.id)
        
        # Refund to wallet if it was a wallet payment
        if order.is_wallet_payment:
            PaymentService._refund_to_wallet(db, order.user_id, order.selling_price, order.order_id)
        
        db.commit()
        db.refresh(order)
        
        return order
    
    @staticmethod
    def _reverse_commissions(db: Session, order_id: int):
        """Reverse commissions for a refunded order"""
        transactions = db.query(WalletTransaction).filter(
            and_(
                WalletTransaction.order_id == order_id,
                WalletTransaction.transaction_type == "commission_credit"
            )
        ).all()
        
        for transaction in transactions:
            wallet = db.query(Wallet).filter(Wallet.id == transaction.wallet_id).first()
            if wallet:
                # Deduct commission
                balance_before = wallet.total_balance
                
                if transaction.status == "pending":
                    wallet.pending_balance -= transaction.amount
                else:
                    wallet.withdrawable_balance -= transaction.amount
                
                wallet.total_balance -= transaction.amount
                wallet.total_earned -= transaction.amount
                balance_after = wallet.total_balance
                
                # Create reversal transaction
                reversal = WalletTransaction(
                    wallet_id=wallet.id,
                    user_id=wallet.user_id,
                    order_id=order_id,
                    transaction_type="deduction",
                    amount=transaction.amount,
                    balance_before=balance_before,
                    balance_after=balance_after,
                    status="completed",
                    description=f"Commission reversal for refunded order",
                    credited_at=datetime.utcnow()
                )
                db.add(reversal)
                
                # Cancel original transaction
                transaction.status = "cancelled"
        
        db.commit()
    
    @staticmethod
    def _refund_to_wallet(db: Session, user_id: int, amount: Decimal, order_id: str):
        """Refund amount to user wallet"""
        wallet = db.query(Wallet).filter(Wallet.user_id == user_id).first()
        if not wallet:
            wallet = Wallet(user_id=user_id)
            db.add(wallet)
            db.flush()
        
        balance_before = wallet.total_balance
        wallet.withdrawable_balance += amount
        wallet.total_balance += amount
        balance_after = wallet.total_balance
        
        transaction = WalletTransaction(
            wallet_id=wallet.id,
            user_id=user_id,
            transaction_type="refund",
            amount=amount,
            balance_before=balance_before,
            balance_after=balance_after,
            status="completed",
            description=f"Refund for order {order_id}",
            credited_at=datetime.utcnow()
        )
        
        db.add(transaction)
        db.commit()
