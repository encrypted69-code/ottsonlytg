"""
SUPABASE CONNECTION TEST
========================
Run this script to verify your Supabase setup before migration.

USAGE:
    python test_supabase_connection.py
"""

import os
from dotenv import load_dotenv

# Load environment
load_dotenv()

print("=" * 50)
print("SUPABASE CONNECTION TEST")
print("=" * 50)

# Check environment variables
print("\n1️⃣ Checking environment variables...")
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

if not SUPABASE_URL:
    print("❌ SUPABASE_URL not found in .env")
    print("   Add: SUPABASE_URL=https://your-project.supabase.co")
    exit(1)
else:
    print(f"✅ SUPABASE_URL found: {SUPABASE_URL}")

if not SUPABASE_KEY:
    print("❌ SUPABASE_SERVICE_ROLE_KEY not found in .env")
    print("   Get it from: Supabase Dashboard → Settings → API")
    exit(1)
else:
    key_preview = SUPABASE_KEY[:20] + "..." + SUPABASE_KEY[-10:]
    print(f"✅ SUPABASE_SERVICE_ROLE_KEY found: {key_preview}")

# Try importing supabase
print("\n2️⃣ Checking supabase package...")
try:
    from supabase import create_client, Client
    print("✅ supabase package installed")
except ImportError:
    print("❌ supabase package not installed")
    print("   Run: pip install supabase")
    exit(1)

# Try connecting
print("\n3️⃣ Testing connection...")
try:
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
    print("✅ Supabase client created")
except Exception as e:
    print(f"❌ Failed to create client: {e}")
    exit(1)

# Try querying tables
print("\n4️⃣ Checking database tables...")

tables_to_check = ["users", "plans", "stocks", "transactions", "subscriptions"]
missing_tables = []

for table in tables_to_check:
    try:
        response = supabase.table(table).select("*").limit(1).execute()
        print(f"✅ Table '{table}' exists")
    except Exception as e:
        print(f"❌ Table '{table}' not found or error: {str(e)[:50]}")
        missing_tables.append(table)

if missing_tables:
    print(f"\n⚠️  Missing tables: {', '.join(missing_tables)}")
    print("   Run supabase_schema.sql in Supabase SQL Editor first!")
    exit(1)

# Test a simple insert (to test_users table)
print("\n5️⃣ Testing write permissions...")
try:
    # Try to create a test record
    test_data = {
        "telegram_id": 999999999,
        "name": "Test User",
        "wallet": 0
    }
    
    # First, check if test user exists
    existing = supabase.table("users").select("telegram_id").eq("telegram_id", 999999999).execute()
    
    if existing.data:
        print("✅ Write test: Test user already exists (skipping insert)")
    else:
        # Insert test user
        supabase.table("users").insert(test_data).execute()
        print("✅ Write test: Successfully created test user")
        
        # Clean up
        supabase.table("users").delete().eq("telegram_id", 999999999).execute()
        print("✅ Cleanup: Test user deleted")
        
except Exception as e:
    print(f"❌ Write test failed: {e}")
    print("   Check if service_role key has write permissions")
    exit(1)

# Final summary
print("\n" + "=" * 50)
print("🎉 ALL TESTS PASSED!")
print("=" * 50)
print("""
Your Supabase setup is ready!

NEXT STEPS:
1. Backup your JSON files: cp -r data/ data_backup/
2. Run migration: python migrate_to_supabase.py
3. Test your bot thoroughly
4. Update handler imports to use supabase_db

Need help? Check MIGRATION_GUIDE.md
""")
