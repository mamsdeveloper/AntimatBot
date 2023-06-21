from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from odetam.exceptions import ItemNotFound

from bot import messages
from bot.utils.chat_queries import get_chat_groups_and_dictionaries
from models import Dictionary


router = Router()


@router.message(F.text.in_(['Показать слова']))
async def list_words_handler(message: Message, state: FSMContext):
    await state.clear()

    try:
        default_dict: Dictionary = await Dictionary.get('default')
    except ItemNotFound:
        return

    groups_and_dicts = await get_chat_groups_and_dictionaries(message.chat.id)
    for group, dictionary in groups_and_dicts:
        full_words = sorted(set(dictionary.full_words))
        partial_words = sorted(set(dictionary.partial_words))
        regex_patterns = sorted(set(dictionary.regex_patterns))
        stop_words = sorted(set(dictionary.stop_words))

        text = messages.build_words_list(group.title, full_words, partial_words, regex_patterns, stop_words)
        text_parts = [text[i:i+4096] for i in range(0, len(text), 4096)]
        for part in text_parts:
            await message.answer(part)
