import re

from aiogram import Bot, Router
from aiogram.filters.chat_member_updated import (IS_MEMBER, IS_NOT_MEMBER,
                                                 ChatMemberUpdatedFilter)
from aiogram.types import (ChatMemberUpdated, InlineKeyboardButton,
                           InlineKeyboardMarkup)

from bot import messages
from bot.callbacks.event_message import AllowNicknameCallback
from models.chat import Chat
from models.group import Group
from models.member import Member
from utils.logging import log

router = Router()


@router.chat_member(ChatMemberUpdatedFilter(IS_NOT_MEMBER >> IS_MEMBER))
async def new_member_handler(event: ChatMemberUpdated, bot: Bot):
    member = await Member.get_or_none(str(event.new_chat_member.user.id))
    if member and member.nickname_pass.get(str(event.chat.id)):
        return

    group = await Group.get_or_none(str(event.chat.id))
    if not group:
        return

    fullname = event.new_chat_member.user.full_name
    fullname = fullname.lower()

    if (
        'bot' in fullname
        or len(re.sub(r'[^a-zа-я]', '', fullname)) <= 2
        or re.search(r'[\u0600-\u06FF\u0530-\u058F\u4E00-\u9FFF]+', fullname)
    ):
        result = await bot.ban_chat_member(event.chat.id, event.new_chat_member.user.id)
        # log(data={
        #     'chat_id': event.chat.id,
        #     'user_id': event.new_chat_member.user.id,
        #     'ban_chat_member_result': result
        # })

        admins: list[Chat] = await Chat.query(Chat.groups.contains(group.key))
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
