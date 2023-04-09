from typing import Any, Callable, Awaitable, Optional

from aiogram import F, Router
from aiogram.types import Message
from odetam.exceptions import ItemNotFound

from analysis.checking import check_full_words, check_partial_words
from analysis.normilize import get_normalized_text
from bot.utils.group_utils import is_user_admin

from bot.utils.message_delete_event import message_delete_event
from models import Dictionary, Group


router = Router()


@router.message.middleware()
async def active_group_middleware(
    handler: Callable[[Message, dict[str, Any]], Awaitable[Any]],
    event: Message,
    data: dict[str, Any]
) -> Optional[Message]:
    if not event.from_user:
        return

    is_admin = await is_user_admin(event.from_user, event.chat)
    if is_admin:
        return
        
    chat_id = event.chat.id
    try:
        group: Group = await Group.get(str(chat_id))
    except ItemNotFound:
        return
    
    if not group.active:
        return
    
    if event.from_user.full_name in group.ignored_users:
        return
    
    data['group'] = group
    return await handler(event, data)


@router.message(F.text, F.from_user.is_bot == False)
async def group_message_handler(message: Message, group: Group) -> None:
    if not message.text:
        return
    
    try:
        dictionary: Dictionary = await Dictionary.get(group.key)
    except ItemNotFound:
        return

    full_check_result = check_full_words(message.text, dictionary.full_words)
    if full_check_result:
        await message_delete_event(message, f'слово "{full_check_result}"')
        return

    partial_search_result = check_partial_words(message.text, dictionary.partial_words)
    if partial_search_result:
        word, part = partial_search_result
        await message_delete_event(message, f'часть "{part}" в слове "{word}"')
        return
    
    text = get_normalized_text(message.text)

    full_check_result = check_full_words(text, dictionary.full_words)
    if full_check_result:
        await message_delete_event(message, f'слово "{full_check_result}"')
        return

    partial_search_result = check_partial_words(text, dictionary.partial_words)
    if partial_search_result:
        word, part = partial_search_result
        await message_delete_event(message, f'часть "{part}" в слове "{word}"')
        return
