from typing import Any, Awaitable, Callable, Dict
from aiogram import Router
from aiogram.types import Message

from . import groups, start, edit_words, list_words, strike_mode, ignored_users


router = Router()
router.include_router(start.router)
router.include_router(groups.router)
router.include_router(edit_words.router)
router.include_router(list_words.router)
router.include_router(strike_mode.router)
router.include_router(ignored_users.router)


@router.message.middleware()
async def private_chat_middleware(
    handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
    event: Message,
    data: Dict[str, Any]
) -> Any:
    if event.chat.type == 'private':
        return await handler(event, data)
