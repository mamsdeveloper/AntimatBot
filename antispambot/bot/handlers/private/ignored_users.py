from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from antispambot.bot import messages
from antispambot.bot.states.private import IgnoredUserState
from antispambot.bot.utils.chat_queries import get_chat_groups
from antispambot.storage.storages import group_storage

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

    groups = get_chat_groups(message.chat.id)
    for group in groups:
        if command == 'Добавить исключение':
            group.ignored_users.append(message.text)
        elif command == 'Убрать исключение':
            if message.text in group.ignored_users:
                group.ignored_users.remove(message.text)

        group_storage.save(group)

    await message.answer(messages.IGNORED_USERS_UPDATED)


@router.message(F.text == 'Пользователи-исключения')
async def list_ignored_users_handler(message: Message, state: FSMContext):
    await state.clear()

    groups = get_chat_groups(message.chat.id)
    for group in groups:
        await message.answer(messages.build_ignored_users_list(group))
