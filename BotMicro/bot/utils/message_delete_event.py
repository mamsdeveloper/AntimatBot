from datetime import datetime

from aiogram import Bot
from aiogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup
from odetam.exceptions import ItemNotFound

from bot import messages
from bot.callbacks.event_message import BanMemberCallback, UnbanMemberCallback
from models import StrikeMemberEvent, Chat, DeleteMessageEvent, Group, History, Member


async def message_delete_event(message: Message, reason: str):
    # delete message and specify reason to Recent Actions
    try:
        await message.delete()
    except Exception as e:
        return str(e)

    msg = await message.answer(messages.DELETE_MESSAGE_REASON.format(reason=reason), disable_notification=True)
    await msg.delete()

    bot = Bot.get_current()
    if not bot:
        return

    # spread notification to group admins
    try:
        group: Group = await Group.get(str(message.chat.id))
    except ItemNotFound:
        return

    member_striked = await update_member_strike(message.from_user.id, group)
    if member_striked:
        try:
            await bot.ban_chat_member(group.key, message.from_user.id)
            strike_member_event = StrikeMemberEvent(
                username=message.from_user.username,
                full_name=message.from_user.full_name,
                message_text=None,
                reason=None,
                time=datetime.now()
            )
        except:
            strike_member_event = None
    else:
        strike_member_event = None

    # register event
    del_msg_event = DeleteMessageEvent(
        username=message.from_user.username,
        full_name=message.from_user.full_name,
        message_text=message.text or 'error',
        reason=reason,
        time=datetime.now()
    )
    try:
        history: History = await History.get(group.key)
    except ItemNotFound as e:
        pass
    else:
        history.events.append(del_msg_event)
        if strike_member_event:
            history.events.append(strike_member_event)

        await history.save()

    admins: list[Chat] = await Chat.query(Chat.groups.contains(group.key))
    for admin in admins:
        await bot.send_message(
            chat_id=admin.key,
            text=messages.DELETE_MESSAGE_EVENT.format(
                title=group.title,
                reason=del_msg_event.reason,
                username=del_msg_event.username,
                full_name=del_msg_event.full_name,
                text=del_msg_event.message_text
            )[:4000] + '...',
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text='Забанить',
                        callback_data=BanMemberCallback(
                            chat_id=message.chat.id, 
                            user_id=message.from_user.id
                        ).pack()
                    )
                ],
                [
                    InlineKeyboardButton(
                        text='Сбросить счетчик банов',
                        callback_data=UnbanMemberCallback(
                            chat_id=message.chat.id, 
                            user_id=message.from_user.id
                        ).pack()
                    )
                ]
            ])
        )
        if strike_member_event:
            await bot.send_message(
                chat_id=admin.key,
                text=messages.STRIKE_MEMBER_EVENT.format(
                    title=group.title,
                    username=strike_member_event.username,
                    full_name=strike_member_event.full_name
                ),
                reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                    [
                        InlineKeyboardButton(
                            text='Разбанить',
                            callback_data=UnbanMemberCallback(
                                chat_id=message.chat.id, 
                                user_id=message.from_user.id
                            ).pack()
                        )
                    ]
                ])
            )


async def update_member_strike(user_id: int, group: Group) -> bool:
    try:
        member: Member = await Member.get(str(user_id))
    except ItemNotFound:
        member = Member(key=str(user_id), strikes_count={group.key: 0})

    member.strikes_count.setdefault(group.key, 0)
    member.strikes_count[group.key] += 1
    await member.save()

    if member.strikes_count[group.key] >= 3:
        return group.strike_mode

    return False
