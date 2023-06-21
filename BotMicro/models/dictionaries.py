from typing import Optional
from odetam.async_model import AsyncDetaModel
from pydantic import Field


class Dictionary(AsyncDetaModel):
    full_words: list[str]
    partial_words: list[str]
    regex_patterns: list[str] = Field(default_factory=list)
    stop_words: list[str] = Field(default_factory=list)
    profanity_filter: bool = False

    class Config:
        table_name = 'dictionaries'
