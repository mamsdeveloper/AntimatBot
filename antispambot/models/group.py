from odetam.async_model import AsyncDetaModel


class Group(AsyncDetaModel):
    title: str
    active: bool
    strike_mode: bool
    strike_limit: int
    ignored_users: list[str]