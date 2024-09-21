from aiogram import Bot
from fastapi import APIRouter, Depends

from web.stubs import SecretStub, BotStub

develop_router = APIRouter(prefix='/develop', tags=['Develop'])


@develop_router.get('')
async def get_meta_info(
    expected_secret: str = Depends(SecretStub),
    bot: Bot = Depends(BotStub),
):
    webhook_info = await bot.get_webhook_info()
    return {'secret_token': expected_secret, 'webhook_info': webhook_info}
