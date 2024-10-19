from aiogram import Router

from antispambot.bot.handlers.error import router as error_router
from antispambot.bot.handlers.groups import router as groups_router
from antispambot.bot.handlers.private import router as private_router

root_router = Router()
root_router.include_router(private_router)
root_router.include_router(groups_router)
root_router.include_router(error_router)
