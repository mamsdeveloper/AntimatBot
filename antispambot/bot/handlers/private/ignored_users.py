from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from bot.states.private import IgnoredUserState

from bot.utils.chat_queries import get_chat_groups
from bot import messages

router = Router()


@router.message(F.text.in_(['Добавить исключение', 'Убрать исключение']))
async def update_ignored_users_handler(message: Message, state: FSMContext):
    await message.answer(messages.ASK_IGNORED_USER)
    await state.update_data(command=message.text)
    await state.set_state(IgnoredUserState.full_name)


@router.message(IgnoredUserState.full_name, F.text)
async def full_name_handler(message: Message, state: FSMContext):
    if not message.text:
        return
    
    data = await state.get_data()
    command = data['command']
    await state.clear()

    groups = await get_chat_groups(message.chat.id)
    for group in groups:
        if command == 'Добавить исключение':
            group.ignored_users.append(message.text)
        elif command == 'Убрать исключение':
            if message.text in group.ignored_users:
                group.ignored_users.remove(message.text)
        
        await group.save()
    
    await message.answer(messages.IGNORED_USERS_UPDATED)


@router.message(F.text == 'Пользователи-исключения')
async def list_ignored_users_handler(message: Message, state: FSMContext):
    await state.clear()
    
    groups = await get_chat_groups(message.chat.id)
    for group in groups:
        await message.answer(messages.build_ignored_users_list(group))
        
