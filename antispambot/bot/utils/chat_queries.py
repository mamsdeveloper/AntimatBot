from odetam.exceptions import ItemNotFound

from models import Chat, Group, Dictionary


async def get_chat_groups(chat_id: int) -> list[Group]:
    groups: list[Group] = []

    try:
        chat: Chat = await Chat.get(str(chat_id))
    except ItemNotFound:
        return groups

    for group_key in chat.groups:
        try:
            group: Group = await Group.get(group_key)
        except ItemNotFound:
            continue

        groups.append(group)

    return groups


async def get_chat_groups_dictionaries(chat_id: int) -> list[Dictionary]:
    dictionaries: list[Dictionary] = []

    try:
        chat: Chat = await Chat.get(str(chat_id))
    except ItemNotFound:
        return dictionaries

    for group_key in chat.groups:
        try:
            dictionary: Dictionary = await Dictionary.get(group_key)
        except ItemNotFound:
            continue

        dictionaries.append(dictionary)

    return dictionaries


async def get_chat_groups_and_dictionaries(chat_id: int) -> list[tuple[Group, Dictionary]]:
    groups_and_dicts: list[tuple[Group, Dictionary]] = []

    try:
        chat: Chat = await Chat.get(str(chat_id))
    except ItemNotFound:
        return groups_and_dicts

    for group_key in chat.groups:
        try:
            group: Group = await Group.get(group_key)
        except ItemNotFound:
            continue

        try:
            dictionary: Dictionary = await Dictionary.get(group_key)
        except ItemNotFound:
            continue

        groups_and_dicts.append((group, dictionary))

    return groups_and_dicts
