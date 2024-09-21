from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class Event(BaseModel):
    event: str = ''
    username: Optional[str]
    full_name: str
    time: datetime
    message_text: Optional[str]
    reason: Optional[str]


class StrikeMemberEvent(Event):
    event = 'ban_user'


class DeleteMessageEvent(Event):
    event = 'delete_message'


class ProfanityFilterEvent(Event):
    event = 'profanity_filter'
