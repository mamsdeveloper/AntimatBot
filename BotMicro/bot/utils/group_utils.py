from aiogram import Bot
from aiogram.types import User, Chat


async def is_user_admin(user: User, chat: Chat) -> bool:
    bot = Bot.get_current()
    if not bot:
        return False
    
    member = await bot.get_chat_member(chat.id, user.id)
    return member.status in {'owner', 'administrator', 'creator'}