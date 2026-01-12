"""
Referral tracking and management service
"""
from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from datetime import datetime
from typing import Optional, List
from .models import User, Referral, ReferralStats, Wallet
from .auth import generate_referral_code


class ReferralService:
    """Service for managing referral operations"""
    
    @staticmethod
    def create_user_with_referral(
        db: Session,
        telegram_id: int,
        username: Optional[str],
        first_name: Optional[str],
        last_name: Optional[str],
        referred_by_code: Optional[str] = None,
        device_id: Optional[str] = None,
        ip_address: Optional[str] = None
    ) -> User:
        """
        Create a new user and handle referral tracking
        
        This implements the 2-level referral system:
        - If user comes via referral link, they're level 1
        - Their referrer's referrer (if exists) gets level 2 tracking
        """
        # Check if user already exists
        existing_user = db.query(User).filter(User.telegram_id == telegram_id).first()
        if existing_user:
            return existing_user
        
        # Find referrer if referral code provided
        referrer = None
        referral_level = 0
        referred_by_id = None
        
        if referred_by_code:
            referrer = db.query(User).filter(User.referral_code == referred_by_code).first()
            if referrer:
                referred_by_id = referrer.id
                referral_level = 1
        
        # Create new user
        new_user = User(
            telegram_id=telegram_id,
            username=username,
            first_name=first_name,
            last_name=last_name,
            referred_by=referred_by_id,
            referral_level=referral_level,
            referral_code="",  # Will be updated after insert
            device_id=device_id,
            ip_address=ip_address
        )
        
        db.add(new_user)
        db.flush()  # Get the ID
        
        # Generate and set referral code
        new_user.referral_code = generate_referral_code(new_user.id)
        
        # Create wallet for user
        wallet = Wallet(user_id=new_user.id)
        db.add(wallet)
        
        # Track referral click and conversion
        if referrer:
            # Level 1 referral tracking
            referral = Referral(
                referrer_id=referrer.id,
                referred_user_id=new_user.id,
                referral_code=referred_by_code,
                level=1,
                converted=False
            )
            db.add(referral)
            
            # Level 2 referral tracking (referrer's referrer)
            if referrer.referred_by:
                level2_referral = Referral(
                    referrer_id=referrer.referred_by,
                    referred_user_id=new_user.id,
                    referral_code=referrer.referral_code,
                    level=2,
                    converted=False
                )
                db.add(level2_referral)
        
        db.commit()
        db.refresh(new_user)
        
        return new_user
    
    @staticmethod
    def track_referral_click(
        db: Session,
        referral_code: str,
        ip_address: Optional[str] = None
    ) -> bool:
        """Track a referral link click"""
        referrer = db.query(User).filter(User.referral_code == referral_code).first()
        if not referrer:
            return False
        
        # Create click record
        click = Referral(
            referrer_id=referrer.id,
            referral_code=referral_code,
            level=1
        )
        db.add(click)
        db.commit()
        
        return True
    
    @staticmethod
    def mark_referral_converted(
        db: Session,
        user_id: int
    ):
        """Mark referrals as converted when user makes first purchase"""
        # Update all referral records for this user
        referrals = db.query(Referral).filter(
            Referral.referred_user_id == user_id,
            Referral.converted == False
        ).all()
        
        for referral in referrals:
            referral.converted = True
            referral.converted_at = datetime.utcnow()
        
        db.commit()
    
    @staticmethod
    def get_referral_stats(db: Session, user_id: int) -> dict:
        """Get comprehensive referral statistics for a user"""
        # Get or create stats record
        stats = db.query(ReferralStats).filter(ReferralStats.user_id == user_id).first()
        
        if not stats:
            # Calculate fresh stats
            total_clicks = db.query(func.count(Referral.id)).filter(
                Referral.referrer_id == user_id
            ).scalar() or 0
            
            total_referrals = db.query(func.count(func.distinct(Referral.referred_user_id))).filter(
                and_(
                    Referral.referrer_id == user_id,
                    Referral.referred_user_id.isnot(None)
                )
            ).scalar() or 0
            
            level1_referrals = db.query(func.count(User.id)).filter(
                and_(
                    User.referred_by == user_id,
                    User.referral_level == 1
                )
            ).scalar() or 0
            
            level2_referrals = db.query(func.count(User.id)).filter(
                and_(
                    User.referred_by == user_id,
                    User.referral_level == 2
                )
            ).scalar() or 0
            
            total_buyers = db.query(func.count(Referral.id)).filter(
                and_(
                    Referral.referrer_id == user_id,
                    Referral.converted == True
                )
            ).scalar() or 0
            
            conversion_rate = (total_buyers / total_clicks * 100) if total_clicks > 0 else 0
            
            # Get wallet data
            wallet = db.query(Wallet).filter(Wallet.user_id == user_id).first()
            
            stats_dict = {
                'total_clicks': total_clicks,
                'total_referrals': total_referrals,
                'level1_referrals': level1_referrals,
                'level2_referrals': level2_referrals,
                'total_buyers': total_buyers,
                'conversion_rate': round(conversion_rate, 2),
                'total_commission_earned': wallet.total_earned if wallet else 0,
                'total_commission_paid': wallet.total_withdrawn if wallet else 0,
                'pending_commission': wallet.pending_balance if wallet else 0
            }
            
            # Create stats record
            stats = ReferralStats(user_id=user_id, **stats_dict)
            db.add(stats)
            db.commit()
            db.refresh(stats)
        
        return {
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
    
    @staticmethod
    def update_referral_stats(db: Session, user_id: int):
        """Update cached referral statistics"""
        stats_dict = ReferralService.get_referral_stats(db, user_id)
        
        stats = db.query(ReferralStats).filter(ReferralStats.user_id == user_id).first()
        if stats:
            for key, value in stats_dict.items():
                setattr(stats, key, value)
            stats.last_updated = datetime.utcnow()
            db.commit()
    
    @staticmethod
    def get_user_referrals(
        db: Session,
        user_id: int,
        level: Optional[int] = None
    ) -> List[User]:
        """Get all users referred by a specific user"""
        query = db.query(User).filter(User.referred_by == user_id)
        
        if level:
            query = query.filter(User.referral_level == level)
        
        return query.all()
    
    @staticmethod
    def get_referral_tree(db: Session, user_id: int) -> dict:
        """Get complete referral tree for a user"""
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            return {}
        
        # Get level 1 referrals
        level1_users = ReferralService.get_user_referrals(db, user_id, level=1)
        
        # Get level 2 referrals (referrals of referrals)
        level2_users = []
        for l1_user in level1_users:
            level2_users.extend(ReferralService.get_user_referrals(db, l1_user.id, level=1))
        
        return {
            'user': {
                'id': user.id,
                'telegram_id': user.telegram_id,
                'username': user.username,
                'referral_code': user.referral_code
            },
            'level1': [
                {
                    'id': u.id,
                    'telegram_id': u.telegram_id,
                    'username': u.username,
                    'total_spent': float(u.total_spent),
                    'total_orders': u.total_orders
                }
                for u in level1_users
            ],
            'level2': [
                {
                    'id': u.id,
                    'telegram_id': u.telegram_id,
                    'username': u.username,
                    'total_spent': float(u.total_spent),
                    'total_orders': u.total_orders
                }
                for u in level2_users
            ],
            'stats': ReferralService.get_referral_stats(db, user_id)
        }
    
    @staticmethod
    def get_top_referrers(db: Session, limit: int = 10) -> List[dict]:
        """Get leaderboard of top referrers by earnings"""
        top_stats = db.query(ReferralStats).order_by(
            ReferralStats.total_commission_earned.desc()
        ).limit(limit).all()
        
        result = []
        for stat in top_stats:
            user = db.query(User).filter(User.id == stat.user_id).first()
            if user:
                result.append({
                    'user_id': user.id,
                    'telegram_id': user.telegram_id,
                    'username': user.username,
                    'first_name': user.first_name,
                    'referral_code': user.referral_code,
                    'stats': {
                        'total_clicks': stat.total_clicks,
                        'total_buyers': stat.total_buyers,
                        'conversion_rate': float(stat.conversion_rate),
                        'total_commission_earned': float(stat.total_commission_earned)
                    }
                })
        
        return result
