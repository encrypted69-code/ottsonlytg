"""
Bulk update stocks - Prime, Netflix (clear old + add new), Pornhub
"""
import os
from dotenv import load_dotenv
from supabase import create_client, Client

load_dotenv()

# Initialize Supabase
supabase_url = os.getenv("SUPABASE_URL")
supabase_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
supabase: Client = create_client(supabase_url, supabase_key)

print("=" * 60)
print("📦 BULK STOCK UPDATE")
print("=" * 60)

# =====================================================
# PRIME VIDEO - Add credentials (ALL - no duplicate check)
# =====================================================
print("\n1️⃣  ADDING PRIME VIDEO CREDENTIALS...")
prime_credentials = [
    "rajenott001449@outlook.com:@rajen123",
    "rajenott001449@outlook.com:@rajen123",
    "rajenott001449@outlook.com:@rajen123",
    "rajenott001449@outlook.com:@rajen123",
    "rajenott001450@outlook.com:@rajen123",
    "rajenott001450@outlook.com:@rajen123",
    "rajenott001450@outlook.com:@rajen123",
    "rajenott001450@outlook.com:@rajen123",
    "rajenott001452@outlook.com:@rajen123",
    "rajenott001452@outlook.com:@rajen123",
    "rajenott001452@outlook.com:@rajen123",
    "rajenott001452@outlook.com:@rajen123"
]

prime_added = 0

# Add all without duplicate check (4 users per credential)
for cred in prime_credentials:
    try:
        supabase.table("stocks").insert({
            "plan_key": "prime_video",
            "credential": cred,
            "is_used": False
        }).execute()
        prime_added += 1
    except Exception as e:
        print(f"   ❌ Failed: {e}")

print(f"   ✅ Added: {prime_added} credentials (including duplicates for sharing)")

# =====================================================
# NETFLIX - DELETE ALL OLD + ADD NEW
# =====================================================
print("\n2️⃣  NETFLIX - CLEARING OLD STOCKS...")
deleted = supabase.table("stocks").delete().eq("plan_key", "netflix_4k").execute()
print(f"   🗑️  Deleted old Netflix stocks")

print("\n   ADDING NEW NETFLIX CREDENTIALS...")
netflix_credentials = [
    "audwns2918@naver.com:audqhd1354**",
    "ida_pradjonggo@yahoo.com:Elliot1234",
    "paritimur@yahoo.com:#Ise210984",
    "alvaradobernalesariel@gmail.com:19Lokillo@",
    "lorenasaam1982@gmail.com:Alejandraymartina1982",
    "upasnaakg@gmail.com:Mahasagar@21",
    "hjh4244@naver.com:gkgk0944",
    "kemadjou9@hotmail.com:Moungang1973@",
    "atosalmon@gmail.com:Salmon40",
    "siddiqui.shabi143@gmail.com:Hannah@143",
    "izaquielsil23@gmail.com:15452812",
    "ulliel@naver.com:wldn0406",
    "mamath0855@gmail.com:Matheopinto08",
    "637961449:animales7",
    "calumsilver@icloud.com:Stonehaven23",
    "loomeshcally@yahoo.co.uk:101289Bhavish",
    "wallacealonsocarvalho@gmail.com:073851fa",
    "raedsonjj@gmail.com:23270406",
    "shaehohnbussines@gmail.com:@Cherbourg99",
    "leoniasilva24@gmail.com:leonia20",
    "nomoreshark@yahoo.co.jp:5770kamome",
    "robinsonsohn013@gmail.com:130710",
    "0792505564:KHABAHLE@23",
    "pecsin.saxena@gmail.com:@Vishal12",
    "duvanrodriguez704@gmail.com:Chirillas0912",
    "sooa0@naver.com:sooa5089",
    "leeju0620@nate.com:wk401616@@",
    "niksharma3609@gmail.com:Tithi@3609",
    "veronique.klein6@free.fr:Melissa1912001",
    "youngbest7968@naver.com:qkqhwjd115",
    "andru.andreea17@icloud.com:Faraparola789!"
]

netflix_added = 0
for cred in netflix_credentials:
    try:
        supabase.table("stocks").insert({
            "plan_key": "netflix_4k",
            "credential": cred,
            "is_used": False
        }).execute()
        netflix_added += 1
    except Exception as e:
        print(f"   ❌ Failed to add: {cred[:20]}... - {e}")

print(f"   ✅ Added: {netflix_added} Netflix credentials")

# =====================================================
# PORNHUB - Add credentials (ALL - no duplicate check)
# =====================================================
print("\n3️⃣  ADDING PORNHUB CREDENTIALS...")
pornhub_credentials = [
    "Ottsonly00090@gmail.com:Pornhub@123",
    "Ottsonly00090@gmail.com:Pornhub@123",
    "Ottsonly00090@gmail.com:Pornhub@123",
    "Ottsonly00090@gmail.com:Pornhub@123",
    "Ottsonly00090@gmail.com:Pornhub@123",
    "Ottsonly00090@gmail.com:Pornhub@123",
    "Ottsonly00090@gmail.com:Pornhub@123",
    "Ottsonly00090@gmail.com:Pornhub@123",
    "Ottsonly00090@gmail.com:Pornhub@123",
    "Ottsonly00090@gmail.com:Pornhub@123",
    "Ottsonly00090@gmail.com:Pornhub@123",
    "Ottsonly00090@gmail.com:Pornhub@123",
    "Ottsonly00090@gmail.com:Pornhub@123",
    "Ottsonly00090@gmail.com:Pornhub@123"
]

pornhub_added = 0

# Add all without duplicate check (multiple users per credential)
for cred in pornhub_credentials:
    try:
        supabase.table("stocks").insert({
            "plan_key": "pornhub",
            "credential": cred,
            "is_used": False
        }).execute()
        pornhub_added += 1
    except Exception as e:
        print(f"   ❌ Failed: {e}")

print(f"   ✅ Added: {pornhub_added} credentials (including duplicates for sharing)")

# =====================================================
# SUMMARY
# =====================================================
print("\n" + "=" * 60)
print("📊 SUMMARY")
print("=" * 60)
print(f"Prime Video:  +{prime_added} credentials")
print(f"Netflix:      +{netflix_added} credentials (old ones deleted)")
print(f"Pornhub:      +{pornhub_added} credential")
print("=" * 60)
print("\n✅ STOCK UPDATE COMPLETE!")

# Show current stock levels
print("\n📦 CURRENT STOCK LEVELS:")
for plan in ["prime_video", "netflix_4k", "pornhub"]:
    count = supabase.table("stocks").select("id", count="exact").eq("plan_key", plan).eq("is_used", False).execute()
    total = supabase.table("stocks").select("id", count="exact").eq("plan_key", plan).execute()
    print(f"   {plan}: {count.count} available / {total.count} total")

print("=" * 60)
