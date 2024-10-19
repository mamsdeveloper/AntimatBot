from antispambot.storage.base import BaseStorageModel


class Chat(BaseStorageModel):
    username: str
    groups: list[str]
