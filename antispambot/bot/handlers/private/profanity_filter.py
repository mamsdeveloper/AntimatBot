from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from antispambot.bot import messages
from antispambot.bot.utils.chat_queries import get_chat_groups_dictionaries
from antispambot.storage.storages import dictionary_storage

router = Router()


@router.message(F.text == 'Активировать фильтр матов')
async def activate_profanity_filter(message: Message, state: FSMContext):
    await state.clear()

    chat_dicts = get_chat_groups_dictionaries(message.chat.id)
    for dictionary in chat_dicts:
        dictionary.profanity_filter = True
        dictionary_storage.save(dictionary)

    await message.answer(messages.SUCCESSFUL_ACTIVATE_FILTER)


@router.message(F.text == 'Выключить фильтр матов')
async def deactivate_profanity_filter(message: Message, state: FSMContext):
    await state.clear()

    chat_dicts = get_chat_groups_dictionaries(message.chat.id)
    for dictionary in chat_dicts:
        dictionary.profanity_filter = False
        dictionary_storage.save(dictionary)

    await message.answer(messages.SUCCESSFUL_DEACTIVATE_FILTER)
