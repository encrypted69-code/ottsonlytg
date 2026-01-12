"""
Configuration management for the application
"""
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings"""
    
    # Database
    DATABASE_URL: str = "postgresql://localhost/ottsonly_referral"
    
    # Security
    SECRET_KEY: str = "change-this-secret-key-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440
    
    # Admin
    SUPER_ADMIN_TELEGRAM_ID: int = 0
    SUPER_ADMIN_PASSWORD: str = "admin123"
    
    # Redis
    REDIS_URL: Optional[str] = "redis://localhost:6379/0"
    
    # Business Logic
    COMBO_SELLING_PRICE: float = 135.00
    COMBO_MAKING_COST: float = 42.00
    COMBO_PROFIT: float = 93.00
    LEVEL1_COMMISSION_PERCENT: int = 30
    LEVEL2_COMMISSION_PERCENT: int = 10
    LEVEL1_COMMISSION_AMOUNT: float = 28.00
    LEVEL2_COMMISSION_AMOUNT: float = 9.00
    COMMISSION_HOLD_HOURS: int = 24
    MIN_WITHDRAWAL_AMOUNT: float = 500.00
    
    # CORS
    FRONTEND_URL: str = "http://localhost:3000"
    
    # Environment
    ENVIRONMENT: str = "development"
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
