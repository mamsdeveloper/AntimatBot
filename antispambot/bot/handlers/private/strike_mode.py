from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from bot import messages
from bot.utils.chat_queries import get_chat_groups
from bot.states.private import StrikeLimitState


router = Router()


@router.message(F.text.in_(['Включить баны', 'Отключить баны']))
async def strike_mode_handler(message: Message, state: FSMContext):
    await state.clear()

    chat_groups = await get_chat_groups(message.chat.id)
    for group in chat_groups:
        group.strike_mode = message.text == 'Включить баны'
        await group.save()
    
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
    
    chat_groups = await get_chat_groups(message.chat.id)
    for group in chat_groups:
        group.strike_limit = strike_limit
        await group.save()
    
    await message.answer(messages.STRIKE_LIMIT_UPDATED)
    await state.clear()