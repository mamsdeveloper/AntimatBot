import logging
from antispambot.models.dictionary import Dictionary
from antispambot.models.group import Group
from antispambot.storage.storages import (
    chat_storage,
    dictionary_storage,
    group_storage,
)


logger = logging.getLogger(__name__)


def get_chat_groups(chat_id: int) -> list[Group]:
    groups: list[Group] = []

    chat = chat_storage.get(str(chat_id))
    if chat is None:
        return groups

    for group_key in chat.groups:
        group = group_storage.get(group_key)
        if group is None:
            continue

        groups.append(group)

    return groups


def get_chat_groups_dictionaries(chat_id: int) -> list[Dictionary]:
    dictionaries: list[Dictionary] = []

    chat = chat_storage.get(str(chat_id))
    if chat is None:
        return dictionaries

    for group_key in chat.groups:
        dictionary = dictionary_storage.get(group_key)
        if dictionary is None:
            continue

        dictionaries.append(dictionary)

    return dictionaries


def get_chat_groups_and_dictionaries(chat_id: int) -> list[tuple[Group, Dictionary]]:
    groups_and_dicts: list[tuple[Group, Dictionary]] = []

    chat = chat_storage.get(str(chat_id))
    if chat is None:
        return groups_and_dicts

    for group_key in chat.groups:
        group = group_storage.get(group_key)
        if group is None:
            continue

        dictionary = dictionary_storage.get(group_key)
        if dictionary is None:
            continue

        groups_and_dicts.append((group, dictionary))

    return groups_and_dicts
