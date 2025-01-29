from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums.parse_mode import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.utils.callback_answer import CallbackAnswerMiddleware

from antispambot.bot.handlers import root_router as root_router
from antispambot.bot.middlewares.callback_message import (
    CallbackMessageMiddleware,
)
from antispambot.bot.middlewares.logging import LoggingMiddleware


def create_bot(token: str) -> Bot:
    bot = Bot(token, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    return bot


def create_dispatcher() -> Dispatcher:
    storage = MemoryStorage()
    dispatcher = Dispatcher(storage=storage)
    dispatcher.include_router(root_router)
    dispatcher.callback_query.middleware(CallbackMessageMiddleware())
    dispatcher.callback_query.middleware(CallbackAnswerMiddleware())
    dispatcher.update.middleware(LoggingMiddleware())
    return dispatcher
