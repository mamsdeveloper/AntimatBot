import logging
import re

from aiogram import Bot, Router
from aiogram.filters.chat_member_updated import (
    IS_MEMBER,
    IS_NOT_MEMBER,
    ChatMemberUpdatedFilter,
)
from aiogram.types import (
    ChatMemberUpdated,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)

from antispambot.bot import messages
from antispambot.bot.callbacks.event_message import AllowNicknameCallback
from antispambot.models.chat import Chat
from antispambot.storage.storages import (
    chat_storage,
    group_storage,
    member_storage,
)

logger = logging.getLogger(__name__)

router = Router()


@router.chat_member(ChatMemberUpdatedFilter(IS_NOT_MEMBER >> IS_MEMBER))
async def new_member_handler(event: ChatMemberUpdated, bot: Bot):
    member = member_storage.get(str(event.new_chat_member.user.id))
    if member is not None:
        if member.nickname_pass.get(str(event.chat.id)) is not None:
            logger.info(f'User {event.new_chat_member.user.id} has nickname pass')
            return

    group = group_storage.get(str(event.chat.id))
    if group is None:
        logger.warning(f'Group {event.chat.id} not found in storage')
        return

    fullname = event.new_chat_member.user.full_name
    fullname = fullname.lower()

    if (
        'bot' in fullname
        or len(re.sub(r'[^a-zа-я]', '', fullname)) <= 2
        or re.search(r'[\u0600-\u06FF\u0530-\u058F\u4E00-\u9FFF]+', fullname)
    ):
        await bot.ban_chat_member(event.chat.id, event.new_chat_member.user.id)
        admins = [
            chat
            for chat in chat_storage.get_all()
            if group.key in chat.groups
        ]
        for admin in admins:
            try:
                await send_ban_member_alert(bot, event, admin)
            except Exception:
                pass


async def send_ban_member_alert(
    bot: Bot,
    event: ChatMemberUpdated,
    admin: Chat,
) -> None:
    await bot.send_message(
        chat_id=admin.key,
        text=messages.WEIRD_NAME_RESTRICTED.format(
            full_name=event.new_chat_member.user.full_name,
            username=event.new_chat_member.user.username,
            title=event.chat.title
        ),
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text='Разрешить никнейм и разблокировать',
                        callback_data=AllowNicknameCallback(
                            chat_id=event.chat.id,
                            user_id=event.new_chat_member.user.id
                        ).pack()
                    )
                ]
            ]
        )
    )
