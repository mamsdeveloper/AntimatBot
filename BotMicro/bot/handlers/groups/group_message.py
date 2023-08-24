from os import getenv

from aiogram import Bot, F, Router
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message
from odetam.exceptions import ItemNotFound

from analysis.checking import (check_full_words, check_partial_words,
                               check_profanity, check_regexps)
from analysis.normilize import get_normalized_text, remove_stop_words

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
        return {'err': 'not text message'}

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
        return {'messages_count': member.messages_count.get(group.key, 0)}


    dictionary: Dictionary = await Dictionary.get(group.key)

    text = message.text
    text = get_normalized_text(text)
    text = remove_stop_words(text, dictionary.stop_words)

    full_check_result = check_full_words(text, dictionary.full_words)
    if full_check_result:
        await message_delete_event(
            group, member, message, f'слово "{full_check_result}"', bot)
        return {'result': full_check_result}

    partial_search_result = check_partial_words(text, dictionary.partial_words)
    if partial_search_result:
        word, part = partial_search_result
        if part:
            reason = f'часть "{part}" в слове "{word}"'
        else:
            reason = f'слово "{part}"'

        await message_delete_event(
            group, member, message, reason, bot)

        return {'result': partial_search_result}

    regex_search_result = check_regexps(text, dictionary.regex_patterns)
    if regex_search_result:
        word, pattern = regex_search_result
        await message_delete_event(
                group, member, message, f'шаблон "{pattern}" в слове "{word}"', bot)

        return {'result': regex_search_result}

    profanity_check_result = check_profanity(text)
    if profanity_check_result:
        await profanity_filter_event(
            group, member, message, profanity_check_result, bot)

        return {'result': profanity_check_result}

    return {'result': 'nothing found'}
