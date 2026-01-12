"""
Seed data generator for testing
"""
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models import User, SystemSetting
from app.auth import generate_referral_code
from app.config import settings
from decimal import Decimal
import random

def create_seed_data():
    """Create seed data for testing"""
    db: Session = SessionLocal()
    
    try:
        print("Creating seed data...")
        
        # Create super admin
        super_admin = User(
            telegram_id=settings.SUPER_ADMIN_TELEGRAM_ID,
            username="superadmin",
            first_name="Super",
            last_name="Admin",
            referral_code="SUPERADMIN001",
            user_type="super_admin"
        )
        db.add(super_admin)
        db.flush()
        
        print(f"✓ Created Super Admin (ID: {super_admin.id})")
        
        # Create test admin
        admin = User(
            telegram_id=987654321,
            username="testadmin",
            first_name="Test",
            last_name="Admin",
            referral_code=generate_referral_code(2),
            user_type="admin"
        )
        db.add(admin)
        db.flush()
        
        print(f"✓ Created Test Admin (ID: {admin.id})")
        
        # Create sample referrers
        referrers = []
        for i in range(5):
            referrer = User(
                telegram_id=100000 + i,
                username=f"referrer{i+1}",
                first_name=f"Referrer",
                last_name=f"User {i+1}",
                referral_code=generate_referral_code(100000 + i),
                user_type="referrer"
            )
            db.add(referrer)
            referrers.append(referrer)
        
        db.flush()
        print(f"✓ Created {len(referrers)} Referrers")
        
        # Create sample customers
        customers = []
        for i in range(20):
            # Randomly assign referrer
            referred_by = random.choice(referrers).id if random.random() > 0.3 else None
            referral_level = 1 if referred_by else 0
            
            customer = User(
                telegram_id=200000 + i,
                username=f"customer{i+1}",
                first_name=f"Customer",
                last_name=f"{i+1}",
                referral_code=generate_referral_code(200000 + i),
                user_type="customer",
                referred_by=referred_by,
                referral_level=referral_level,
                total_orders=random.randint(0, 3),
                total_spent=Decimal(str(random.randint(0, 500)))
            )
            db.add(customer)
            customers.append(customer)
        
        db.flush()
        print(f"✓ Created {len(customers)} Customers")
        
        # Ensure system settings exist
        settings_list = [
            ('combo_selling_price', '135.00', 'number', 'Selling price of Combo OTT Plan'),
            ('combo_making_cost', '42.00', 'number', 'Making cost of Combo OTT Plan'),
            ('combo_profit', '93.00', 'number', 'Profit per sale'),
            ('level1_commission_percent', '30', 'number', 'Level 1 referral commission percentage'),
            ('level2_commission_percent', '10', 'number', 'Level 2 referral commission percentage'),
            ('level1_commission_amount', '28.00', 'number', 'Level 1 commission amount in rupees'),
            ('level2_commission_amount', '9.00', 'number', 'Level 2 commission amount in rupees'),
            ('commission_hold_hours', '24', 'number', 'Hours to hold commission before making withdrawable'),
            ('min_withdrawal_amount', '500.00', 'number', 'Minimum withdrawal amount'),
            ('referral_enabled', 'true', 'boolean', 'Enable/disable referral system'),
            ('withdrawal_enabled', 'true', 'boolean', 'Enable/disable withdrawals'),
        ]
        
        for key, value, type_, desc in settings_list:
            setting = SystemSetting(
                setting_key=key,
                setting_value=value,
                setting_type=type_,
                description=desc
            )
            db.add(setting)
        
        print(f"✓ Created {len(settings_list)} System Settings")
        
        db.commit()
        
        print("\n✅ Seed data created successfully!")
        print("\n📋 Test Credentials:")
        print(f"   Super Admin Telegram ID: {settings.SUPER_ADMIN_TELEGRAM_ID}")
        print(f"   Password: {settings.SUPER_ADMIN_PASSWORD}")
        print(f"   Test Admin Telegram ID: 987654321")
        
    except Exception as e:
        print(f"❌ Error creating seed data: {e}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    create_seed_data()
