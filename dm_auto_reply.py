"""
Telegram DM Auto-Reply Automation
This script automatically replies to incoming direct messages on your personal Telegram account
"""

from telethon import TelegramClient, events
import json
import os
from datetime import datetime, timedelta

# Configuration
API_ID = '37157105'  # Get from https://my.telegram.org
API_HASH = '4a35aa9cd3402605270979286f4097da'  # Get from https://my.telegram.org
PHONE = '+447366497014'  # Your phone number with country code (e.g., +1234567890)

# Get the directory where the script is located
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_PATH = os.path.join(SCRIPT_DIR, 'config.json')

# Load auto-reply message from config
def load_config():
    if os.path.exists(CONFIG_PATH):
        with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
            return json.load(f)
    else:
        # Default config
        config = {
            "auto_reply_message": "Thanks for your message! I'll get back to you soon.",
            "offer_message": "Special offer details here.",
            "confirmation_message": "Thank you! Our staff will contact you shortly.",
            "enabled": True,
            "exclude_users": []  # List of user IDs to exclude from auto-reply
        }
        with open(CONFIG_PATH, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=4)
        return config

# Initialize the client
client = TelegramClient('session_name', API_ID, API_HASH)

# Dictionary to track users: {user_id: {'stage': 'initial/yes_replied/ok_replied', 'last_auto_reply': datetime}}
user_states = {}

def can_send_auto_reply(sender_id):
    """Check if user can receive auto-reply (24 hours cooldown)"""
    if sender_id not in user_states:
        return True
    
    last_reply = user_states[sender_id].get('last_auto_reply')
    if not last_reply:
        return True
    
    # Check if 24 hours have passed
    if datetime.now() - last_reply >= timedelta(days=1):
        return True
    
    return False

@client.on(events.NewMessage(incoming=True, func=lambda e: e.is_private))
async def auto_reply_handler(event):
    """Automatically reply to incoming private messages"""
    config = load_config()
    
    # Check if auto-reply is enabled
    if not config.get('enabled', True):
        return
    
    # Get sender info
    sender = await event.get_sender()
    sender_id = sender.id
    
    # Skip if user is in exclude list
    if sender_id in config.get('exclude_users', []):
        print(f"Skipping auto-reply for excluded user: {sender.first_name} ({sender_id})")
        return
    
    # Skip if message is from yourself
    me = await client.get_me()
    if sender_id == me.id:
        return
    
    # Get message text
    message_text = event.message.text.lower().strip() if event.message.text else ""
    
    # Reset command - clear user state
    if message_text == "/reset":
        if sender_id in user_states:
            del user_states[sender_id]
        await event.reply("✅ Reset! Send any message to get the auto-reply again.")
        return
    
    # Initialize user state if not exists
    if sender_id not in user_states:
        user_states[sender_id] = {'stage': 'new', 'last_auto_reply': None}
    
    current_stage = user_states[sender_id].get('stage', 'new')
    
    # Stage 1: User replies with "yes" to get offer details
    if current_stage == 'initial' and message_text == "yes":
        offer_message = config.get('offer_message', '')
        if not offer_message:
            print(f"ERROR: offer_message is empty in config!")
            await event.reply("Sorry, there was an error. Please contact support.")
            return
        await event.reply(offer_message)
        user_states[sender_id]['stage'] = 'yes_replied'
        print(f"Sent offer details to {sender.first_name} ({sender_id})")
        return
    
    # Stage 2: User replies with "ok" after seeing the offer
    if current_stage == 'yes_replied' and message_text == "ok":
        confirmation_message = config.get('confirmation_message', 'Thank you! Our staff will contact you shortly.')
        await event.reply(confirmation_message)
        user_states[sender_id]['stage'] = 'ok_replied'
        print(f"User {sender.first_name} ({sender_id}) confirmed with 'ok'")
        return
    
    # If user already has a stage (initial, yes_replied, or ok_replied), don't send auto-reply again
    if current_stage in ['initial', 'yes_replied', 'ok_replied']:
        print(f"User {sender.first_name} ({sender_id}) is at stage '{current_stage}', skipping auto-reply.")
        return
    
    # Check if user can receive auto-reply (24 hour cooldown)
    if not can_send_auto_reply(sender_id):
        hours_left = 24 - (datetime.now() - user_states[sender_id]['last_auto_reply']).total_seconds() / 3600
        print(f"User {sender.first_name} ({sender_id}) already received auto-reply. {hours_left:.1f} hours left until next one.")
        return
    
    # Send initial auto-reply with personalized first name
    auto_reply_template = config.get('auto_reply_message', 'Thanks for your message!')
    first_name = sender.first_name or "there"
    auto_reply = auto_reply_template.replace('{first_name}', first_name)
    
    await event.reply(auto_reply)
    
    # Update user state
    user_states[sender_id]['stage'] = 'initial'
    user_states[sender_id]['last_auto_reply'] = datetime.now()
    
    print(f"Auto-replied to {first_name} ({sender_id}). Next auto-reply available in 24 hours.")

async def main():
    """Start the client"""
    print("Starting Telegram DM Auto-Reply...")
    print("Press Ctrl+C to stop")
    
    # Connect and start
    await client.start(phone=PHONE)
    print("Client started successfully!")
    print(f"Logged in as: {(await client.get_me()).first_name}")
    
    # Keep the client running
    await client.run_until_disconnected()

if __name__ == '__main__':
    import asyncio
    asyncio.run(main())
1