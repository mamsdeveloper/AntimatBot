from odetam.async_model import AsyncDetaModel

from models.events import Event


class History(AsyncDetaModel):
    events: list[Event]
