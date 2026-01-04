TELEGRAM DM AUTO-REPLY SETUP
============================

1. GET API CREDENTIALS:
   - Go to https://my.telegram.org
   - Log in with your phone number
   - Go to "API development tools"
   - Create a new application
   - Copy your API_ID and API_HASH

2. SETUP:
   - Open dm_auto_reply.py
   - Replace 'YOUR_API_ID' with your API ID
   - Replace 'YOUR_API_HASH' with your API hash
   - Replace 'YOUR_PHONE_NUMBER' with your phone (e.g., +1234567890)

3. INSTALL DEPENDENCIES:
   pip install -r requirements.txt

4. RUN THE SCRIPT:
   python dm_auto_reply.py
   
   First time: You'll need to enter the verification code sent to your Telegram

5. CUSTOMIZE AUTO-REPLY:
   - Edit config.json to change your auto-reply message
   - Set "enabled": false to disable auto-replies temporarily
   - Add user IDs to "exclude_users" to skip auto-replying to specific people

NOTES:
- The script only replies to PRIVATE MESSAGES (DMs)
- It will NOT reply to groups or channels
- It will NOT reply to yourself
- Keep the script running for auto-replies to work
