from aiogram import Router

from .groups import router as groups_router
from .private import  router as private_router

root_router = Router()
root_router.include_router(private_router)
root_router.include_router(groups_router)
