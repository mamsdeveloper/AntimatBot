from aiogram import Bot
from aiogram.exceptions import TelegramAPIError
from aiogram.types import Chat, User


async def is_user_admin(user: User, chat: Chat, bot: Bot) -> bool:
    if not bot:
        return False

    try:
        member = await bot.get_chat_member(chat.id, user.id)
        return member.status in {'owner', 'administrator', 'creator'}
    except TelegramAPIError:
        # user immediately left group and we cannot get his info
        return False
