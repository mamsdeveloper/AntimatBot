from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from antispambot.bot import messages
from antispambot.bot.utils.chat_queries import get_chat_groups_and_dictionaries
from antispambot.storage.storages import dictionary_storage

router = Router()


@router.message(F.text.in_(['Показать слова']))
async def list_words_handler(message: Message, state: FSMContext):
    await state.clear()

    default_dict = dictionary_storage.get('default')
    if default_dict is None:
        return

    groups_and_dicts = get_chat_groups_and_dictionaries(message.chat.id)
    for group, dictionary in groups_and_dicts:
        full_words = sorted(set(dictionary.full_words))
        partial_words = sorted(set(dictionary.partial_words))
        regex_patterns = sorted(set(dictionary.regex_patterns))
        stop_words = sorted(set(dictionary.stop_words))

        text = messages.build_words_list(group.title, full_words, partial_words, regex_patterns, stop_words)
        text_parts = [text[i:i+4096] for i in range(0, len(text), 4096)]
        for part in text_parts:
            await message.answer(part)
