"""
Admin panel service for dashboard and management
"""
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_, desc
from datetime import datetime, timedelta
from decimal import Decimal
from typing import Optional, List, Dict
from ..models import (
    User, Order, Wallet, WalletTransaction, Withdrawal,
    Referral, ReferralStats, FraudFlag, SystemSetting, AdminLog
)


class AdminService:
    """Service for admin panel operations"""
    
    @staticmethod
    def get_dashboard_stats(db: Session) -> Dict:
        """Get comprehensive dashboard statistics"""
        today = datetime.utcnow().date()
        today_start = datetime.combine(today, datetime.min.time())
        
        # New users today
        new_users_today = db.query(func.count(User.id)).filter(
            User.join_date >= today_start
        ).scalar() or 0
        
        # Buyers today (users who made purchase today)
        buyers_today = db.query(func.count(func.distinct(Order.user_id))).filter(
            and_(
                Order.created_at >= today_start,
                Order.payment_status == "success"
            )
        ).scalar() or 0
        
        # Revenue today
        revenue_today = db.query(func.sum(Order.selling_price)).filter(
            and_(
                Order.created_at >= today_start,
                Order.payment_status == "success"
            )
        ).scalar() or Decimal('0')
        
        # Profit today (revenue - making cost)
        profit_today = db.query(func.sum(Order.profit)).filter(
            and_(
                Order.created_at >= today_start,
                Order.payment_status == "success"
            )
        ).scalar() or Decimal('0')
        
        # Referral payout today (commissions credited)
        referral_payout_today = db.query(func.sum(WalletTransaction.amount)).filter(
            and_(
                WalletTransaction.created_at >= today_start,
                WalletTransaction.transaction_type == "commission_credit",
                WalletTransaction.status == "completed"
            )
        ).scalar() or Decimal('0')
        
        # Active referrers today (who got clicks/signups)
        active_referrers_today = db.query(func.count(func.distinct(Referral.referrer_id))).filter(
            Referral.clicked_at >= today_start
        ).scalar() or 0
        
        # Total statistics
        total_users = db.query(func.count(User.id)).scalar() or 0
        
        total_buyers = db.query(func.count(func.distinct(Order.user_id))).filter(
            Order.payment_status == "success"
        ).scalar() or 0
        
        total_revenue = db.query(func.sum(Order.selling_price)).filter(
            Order.payment_status == "success"
        ).scalar() or Decimal('0')
        
        total_profit = db.query(func.sum(Order.profit)).filter(
            Order.payment_status == "success"
        ).scalar() or Decimal('0')
        
        pending_withdrawals = db.query(func.count(Withdrawal.id)).filter(
            Withdrawal.status == "pending"
        ).scalar() or 0
        
        pending_withdrawal_amount = db.query(func.sum(Withdrawal.amount)).filter(
            Withdrawal.status == "pending"
        ).scalar() or Decimal('0')
        
        # Orders today
        orders_today = db.query(func.count(Order.id)).filter(
            and_(
                Order.created_at >= today_start,
                Order.payment_status == "success"
            )
        ).scalar() or 0
        
        return {
            'new_users_today': new_users_today,
            'buyers_today': buyers_today,
            'revenue_today': float(revenue_today),
            'net_profit_today': float(profit_today),
            'referral_payout_today': float(referral_payout_today),
            'active_referrers_today': active_referrers_today,
            'orders_today': orders_today,
            'total_users': total_users,
            'total_buyers': total_buyers,
            'total_revenue': float(total_revenue),
            'total_profit': float(total_profit),
            'pending_withdrawals': pending_withdrawals,
            'pending_withdrawal_amount': float(pending_withdrawal_amount)
        }
    
    @staticmethod
    def get_users(
        db: Session,
        search: Optional[str] = None,
        user_type: Optional[str] = None,
        is_buyer: Optional[bool] = None,
        is_suspicious: Optional[bool] = None,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None,
        page: int = 1,
        limit: int = 50
    ) -> Dict:
        """Get filtered and paginated user list"""
        query = db.query(User)
        
        # Apply filters
        if search:
            query = query.filter(
                or_(
                    User.username.ilike(f"%{search}%"),
                    User.first_name.ilike(f"%{search}%"),
                    User.telegram_id.cast(db.bind.dialect.NUMERIC).like(f"%{search}%")
                )
            )
        
        if user_type:
            query = query.filter(User.user_type == user_type)
        
        if is_buyer is not None:
            if is_buyer:
                query = query.filter(User.total_orders > 0)
            else:
                query = query.filter(User.total_orders == 0)
        
        if is_suspicious is not None:
            query = query.filter(User.is_suspicious == is_suspicious)
        
        if date_from:
            query = query.filter(User.join_date >= date_from)
        
        if date_to:
            query = query.filter(User.join_date <= date_to)
        
        # Get total count
        total = query.count()
        
        # Paginate
        offset = (page - 1) * limit
        users = query.order_by(desc(User.join_date)).offset(offset).limit(limit).all()
        
        # Calculate pages
        pages = (total + limit - 1) // limit
        
        return {
            'total': total,
            'page': page,
            'limit': limit,
            'pages': pages,
            'data': users
        }
    
    @staticmethod
    def get_orders(
        db: Session,
        search: Optional[str] = None,
        payment_status: Optional[str] = None,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None,
        page: int = 1,
        limit: int = 50
    ) -> Dict:
        """Get filtered and paginated order list"""
        query = db.query(Order)
        
        # Apply filters
        if search:
            query = query.filter(
                or_(
                    Order.order_id.ilike(f"%{search}%"),
                    Order.transaction_id.ilike(f"%{search}%")
                )
            )
        
        if payment_status:
            query = query.filter(Order.payment_status == payment_status)
        
        if date_from:
            query = query.filter(Order.created_at >= date_from)
        
        if date_to:
            query = query.filter(Order.created_at <= date_to)
        
        # Get total count
        total = query.count()
        
        # Paginate
        offset = (page - 1) * limit
        orders = query.order_by(desc(Order.created_at)).offset(offset).limit(limit).all()
        
        # Calculate pages
        pages = (total + limit - 1) // limit
        
        return {
            'total': total,
            'page': page,
            'limit': limit,
            'pages': pages,
            'data': orders
        }
    
    @staticmethod
    def get_referrer_performance(
        db: Session,
        page: int = 1,
        limit: int = 50
    ) -> Dict:
        """Get referrer performance metrics"""
        # Get users who are referrers or admins
        query = db.query(User).filter(
            User.user_type.in_(['referrer', 'admin', 'super_admin'])
        )
        
        total = query.count()
        offset = (page - 1) * limit
        
        users = query.offset(offset).limit(limit).all()
        
        result = []
        for user in users:
            # Get stats
            stats = db.query(ReferralStats).filter(ReferralStats.user_id == user.id).first()
            
            if not stats:
                # Calculate on the fly
                from .referral_service import ReferralService
                stats_dict = ReferralService.get_referral_stats(db, user.id)
            else:
                stats_dict = {
                    'total_clicks': stats.total_clicks,
                    'total_referrals': stats.total_referrals,
                    'level1_referrals': stats.level1_referrals,
                    'level2_referrals': stats.level2_referrals,
                    'total_buyers': stats.total_buyers,
                    'conversion_rate': float(stats.conversion_rate),
                    'total_commission_earned': float(stats.total_commission_earned),
                    'total_commission_paid': float(stats.total_commission_paid),
                    'pending_commission': float(stats.pending_commission)
                }
            
            result.append({
                'user_id': user.id,
                'telegram_id': user.telegram_id,
                'username': user.username,
                'first_name': user.first_name,
                'referral_code': user.referral_code,
                'user_type': user.user_type,
                'stats': stats_dict
            })
        
        pages = (total + limit - 1) // limit
        
        return {
            'total': total,
            'page': page,
            'limit': limit,
            'pages': pages,
            'data': result
        }
    
    @staticmethod
    def get_payment_monitoring(db: Session, days: int = 7) -> Dict:
        """Get payment monitoring statistics"""
        date_from = datetime.utcnow() - timedelta(days=days)
        
        # QR generated count (all orders created)
        qr_generated = db.query(func.count(Order.id)).filter(
            Order.created_at >= date_from
        ).scalar() or 0
        
        # Payment success count
        payment_success = db.query(func.count(Order.id)).filter(
            and_(
                Order.created_at >= date_from,
                Order.payment_status == "success"
            )
        ).scalar() or 0
        
        # Payment failed
        payment_failed = db.query(func.count(Order.id)).filter(
            and_(
                Order.created_at >= date_from,
                Order.payment_status == "failed"
            )
        ).scalar() or 0
        
        # Payment pending (dropoffs)
        payment_dropoff = db.query(func.count(Order.id)).filter(
            and_(
                Order.created_at >= date_from,
                Order.payment_status == "pending"
            )
        ).scalar() or 0
        
        # Conversion rate
        conversion_rate = (payment_success / qr_generated * 100) if qr_generated > 0 else 0
        
        # Average order value
        avg_order_value = db.query(func.avg(Order.selling_price)).filter(
            and_(
                Order.created_at >= date_from,
                Order.payment_status == "success"
            )
        ).scalar() or Decimal('0')
        
        return {
            'period_days': days,
            'qr_generated_count': qr_generated,
            'payment_success_count': payment_success,
            'payment_failed_count': payment_failed,
            'payment_dropoff_count': payment_dropoff,
            'conversion_rate': round(conversion_rate, 2),
            'average_order_value': float(avg_order_value)
        }
    
    @staticmethod
    def get_system_settings(db: Session) -> List[SystemSetting]:
        """Get all system settings"""
        return db.query(SystemSetting).all()
    
    @staticmethod
    def update_system_setting(
        db: Session,
        setting_key: str,
        setting_value: str,
        updated_by: int
    ) -> SystemSetting:
        """Update a system setting"""
        setting = db.query(SystemSetting).filter(
            SystemSetting.setting_key == setting_key
        ).first()
        
        if not setting:
            raise ValueError("Setting not found")
        
        setting.setting_value = setting_value
        setting.updated_by = updated_by
        setting.updated_at = datetime.utcnow()
        
        db.commit()
        db.refresh(setting)
        
        return setting
    
    @staticmethod
    def get_audit_logs(
        db: Session,
        admin_id: Optional[int] = None,
        action_type: Optional[str] = None,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None,
        page: int = 1,
        limit: int = 100
    ) -> Dict:
        """Get admin audit logs"""
        query = db.query(AdminLog)
        
        if admin_id:
            query = query.filter(AdminLog.admin_id == admin_id)
        
        if action_type:
            query = query.filter(AdminLog.action_type == action_type)
        
        if date_from:
            query = query.filter(AdminLog.created_at >= date_from)
        
        if date_to:
            query = query.filter(AdminLog.created_at <= date_to)
        
        total = query.count()
        offset = (page - 1) * limit
        
        logs = query.order_by(desc(AdminLog.created_at)).offset(offset).limit(limit).all()
        
        pages = (total + limit - 1) // limit
        
        return {
            'total': total,
            'page': page,
            'limit': limit,
            'pages': pages,
            'data': logs
        }
    
    @staticmethod
    def get_kpi_metrics(db: Session, days: int = 30) -> Dict:
        """Get key performance indicators"""
        date_from = datetime.utcnow() - timedelta(days=days)
        
        # Daily buyers
        daily_buyers = db.query(
            func.date(Order.created_at).label('date'),
            func.count(func.distinct(Order.user_id)).label('buyers')
        ).filter(
            and_(
                Order.created_at >= date_from,
                Order.payment_status == "success"
            )
        ).group_by(func.date(Order.created_at)).all()
        
        # Overall conversion rate
        total_users = db.query(func.count(User.id)).filter(
            User.join_date >= date_from
        ).scalar() or 0
        
        total_buyers = db.query(func.count(func.distinct(Order.user_id))).filter(
            and_(
                Order.created_at >= date_from,
                Order.payment_status == "success"
            )
        ).scalar() or 0
        
        conversion_rate = (total_buyers / total_users * 100) if total_users > 0 else 0
        
        # Referral sales percentage
        total_sales = db.query(func.count(Order.id)).filter(
            and_(
                Order.created_at >= date_from,
                Order.payment_status == "success"
            )
        ).scalar() or 0
        
        referral_sales = db.query(func.count(Order.id)).filter(
            and_(
                Order.created_at >= date_from,
                Order.payment_status == "success",
                Order.referral_source.isnot(None)
            )
        ).scalar() or 0
        
        referral_sales_percent = (referral_sales / total_sales * 100) if total_sales > 0 else 0
        
        # Net profit per day
        total_profit = db.query(func.sum(Order.profit)).filter(
            and_(
                Order.created_at >= date_from,
                Order.payment_status == "success"
            )
        ).scalar() or Decimal('0')
        
        net_profit_per_day = float(total_profit) / days if days > 0 else 0
        
        return {
            'period_days': days,
            'total_users': total_users,
            'total_buyers': total_buyers,
            'conversion_rate': round(conversion_rate, 2),
            'total_sales': total_sales,
            'referral_sales': referral_sales,
            'referral_sales_percent': round(referral_sales_percent, 2),
            'net_profit_per_day': round(net_profit_per_day, 2),
            'daily_buyers': [{'date': str(d.date), 'buyers': d.buyers} for d in daily_buyers]
        }
