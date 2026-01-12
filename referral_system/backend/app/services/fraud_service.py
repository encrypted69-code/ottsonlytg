"""
Fraud detection and prevention service
"""
from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from typing import List, Optional
from datetime import datetime, timedelta
from ..models import FraudFlag, User, Order, Referral


class FraudDetectionService:
    """Service for detecting and managing fraudulent activity"""
    
    @staticmethod
    def check_duplicate_upi(db: Session, upi_id: str, user_id: int) -> bool:
        """Check if UPI ID has been used by multiple users"""
        if not upi_id:
            return False
        
        # Count how many different users have used this UPI
        user_count = db.query(func.count(func.distinct(Order.user_id))).filter(
            and_(
                Order.upi_id == upi_id,
                Order.payment_status == "success"
            )
        ).scalar() or 0
        
        if user_count > 1:
            # Flag the current user
            FraudDetectionService.create_flag(
                db=db,
                user_id=user_id,
                flag_type="duplicate_upi",
                severity="high",
                description=f"UPI ID {upi_id} has been used by {user_count} different users",
                metadata={"upi_id": upi_id, "user_count": user_count}
            )
            return True
        
        return False
    
    @staticmethod
    def check_duplicate_device(db: Session, device_id: str, user_id: int) -> bool:
        """Check if device has been used by multiple users"""
        if not device_id:
            return False
        
        # Count how many different users have this device
        user_count = db.query(func.count(User.id)).filter(
            User.device_id == device_id
        ).scalar() or 0
        
        if user_count > 2:  # Allow 2 users per device (family sharing)
            FraudDetectionService.create_flag(
                db=db,
                user_id=user_id,
                flag_type="duplicate_device",
                severity="medium",
                description=f"Device ID has been used by {user_count} different users",
                metadata={"device_id": device_id, "user_count": user_count}
            )
            return True
        
        return False
    
    @staticmethod
    def check_duplicate_ip(db: Session, ip_address: str, user_id: int) -> bool:
        """Check if IP address has been used by multiple users"""
        if not ip_address:
            return False
        
        # Count how many different users have this IP
        user_count = db.query(func.count(User.id)).filter(
            User.ip_address == ip_address
        ).scalar() or 0
        
        if user_count > 5:  # Allow multiple users per IP (shared networks)
            FraudDetectionService.create_flag(
                db=db,
                user_id=user_id,
                flag_type="duplicate_ip",
                severity="low",
                description=f"IP address has been used by {user_count} different users",
                metadata={"ip_address": ip_address, "user_count": user_count}
            )
            return True
        
        return False
    
    @staticmethod
    def check_referral_pattern(db: Session, user_id: int) -> bool:
        """Check for suspicious referral patterns"""
        # Get referral stats
        total_referrals = db.query(func.count(Referral.id)).filter(
            and_(
                Referral.referrer_id == user_id,
                Referral.referred_user_id.isnot(None)
            )
        ).scalar() or 0
        
        if total_referrals < 10:
            return False  # Not enough data
        
        # Check conversion rate
        conversions = db.query(func.count(Referral.id)).filter(
            and_(
                Referral.referrer_id == user_id,
                Referral.converted == True
            )
        ).scalar() or 0
        
        conversion_rate = (conversions / total_referrals) * 100 if total_referrals > 0 else 0
        
        # Flag if very low conversion rate (potential fake referrals)
        if conversion_rate < 5 and total_referrals > 20:
            FraudDetectionService.create_flag(
                db=db,
                user_id=user_id,
                flag_type="high_referral_low_conversion",
                severity="high",
                description=f"{total_referrals} referrals but only {conversion_rate:.2f}% conversion rate",
                metadata={
                    "total_referrals": total_referrals,
                    "conversions": conversions,
                    "conversion_rate": conversion_rate
                }
            )
            return True
        
        return False
    
    @staticmethod
    def check_rapid_signups(db: Session, user_id: int) -> bool:
        """Check if user is creating rapid referral signups"""
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            return False
        
        # Check signups in last 24 hours
        yesterday = datetime.utcnow() - timedelta(days=1)
        
        recent_referrals = db.query(func.count(User.id)).filter(
            and_(
                User.referred_by == user_id,
                User.join_date >= yesterday
            )
        ).scalar() or 0
        
        # Flag if more than 10 referrals in 24 hours
        if recent_referrals > 10:
            FraudDetectionService.create_flag(
                db=db,
                user_id=user_id,
                flag_type="suspicious_pattern",
                severity="medium",
                description=f"{recent_referrals} referrals created in last 24 hours",
                metadata={
                    "recent_referrals": recent_referrals,
                    "timeframe": "24h"
                }
            )
            return True
        
        return False
    
    @staticmethod
    def check_same_user_referrals(db: Session, user_id: int) -> bool:
        """Check if referrals are from similar looking accounts"""
        # Get all referrals
        referrals = db.query(User).filter(User.referred_by == user_id).all()
        
        if len(referrals) < 5:
            return False
        
        # Check for similar usernames, devices, IPs
        device_ids = [r.device_id for r in referrals if r.device_id]
        ip_addresses = [r.ip_address for r in referrals if r.ip_address]
        
        # Check for high overlap
        unique_devices = len(set(device_ids))
        unique_ips = len(set(ip_addresses))
        
        if len(device_ids) > 0 and unique_devices / len(device_ids) < 0.3:
            FraudDetectionService.create_flag(
                db=db,
                user_id=user_id,
                flag_type="suspicious_pattern",
                severity="critical",
                description=f"Referrals show {unique_devices} unique devices out of {len(device_ids)} users",
                metadata={
                    "unique_devices": unique_devices,
                    "total_referrals": len(device_ids)
                }
            )
            return True
        
        return False
    
    @staticmethod
    def create_flag(
        db: Session,
        user_id: int,
        flag_type: str,
        severity: str,
        description: str,
        metadata: Optional[dict] = None,
        auto_detected: bool = True,
        flagged_by: Optional[int] = None
    ) -> FraudFlag:
        """Create a fraud flag"""
        # Check if similar flag already exists
        existing_flag = db.query(FraudFlag).filter(
            and_(
                FraudFlag.user_id == user_id,
                FraudFlag.flag_type == flag_type,
                FraudFlag.resolved == False
            )
        ).first()
        
        if existing_flag:
            return existing_flag
        
        flag = FraudFlag(
            user_id=user_id,
            flag_type=flag_type,
            severity=severity,
            description=description,
            metadata=metadata,
            auto_detected=auto_detected,
            flagged_by=flagged_by
        )
        
        db.add(flag)
        
        # Mark user as suspicious if high or critical severity
        if severity in ['high', 'critical']:
            user = db.query(User).filter(User.id == user_id).first()
            if user:
                user.is_suspicious = True
        
        db.commit()
        db.refresh(flag)
        
        return flag
    
    @staticmethod
    def resolve_flag(
        db: Session,
        flag_id: int,
        resolved_by: int,
        resolution_notes: Optional[str] = None
    ) -> FraudFlag:
        """Resolve a fraud flag"""
        flag = db.query(FraudFlag).filter(FraudFlag.id == flag_id).first()
        if not flag:
            raise ValueError("Flag not found")
        
        flag.resolved = True
        flag.resolved_at = datetime.utcnow()
        flag.resolved_by = resolved_by
        flag.resolution_notes = resolution_notes
        
        # Check if user has any other unresolved flags
        other_flags = db.query(FraudFlag).filter(
            and_(
                FraudFlag.user_id == flag.user_id,
                FraudFlag.resolved == False,
                FraudFlag.id != flag_id
            )
        ).count()
        
        # Remove suspicious status if no other flags
        if other_flags == 0:
            user = db.query(User).filter(User.id == flag.user_id).first()
            if user:
                user.is_suspicious = False
        
        db.commit()
        db.refresh(flag)
        
        return flag
    
    @staticmethod
    def get_user_flags(
        db: Session,
        user_id: int,
        include_resolved: bool = False
    ) -> List[FraudFlag]:
        """Get all flags for a user"""
        query = db.query(FraudFlag).filter(FraudFlag.user_id == user_id)
        
        if not include_resolved:
            query = query.filter(FraudFlag.resolved == False)
        
        return query.order_by(FraudFlag.created_at.desc()).all()
    
    @staticmethod
    def get_all_flags(
        db: Session,
        severity: Optional[str] = None,
        resolved: Optional[bool] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[FraudFlag]:
        """Get all fraud flags"""
        query = db.query(FraudFlag)
        
        if severity:
            query = query.filter(FraudFlag.severity == severity)
        
        if resolved is not None:
            query = query.filter(FraudFlag.resolved == resolved)
        
        return query.order_by(FraudFlag.created_at.desc()).offset(offset).limit(limit).all()
    
    @staticmethod
    def run_fraud_checks(db: Session, user_id: int, upi_id: Optional[str] = None) -> List[FraudFlag]:
        """Run all fraud checks for a user"""
        flags = []
        
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            return flags
        
        # Check duplicate UPI
        if upi_id and FraudDetectionService.check_duplicate_upi(db, upi_id, user_id):
            flags.append("duplicate_upi")
        
        # Check duplicate device
        if user.device_id and FraudDetectionService.check_duplicate_device(db, user.device_id, user_id):
            flags.append("duplicate_device")
        
        # Check duplicate IP
        if user.ip_address and FraudDetectionService.check_duplicate_ip(db, user.ip_address, user_id):
            flags.append("duplicate_ip")
        
        # Check referral patterns
        if FraudDetectionService.check_referral_pattern(db, user_id):
            flags.append("high_referral_low_conversion")
        
        # Check rapid signups
        if FraudDetectionService.check_rapid_signups(db, user_id):
            flags.append("suspicious_pattern")
        
        # Check same user referrals
        if FraudDetectionService.check_same_user_referrals(db, user_id):
            flags.append("suspicious_pattern")
        
        return flags
    
    @staticmethod
    def block_user(db: Session, user_id: int, admin_id: int, reason: str):
        """Block a user account"""
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise ValueError("User not found")
        
        user.is_blocked = True
        user.is_suspicious = True
        
        # Create flag
        FraudDetectionService.create_flag(
            db=db,
            user_id=user_id,
            flag_type="manual_flag",
            severity="critical",
            description=f"User blocked: {reason}",
            auto_detected=False,
            flagged_by=admin_id
        )
        
        db.commit()
    
    @staticmethod
    def unblock_user(db: Session, user_id: int, admin_id: int):
        """Unblock a user account"""
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise ValueError("User not found")
        
        user.is_blocked = False
        
        # Resolve all manual flags
        manual_flags = db.query(FraudFlag).filter(
            and_(
                FraudFlag.user_id == user_id,
                FraudFlag.flag_type == "manual_flag",
                FraudFlag.resolved == False
            )
        ).all()
        
        for flag in manual_flags:
            flag.resolved = True
            flag.resolved_at = datetime.utcnow()
            flag.resolved_by = admin_id
            flag.resolution_notes = "User unblocked by admin"
        
        db.commit()
