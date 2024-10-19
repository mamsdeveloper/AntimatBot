from antispambot.storage.base import BaseStorageModel


class Group(BaseStorageModel):
    title: str
    active: bool
    strike_mode: bool
    strike_limit: int
    ignored_users: list[str]