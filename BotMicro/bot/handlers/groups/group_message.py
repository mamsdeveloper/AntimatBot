from multiprocessing import process
from os import getenv
from time import time

from aiogram import Bot, F, Router
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message
from odetam.exceptions import ItemNotFound

from analysis.checking import (check_full_words, check_partial_words,
                               check_profanity)
from analysis.normilize import get_normalized_text
from bot import messages
from bot.callbacks.event_message import BanMemberCallback, DeleteMessageCallback
from bot.utils.message_delete_event import message_delete_event
from models import Dictionary, Group
from models.chat import Chat
from models.member import Member
from utils.logging import log

router = Router()


@router.edited_message(F.text, F.from_user.is_bot == False)
@router.message(F.text, F.from_user.is_bot == False)
async def group_message_handler(message: Message, bot: Bot, group: Group) -> None:
    if not message.text:
        return

    try:
        st = time()
        profanity_check_result = check_profanity(message.text)
        process_time = time() - st
        if profanity_check_result:
            admins: list[Chat] = await Chat.query(Chat.groups.contains(group.key))
            for admin in admins:
                await bot.send_message(
                    chat_id=admin.key,
                    text=messages.TEST_FILTER.format(
                        text=message.text,
                        word=profanity_check_result,
                        process_time=process_time
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
            return
    except Exception as e:
        log({'error': str(e), 'message': message.text})

    try:
        member: Member = await Member.get(str(message.from_user.id))
    except ItemNotFound:
        member = Member(key=str(message.from_user.id),
                        strikes_count={group.key: 0})

    member.messages_count.setdefault(group.key, 0)
    member.messages_count[group.key] += 1
    await member.save()

    if member.messages_count.get(group.key, 0) >= int(getenv('MESSAGES_THRESHOLD', 5)):
        return

    text_without_excludes = message.text
    text_without_excludes = text_without_excludes.replace(
        'https://t.me/Yasnosvet_talks', '')
    text_without_excludes = text_without_excludes.replace(
        'https://t.me/Yasnosvet_thanks', '')
    text_without_excludes = text_without_excludes.replace(
        'https://t.me/Yasnosvet_ask', '')
    text_without_excludes = text_without_excludes.replace(
        'https://taplink.cc/pavelangel369', '')

    try:
        dictionary: Dictionary = await Dictionary.get(group.key)
    except ItemNotFound:
        return

    full_check_result = check_full_words(
        text_without_excludes, dictionary.full_words)
    if full_check_result:
        await message_delete_event(member, message, f'слово "{full_check_result}"')
        return

    partial_search_result = check_partial_words(
        text_without_excludes, dictionary.partial_words)
    if partial_search_result:
        word, part = partial_search_result
        if part:
            await message_delete_event(member, message, f'часть "{part}" в слове "{word}"')
        else:
            await message_delete_event(member, message, f'слово "{part}"')
        return

    normalized_text = get_normalized_text(text_without_excludes)

    full_check_result = check_full_words(
        normalized_text, dictionary.full_words)
    if full_check_result:
        await message_delete_event(member, message, f'слово "{full_check_result}"')
        return

    partial_search_result = check_partial_words(
        normalized_text, dictionary.partial_words)
    if partial_search_result:
        word, part = partial_search_result
        if part:
            await message_delete_event(member, message, f'часть "{part}" в слове "{word}"')
        else:
            await message_delete_event(member, message, f'слово "{part}"')
        return
