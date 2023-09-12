from datetime import datetime
from typing import Any, Awaitable, Callable, Dict

from aiogram.dispatcher.middlewares.base import BaseMiddleware
from aiogram.types import TelegramObject
from deta import Base  # type: ignore


EXPIRE_IN = 604800  # week


class LoggingMiddleware(BaseMiddleware):
    def __init__(self, expire_in: int = EXPIRE_IN) -> None:
        self.expire_in = expire_in

    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any]
    ) -> Any:
        time = datetime.now()

        logging_base = Base('logs')
        logging_base.put(
            key=str(2 * 10**9 - time.timestamp()),
            data={'time': time.isoformat(), 'update': event.json()},
            expire_in=self.expire_in,
        )

        return await handler(event, data)
