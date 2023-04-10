from typing import Any, Callable, Awaitable

from aiogram.types import Message
from odetam.exceptions import ItemNotFound

from bot.utils.group_utils import is_user_admin

from models import Group

from typing import Any, Awaitable, Callable, Dict

from aiogram.dispatcher.middlewares.base import BaseMiddleware
from aiogram.types import TelegramObject


class ActiveGroupMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any]
    ) -> Any:
        if isinstance(event, Message):
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
