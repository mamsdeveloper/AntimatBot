from aiogram import Router, F
from aiogram.filters import ChatMemberUpdatedFilter, IS_ADMIN
from aiogram.types import ChatMemberUpdated
from bot.handlers.private import ignored_users

from models import Group, History, Dictionary


router = Router()


@router.my_chat_member(ChatMemberUpdatedFilter(IS_ADMIN))
async def new_group_handler(event: ChatMemberUpdated):
    group = Group(
        key=str(event.chat.id),
        title=event.chat.title or '',
        active=True ,
        strike_mode=True,
        strike_limit=3,
        ignored_users=[]
    )
    await group.save()

    history = History(key=group.key, events=[])
    await history.save()

    dictionary: Dictionary = await Dictionary.get('default')
    dictionary.key = group.key
    await dictionary.save()