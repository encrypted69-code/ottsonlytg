"""
FORCE SUBSCRIBE UTILITY
========================
Checks if a user has joined the required Telegram channel.
"""

from aiogram import Bot
from config.settings import BOT_TOKEN, FORCE_SUBSCRIBE_CHANNEL_ID
from typing import Optional


async def is_user_subscribed(user_id: int) -> bool:
    """
    Check if a user is subscribed to the force subscribe channel.
    
    Args:
        user_id: Telegram user ID to check
        
    Returns:
        True if user is a valid member, False otherwise
    """
    bot = Bot(token=BOT_TOKEN)
    
    try:
        # Get chat member status
        member = await bot.get_chat_member(
            chat_id=FORCE_SUBSCRIBE_CHANNEL_ID,
            user_id=user_id
        )
        
        # Valid member statuses
        valid_statuses = ["member", "administrator", "creator"]
        
        is_subscribed = member.status in valid_statuses
        
        return is_subscribed
        
    except Exception as e:
        # Handle errors gracefully
        print(f"[FORCE SUBSCRIBE] Error checking subscription for user {user_id}: {e}")
        return False
        
    finally:
        try:
            session = await bot.get_session()
            await session.close()
        except:
            pass
