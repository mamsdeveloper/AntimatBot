from typing import Any, Awaitable, Callable, Dict

from aiogram import Router
from aiogram.types import Message

from . import group_message, new_group


router = Router()
router.include_router(group_message.router)
router.include_router(new_group.router)


@router.message.middleware()
async def group_chat_middleware(
    handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
    event: Message,
    data: Dict[str, Any]
) -> Any:
    if event.from_user and event.from_user.full_name == 'Telegram':
        return
    
    if event.chat.type in ('group', 'supergroup'):
        return await handler(event, data)
