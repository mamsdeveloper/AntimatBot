from typing import Any, Awaitable, Callable, Dict

from aiogram import Router
from aiogram.types import Message, TelegramObject

from antispambot.bot.handlers.groups.group_message import (
    router as group_message_router,
)
from antispambot.bot.handlers.groups.new_group import (
    router as new_group_router,
)
from antispambot.bot.handlers.groups.new_member import (
    router as new_member_router,
)
from antispambot.bot.middlewares.active_group import ActiveGroupMiddleware

router = Router()
router.include_router(group_message_router)
router.include_router(new_group_router)
router.include_router(new_member_router)

router.message.middleware(ActiveGroupMiddleware())
router.edited_message.middleware(ActiveGroupMiddleware())
router.chat_member.middleware(ActiveGroupMiddleware())


@router.message.middleware
async def group_chat_middleware(
    handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
    event: TelegramObject,
    data: Dict[str, Any]
) -> Any:
    if isinstance(event, Message):
        if event.from_user and event.from_user.full_name == 'Telegram':
            return

        if event.chat.type in ('group', 'supergroup'):
            return await handler(event, data)
