from odetam.async_model import AsyncDetaModel


class Member(AsyncDetaModel):
    strikes_count: dict[str, int]