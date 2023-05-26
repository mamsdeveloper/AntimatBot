from os import getenv

from aiogram import Bot, F, Router
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message
from odetam.exceptions import ItemNotFound

from analysis.checking import (check_full_words, check_partial_words,
                               check_profanity)
from analysis.normilize import get_normalized_text

from bot.messages import PROFANITY_EVENT
from bot.utils.events import message_delete_event, profanity_filter_event
from bot.utils.spread import SendMessage, forward_messages, spread_messages
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

    member = await Member.get_or_none(str(message.from_user.id))
    if not member:
        member = Member(
            key=str(message.from_user.id),
            strikes_count={group.key: 0}
        )

    member.messages_count.setdefault(group.key, 0)
    member.messages_count[group.key] += 1
    await member.save()  # type: ignore

    messages_threshold = int(getenv('MESSAGES_THRESHOLD', 5))
    if member.messages_count.get(group.key, 0) >= messages_threshold:
        return

    text = message.text
    text = text.replace(
        'https://t.me/Yasnosvet_talks', '')
    text = text.replace(
        'https://t.me/Yasnosvet_thanks', '')
    text = text.replace(
        'https://t.me/Yasnosvet_ask', '')
    text = text.replace(
        'https://taplink.cc/pavelangel369', '')

    dictionary: Dictionary = await Dictionary.get(group.key)

    full_check_result = check_full_words(text, dictionary.full_words)
    if full_check_result:
        await message_delete_event(
            group, member, message, f'слово "{full_check_result}"', bot)
        return

    partial_search_result = check_partial_words(text, dictionary.partial_words)
    if partial_search_result:
        word, part = partial_search_result
        if part:
            await message_delete_event(
                group, member, message, f'часть "{part}" в слове "{word}"', bot)
        else:
            await message_delete_event(
                group, member, message, f'слово "{part}"', bot)
        return

    normalized_text = get_normalized_text(text)

    full_check_result = check_full_words(
        normalized_text, dictionary.full_words)
    if full_check_result:
        await message_delete_event(
            group, member, message, f'слово "{full_check_result}"', bot)
        return

    partial_search_result = check_partial_words(
        normalized_text, dictionary.partial_words)
    if partial_search_result:
        word, part = partial_search_result
        if part:
            reason = f'часть "{part}" в слове "{word}"'
        else:
            reason = f'слово "{part}"'

        await message_delete_event(
            group, member, message, reason, bot)

        return

    profanity_check_result = check_profanity(message.text)
    if profanity_check_result:
        await profanity_filter_event(
            group, member, message, profanity_check_result, bot)
