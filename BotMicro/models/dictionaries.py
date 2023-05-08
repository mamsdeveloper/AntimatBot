from typing import Optional
from odetam.async_model import AsyncDetaModel


class Dictionary(AsyncDetaModel):
    full_words: list[str]
    partial_words: list[str]
    profanity_trie: Optional[str] = None  # pickled VarTrie

    class Config:
        table_name = 'dictionaries'
