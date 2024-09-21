from typing import Any, Awaitable, Callable, Dict

from aiogram import Router
from aiogram.types import Message

from .edit_words import router as edit_words_router
from .event_message import router as event_message_router
from .groups import router as groups_router
from .ignored_users import router as ignored_users_router
from .list_words import router as list_words_router
from .start import router as start_router
from .strike_mode import router as strike_mode_router
from .profanity_filter import router as profanity_filter_router

router = Router()
router.include_router(start_router)
router.include_router(groups_router)
router.include_router(edit_words_router)
router.include_router(list_words_router)
router.include_router(strike_mode_router)
router.include_router(ignored_users_router)
router.include_router(event_message_router)
router.include_router(profanity_filter_router)


@router.message.middleware()
async def private_chat_middleware(
    handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
    event: Message,
    data: Dict[str, Any]
) -> Any:
    if event.chat.type == 'private':
        return await handler(event, data)
