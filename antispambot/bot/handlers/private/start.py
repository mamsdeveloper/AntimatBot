from aiogram import F, Router
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import KeyboardButton, Message, ReplyKeyboardMarkup

from antispambot.bot import messages
from antispambot.models.chat import Chat
from antispambot.storage.storages import chat_storage

router = Router()


@router.message(CommandStart())
@router.message(F.text == 'Начать диалог')
async def start_handler(message: Message, state: FSMContext) -> None:
    await state.clear()
    await message.answer(
        messages.GREETING,
        reply_markup=ReplyKeyboardMarkup(keyboard=[
            [
                KeyboardButton(text='Начать диалог'),
                KeyboardButton(text='Мои группы и настройки'),
                KeyboardButton(text='Показать слова')
            ],
            [
                KeyboardButton(text='Добавить полные слова'),
                KeyboardButton(text='Убрать полные слова'),
                KeyboardButton(text='Убрать все полные слова'),
            ],
            [
                KeyboardButton(text='Добавить частичные слова'),
                KeyboardButton(text='Убрать частичные слова'),
                KeyboardButton(text='Убрать все частичные слова'),
            ],
            [
                KeyboardButton(text='Добавить шаблоны слов'),
                KeyboardButton(text='Убрать шаблоны слов'),
                KeyboardButton(text='Убрать все шаблоны'),
            ],
            [
                KeyboardButton(text='Добавить пропуск слов'),
                KeyboardButton(text='Убрать пропуск слов'),
                KeyboardButton(text='Убрать все пропуски'),
            ],
            [
                KeyboardButton(text='Активировать фильтр матов'),
                KeyboardButton(text='Выключить фильтр матов'),
            ],
            [
                KeyboardButton(text='Включить баны'),
                KeyboardButton(text='Отключить баны'),
                KeyboardButton(text='Установить лимит бана'),
            ],
            [
                KeyboardButton(text='Добавить исключение'),
                KeyboardButton(text='Убрать исключение'),
                KeyboardButton(text='Пользователи-исключения'),
            ],
        ])
    )
    if not message.from_user:
        return

    chat = chat_storage.get(str(message.chat.id))
    if chat is None:
        chat = Chat(
            key=str(message.chat.id),
            username=message.from_user.full_name,
            groups=[]
        )
        chat_storage.save(chat)
