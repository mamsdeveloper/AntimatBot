from aiogram import Bot, Router
from aiogram.types import CallbackQuery, Message
from odetam.exceptions import ItemNotFound

from bot.callbacks.event_message import AllowNicknameCallback, BanMemberCallback, DeleteMessageCallback, UnbanMemberCallback
from models.member import Member

router = Router()


@router.callback_query(BanMemberCallback.filter())
async def ban_member_handler(query: CallbackQuery, message: Message, callback_data: BanMemberCallback, bot: Bot) -> None:
    await bot.ban_chat_member(callback_data.chat_id, callback_data.user_id)
    await message.edit_reply_markup(reply_markup=None)


@router.callback_query(UnbanMemberCallback.filter())
async def unban_member_handler(query: CallbackQuery, message: Message, callback_data: UnbanMemberCallback, bot: Bot) -> None:
    await bot.unban_chat_member(callback_data.chat_id, callback_data.user_id, only_if_banned=True)

    group_key = str(callback_data.chat_id)
    try:
        member: Member = await Member.get(str(callback_data.user_id))
    except ItemNotFound:
        member = Member(key=str(callback_data.user_id), strikes_count={})

    member.strikes_count[group_key] = 0
    await member.save()

    await message.edit_reply_markup(reply_markup=None)


@router.callback_query(AllowNicknameCallback.filter())
async def allow_nickname_handler(query: CallbackQuery, message: Message, callback_data: AllowNicknameCallback, bot: Bot) -> None:
    await bot.unban_chat_member(callback_data.chat_id, callback_data.user_id, only_if_banned=True)

    try:
        member: Member = await Member.get(str(callback_data.user_id))
    except ItemNotFound:
        member = Member(key=str(callback_data.user_id), strikes_count={})

    member.strikes_count[str(callback_data.chat_id)] = 0
    member.nickname_pass[str(callback_data.chat_id)] = True
    await member.save()

    await message.edit_reply_markup(reply_markup=None)


@router.callback_query(DeleteMessageCallback.filter())
async def delete_message_handler(query: CallbackQuery, message: Message, callback_data: DeleteMessageCallback, bot: Bot) -> None:
    await bot.delete_message(callback_data.chat_id, callback_data.message_id)
    await message.edit_reply_markup(reply_markup=None)
