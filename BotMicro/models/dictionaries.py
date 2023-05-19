from typing import Optional
from odetam.async_model import AsyncDetaModel


class Dictionary(AsyncDetaModel):
    full_words: list[str]
    partial_words: list[str]
    profanity_filter: bool = False

    class Config:
        table_name = 'dictionaries'
