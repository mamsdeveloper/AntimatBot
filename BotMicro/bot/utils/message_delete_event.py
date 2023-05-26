from datetime import datetime

from aiogram import Bot
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message
from odetam.exceptions import ItemNotFound

from bot.callbacks.event_message import BanMemberCallback, UnbanMemberCallback
from bot.messages import (DELETE_MESSAGE_EVENT, DELETE_MESSAGE_REASON,
                          STRIKE_MEMBER_EVENT)
from bot.utils.spread import SendMessage, spread_messages
from models import (Chat, DeleteMessageEvent, Group, History, Member,
                    StrikeMemberEvent)


async def message_delete_event(member: Member, message: Message, reason: str):
    # delete message and specify reason to Recent Actions
    try:
        await message.delete()
    except Exception as e:
        return str(e)

    msg = await message.answer(DELETE_MESSAGE_REASON.format(reason=reason), disable_notification=True)
    await msg.delete()

    bot = Bot.get_current()
    if not bot:
        return

    # spread notification to group admins
    try:
        group: Group = await Group.get(str(message.chat.id))
    except ItemNotFound:
        return

    member_striked = await update_member_strike(member, group)
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
    except ItemNotFound:
        pass
    else:
        history.events.append(del_msg_event)
        if strike_member_event:
            history.events.append(strike_member_event)

        await history.save()

    delete_event_text = DELETE_MESSAGE_EVENT.format(
        title=group.title,
        reason=del_msg_event.reason,
        username=del_msg_event.username,
        full_name=del_msg_event.full_name,
        text=del_msg_event.message_text
    )[:4000] + '...'
    delete_event_markup = InlineKeyboardMarkup(inline_keyboard=[
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
    delete_event_message = SendMessage(
        text=delete_event_text, reply_markup=delete_event_markup)

    messages = [delete_event_message]
    if strike_member_event:
        strike_event_text = STRIKE_MEMBER_EVENT.format(
            title=group.title,
            username=strike_member_event.username,
            full_name=strike_member_event.full_name
        )
        strike_event_markup = InlineKeyboardMarkup(inline_keyboard=[
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
        strike_event_message = SendMessage(
            text=strike_event_text, reply_markup=strike_event_markup)

        messages.append(strike_event_message)

    admins_chats: list[Chat] = await Chat.query(Chat.groups.contains(group.key))
    admins_chats_ids = [int(chat.key) for chat in admins_chats]
    await spread_messages(admins_chats_ids, messages, bot)


async def update_member_strike(member: Member, group: Group) -> bool:
    member.strikes_count.setdefault(group.key, 0)
    member.strikes_count[group.key] += 1
    await member.save()

    if member.strikes_count[group.key] >= 3:
        return group.strike_mode

    return False
