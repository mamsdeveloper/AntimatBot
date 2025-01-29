from typing import Any, Awaitable, Callable, Dict

from aiogram.dispatcher.middlewares.base import BaseMiddleware
from aiogram.types import Message, TelegramObject

from antispambot.bot.utils.group_utils import is_user_admin
from antispambot.storage.storages import group_storage


class ActiveGroupMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:
        if isinstance(event, Message):
            if not event.from_user:
                return

            if event.from_user.full_name == 'Telegram':
                return

            if event.bot is None:
                return

            is_admin = await is_user_admin(event.from_user, event.chat, event.bot)
            if is_admin:
                return

            chat_id = event.chat.id
            group = group_storage.get(str(chat_id))
            if group is None:
                return

            if not group.active:
                return

            if event.from_user.full_name in group.ignored_users:
                return

            data['group'] = group

        return await handler(event, data)
