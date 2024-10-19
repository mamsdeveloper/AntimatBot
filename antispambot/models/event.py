from datetime import datetime
from typing import Optional

from antispambot.storage.base import BaseStorageModel


class Event(BaseStorageModel):
    event: str
    username: Optional[str]
    full_name: str
    time: datetime
    message_text: Optional[str]
    reason: Optional[str]


class StrikeMemberEvent(Event):
    event: str = 'ban_user'


class DeleteMessageEvent(Event):
    event: str = 'delete_message'
