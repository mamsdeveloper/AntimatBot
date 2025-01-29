from os import getenv
from venv import logger

from aiogram import Bot, F, Router
from aiogram.types import Message

from antispambot.analysis.checking import (
    check_emoji,
    check_full_words,
    check_partial_words,
    check_regexps,
    check_substitution,
)
from antispambot.analysis.normilize import (
    get_normalized_text,
    remove_stop_words,
)
from antispambot.bot.utils.events import message_delete_event
from antispambot.bot.utils.message import get_full_text
from antispambot.models.group import Group
from antispambot.models.member import Member
from antispambot.storage.storages import dictionary_storage, member_storage

router = Router()


@router.edited_message(F.from_user.is_bot == False)
@router.message(F.from_user.is_bot == False)
async def group_message_handler(message: Message, bot: Bot, group: Group) -> None:
    member = member_storage.get(str(message.from_user.id))
    if member is None:
        member = Member(
            key=str(message.from_user.id),
            strikes_count={group.key: 0}
        )

    member.messages_count.setdefault(group.key, 0)
    member.messages_count[group.key] += 1
    member_storage.save(member)

    messages_threshold = int(getenv('MESSAGES_THRESHOLD', 5))
    if member.messages_count.get(group.key, 0) >= messages_threshold:
        logger.debug(f'User {member.key} has reached the messages threshold in group {group.key}')
        return

    dictionary = dictionary_storage.get(group.key)
    if dictionary is None:
        logger.warning(f'Dictionary for group {group.key} is not found')
        return

    text = get_full_text(message)
    text = get_normalized_text(text)
    text = remove_stop_words(text, dictionary.stop_words)

    substitution_result = check_substitution(text)
    if substitution_result:
        await message_delete_event(group, member, message, f'замена букв в слове "{substitution_result}"', bot)
        return

    emoji_result = check_emoji(text)
    if emoji_result:
        await message_delete_event(group, member, message, 'сообщение содержит только эмодзи', bot)
        return

    full_check_result = check_full_words(text, dictionary.full_words)
    if full_check_result:
        await message_delete_event(group, member, message, f'слово "{full_check_result}"', bot)
        return

    partial_search_result = check_partial_words(text, dictionary.partial_words)
    if partial_search_result:
        word, part = partial_search_result
        if part:
            reason = f'часть "{part}" в слове "{word}"'
        else:
            reason = f'слово "{part}"'

        await message_delete_event(group, member, message, reason, bot)
        return

    regex_search_result = check_regexps(text, dictionary.regex_patterns)
    if regex_search_result:
        word, pattern = regex_search_result
        await message_delete_event(group, member, message, f'шаблон "{pattern}" в слове "{word}"', bot)
        return

    return
