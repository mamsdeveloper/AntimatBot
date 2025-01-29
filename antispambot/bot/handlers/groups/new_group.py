from aiogram import Router
from aiogram.filters import IS_ADMIN, ChatMemberUpdatedFilter
from aiogram.types import ChatMemberUpdated

from antispambot.models.dictionary import Dictionary
from antispambot.models.group import Group
from antispambot.storage.storages import dictionary_storage, group_storage

router = Router()


@router.my_chat_member(ChatMemberUpdatedFilter(IS_ADMIN))
async def new_group_handler(event: ChatMemberUpdated):
    group = Group(
        key=str(event.chat.id),
        title=event.chat.title or '',
        active=True,
        strike_mode=True,
        strike_limit=3,
        ignored_users=[]
    )
    group_storage.save(group)

    dictionary = dictionary_storage.get('default')
    if dictionary is None:
        dictionary = Dictionary(key='default', full_words=[], partial_words=[])

    dictionary.key = group.key
    dictionary_storage.save(dictionary)
