from pathlib import Path

from antispambot.models.chat import Chat
from antispambot.models.dictionary import Dictionary
from antispambot.models.event import Event
from antispambot.models.group import Group
from antispambot.models.member import Member
from antispambot.storage.base import JsonStorage

STORAGE_PATH = Path('./storage')

chat_storage = JsonStorage(Chat, STORAGE_PATH.joinpath('chat.json'))
dictionary_storage = JsonStorage(Dictionary, STORAGE_PATH.joinpath('dictionary.json'))
event_storage = JsonStorage(Event, STORAGE_PATH.joinpath('event.json'))
group_storage = JsonStorage(Group, STORAGE_PATH.joinpath('group.json'))
member_storage = JsonStorage(Member, STORAGE_PATH.joinpath('member.json'))
