from datetime import datetime
import logging

from aiogram import Bot
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message

from antispambot.bot.callbacks.event_message import (
    BanMemberCallback,
    DeleteMessageCallback,
    UnbanMemberCallback,
)
from antispambot.bot.messages import (
    DELETE_MESSAGE_EVENT,
    DELETE_MESSAGE_REASON,
    PROFANITY_EVENT,
    STRIKE_MEMBER_EVENT,
)
from antispambot.bot.utils.spread import (
    SendMessage,
    forward_messages,
    spread_messages,
)
from antispambot.models.event import (
    DeleteMessageEvent,
    Event,
    ProfanityFilterEvent,
    StrikeMemberEvent,
)
from antispambot.models.group import Group
from antispambot.models.member import Member
from antispambot.storage.storages import chat_storage, member_storage


logger = logging.getLogger(__name__)


async def message_delete_event(
    group: Group,
    member: Member,
    message: Message,
    reason: str,
    bot: Bot
) -> Event:
    assert message.from_user
    logger.info(f'Deleting message {message.message_id} from {message.from_user.username} in group {group.key}: {reason}')

    await message.delete()

    # send info to Recent Actions
    await send_to_recent_actions(
        message,
        DELETE_MESSAGE_REASON.format(reason=reason)
    )

    # register event
    del_msg_event = DeleteMessageEvent(
        key=str(message.message_id),
        username=message.from_user.username,
        full_name=message.from_user.full_name,
        message_text=message.text or 'error',
        reason=reason,
        time=datetime.now()
    )

    # send info to admins
    delete_event_message = SendMessage(
        text=DELETE_MESSAGE_EVENT.format(
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
    # admins_chats = [
    #     chat
    #     for chat in chat_storage.get_all()
    #     if group.key in chat.groups
    # ]
    admins_chats = []
    logger.info(group.key)
    for chat in chat_storage.get_all():
        if chat.groups:
            logger.info(f'{chat.key}: {chat.groups}')

        if group.key in chat.groups:
            admins_chats.append(chat)

    logger.info(f'Admins chats: {admins_chats}')
    admins_chats_ids = [int(chat.key) for chat in admins_chats]
    await spread_messages(admins_chats_ids, [delete_event_message], bot)

    # update strikes and ban member if needed
    member_striked = await update_member_strike(group, member)
    if member_striked:
        await strike_member_event(group, member, message, bot)

    logger.info(f'Success: {del_msg_event}')
    return del_msg_event


async def strike_member_event(
    group: Group,
    member: Member,
    message: Message,
    bot: Bot
) -> Event:
    assert message.from_user
    logger.info(f'Striking member {message.from_user.username} in group {group.key}')

    # send info to Recent Actions
    await send_to_recent_actions(
        message,
        STRIKE_MEMBER_EVENT.format(
            title=group.title,
            username=message.from_user.username,
            full_name=message.from_user.full_name,
        )
    )

    # register event
    strike_member_event = StrikeMemberEvent(
        key=str(message.message_id),
        username=message.from_user.username,
        full_name=message.from_user.full_name,
        message_text=None,
        reason=None,
        time=datetime.now()
    )

    # send event to admins
    strike_event_message = SendMessage(
        text=STRIKE_MEMBER_EVENT.format(
            title=group.title,
            username=strike_member_event.username,
            full_name=strike_member_event.full_name
        ),
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(
                    text='Разбанить',
                    callback_data=UnbanMemberCallback(
                        chat_id=int(group.key),
                        user_id=message.from_user.id
                    ).pack()
                )
            ]
        ])
    )
    admins_chats = [
        chat
        for chat in chat_storage.get_all()
        if group.key in chat.groups
    ]
    admins_chats_ids = [int(chat.key) for chat in admins_chats]
    await spread_messages(admins_chats_ids, [strike_event_message], bot)

    logger.info(f'Success: {strike_member_event}')
    return strike_member_event


async def profanity_filter_event(
    group: Group,
    member: Member,
    message: Message,
    word: str,
    bot: Bot
) -> Event:
    assert message.from_user
    logger.info(f'Profanity filter event in group {group.key}: {word}')

    # register event
    profanity_filter_event = ProfanityFilterEvent(
        key=str(message.message_id),
        username=message.from_user.username,
        full_name=message.from_user.full_name,
        message_text=message.text or 'error',
        reason=word,
        time=datetime.now()
    )

    # send message to admins
    profanity_event_message = SendMessage(
        text=PROFANITY_EVENT.format(
            title=group.title,
            word=profanity_filter_event.reason,
        ),
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(
                    text='Удалить сообщение',
                    callback_data=DeleteMessageCallback(
                        chat_id=message.chat.id,
                        message_id=message.message_id
                    ).pack()
                ),
                InlineKeyboardButton(
                    text='Забанить',
                    callback_data=BanMemberCallback(
                        chat_id=message.chat.id,
                        user_id=message.from_user.id
                    ).pack()
                )
            ]
        ])
    )

    admins_chats = [
        chat
        for chat in chat_storage.get_all()
        if group.key in chat.groups
    ]
    admins_chats_ids = [int(chat.key) for chat in admins_chats]
    await spread_messages(admins_chats_ids, [profanity_event_message], bot)
    await forward_messages(admins_chats_ids, [message], bot)

    logger.info(f'Success: {profanity_filter_event}')
    return profanity_filter_event


async def update_member_strike(group: Group, member: Member) -> bool:
    member.strikes_count.setdefault(group.key, 0)
    member.strikes_count[group.key] += 1
    member_storage.save(member)

    if member.strikes_count[group.key] >= 3:
        return group.strike_mode

    return False


async def send_to_recent_actions(message: Message, text: str,):
    message = await message.answer(text)
    await message.delete()
