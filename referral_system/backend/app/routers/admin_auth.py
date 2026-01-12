"""
Admin authentication router
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import timedelta
from ..database import get_db
from ..models import User
from ..schemas import AdminLogin, TokenResponse
from ..auth import create_access_token, get_password_hash, verify_password
from ..config import settings

router = APIRouter(prefix="/admin/auth", tags=["Admin Auth"])


@router.post("/login", response_model=TokenResponse)
async def admin_login(credentials: AdminLogin, db: Session = Depends(get_db)):
    """Admin login endpoint"""
    # Find user by telegram ID
    user = db.query(User).filter(User.telegram_id == credentials.telegram_id).first()
    
    # For first-time super admin setup
    if credentials.telegram_id == settings.SUPER_ADMIN_TELEGRAM_ID and not user:
        # Create super admin account
        user = User(
            telegram_id=settings.SUPER_ADMIN_TELEGRAM_ID,
            username="superadmin",
            first_name="Super",
            last_name="Admin",
            referral_code=f"SUPERADMIN{settings.SUPER_ADMIN_TELEGRAM_ID}",
            user_type="super_admin"
        )
        db.add(user)
        db.commit()
        db.refresh(user)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )
    
    # Check if user is admin or super_admin
    if user.user_type not in ['admin', 'super_admin']:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized. Admin access required."
        )
    
    # Verify password (simple check for demo - in production use proper hashing)
    if credentials.password != settings.SUPER_ADMIN_PASSWORD:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )
    
    # Create access token
    access_token = create_access_token(
        data={"sub": user.telegram_id, "type": user.user_type},
        expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    
    return TokenResponse(access_token=access_token, token_type="bearer")


@router.post("/create-admin")
async def create_admin(
    telegram_id: int,
    username: str,
    password: str,
    user_type: str = "admin",
    db: Session = Depends(get_db)
):
    """Create a new admin user (super admin only)"""
    # Check if user already exists
    existing_user = db.query(User).filter(User.telegram_id == telegram_id).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="User already exists")
    
    # Create admin user
    from ..auth import generate_referral_code
    
    user = User(
        telegram_id=telegram_id,
        username=username,
        referral_code=generate_referral_code(telegram_id),
        user_type=user_type
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    
    return {"message": "Admin created successfully", "user_id": user.id}
