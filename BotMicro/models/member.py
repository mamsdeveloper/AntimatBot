from odetam.async_model import AsyncDetaModel
from pydantic import Field


class Member(AsyncDetaModel):
    strikes_count: dict[str, int]
    messages_count: dict[str, int] = Field(default_factory=dict)
