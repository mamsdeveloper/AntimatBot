from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from antispambot.bot import messages
from antispambot.bot.states.private import EditWords
from antispambot.bot.utils.chat_queries import get_chat_groups_dictionaries
from antispambot.storage.storages import dictionary_storage

router = Router()


@router.message(F.text.in_(['Убрать все полные слова', 'Убрать все частичные слова', 'Убрать все шаблоны', 'Убрать все пропуски']))
async def drop_words_handler(message: Message, state: FSMContext):
    await state.clear()

    chat_dicts = get_chat_groups_dictionaries(message.chat.id)
    for dictionary in chat_dicts:
        if message.text == 'Убрать все полные слова':
            dictionary.full_words = []
        elif message.text == 'Убрать все частичные слова':
            dictionary.partial_words = []
        elif message.text == 'Убрать все шаблоны':
            dictionary.regex_patterns = []

        dictionary_storage.save(dictionary)

    await message.answer(messages.SUCCESSFUL_DROP_WORDS)


@router.message(F.text.in_(['Восстановить словарь полных слов', 'Восстановить словарь частичных слов']))
async def repair_words_handler(message: Message, state: FSMContext):
    await state.clear()

    default_dict = dictionary_storage.get('default')
    if default_dict is None:
        return

    chat_dicts = get_chat_groups_dictionaries(message.chat.id)
    for dictionary in chat_dicts:
        if message.text == 'Восстановить словарь полных слов':
            dictionary.full_words = default_dict.full_words
        elif message.text == 'Восстановить словарь частичных слов':
            dictionary.partial_words = default_dict.partial_words

        dictionary_storage.save(dictionary)

    await message.answer(messages.SUCCESSFUL_REPAIR_WORDS)


@router.message(F.text.in_([
    'Добавить полные слова',
    'Убрать полные слова',
    'Добавить частичные слова',
    'Убрать частичные слова',
    'Добавить шаблоны слов',
    'Убрать шаблоны слов',
    'Добавить пропуск слов',
    'Убрать пропуск слов'
]))
async def edit_words_handler(message: Message, state: FSMContext):
    await state.clear()
    await state.update_data(command=message.text)
    await message.answer(messages.ASK_WORDS)
    await state.set_state(EditWords.words)


@router.message(EditWords.words, F.text)
async def words_handler(message: Message, state: FSMContext):
    if not message.text:
        return

    words = message.text.split(',')
    words = [word.strip().lower() for word in words]

    data = await state.get_data()
    action = data.get('command')
    await state.clear()

    chat_dicts = get_chat_groups_dictionaries(message.chat.id)
    for dictionary in chat_dicts:
        if action == 'Добавить полные слова':
            dictionary.full_words.extend(words)
        elif action == 'Убрать полные слова':
            dictionary.full_words = [word for word in dictionary.full_words if word not in words]
        elif action == 'Добавить частичные слова':
            dictionary.partial_words.extend(words)
        elif action == 'Убрать частичные слова':
            dictionary.partial_words = [word for word in dictionary.partial_words if word not in words]
        elif action == 'Добавить шаблоны слов':
            dictionary.regex_patterns.extend(words)
        elif action == 'Убрать шаблоны слов':
            dictionary.regex_patterns = [word for word in dictionary.regex_patterns if word not in words]
        elif action == 'Добавить пропуск слов':
            dictionary.stop_words.extend(words)
        elif action == 'Убрать пропуск слов':
            dictionary.stop_words = [word for word in dictionary.stop_words if word not in words]

        dictionary_storage.save(dictionary)

    await message.answer(messages.SUCCESSFUL_UPDATE_WORDS)