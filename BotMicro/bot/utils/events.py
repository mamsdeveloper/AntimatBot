from datetime import datetime

from aiogram import Bot
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message

from bot.callbacks.event_message import (BanMemberCallback,
                                         DeleteMessageCallback,
                                         UnbanMemberCallback)
from bot.messages import (DELETE_MESSAGE_EVENT, DELETE_MESSAGE_REASON,
                          PROFANITY_EVENT, STRIKE_MEMBER_EVENT)
from bot.utils.spread import SendMessage, forward_messages, spread_messages
from models import (Chat, DeleteMessageEvent, Group, History, Member,
                    StrikeMemberEvent)
from models.events import Event, ProfanityFilterEvent


async def message_delete_event(
    group: Group,
    member: Member,
    message: Message,
    reason: str,
    bot: Bot
) -> Event:
    await message.delete()

    # send info to Recent Actions
    await send_to_recent_actions(
        message,
        DELETE_MESSAGE_REASON.format(reason=reason)
    )

    # register event
    del_msg_event = DeleteMessageEvent(
        username=message.from_user.username,
        full_name=message.from_user.full_name,
        message_text=message.text or 'error',
        reason=reason,
        time=datetime.now()
    )
    history: History = await History.get(group.key)
    history.events.append(del_msg_event)
    await history.save()  # type: ignore

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
    admins_chats: list[Chat] = await Chat.query(Chat.groups.contains(group.key))
    admins_chats_ids = [int(chat.key) for chat in admins_chats]
    await spread_messages(admins_chats_ids, [delete_event_message], bot)

    # update strikes and ban member if needed
    member_striked = await update_member_strike(group, member)
    if member_striked:
        await strike_member_event(group, member, message, bot)

    return del_msg_event


async def strike_member_event(
    group: Group,
    member: Member,
    message: Message,
    bot: Bot
) -> Event:
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
        username=message.from_user.username,
        full_name=message.from_user.full_name,
        message_text=None,
        reason=None,
        time=datetime.now()
    )
    history: History = await History.get(group.key)
    history.events.append(strike_member_event)
    await history.save()  # type: ignore

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
                        chat_id=group.key,
                        user_id=message.from_user.id
                    ).pack()
                )
            ]
        ])
    )
    admins_chats: list[Chat] = await Chat.query(Chat.groups.contains(group.key))
    admins_chats_ids = [int(chat.key) for chat in admins_chats]
    await spread_messages(admins_chats_ids, [strike_event_message], bot)

    return strike_member_event


async def profanity_filter_event(
    group: Group,
    member: Member,
    message: Message,
    word: str,
    bot: Bot
) -> Event:
    # register event
    profanity_filter_event = ProfanityFilterEvent(
        username=message.from_user.username,
        full_name=message.from_user.full_name,
        message_text=message.text or 'error',
        reason=word,
        time=datetime.now()
    )
    history: History = await History.get(group.key)
    history.events.append(profanity_filter_event)
    await history.save()  # type: ignore

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

    admins_chats: list[Chat] = await Chat.query(Chat.groups.contains(group.key))
    admins_chats_ids = [int(chat.key) for chat in admins_chats]
    await spread_messages(admins_chats_ids, [profanity_event_message], bot)
    await forward_messages(admins_chats_ids, [message], bot)

    return profanity_filter_event


async def update_member_strike(group: Group, member: Member) -> bool:
    member.strikes_count.setdefault(group.key, 0)
    member.strikes_count[group.key] += 1
    await member.save()

    if member.strikes_count[group.key] >= 3:
        return group.strike_mode

    return False


async def send_to_recent_actions(message: Message, text: str,):
    message = await message.answer(text)
    await message.delete()
