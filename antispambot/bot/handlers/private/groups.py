from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from bot import messages
from bot.utils.chat_queries import get_chat_groups_and_dictionaries


router = Router()


@router.message(F.text == 'Мои группы и настройки')
async def start_handler(message: Message, state: FSMContext) -> None:
    await state.clear()

    groups_and_dicts = await get_chat_groups_and_dictionaries(message.chat.id)
    if not groups_and_dicts:
        await message.answer(messages.NO_AVAILABLE_GROUPS)
    else:
        await message.answer(messages.build_groups_list(groups_and_dicts))
 