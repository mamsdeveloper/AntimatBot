from pydantic import Field

from antispambot.storage.base import BaseStorageModel


class Member(BaseStorageModel):
    strikes_count: dict[str, int]
    messages_count: dict[str, int] = Field(default_factory=dict)
    nickname_pass: dict[str, bool] = Field(default_factory=dict)
