from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from antispambot.bot import messages
from antispambot.bot.states.private import StrikeLimitState
from antispambot.bot.utils.chat_queries import get_chat_groups
from antispambot.storage.storages import group_storage

router = Router()


@router.message(F.text.in_(['Включить баны', 'Отключить баны']))
async def strike_mode_handler(message: Message, state: FSMContext):
    await state.clear()

    chat_groups = get_chat_groups(message.chat.id)
    for group in chat_groups:
        group.strike_mode = message.text == 'Включить баны'
        group_storage.save(group)

    if message.text == 'Включить баны':
        await message.answer(messages.STRIKES_ENABLED)
    elif message.text == 'Отключить баны':
        await message.answer(messages.STRIKES_DISABLED)


@router.message(F.text == 'Установить лимит бана')
async def strike_limit_handler(message: Message, state: FSMContext):
    await message.answer(messages.ASK_STRIKE_LIMIT)
    await state.set_state(StrikeLimitState.limit)


@router.message(StrikeLimitState.limit, F.text)
async def strike_limit_number_handler(message: Message, state: FSMContext):
    if not message.text:
        return

    if not message.text.isdigit():
        await message.answer(messages.STRIKE_LIMIT_NOT_DIGIT)
        return

    strike_limit = int(message.text)

    chat_groups = get_chat_groups(message.chat.id)
    for group in chat_groups:
        group.strike_limit = strike_limit
        group_storage.save(group)

    await message.answer(messages.STRIKE_LIMIT_UPDATED)
    await state.clear()
