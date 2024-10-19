from pydantic import Field

from antispambot.storage.base import BaseStorageModel


class Dictionary(BaseStorageModel):
    full_words: list[str]
    partial_words: list[str]
    regex_patterns: list[str] = Field(default_factory=list)
    stop_words: list[str] = Field(default_factory=list)
    profanity_filter: bool = False
