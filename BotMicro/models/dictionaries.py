from odetam.async_model import AsyncDetaModel


class Dictionary(AsyncDetaModel):
    full_words: list[str]
    partial_words: list[str]


    class Config:
        table_name = 'dictionaries'
