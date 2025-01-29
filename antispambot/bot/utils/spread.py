from asyncio import gather
from typing import Union

from aiogram import Bot
from aiogram.types import InlineKeyboardMarkup, Message, ReplyKeyboardMarkup
from pydantic import BaseModel


class SendMessage(BaseModel):
    text: str
    reply_markup: Union[InlineKeyboardMarkup, ReplyKeyboardMarkup, None]


async def spread_messages(
    chat_ids: list[int],
    messages: list[SendMessage],
    bot: Bot
) -> list[Union[BaseException, Message]]:
    targets = [
        bot.send_message(
            chat_id,
            text=message.text,
            reply_markup=message.reply_markup
        )
        for chat_id in chat_ids
        for message in messages
    ]
    results: list[Union[BaseException, Message]] = await gather(
        *targets,
        return_exceptions=True
    )
    return results


async def forward_messages(
    chat_ids: list[int],
    messages: list[Message],
    bot: Bot
) -> list[Union[BaseException, Message]]:
    targets = [
        bot.forward_message(
            chat_id,
            message.chat.id,
            message.message_id
        )
        for chat_id in chat_ids
        for message in messages
    ]
    results: list[Union[BaseException, Message]] = await gather(
        *targets,
        return_exceptions=True
    )
    return results
