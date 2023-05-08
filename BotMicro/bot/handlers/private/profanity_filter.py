from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from bot import messages

router = Router()


@router.message(F.text == 'Активировать фильтр матов')
async def activate_profanity_filter(message: Message, state: FSMContext):
    await state.clear()

    await message.answer(messages.SUCCESSFUL_ACTIVATE_FILTER)


@router.message(F.text == 'Выключить фильтр матов')
async def deactivate_profanity_filter(message: Message, state: FSMContext):
    await state.clear()

    await message.answer(messages.SUCCESSFUL_DEACTIVATE_FILTER)
