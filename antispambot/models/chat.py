from odetam.async_model import AsyncDetaModel


class Chat(AsyncDetaModel):
    username: str 
    groups: list[str]
