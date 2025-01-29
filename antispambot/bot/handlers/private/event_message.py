from aiogram import Bot, Router
from aiogram.types import CallbackQuery, Message

from antispambot.bot.callbacks.event_message import (
    AllowNicknameCallback,
    BanMemberCallback,
    DeleteMessageCallback,
    UnbanMemberCallback,
)
from antispambot.models.member import Member
from antispambot.storage.storages import member_storage

router = Router()


@router.callback_query(BanMemberCallback.filter())
async def ban_member_handler(query: CallbackQuery, message: Message, callback_data: BanMemberCallback, bot: Bot) -> None:
    await bot.ban_chat_member(callback_data.chat_id, callback_data.user_id)
    await message.edit_reply_markup(reply_markup=None)


@router.callback_query(UnbanMemberCallback.filter())
async def unban_member_handler(query: CallbackQuery, message: Message, callback_data: UnbanMemberCallback, bot: Bot) -> None:
    await bot.unban_chat_member(callback_data.chat_id, callback_data.user_id, only_if_banned=True)

    group_key = str(callback_data.chat_id)
    member = member_storage.get(str(callback_data.user_id))
    if member is None:
        member = Member(key=str(callback_data.user_id), strikes_count={})

    member.strikes_count[group_key] = 0
    member_storage.save(member)
    await message.edit_reply_markup(reply_markup=None)


@router.callback_query(AllowNicknameCallback.filter())
async def allow_nickname_handler(query: CallbackQuery, message: Message, callback_data: AllowNicknameCallback, bot: Bot) -> None:
    await bot.unban_chat_member(callback_data.chat_id, callback_data.user_id, only_if_banned=True)

    member = member_storage.get(str(callback_data.user_id))
    if member is None:
        member = Member(key=str(callback_data.user_id), strikes_count={})

    member.strikes_count[str(callback_data.chat_id)] = 0
    member.nickname_pass[str(callback_data.chat_id)] = True
    member_storage.save(member)
    await message.edit_reply_markup(reply_markup=None)


@router.callback_query(DeleteMessageCallback.filter())
async def delete_message_handler(query: CallbackQuery, message: Message, callback_data: DeleteMessageCallback, bot: Bot) -> None:
    await bot.delete_message(callback_data.chat_id, callback_data.message_id)
    await message.edit_reply_markup(reply_markup=None)
