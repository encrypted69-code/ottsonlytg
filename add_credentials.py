"""
Simple script to add OTT credentials to the database
"""
from utils.supabase_db import add_credentials, get_stock_count

print("=" * 50)
print("📦 ADD OTT CREDENTIALS")
print("=" * 50)

print("\nAvailable plans:")
print("1. netflix_4k")
print("2. prime_video")
print("3. youtube")
print("4. combo")
print("5. pornhub")
print("6. spotify")
print("7. sonyliv")
print("8. zee5")

plan_key = input("\nEnter plan key (e.g., netflix_4k): ").strip()

print("\n📝 Enter credentials in format: email:password")
print("   For multiple credentials, enter one per line")
print("   Press Enter twice when done\n")

credentials = []
print("Enter credentials (press Enter on empty line to finish):")
while True:
    line = input().strip()
    if not line:
        break
    if ":" in line:
        credentials.append(line)
    else:
        print("⚠️  Invalid format! Use email:password")

if not credentials:
    print("❌ No credentials entered!")
    exit()

print(f"\n📊 Adding {len(credentials)} credentials to {plan_key}...")

result = add_credentials(plan_key, credentials)

print("\n" + "=" * 50)
print("✅ DONE!")
print("=" * 50)
print(f"➕ Added: {result['added']}")
print(f"❌ Duplicates: {result['duplicates']}")
print(f"📊 Total Stock: {result['total']}")
print("=" * 50)
